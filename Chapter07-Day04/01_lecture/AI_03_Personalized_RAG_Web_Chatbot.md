# 개인화 RAG 웹 챗봇 만들기

> Ollama + multilingual-E5 + LangChain + Redis Memory/AOF + Milvus + Streamlit

## 1. 프로젝트 목표

이 프로젝트는 사용자가 웹 URL이나 PPTX·DOCX 문서를 제출하면 내용을 수집하고, 한국어 임베딩 모델로 벡터화해 Milvus에 저장한 뒤, 로컬 EXAONE이 검색 근거와 이전 대화를 함께 읽고 답하는 개인화 웹 챗봇을 만든다.

완성 프로그램은 다음 기능을 제공한다.

1. 블로그·뉴스·공식 사이트 URL을 제출해 본문을 수집한다.
2. PPTX·DOCX 파일을 웹 화면에서 업로드한다.
3. `intfloat/multilingual-e5-small`로 문서와 질문을 384차원 벡터로 변환한다.
4. 사용자별 문서 벡터와 metadata를 Milvus에 저장한다.
5. Milvus가 질문과 의미가 가까운 Top-k 문맥을 검색한다.
6. Redis가 사용자 프로필, 최근 대화와 직전 검색 문맥을 기억한다.
7. Redis의 메모리 데이터를 AOF와 Docker 볼륨에 파일로 영속화한다.
8. 대화 내용을 JSONL 파일에도 이중 저장한다.
9. LangChain이 검색 근거·이전 대화·개인화 정보를 조합해 Ollama의 EXAONE에 전달한다.
10. Streamlit 화면에 답변과 URL·파일·페이지 출처를 표시한다.

## 2. 핵심 개념

### 2.1 RAG는 모델 재학습이 아니다

업로드한 문서가 EXAONE의 모델 가중치에 들어가는 것은 아니다. 문서는 chunk로 나뉜 뒤 E5 벡터로 Milvus에 저장된다. 질문이 들어오면 관련 chunk만 검색해 프롬프트의 `context`에 넣는다.

```text
외부 URL·PPTX·DOCX
        ↓
텍스트 추출 → 청킹 → passage: 임베딩 → Milvus 저장
                                              ↓
질문 → query: 임베딩 → 사용자별 Top-k 검색 ─────┘
                                              ↓
사용자 프로필 + 최근 대화 + 직전 문맥 + 현재 검색 근거
                                              ↓
                                    Ollama EXAONE 답변
```

### 2.2 저장소의 역할을 분리한다

| 저장소 | 저장 내용 | 사용하는 이유 |
|---|---|---|
| Milvus | 문서 chunk, 384차원 벡터, URL·파일·페이지, `user_id` | 의미 기반 장기 지식 검색 |
| Redis 메모리 | 사용자 프로필, 최근 대화, 직전 검색 문맥 | 매 질문마다 빠르게 기억 복원 |
| Redis AOF | Redis에서 발생한 쓰기 명령 | 컨테이너 재시작 후 Redis 상태 복원 |
| Docker Volume | AOF/RDB 파일이 저장되는 `/data` | 컨테이너가 삭제되어도 파일 유지 |
| JSONL 파일 | 사용자·세션별 전체 대화 감사 로그 | 검색·백업·이관·문제 분석 |
| 업로드 폴더 | 사용자가 제출한 원본 PPTX·DOCX | 재색인과 원문 확인 |

Redis는 기본적으로 메모리에서 빠르게 동작한다. 파일 저장은 Redis의 AOF/RDB 영속화와 Docker 볼륨으로 구현한다. 이 프로젝트는 복구 가능성을 높이기 위해 AOF `everysec`와 JSONL 대화 로그를 함께 사용한다.

## 3. 개인화 범위와 데이터 분리

모든 요청은 `user_id`와 `session_id`를 갖는다.

- `user_id`: 사용자 프로필과 개인 문서를 구분한다.
- `session_id`: 같은 사용자의 서로 다른 대화를 구분한다.
- Milvus 검색: `user_id` 조건을 적용해 다른 사용자의 문서를 제외한다.
- Redis 키: `user_id`와 `session_id`를 포함해 대화를 분리한다.
- 파일 경로: 사용자별 하위 폴더로 업로드와 대화 로그를 분리한다.

