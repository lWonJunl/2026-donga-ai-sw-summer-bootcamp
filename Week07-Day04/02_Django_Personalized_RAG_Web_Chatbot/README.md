# Django EXAONE Chat

Streamlit 없이 Django와 SQLite로 만든 회원별 로컬 AI 채팅 사이트입니다. 로컬 Ollama의 `exaone3.5:7.8b` 모델을 사용하며, ChatGPT와 비슷한 형태로 대화를 생성하고 관리할 수 있습니다.

## 주요 기능

- Django 회원가입, 로그인, 로그아웃
- 계정별 대화 목록과 메시지 완전 분리
- SQLite를 이용한 대화 및 개인 설정 저장
- Redis를 이용한 최근 대화 맥락 캐시
- URL·PPTX·DOCX 개인 지식 수집과 Milvus 벡터 검색
- 채팅 프롬프트에 포함된 공개 URL 자동 수집(메시지당 최대 3개)
- `multilingual-e5-small` 임베딩과 사용자 ID 기반 검색 격리
- 답변 근거(파일/페이지/URL) 표시 및 Redis·JSONL 대화 메모리
- 등록 자료 삭제 시 Milvus 벡터와 업로드 원본까지 함께 정리
- Ollama 답변 실시간 스트리밍
- 답변 생성 중단 및 마지막 답변 다시 생성
- 최근 대화 맥락 유지와 짧은 후속 질문 해석
- 첫 대화를 바탕으로 대화 제목 자동 생성
- 대화 제목 직접 수정 및 대화 삭제
- Markdown, 인라인 코드, 코드 블록 표시
- 메시지 전체 복사 및 코드 블록만 복사
- 메시지 전송 시각 표시
- 개인 시스템 프롬프트 설정
- 채팅 입력창에서 창의성 값 조절
- 데스크톱 및 모바일 사이드바 접기

## 사용 기술

- Python 3.10
- Django 5.2
- SQLite
- Redis
- Milvus, LangChain, Sentence Transformers
- Docker Desktop
- HTML, CSS, JavaScript
- Ollama REST API
- EXAONE 3.5 7.8B

## 사전 준비

다음 프로그램이 필요합니다.

1. Python 3.10 이상
2. Ollama
3. Docker Desktop
4. Git(선택 사항)

Ollama를 설치한 후 모델을 준비합니다.

```powershell
ollama pull exaone3.5:7.8b
```

설치된 모델은 다음 명령으로 확인할 수 있습니다.

```powershell
ollama list
```

## 설치

PowerShell에서 이 README가 있는 폴더로 이동합니다.

```powershell
cd .\Week07-Day04\02_Django_Personalized_RAG_Web_Chatbot
```

가상환경을 생성하고 활성화합니다.

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

필요한 패키지를 설치합니다.

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

SQLite 테이블을 생성합니다.

```powershell
python manage.py migrate
```

## 실행

Redis와 Milvus를 AOF/로컬 볼륨 영속화 구성으로 실행합니다.

```powershell
docker compose -f docker-compose.rag.yml up -d
docker exec Redis redis-cli ping
```

정상이라면 두 번째 명령에서 `PONG`이 출력됩니다. 기존에 같은 이름의 `Redis`
컨테이너가 있다면 먼저 Docker Desktop에서 중지·제거한 뒤 Compose 구성을 실행하세요.

Docker Desktop에서 Redis만 직접 실행하려면 다음처럼 로컬 호스트에만 공개합니다.

- 컨테이너 이름: `Redis`
- 호스트 주소 및 포트: `127.0.0.1:6379`
- 컨테이너 포트: `6379`

PowerShell에서는 다음 명령으로 같은 구성을 실행할 수 있습니다.

```powershell
docker run --name Redis -p 127.0.0.1:6379:6379 -v exaone-redis:/data -d redis:latest redis-server --appendonly yes
docker exec Redis redis-cli ping
```

정상이라면 두 번째 명령에서 `PONG`이 출력됩니다.

`-p 6379:6379`처럼 호스트 주소를 생략하면 Redis가 외부 네트워크에도
노출될 수 있으므로 사용하지 않습니다. 이 프로젝트는 로컬 학습용이며 운영 배포용
설정은 별도로 구성해야 합니다.

첫 번째 PowerShell에서 Ollama 서버를 실행합니다.

```powershell
ollama serve
```

