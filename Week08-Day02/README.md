# Week08-Day02 · RAG 전처리 고도화

Week08-Day02는 [Week07-Day04의 Django 개인화 RAG 챗봇](../Week07-Day04/02_Django_Personalized_RAG_Web_Chatbot)을 기반으로 문서 전처리와 검색 품질을 개선한 버전입니다. 채팅 UI와 사용자별 데이터 격리는 유지하면서, PDF/OCR 문서를 더 안정적으로 구조화하고 LangGraph 기반 파이프라인으로 Milvus 색인 과정을 확장했습니다.

## Week07-Day04와 달라진 점

| 구분 | Week07-Day04 | Week08-Day02 |
| --- | --- | --- |
| 전처리 흐름 | `rag_ingest.py`에서 분할·태깅을 직접 처리 | LangGraph 그래프에서 분할 → 요약·키워드 → 태깅을 단계별 처리 |
| 청크 설정 | 일반적인 800자 청크, 120자 overlap | 한글 문서에 맞춘 600자 청크, 100자 overlap |
| 문서 정보 | 본문과 기본 출처 메타데이터 중심 | 각 청크에 요약, 주요 키워드, 글자 수를 추가 |
| Milvus 검색 | 임베딩 유사도와 기본 용어 재정렬 | 키워드·요약을 임베딩에 포함하고 키워드 일치도를 가중해 재정렬 |
| PDF/OCR | PDF 텍스트 추출과 OCR 지원 | OCR 결과를 제목·질문·답변·참고사항 규칙으로 구조화하고 FAQ 경계 보정 |
| 프롬프트 문맥 | 검색 본문과 출처를 전달 | 내부 문서의 키워드·요약·본문을 함께 전달하고 내부 자료 우선 사용을 명시 |
| 의존성 | LangChain 기반 RAG | LangChain에 LangGraph를 추가해 전처리 단계를 확장 |

## 유지된 기능

- Django 회원가입·로그인과 계정별 대화 분리
- Ollama `exaone3.5:7.8b` 스트리밍 응답
- SQLite 대화 저장, Redis 최근 문맥 캐시와 폴백
- Milvus `user_id` 기반 벡터 검색 격리
- URL·DOCX·PPTX·PDF 자료 등록과 원본·벡터 삭제
- 답변 중단·재생성, 대화 제목 자동 생성·수정
- 검색 출처와 페이지 표시, Markdown·코드 블록 표시

## Week08 RAG 처리 흐름

```text
파일 또는 URL 등록
        ↓
PDF/DOCX/PPTX/OCR 로더
        ↓
LangGraph: 600자 분할(100자 overlap)
        ↓
청크 요약 + 주요 키워드 추출
        ↓
사용자·출처 메타데이터 태깅
        ↓
키워드가 포함된 내용으로 Milvus 임베딩 저장
        ↓
질문 시 내부 문서 검색 → 키워드 재정렬 → Ollama 프롬프트 전달
```

## 주요 파일

```text
chat/rag_graph.py      LangGraph 전처리 그래프와 요약·키워드 추출
chat/rag_ingest.py     파일·URL 수집과 그래프 호출
chat/rag_loaders.py    PDF/OCR/DOCX/PPTX/URL 로더
chat/rag_store.py      Milvus 저장·검색·키워드 재정렬·삭제
chat/rag_pipeline.py   후속 질문 재작성과 내부 문서 우선 프롬프트
chat/tests.py          업로드·검색·사용자 격리·스트리밍 회귀 테스트
```

## 실행

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
docker compose -f docker-compose.rag.yml up -d
python manage.py migrate
python manage.py runserver
```

Ollama 모델은 별도로 준비합니다.

```powershell
ollama pull exaone3.5:7.8b
```

## 게시 범위

GitHub에는 애플리케이션 소스, 마이그레이션, 테스트, 설정 예시만 포함합니다. `.env`, `.venv`, `data/`, 업로드 원본, SQLite DB, 로그와 Python 캐시는 포함하지 않습니다.

## 테스트

```powershell
python manage.py test chat
```