예시 Redis 키:

```text
profile:bigchoi
chat:bigchoi:session-001
context:bigchoi:session-001
```

운영 환경에서는 로그인·인가를 통해 서버가 `user_id`를 결정해야 한다. 브라우저가 보낸 임의의 `user_id`를 그대로 신뢰하면 다른 사용자의 데이터에 접근할 수 있다.

## 4. 프로젝트 폴더 구조

```text
AI_03_PERSONAL_RAG/
├─ app.py
├─ config.py
├─ embeddings.py
├─ loaders.py
├─ vector_store.py
├─ memory.py
├─ ingest.py
├─ rag.py
├─ requirements.txt
├─ .env
├─ docker-compose.redis.yml
├─ data/
│  ├─ uploads/
│  │  └─ {user_id}/
│  ├─ chat_logs/
│  │  └─ {user_id}/{session_id}.jsonl
│  └─ redis/
└─ README.md
```

Milvus는 AI_02 강의에서 실행한 Docker Standalone의 `http://127.0.0.1:19530`을 재사용한다.

## 5. 실행 환경 준비

### 5.1 Ollama와 EXAONE 확인

Ollama 프로그램 설치는 Python의 `ollama` 패키지 설치와 별개다. 먼저 Windows용 Ollama 프로그램과 EXAONE 모델이 실행되어야 한다.

```powershell
ollama list
ollama run exaone3.5:7.8b
```

API 상태 확인:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

`models` 배열에 실제 모델 이름이 표시되어야 한다. 코드의 `OLLAMA_MODEL`은 이 이름과 완전히 같아야 한다.

### 5.2 Python 3.10 가상환경

```powershell
mkdir AI_03_PERSONAL_RAG
cd AI_03_PERSONAL_RAG
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
```

### 5.3 requirements.txt

```text
streamlit
python-dotenv
redis
langchain
langchain-core
langchain-community
langchain-text-splitters
langchain-huggingface
langchain-milvus
langchain-ollama
sentence-transformers
pymilvus
beautifulsoup4
lxml
unstructured[pptx,docx]
```

설치:

```powershell
python -m pip install -r requirements.txt
```

## 6. Redis: 메모리와 파일 저장을 함께 사용한다

### 6.1 docker-compose.redis.yml

```yaml
services:
  redis:
    image: redis:latest
    container_name: ai03-redis
    ports:
      - "6379:6379"
    command:
      - redis-server
      - --appendonly
      - "yes"
      - --appendfsync
      - everysec
      - --save
      - "60"
      - "1"
    volumes:
      - ./data/redis:/data
    restart: unless-stopped
```

설정 의미:

- 메모리: 대화 조회와 저장은 Redis 메모리에서 빠르게 처리한다.
- `appendonly yes`: 모든 쓰기 명령을 AOF에 기록한다.
- `appendfsync everysec`: 약 1초 단위로 파일에 동기화해 속도와 복구 가능성을 절충한다.
- `save 60 1`: 60초 동안 변경이 한 건 이상 있으면 RDB 스냅샷도 만든다.
- `./data/redis:/data`: AOF와 RDB를 Windows 프로젝트 폴더에 남긴다.

실행과 확인:

```powershell
docker compose -f docker-compose.redis.yml up -d
docker exec ai03-redis redis-cli PING
docker exec ai03-redis redis-cli INFO persistence
```

정상 결과:

```text
PONG
aof_enabled:1
```

`docker compose down`은 컨테이너를 제거하지만 `./data/redis` 파일은 유지된다. `down -v` 또는 데이터 폴더 삭제는 영속 데이터를 제거할 수 있으므로 주의한다.

## 7. 환경설정

### 7.1 .env

```dotenv
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=exaone3.5:7.8b
EMBED_MODEL=intfloat/multilingual-e5-small
MILVUS_URI=http://127.0.0.1:19530
MILVUS_COLLECTION=ai03_personal_docs
REDIS_URL=redis://127.0.0.1:6379/0
TOP_K=4
MAX_HISTORY_TURNS=8
```

비밀번호, 토큰, 내부 URL을 Git 저장소에 올리지 않는다. 운영 환경에서는 Redis 인증과 TLS를 적용한다.

### 7.2 config.py