Ollama 앱이 이미 백그라운드에서 실행 중이라면 이 명령은 생략할 수 있습니다.

두 번째 PowerShell에서 가상환경을 활성화하고 Django 서버를 실행합니다.

```powershell
cd .\Week07-Day04\02_Django_Personalized_RAG_Web_Chatbot
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

`python`이 다른 전역 Python을 가리키면 `redis` 패키지를 찾지 못할 수 있으므로,
반드시 위와 같이 `.venv`를 활성화한 터미널에서 서버를 실행합니다.

브라우저에서 아래 주소로 접속합니다.

- 회원가입: <http://127.0.0.1:8000/signup/>
- 로그인: <http://127.0.0.1:8000/login/>
- 채팅: <http://127.0.0.1:8000/>
- 내 지식 자료: <http://127.0.0.1:8000/knowledge/>

저장소에는 테스트 계정이나 `db.sqlite3`가 포함되지 않습니다. 처음 실행한 경우 회원가입 화면에서 계정을 생성하세요.

## 사용 방법

1. 회원가입하거나 기존 계정으로 로그인합니다.
2. 입력창에 메시지를 입력하고 `Enter` 또는 전송 버튼을 누릅니다.
3. 줄바꿈은 `Shift + Enter`를 사용합니다.
4. 입력창 아래의 `창의성` 버튼으로 응답의 다양성을 조절합니다.
5. 답변 생성 중에는 중지 버튼을 눌러 현재까지의 답변을 저장할 수 있습니다.
6. 대화 목록에서 제목을 수정하거나 대화를 삭제할 수 있습니다.
7. `내 지식 자료`에서 공개 URL 또는 PPTX·DOCX를 등록한 뒤 관련 질문을 합니다.
8. 채팅에 URL과 질문을 함께 붙여 넣으면 새 링크를 자동 등록하고 같은 답변부터 활용합니다.

첫 문서 등록 시 임베딩 모델을 내려받으므로 시간이 걸릴 수 있습니다. 문서 검색이나
Redis가 일시적으로 실패하면 기존 SQLite 기반 일반 채팅으로 자동 전환됩니다.

## 개인화 RAG 동작

- 로그인 사용자의 Django 사용자 ID가 Milvus의 `user_id` 파티션 키로 저장됩니다.
- 프롬프트의 URL은 정규화해 중복 색인을 방지하며 이미 등록된 자료는 그대로 재사용합니다.
- 링크 수집이 실패해도 다른 링크 처리와 일반 채팅은 계속됩니다.
- 검색 필터는 서버에서 생성하므로 다른 계정의 문서가 검색되지 않습니다.
- 후속 질문은 최근 대화를 바탕으로 독립 검색어로 재작성됩니다.
- 검색 문서는 신뢰할 수 없는 입력으로 취급하며 문서 안의 명령은 실행하지 않습니다.
- 답변이 참조한 자료와 페이지가 메시지의 `sources` 필드에 함께 보존됩니다.
- Redis에는 사용자·대화별 최근 메모리와 직전 검색 문맥을 30일간 저장합니다.
- 전체 감사 로그는 `data/chat_logs/<user_id>/<conversation_id>.jsonl`에 기록됩니다.
- 업로드 원본, Redis/Milvus 데이터와 JSONL 로그는 `data/`에 저장되며 Git에서 제외됩니다.

환경 변수 예시는 `.env.example`에 있습니다. PowerShell에서는 필요한 값을 현재
세션에 `$env:RAG_MILVUS_URI='http://127.0.0.1:19530'` 형태로 지정할 수 있습니다.

## 창의성 설정

창의성 값은 계정별로 SQLite에 저장되고 다음 답변부터 Ollama의 `temperature` 옵션에 전달됩니다.

- `0.0`: 결과가 비교적 일정하고 보수적임
- `0.7`: 정확성과 다양성의 균형
- `1.5`: 표현과 결과가 더 다양함

대화 제목은 안정적인 결과를 위해 별도의 낮은 값 `0.2`로 생성합니다.

## 대화 데이터와 맥락

- 각 사용자는 본인의 대화만 조회할 수 있습니다.
- 전체 대화는 SQLite에 영구 저장됩니다.
- 현재 대화방의 최근 메시지 최대 12개는 Redis에 1시간 동안 캐시되고 Ollama에 전달됩니다.
- Redis가 중단되어도 SQLite에서 맥락을 읽어 채팅을 계속할 수 있습니다.
- Redis 주소와 캐시 시간은 `REDIS_URL`, `CHAT_CONTEXT_CACHE_TIMEOUT` 환경 변수로 변경할 수 있습니다.
- 새 대화에서는 이전 대화방의 메시지를 사용하지 않습니다.
- 대화를 삭제하면 제목과 모든 메시지가 DB에서 삭제되고 이후 맥락에서도 제외됩니다.
- 개인 시스템 프롬프트와 창의성 설정은 같은 계정의 모든 대화에 공통 적용됩니다.

## 프로젝트 구조

```text
02_Django_Personalized_RAG_Web_Chatbot/
├─ chat/
│  ├─ migrations/          # SQLite 스키마 변경 기록
│  ├─ static/chat/         # 채팅 화면 CSS
│  ├─ templates/chat/      # 채팅, 계정, 개인 설정 화면
│  ├─ templatetags/        # 서버 측 Markdown 표시
│  ├─ forms.py             # 회원가입, 개인 설정, 지식 등록 폼
│  ├─ context_cache.py     # Redis 최근 맥락 캐시와 SQLite 폴백
│  ├─ models.py            # 대화, 메시지, 사용자 설정, 지식 자료 모델
│  ├─ ollama.py            # Ollama API 연결과 스트리밍
│  ├─ rag_embeddings.py    # multilingual-e5 임베딩
│  ├─ rag_ingest.py        # 문서 청킹, 색인, 자료 삭제
│  ├─ rag_loaders.py       # URL·PPTX·DOCX 안전 로더
│  ├─ rag_memory.py        # Redis 메모리와 JSONL 로그
│  ├─ rag_pipeline.py      # 후속 질문 재작성과 RAG 프롬프트
│  ├─ rag_store.py         # 사용자별 Milvus 검색·삭제
│  ├─ rag_urls.py          # 프롬프트 URL 추출·정규화
│  ├─ signals.py           # 메시지 변경 시 Redis 캐시 갱신
│  ├─ urls.py              # chat 앱 URL
│  ├─ views.py             # 계정, 대화, 스트리밍 처리
│  └─ tests.py             # Django 자동 테스트
├─ exaone_site/
│  ├─ settings.py          # Django 프로젝트 설정
│  ├─ urls.py              # 최상위 URL
│  └─ wsgi.py
├─ manage.py
├─ docker-compose.rag.yml
├─ requirements.txt
└─ README.md
```

## 데이터베이스

기본 DB는 프로젝트 루트의 `db.sqlite3`입니다. 이 파일에는 계정, 대화, 메시지, 개인 설정이 저장되므로 외부에 공유하지 않는 것이 좋습니다.

`db.sqlite3`는 Git에 포함되지 않으며 다음 명령을 실행하면 빈 DB를 다시 만들 수 있습니다.

```powershell
python manage.py migrate
```

## 테스트

```powershell
python manage.py test chat
```

전체 테스트가 통과하면 계정 분리, 대화 관리, 스트리밍 저장, 자동 제목, Markdown, 복사 버튼과 창의성 저장 등의 주요 기능이 정상적으로 구성된 상태입니다.

## 문제 해결

### 답변이 계속 `생각 중…`으로 표시되는 경우

Ollama가 실행 중인지 확인합니다.

```powershell
ollama list
ollama ps
```

처음 모델을 불러올 때는 CPU와 메모리 상태에 따라 답변 시작까지 시간이 걸릴 수 있습니다.

### Ollama 연결 오류가 발생하는 경우

Ollama 기본 주소 `http://127.0.0.1:11434`가 사용 가능한지 확인하고 Ollama를 다시 실행합니다.

```powershell
ollama serve
```

### `HTTP ERROR 405`가 표시되는 경우

메시지 전송, 대화 삭제, 제목 변경 같은 주소는 POST 요청 전용입니다. 해당 URL을 주소창에서 직접 열지 말고 사이트의 버튼을 사용하세요.

### 모델이 CPU에서 실행되는지 확인하는 방법

```powershell
ollama ps
```

`PROCESSOR`가 `100% CPU`라면 CPU에서 실행 중입니다. 현재 Ollama는 Intel NPU를 직접 지원하지 않으므로 NPU 실행에는 별도의 OpenVINO 기반 구현이 필요합니다.