```python
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHAT_LOG_DIR = DATA_DIR / "chat_logs"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "exaone3.5:7.8b")
EMBED_MODEL = os.getenv(
    "EMBED_MODEL", "intfloat/multilingual-e5-small"
)
MILVUS_URI = os.getenv("MILVUS_URI", "http://127.0.0.1:19530")
MILVUS_COLLECTION = os.getenv(
    "MILVUS_COLLECTION", "ai03_personal_docs"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
TOP_K = int(os.getenv("TOP_K", "4"))
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "8"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHAT_LOG_DIR.mkdir(parents=True, exist_ok=True)
```

## 8. 한국어 E5 임베딩

`intfloat/multilingual-e5-small`은 질문 앞에 `query:`, 검색 대상 문서 앞에 `passage:` 접두어를 붙이는 비대칭 검색 방식을 사용한다. 출력 벡터는 384차원이며 정규화한다.

### embeddings.py

```python
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBED_MODEL


class E5Embeddings(Embeddings):
    def __init__(self, model_name: str = EMBED_MODEL):
        self.base = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        passages = [f"passage: {text}" for text in texts]
        return self.base.embed_documents(passages)

    def embed_query(self, text: str) -> list[float]:
        return self.base.embed_query(f"query: {text}")


embeddings = E5Embeddings()
```

확인:

```powershell
python -c "from embeddings import embeddings; print(len(embeddings.embed_query('연차 신청 방법')))"
```

예상 결과는 `384`다.

## 9. 외부 RAG 자료 수집과 제출

### 9.1 수집 정책

- 본인이 열람·수집할 권한이 있는 URL과 파일만 사용한다.
- 사이트 이용 약관과 robots 정책을 확인한다.
- 개인정보, 비밀정보, 인증정보는 색인하지 않는다.
- URL·파일명·페이지·사용자·문서 해시를 metadata에 남긴다.
- 업로드 확장자만 믿지 말고 운영 환경에서는 MIME과 파일 구조를 검사한다.

### 9.2 loaders.py

```python
from pathlib import Path

from langchain_community.document_loaders import (
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    WebBaseLoader,
)
from langchain_core.documents import Document


def load_url(url: str) -> list[Document]:
    loader = WebBaseLoader(
        web_paths=(url,),
        header_template={"User-Agent": "AI03-Personal-RAG/1.0"},
    )
    return loader.load()


def load_file(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pptx":
        return UnstructuredPowerPointLoader(
            str(path), mode="elements"
        ).load()
    if suffix == ".docx":
        return UnstructuredWordDocumentLoader(
            str(path), mode="elements"
        ).load()
    raise ValueError(f"지원하지 않는 파일 형식: {suffix}")
```

## 10. Milvus 벡터 저장소

하나의 컬렉션을 공유하되 `user_id`를 partition key와 검색 필터로 사용한다. 이렇게 하면 사용자의 질문이 다른 사용자의 문서를 검색하지 않는다.

### vector_store.py

```python
from langchain_milvus import Milvus

from config import MILVUS_COLLECTION, MILVUS_URI
from embeddings import embeddings


def create_vector_store() -> Milvus:
    return Milvus(
        embedding_function=embeddings,
        connection_args={"uri": MILVUS_URI},
        collection_name=MILVUS_COLLECTION,
        partition_key_field="user_id",
        index_params={"metric_type": "COSINE"},
        auto_id=True,
        drop_old=False,
    )
```

컬렉션을 처음 만든 뒤 `user_id` 필드나 384차원 스키마를 바꾸려면 새 컬렉션 이름을 사용하는 편이 안전하다.

## 11. 문서 청킹·metadata·색인

### ingest.py

```python
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import UPLOAD_DIR
from loaders import load_file, load_url
from vector_store import create_vector_store


USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,50}$")


def validate_user_id(user_id: str) -> str:
    if not USER_ID_PATTERN.fullmatch(user_id):
        raise ValueError("user_id는 영문·숫자·_·-만 사용할 수 있습니다.")
    return user_id


def tag_documents(
    documents: list[Document], user_id: str, source_type: str
) -> list[Document]:
    for doc in documents:
        doc.metadata["user_id"] = user_id
        doc.metadata["source_type"] = source_type
        doc.metadata.setdefault("source", "unknown")
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for chunk in chunks:
        source = str(chunk.metadata.get("source", "unknown"))
        raw = f"{source}\n{chunk.page_content}".encode("utf-8")
        chunk.metadata["chunk_id"] = hashlib.sha256(raw).hexdigest()
    return chunks


def ingest_urls(user_id: str, urls: list[str]) -> int:
    user_id = validate_user_id(user_id)
    documents: list[Document] = []
    for url in urls:
        documents.extend(tag_documents(load_url(url), user_id, "web"))
    return store_documents(documents)


def ingest_uploaded_files(user_id: str, files) -> int:
    user_id = validate_user_id(user_id)
    user_dir = UPLOAD_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)

    documents: list[Document] = []
    for uploaded in files:
        safe_name = Path(uploaded.name).name
        path = user_dir / safe_name
        path.write_bytes(uploaded.getbuffer())
        loaded = load_file(path)
        for doc in loaded:
            doc.metadata["source"] = str(path)
        documents.extend(
            tag_documents(loaded, user_id, path.suffix.lower().lstrip("."))
        )
    return store_documents(documents)


def store_documents(documents: list[Document]) -> int:
    clean = [doc for doc in documents if doc.page_content.strip()]
    if not clean:
        return 0
    chunks = split_documents(clean)
    ids = create_vector_store().add_documents(chunks)
    return len(ids)
```

주의: 예제는 학습을 위해 단순화했다. 같은 `chunk_id`의 중복 삽입을 막으려면 별도 ID 필드와 upsert 정책을 추가해야 한다.

## 12. Redis 대화 기억과 JSONL 파일 백업

Redis에는 최근 대화와 직전 검색 문맥을 저장한다. JSONL은 전체 대화를 순차 기록한다.

### memory.py

```python
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import redis
from langchain_core.messages import AIMessage, HumanMessage

from config import CHAT_LOG_DIR, MAX_HISTORY_TURNS, REDIS_URL


class ConversationMemory:
    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self.redis = redis.Redis.from_url(
            REDIS_URL, decode_responses=True
        )
        self.chat_key = f"chat:{user_id}:{session_id}"
        self.context_key = f"context:{user_id}:{session_id}"
        self.profile_key = f"profile:{user_id}"
        self.log_path = (
            CHAT_LOG_DIR / user_id / f"{session_id}.jsonl"
        )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def ping(self) -> bool:
        return bool(self.redis.ping())

    def save_profile(self, profile: dict[str, str]) -> None:
        clean = {key: value for key, value in profile.items() if value}
        if clean:
            self.redis.hset(self.profile_key, mapping=clean)

    def load_profile(self) -> dict[str, str]:
        return self.redis.hgetall(self.profile_key)

    def add_message(self, role: str, content: str) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content,
        }
        payload = json.dumps(record, ensure_ascii=False)
        pipe = self.redis.pipeline()
        pipe.rpush(self.chat_key, payload)
        pipe.ltrim(self.chat_key, -(MAX_HISTORY_TURNS * 2), -1)
        pipe.execute()

        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(payload + "\n")

    def load_messages(self):
        rows = self.redis.lrange(self.chat_key, 0, -1)
        messages = []
        for row in rows:
            item = json.loads(row)
            if item["role"] == "user":
                messages.append(HumanMessage(item["content"]))
            elif item["role"] == "assistant":
                messages.append(AIMessage(item["content"]))
        return messages

    def save_last_context(self, context: str) -> None:
        self.redis.set(self.context_key, context)

    def load_last_context(self) -> str:
        return self.redis.get(self.context_key) or ""

    def clear_session(self) -> None:
        self.redis.delete(self.chat_key, self.context_key)
```

기억 정책:

- Redis에는 최근 `MAX_HISTORY_TURNS`만 남겨 프롬프트 길이를 제한한다.
- JSONL에는 전체 대화를 남긴다.
- 민감정보를 로그에 저장하지 않도록 입력 필터와 보존 정책을 추가한다.
- 오래된 Redis 키에 TTL을 적용하려면 `expire()`를 추가한다.
- JSONL은 암호화되지 않은 일반 텍스트이므로 운영 환경에서는 접근 권한과 암호화를 적용한다.

## 13. 이전 대화로 질문을 독립형 질문으로 바꾼다

사용자가 다음처럼 말할 수 있다.

```text
사용자: 연차 신청 절차를 알려줘.
챗봇: 전자결재에서 신청합니다.
사용자: 승인자는 누구야?
```

마지막 질문만 Milvus에 검색하면 `승인자`가 무엇의 승인자인지 불분명하다. 최근 대화를 이용해 다음과 같이 다시 쓴 뒤 검색한다.

```text
회사 연차 신청 절차에서 승인자는 누구인가?
```

이 과정은 기억을 그대로 답변으로 사용하는 것이 아니라, 검색 질문을 명확하게 만드는 단계다.

## 14. LangChain + EXAONE RAG 체인

### rag.py

```python
from __future__ import annotations

import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, TOP_K
from memory import ConversationMemory
from vector_store import create_vector_store


SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,50}$")

REWRITE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "최근 대화를 참고해 현재 질문을 독립적인 한국어 검색 질문으로 "
            "다시 쓰세요. 답변하지 말고 검색 질문만 출력하세요.",
        ),
        MessagesPlaceholder("history"),
        ("human", "현재 질문: {question}"),
    ]
)

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "당신은 개인화 한국어 문서 도우미입니다. "
            "현재 검색 근거를 가장 우선하고, 이전 검색 문맥은 대화 연결을 "
            "위한 보조 자료로만 사용하세요. 근거가 없으면 문서에서 "
            "확인할 수 없다고 답하세요. 출처 번호를 답변에 표시하세요.\n\n"
            "사용자 프로필:\n{profile}",
        ),
        MessagesPlaceholder("history"),
        (
            "human",
            "이전 검색 문맥:\n{previous_context}\n\n"
            "현재 검색 근거:\n{current_context}\n\n"
            "현재 질문:\n{question}",
        ),
    ]
)


def create_llm() -> ChatOllama:
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
        num_ctx=4096,
        num_predict=384,
        keep_alive="30m",
    )


def format_docs(documents) -> str:
    blocks = []
    for index, doc in enumerate(documents, 1):
        metadata = doc.metadata
        source = metadata.get("source", "unknown")
        page = metadata.get("page_number", metadata.get("page", "-"))
        blocks.append(
            f"[{index}] source={source} page={page}\n{doc.page_content}"
        )
    return "\n\n".join(blocks)


def source_list(documents) -> list[dict]:
    return [
        {
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get(
                "page_number", doc.metadata.get("page", "-")
            ),
            "source_type": doc.metadata.get("source_type", "unknown"),
        }
        for doc in documents
    ]


class PersonalRAG:
    def __init__(self, user_id: str, session_id: str):
        if not SAFE_ID.fullmatch(user_id) or not SAFE_ID.fullmatch(session_id):
            raise ValueError("user_id와 session_id 형식을 확인하세요.")
        self.user_id = user_id
        self.memory = ConversationMemory(user_id, session_id)
        self.vector_store = create_vector_store()
        self.llm = create_llm()
        self.rewrite_chain = REWRITE_PROMPT | self.llm | StrOutputParser()
        self.answer_chain = ANSWER_PROMPT | self.llm | StrOutputParser()

    def ask(self, question: str) -> tuple[str, list[dict]]:
        history = self.memory.load_messages()
        standalone_question = question
        if history:
            standalone_question = self.rewrite_chain.invoke(
                {"history": history, "question": question}
            ).strip()

        expr = f'user_id == "{self.user_id}"'
        documents = self.vector_store.similarity_search(
            standalone_question,
            k=TOP_K,
            expr=expr,
        )
        current_context = format_docs(documents)
        previous_context = self.memory.load_last_context()
        profile = self.memory.load_profile()

        answer = self.answer_chain.invoke(
            {
                "profile": profile or "등록된 개인화 정보 없음",
                "history": history,
                "previous_context": previous_context or "없음",
                "current_context": current_context or "검색 결과 없음",
                "question": question,
            }
        )

        self.memory.add_message("user", question)
        self.memory.add_message("assistant", answer)
        self.memory.save_last_context(current_context)
        return answer, source_list(documents)
```

### 질문 처리 순서

1. Redis에서 사용자 프로필과 최근 대화를 읽는다.
2. 후속 질문이면 최근 대화로 독립형 검색 질문을 만든다.
3. E5가 검색 질문에 `query:` 접두어를 붙여 벡터화한다.
4. Milvus가 `user_id`로 필터링한 뒤 Top-k chunk를 찾는다.
5. Redis에서 직전 검색 문맥을 읽는다.
6. 현재 근거·이전 문맥·최근 대화·사용자 프로필을 프롬프트에 넣는다.
7. Ollama의 EXAONE이 답변을 생성한다.
8. 질문·답변·현재 검색 문맥을 Redis에 저장한다.
9. 질문과 답변을 JSONL 파일에도 기록한다.

## 15. Streamlit 개인화 웹 화면

### app.py

```python
from __future__ import annotations

import uuid

import streamlit as st

from ingest import ingest_uploaded_files, ingest_urls, validate_user_id
from memory import ConversationMemory
from rag import PersonalRAG


st.set_page_config(page_title="개인화 RAG 챗봇", page_icon="🧠")
st.title("개인화 로컬 RAG 챗봇")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

with st.sidebar:
    st.header("사용자 설정")
    user_id = st.text_input("사용자 ID", value="bigchoi")
    user_name = st.text_input("표시 이름", value="")
    interests = st.text_input("관심 분야", value="")

    st.header("외부 RAG 자료 제출")
    url_text = st.text_area(
        "수집할 URL",
        placeholder="URL을 한 줄에 하나씩 입력하세요.",
    )
    uploaded_files = st.file_uploader(
        "PPTX·DOCX 업로드",
        type=["pptx", "docx"],
        accept_multiple_files=True,
    )

    if st.button("자료 수집·벡터화"):
        try:
            user_id = validate_user_id(user_id)
            urls = [line.strip() for line in url_text.splitlines() if line.strip()]
            count = 0
            if urls:
                count += ingest_urls(user_id, urls)
            if uploaded_files:
                count += ingest_uploaded_files(user_id, uploaded_files)
            st.success(f"Milvus에 {count}개 chunk를 저장했습니다.")
        except Exception as error:
            st.exception(error)

    if st.button("현재 대화 기억 삭제"):
        try:
            memory = ConversationMemory(
                validate_user_id(user_id), st.session_state.session_id
            )
            memory.clear_session()
            st.success("Redis의 현재 세션 기억을 삭제했습니다.")
        except Exception as error:
            st.exception(error)

try:
    user_id = validate_user_id(user_id)
    memory = ConversationMemory(user_id, st.session_state.session_id)
    memory.save_profile(
        {"name": user_name, "interests": interests}
    )
    history = memory.load_messages()
except Exception as error:
    st.error(str(error))
    st.stop()

for message in history:
    role = "user" if message.type == "human" else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

question = st.chat_input("개인 문서에 대해 질문하세요")
if question:
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("개인 문서에서 근거를 찾는 중입니다..."):
            try:
                rag = PersonalRAG(user_id, st.session_state.session_id)
                answer, sources = rag.ask(question)
                st.markdown(answer)
                if sources:
                    with st.expander("검색 출처"):
                        for source in sources:
                            st.write(source)
            except Exception as error:
                st.exception(error)
```

Streamlit은 코드를 위에서 아래로 다시 실행한다. 채팅 입력창이 보이지 않을 때는 `st.chat_input()`보다 앞에서 예외가 발생했는지 터미널 로그를 먼저 확인한다.

## 16. 실행 순서

### 16.1 서비스 확인

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
docker compose ps
docker exec ai03-redis redis-cli PING
```

확인할 포트:

| 서비스 | 주소 |
|---|---|
| Ollama | `http://127.0.0.1:11434` |
| Milvus | `http://127.0.0.1:19530` |
| Milvus WebUI | `http://127.0.0.1:9091/webui/` |
| Redis | `redis://127.0.0.1:6379/0` |
| Streamlit | `http://localhost:8501` |

### 16.2 웹 앱 실행

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

### 16.3 최초 사용

1. 사용자 ID를 입력한다.
2. 이름과 관심 분야를 입력한다.
3. 허용된 URL 또는 PPTX·DOCX를 제출한다.
4. `자료 수집·벡터화`를 누른다.
5. Milvus WebUI에서 `ai03_personal_docs`와 엔티티 수를 확인한다.
6. 문서에 답이 있는 질문을 입력한다.
7. 답변 아래의 출처를 원문과 대조한다.
8. 후속 질문을 입력해 이전 대화가 반영되는지 확인한다.
9. Redis 컨테이너를 재시작한 뒤 대화가 복원되는지 확인한다.

## 17. 기능 검증 시나리오

### 17.1 검색 품질

```text
질문 1: 문서에 명확한 정답이 있는 질문
질문 2: 여러 문서 조각을 조합해야 하는 질문
질문 3: 문서에 없는 질문
```

합격 기준:

- 질문 1과 2는 관련 Top-k 문서를 포함한다.
- 질문 3은 추측하지 않고 확인할 수 없다고 답한다.
- 모든 답변에 URL·파일·페이지 출처가 표시된다.

### 17.2 대화 기억

```text
사용자: 연차 신청 절차를 알려줘.
사용자: 승인자는 누구야?
사용자: 방금 답을 두 문장으로 요약해줘.
```

합격 기준:

- 두 번째 질문이 연차 승인자를 뜻한다고 해석한다.
- 세 번째 질문이 직전 답변을 대상으로 한다.
- 브라우저 새로고침 후 같은 세션에서는 대화가 복원된다.

### 17.3 사용자 격리

1. 사용자 A로 A 문서를 색인한다.
2. 사용자 B로 같은 질문을 한다.
3. B의 검색 결과에 A 문서가 나타나지 않는지 확인한다.

### 17.4 파일 영속화

```powershell
docker restart ai03-redis
docker exec ai03-redis redis-cli KEYS "chat:*"
Get-ChildItem .\data\redis -Recurse
Get-ChildItem .\data\chat_logs -Recurse
```

합격 기준:

- Redis 재시작 후 키가 복원된다.
- `data/redis`에 AOF/RDB 관련 파일이 있다.
- `data/chat_logs/{user_id}/{session_id}.jsonl`에 대화가 남는다.

## 18. 자주 발생하는 오류

### `ollama`가 명령으로 인식되지 않음

원인: Python 패키지만 설치했거나 Ollama 프로그램 경로가 PATH에 반영되지 않았다.

해결:

1. Windows용 Ollama 프로그램을 설치한다.
2. PowerShell을 새로 연다.
3. `ollama --version`과 `ollama list`를 확인한다.

### `model 'exaone3.5:7.8b' not found`

```powershell
ollama list
ollama pull exaone3.5:7.8b
```

실제 설치 이름과 `.env`의 `OLLAMA_MODEL`을 일치시킨다.

### Redis `Connection refused`

```powershell
docker ps --filter name=ai03-redis
docker logs ai03-redis
docker exec ai03-redis redis-cli PING
```

### Redis 재시작 후 대화가 사라짐

- `appendonly yes`인지 확인한다.
- `data/redis:/data` 볼륨이 연결되었는지 확인한다.
- `docker compose down -v` 또는 데이터 폴더 삭제 여부를 확인한다.
- `INFO persistence`에서 `aof_enabled:1`을 확인한다.

### Milvus `connection refused: 19530`

Docker Desktop과 Milvus Standalone 상태를 확인한다.

```powershell
docker compose ps
```

### `vector dimension mismatch`

기존 컬렉션이 다른 임베딩 차원으로 만들어졌다. `multilingual-e5-small`은 384차원이므로 새 컬렉션 이름으로 재색인한다.

### 검색 결과가 다른 사용자 문서를 포함함

- 모든 chunk metadata에 `user_id`가 있는지 확인한다.
- 컬렉션 생성 시 `partition_key_field="user_id"`인지 확인한다.
- 검색의 `expr` 조건이 서버 인증으로 확정한 사용자 ID를 사용하는지 확인한다.

### 한국어 검색 결과가 무관함

- 질문은 `query:`, 문서는 `passage:`인지 확인한다.
- 색인과 검색에서 같은 E5 모델을 사용하는지 확인한다.
- `normalize_embeddings=True`와 `COSINE` 설정을 확인한다.
- Top-k와 chunk 크기를 평가 질문으로 비교한다.

### 채팅 입력창이 보이지 않음

`st.chat_input()` 실행 전에 Redis·Milvus·Ollama 초기화 오류가 발생하면 화면 렌더링이 중단될 수 있다. Streamlit을 실행한 터미널에서 첫 번째 예외를 확인하고, 외부 서비스 연결을 `try/except`로 감싼다.

## 19. 노트북 최적화

- `multilingual-e5-small`을 CPU에서 한 번만 로드하고 Streamlit 캐시를 적용한다.
- EXAONE의 `num_ctx`와 `num_predict`를 작게 시작한다.
- Top-k는 3~4로 시작한다.
- 최근 대화는 6~8턴만 프롬프트에 넣는다.
- 전체 대화는 JSONL에 보존하고, 긴 대화는 요약 메모리로 전환한다.
- URL과 파일 색인은 질문 때마다 하지 않고 제출 시에만 실행한다.
- 문서 해시와 `chunk_id`로 중복 색인을 방지한다.
- 검색 시간과 생성 시간을 따로 측정한다.

Streamlit 캐시 예시:

```python
@st.cache_resource
def get_rag(user_id: str, session_id: str):
    return PersonalRAG(user_id, session_id)
```

사용자나 세션이 바뀌면 캐시 키도 달라진다는 점을 확인한다.

## 20. 운영 전 보안 체크

- 사용자가 입력한 URL로 서버 내부 주소에 접근하지 못하도록 SSRF 방어를 적용한다.
- 허용 도메인과 최대 다운로드 크기를 제한한다.
- 업로드 확장자·MIME·파일 구조와 악성코드를 검사한다.
- 로그인과 사용자별 권한 검사를 서버에서 수행한다.
- Redis와 Milvus를 인터넷에 직접 노출하지 않는다.
- Redis 비밀번호·TLS·네트워크 접근 제어를 적용한다.
- 프롬프트 인젝션이 포함된 외부 문서를 신뢰하지 않는다.
- 검색 문서는 데이터일 뿐 시스템 명령이 아니라고 프롬프트에 명시한다.
- 개인정보의 보존 기간, 삭제 기능과 감사 로그 정책을 정한다.
- 모델 답변과 출처를 함께 표시하고 중요한 판단은 사람이 검증한다.

## 21. 완성 기준

- [ ] Ollama API와 EXAONE 모델이 응답한다.
- [ ] E5 질문·문서 접두어와 384차원 정규화가 적용된다.
- [ ] URL·PPTX·DOCX 제출이 동작한다.
- [ ] 사용자별 chunk가 Milvus에 저장된다.
- [ ] 사용자 필터가 다른 사용자의 문서를 차단한다.
- [ ] Top-k 검색 결과가 질문의 정답 근거를 포함한다.
- [ ] Redis가 프로필·최근 대화·직전 문맥을 기억한다.
- [ ] 후속 질문이 독립형 검색 질문으로 변환된다.
- [ ] Redis 재시작 후 AOF에서 대화가 복원된다.
- [ ] JSONL 대화 파일이 생성된다.
- [ ] EXAONE 답변에 URL·파일·페이지 출처가 표시된다.
- [ ] 문서에 없는 질문은 추측하지 않는다.

## 22. 공식 참고 자료

- multilingual-E5-small 모델 카드: https://huggingface.co/intfloat/multilingual-e5-small
- LangChain Hugging Face embeddings: https://docs.langchain.com/oss/python/integrations/embeddings/sentence_transformers
- LangChain ChatOllama: https://docs.langchain.com/oss/python/integrations/chat/ollama
- LangChain Redis 통합: https://docs.langchain.com/oss/python/integrations/providers/redis
- Redis 영속화: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/
- Redis Docker와 파일 저장: https://redis.io/tutorials/operate/orchestration/docker/
- LangChain + Milvus RAG: https://milvus.io/docs/integrate_with_langchain.md
- Milvus 사용자별 검색: https://milvus.io/docs/basic_usage_langchain.md
- Streamlit 채팅 입력: https://docs.streamlit.io/develop/api-reference/chat/st.chat_input

---

이 설계에서 Milvus는 **개인 문서의 장기 지식**, Redis는 **사용자와 세션의 대화 기억**, Ollama EXAONE은 **검색 근거를 읽고 답변을 생성하는 로컬 언어 모델**을 담당한다. 세 저장 계층의 역할을 섞지 않는 것이 정확도·속도·복구·보안을 함께 관리하는 핵심이다.
