# EXAONE 웹 챗봇 만들기

Streamlit과 Ollama를 연결해 내 PC에서 실행되는 EXAONE 3.5 7.8B 모델과 브라우저로 대화하는 웹 챗봇을 만든다. 완성된 앱은 사용자와 AI의 말풍선을 구분하고, 답변을 실시간으로 스트리밍하며, 이전 대화 문맥을 유지한다.

## 학습 목표

- Python 가상환경에서 Streamlit 프로젝트를 준비한다.
- Streamlit의 채팅 UI와 세션 상태를 이해한다.
- Ollama API를 통해 EXAONE 모델을 호출한다.
- 모델의 답변을 실시간으로 스트리밍한다.
- 시스템 프롬프트, Temperature, 대화 초기화 기능을 추가한다.
- 노트북 환경에 맞게 문맥과 생성량을 조절한다.
- 웹, Python, Ollama, 모델 오류를 계층별로 진단한다.

## 동작 구조

```text
Browser
   |
   v
Streamlit
   |
   v
Python Ollama Client
   |
   | http://127.0.0.1:11434
   v
Ollama API
   |
   v
EXAONE 3.5 7.8B
```

질문은 브라우저에서 EXAONE 방향으로 전달되고, 생성된 텍스트 조각은 반대 방향으로 브라우저에 스트리밍된다.

## 시작 전 확인

- [ ] 가상환경에서 `Python 3.10.x`가 실행된다.
- [ ] Ollama API `127.0.0.1:11434`가 응답한다.
- [ ] `ollama list`에 `exaone3.5:7.8b`가 있다.
- [ ] VS Code에서 실습 프로젝트 폴더를 열었다.

---

## 1. 프로젝트 준비

### 실습 폴더 생성

```powershell
mkdir AI_01_Chatbot
cd AI_01_Chatbot
```

### Python 3.10 가상환경 생성

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

프롬프트 앞에 `(.venv)`가 나타나는지 확인한다.

### 패키지 설치

```powershell
python -m pip install -U streamlit ollama
python -m pip show streamlit ollama
```

두 패키지의 `Name`, `Version`, `Location`이 출력되면 올바른 가상환경에 설치된 것이다.

### Ollama와 모델 확인

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
ollama list
```

- API 응답에 `models` 배열이 있어야 한다.
- `ollama list`의 `NAME` 열에 `exaone3.5:7.8b`가 있어야 한다.
- 코드의 모델명은 `ollama list`에 표시된 이름과 정확히 같아야 한다.

### 프로젝트 구조

```text
AI_01_Chatbot/
|-- .venv/
|-- app.py
`-- requirements.txt
```

`requirements.txt`에는 다음 패키지를 기록한다.

```text
streamlit
ollama
```

다른 PC에서는 다음 명령으로 같은 패키지를 준비할 수 있다.

```powershell
python -m pip install -r requirements.txt
```

---

## 2. Streamlit 채팅 UI

Streamlit은 HTML과 JavaScript를 직접 작성하지 않아도 Python의 `st.*` 명령으로 웹 화면을 만들 수 있다. 사용자가 위젯을 조작하면 스크립트 전체를 위에서 아래로 다시 실행한다. 일반 변수는 다시 만들어지지만 `st.session_state`에 저장한 값은 같은 사용자 세션에서 유지된다.

### 최소 Echo Bot

먼저 AI를 연결하지 않고 입력창과 말풍선이 동작하는지 확인한다. `app.py`를 다음과 같이 작성한다.

```python
import streamlit as st

st.set_page_config(page_title="EXAONE Chat")
st.title("EXAONE 로컬 챗봇")

prompt = st.chat_input("질문을 입력하세요")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        st.write(f"입력한 질문: {prompt}")
```

실행한다.

```powershell
python -m streamlit run app.py
```

브라우저가 자동으로 열리지 않으면 터미널의 Local URL인 `http://localhost:8501`에 접속한다. 종료할 때는 실행 중인 터미널에서 `Ctrl+C`를 누른다.

### 주요 Streamlit API

| API | 역할 |
| --- | --- |
| `st.set_page_config(...)` | 브라우저 탭 제목과 아이콘 설정 |
| `st.title(text)` | 페이지의 큰 제목 출력 |
| `st.caption(text)` | 보조 설명 출력 |
| `st.chat_input(placeholder)` | 화면 하단의 채팅 입력창 생성 |
| `st.chat_message(role)` | `user` 또는 `assistant` 말풍선 생성 |
| `st.session_state` | rerun 사이에 사용자 세션의 값 보존 |
| `st.write_stream(iterable)` | 문자열 조각을 즉시 출력하고 완성된 문자열 반환 |
| `st.rerun()` | 변경된 상태로 스크립트를 즉시 다시 실행 |

`st.chat_input()`은 입력 전에는 `None`, 전송 후에는 사용자가 입력한 문자열을 반환한다.

---

## 3. 대화 기록 유지하기

### 세션 상태 초기화

첫 실행에서만 빈 메시지 목록을 만든다.

```python
if "messages" not in st.session_state:
    st.session_state.messages = []
```

초기화하지 않은 세션 키를 바로 읽으면 예외가 발생하므로 먼저 존재 여부를 확인한다.

### 저장된 메시지 복원

Streamlit은 입력할 때마다 rerun되므로 저장된 메시지를 매번 순서대로 다시 그린다.

```python
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

### 질문과 Echo 응답 저장

```python
if prompt := st.chat_input("질문을 입력하세요"):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    response = f"Echo: {prompt}"

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
```

사용자와 assistant 모두 **화면 표시**와 **`messages.append()` 기록**을 한 쌍으로 유지해야 다음 rerun에서도 대화가 사라지지 않는다.

### Echo Bot 합격 기준

1. 질문을 전송한다.
2. 사용자 말풍선이 나타난다.
3. `Echo:` 응답이 나타난다.
4. 다음 질문을 보내도 이전 대화가 유지된다.

Echo Bot이 정상이라면 입력, 말풍선, 대화 기록 문제는 해결된 것이다. 이후 발생하는 문제를 Ollama 연결 구간으로 좁힐 수 있다.

---

## 4. Ollama와 EXAONE 연결

### 클라이언트 생성

```python
from ollama import Client

OLLAMA_HOST = "http://127.0.0.1:11434"
MODEL = "exaone3.5:7.8b"

client = Client(host=OLLAMA_HOST)
```

`Client`는 실행 중인 Ollama 서버에 HTTP 요청을 보내며, 같은 서버 주소로 `chat`, `list`, `show`, `pull` 등의 메서드를 호출한다.

### 메시지 구조

Ollama의 `messages`는 다음 역할과 내용으로 구성된 목록이다.

```python
messages = [
    {"role": "system", "content": "챗봇의 공통 행동 규칙"},
    {"role": "user", "content": "사용자 질문"},
    {"role": "assistant", "content": "모델 답변"},
]
```

이전 메시지를 함께 보내야 모델이 앞선 대화 문맥을 참고할 수 있다.

### 단일 응답으로 연결 확인

Streamlit에 연결하기 전에 간단한 호출로 모델 응답을 확인한다.

```python
response = client.chat(
    model=MODEL,
    messages=[
        {"role": "user", "content": "안녕하세요"}
    ],
)

print(response.message.content)
```

`stream=False`인 기본 호출은 하나의 `ChatResponse` 객체를 반환한다. 최종 답변 문자열은 `response.message.content`에서 읽는다.

### 스트리밍 응답

`stream=True`로 호출하면 답변이 여러 `chunk`로 나뉘어 도착한다.

```python
stream = client.chat(
    model=MODEL,
    messages=st.session_state.messages,
    stream=True,
)

for chunk in stream:
    print(chunk.message.content, end="")
```

Streamlit에서는 generator를 `st.write_stream()`에 전달한다.

```python
with st.chat_message("assistant"):
    response = st.write_stream(
        chunk.message.content
        for chunk in client.chat(
            model=MODEL,
            messages=st.session_state.messages,
            stream=True,
        )
    )
```

텍스트 조각이 타이핑 효과로 표시되고, 완료 후 전체 문자열이 `response`에 반환된다. 이 문자열을 세션에 저장해야 다음 질문에서 이전 답변도 문맥으로 전달된다.

```python
st.session_state.messages.append(
    {"role": "assistant", "content": response}
)
```

---

## 5. 기본 완성 코드

설정, 기록 복원, 질문 처리, 스트리밍을 하나의 `app.py`로 조립한다.

```python
import streamlit as st
from ollama import Client

MODEL = "exaone3.5:7.8b"
SYSTEM_PROMPT = (
    "당신은 초보자를 돕는 AI 강사입니다. "
    "답변은 한국어로 핵심부터 설명하세요."
)

client = Client(host="http://127.0.0.1:11434")

st.set_page_config(
    page_title="EXAONE Chat",
    page_icon="🤖",
)
st.title("EXAONE 로컬 챗봇")
st.caption("Streamlit + Ollama")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(
            chunk.message.content
            for chunk in client.chat(
                model=MODEL,
                messages=st.session_state.messages,
                stream=True,
            )
        )

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
```

실행한다.

```powershell
python -m streamlit run app.py
```

`http://localhost:8501`에서 제목, 입력창, 역할별 말풍선과 EXAONE의 스트리밍 응답이 나타나면 성공이다.

### 대화 기억 테스트

다음 질문을 순서대로 보내 앞선 문맥이 유지되는지 확인한다.

1. `가상환경을 한 문장으로 설명해줘`
2. `방금 설명을 초등학생도 이해하게 바꿔줘`
3. `첫 답변과 두 번째 답변의 차이를 알려줘`

---

## 6. 노트북 환경 최적화

### CPU와 GPU 사용 상태 확인

```powershell
ollama ps
```

`PROCESSOR`의 의미는 다음과 같다.

| 표시 | 의미 |
| --- | --- |
| `100% GPU` | 모델 전체가 GPU에 적재됨 |
| `CPU/GPU` | CPU와 GPU에 부분 적재됨 |
| `100% CPU` | 시스템 메모리에서 CPU로 실행됨 |

노트북에서는 7.8B Q4_K_M 약 4.8GB 모델을 현실적인 시작점으로 사용한다. 같은 모델의 Q8_0은 약 8.3GB, FP16은 약 16GB이다.

### 권장 시작값

| 설정 | 시작값 | 역할 |
| --- | ---: | --- |
| `num_ctx` | `2048` | 시스템 프롬프트, 이전 대화, 현재 질문을 포함한 문맥 크기 |
| `num_predict` | `256` | 생성할 최대 토큰 수 |
| `keep_alive` | `"30m"` | 응답 후 모델을 메모리에 유지할 시간 |
| 최근 메시지 | `10개` | 모델에 전달할 최근 대화 수 |

32K 문맥을 지원하더라도 항상 32K를 사용할 필요는 없다. 문맥이 커질수록 메모리 부담이 증가하므로 짧은 질의응답에서는 2048부터 시작하고 긴 문서가 필요할 때만 늘린다.

`keep_alive="30m"`은 연속 질문의 재로딩을 줄이지만 RAM, VRAM과 배터리를 계속 사용한다.

### 모델에 전달할 대화 제한

화면에는 전체 대화를 유지하면서 모델에는 시스템 메시지와 최근 10개 메시지만 보낸다.

```python
system_message = st.session_state.messages[:1]
recent_messages = st.session_state.messages[1:][-10:]
request_messages = system_message + recent_messages
```

### 최적화된 호출

```python
stream = client.chat(
    model=MODEL,
    messages=request_messages,
    stream=True,
    keep_alive="30m",
    options={
        "num_ctx": 2048,
        "num_predict": 256,
        "temperature": temperature,
    },
)
```

최적화 전후에는 같은 질문으로 다음 항목을 비교한다.

- 첫 번째와 두 번째 질문에서 응답이 시작되는 시간
- 전체 답변이 끝나는 시간
- `ollama ps`의 `PROCESSOR` 상태
- 작업 관리자의 RAM과 GPU 메모리 사용량

---

## 7. 챗봇 기능 확장

### 시스템 프롬프트

시스템 프롬프트는 사용자가 매번 요청하지 않아도 답변 언어, 대상 수준, 형식과 역할을 고정한다. 사실이나 사용자 질문을 대신 저장하는 용도는 아니다.

```python
SYSTEM_PROMPT = (
    "당신은 초보자를 돕는 AI 강사입니다. "
    "한국어로 핵심부터 설명하고 예제를 보여주세요."
)

st.session_state.messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]
```

시스템 메시지는 모든 요청에 전달하되 화면에서는 숨긴다.

### Temperature 조절

```python
with st.sidebar:
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.5,
        value=0.7,
        step=0.1,
    )
```

- 낮은 값: 답변이 비교적 일관적이어서 강의 설명이나 재현성이 중요한 작업에 적합하다.
- 높은 값: 표현이 다양해져 아이디어 탐색에 적합하다.

호출 옵션에 선택한 값을 전달한다.

```python
options={"temperature": temperature}
```

### 대화 초기화

```python
if st.button("대화 초기화"):
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    st.rerun()
```

버튼을 누르면 사용자와 assistant 기록은 사라지고 시스템 메시지만 남는다. `st.rerun()`은 변경된 상태로 화면을 즉시 다시 그린다.

---

## 8. 확장 기능을 포함한 통합 코드

다음 코드는 강의의 시스템 프롬프트, Temperature, 초기화, 최근 문맥 제한, 노트북 권장값과 오류 안내를 하나로 합친 예시다.

```python
import streamlit as st
from ollama import Client

MODEL = "exaone3.5:7.8b"
OLLAMA_HOST = "http://127.0.0.1:11434"
SYSTEM_PROMPT = (
    "당신은 초보자를 돕는 AI 강사입니다. "
    "한국어로 핵심부터 설명하고 예제를 보여주세요."
)

client = Client(host=OLLAMA_HOST)

st.set_page_config(
    page_title="EXAONE Chat",
    page_icon="🤖",
)
st.title("EXAONE 로컬 챗봇")
st.caption("Streamlit + Ollama")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

with st.sidebar:
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.5,
        value=0.7,
        step=0.1,
    )

    if st.button("대화 초기화"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()

for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    system_message = st.session_state.messages[:1]
    recent_messages = st.session_state.messages[1:][-10:]
    request_messages = system_message + recent_messages

    try:
        with st.chat_message("assistant"):
            stream = client.chat(
                model=MODEL,
                messages=request_messages,
                stream=True,
                keep_alive="30m",
                options={
                    "num_ctx": 2048,
                    "num_predict": 256,
                    "temperature": temperature,
                },
            )
            response = st.write_stream(
                chunk.message.content for chunk in stream
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )
    except Exception as error:
        st.error(f"Ollama 연결 또는 모델 호출에 실패했습니다: {error}")
        st.code(
            "Invoke-RestMethod http://127.0.0.1:11434/api/tags",
            language="powershell",
        )
```

오류가 발생한 assistant 응답은 대화 기록에 추가하지 않는다. 사용자가 같은 질문을 다시 시도하거나 대화를 초기화할 수 있다.

---

## 문제 해결

### `Failed to connect to Ollama`

Ollama 앱을 실행하고 API부터 확인한다.

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

API가 응답하지 않는다면 Streamlit 코드보다 Ollama 서버 상태를 먼저 해결한다.

### `model 'exaone3.5:7.8b' not found`

실제 모델명을 확인한다.

```powershell
ollama list
```

모델이 없다면 먼저 내려받는다.

```powershell
ollama run exaone3.5:7.8b
```

`MODEL` 값은 `ollama list`의 `NAME`과 정확히 일치해야 한다.

### Streamlit 명령을 찾을 수 없음

가상환경을 활성화하고 현재 Python에 Streamlit을 설치한 뒤 모듈 방식으로 실행한다.

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install streamlit
python -m streamlit run app.py
```

### 브라우저는 열렸지만 앱이 표시되지 않음

Streamlit 실행 터미널에서 **가장 먼저 발생한 traceback**과 `app.py` 줄 번호를 확인한다. 코드를 수정해 저장한 뒤 다시 실행한다.

### 계층별 점검 순서

```text
브라우저 localhost:8501
        ↓
Streamlit 실행 여부
        ↓
Python traceback
        ↓
Ollama API 11434
        ↓
EXAONE 모델 이름과 설치 상태
```

---

## 실습 과제

### 실습 1: 수업 도우미 챗봇

목표는 답변을 항상 3단계로 설명하는 챗봇을 만드는 것이다.

1. `SYSTEM_PROMPT`에 대상과 답변 형식을 작성한다.
2. 가상환경 관련 질문을 두 번 이어서 보낸다.
3. 후속 질문이 이전 대화를 기억하는지 확인한다.

합격 기준은 각 답변이 1, 2, 3단계 구조이고 후속 질문이 앞선 문맥을 사용하는 것이다.

### 실습 2: 답변 다양성 비교

1. 사이드바에 Temperature 슬라이더를 추가한다.
2. `0.1`과 `1.2`에서 같은 질문을 보낸다.
3. 표현과 일관성의 차이를 기록한다.

합격 기준은 두 설정의 차이를 화면의 실제 결과로 설명할 수 있는 것이다.

### 실습 3: 오류 친화형 챗봇

1. `client.chat()`을 `try/except`로 감싼다.
2. `st.error()`로 오류 요약을 출력한다.
3. Ollama API 11434 확인 명령을 안내한다.

합격 기준은 Ollama 서버를 끈 상태에서도 앱이 종료되지 않고 해결 방법을 보여 주는 것이다.

---

## 최종 검증 체크리스트

- [ ] `http://localhost:8501`에 접속할 수 있다.
- [ ] 사용자와 assistant의 말풍선이 구분된다.
- [ ] EXAONE 답변이 실시간으로 스트리밍된다.
- [ ] 후속 질문에서 이전 대화 문맥이 유지된다.
- [ ] 시스템 프롬프트가 답변 기준에 반영된다.
- [ ] Temperature 값에 따라 답변 특성이 달라진다.
- [ ] 대화 초기화 버튼이 정상 작동한다.
- [ ] Ollama 연결 실패 시 오류와 해결 방법이 표시된다.

## 핵심 정리

- Streamlit은 위젯 입력 때마다 스크립트를 다시 실행하므로 대화는 `st.session_state`에 저장해야 한다.
- 메시지는 `system`, `user`, `assistant` 역할과 `content`로 구성한다.
- `stream=True`와 `st.write_stream()`을 연결하면 생성 중인 답변을 즉시 표시할 수 있다.
- 화면에 표시한 메시지와 세션에 저장한 메시지를 항상 같은 내용으로 유지해야 한다.
- 노트북에서는 Q4_K_M, `num_ctx=2048`, `num_predict=256`, 최근 대화 10개를 시작점으로 삼는다.
- 오류는 브라우저, Streamlit, Python, Ollama API, 모델 순서로 분리해서 확인한다.

이 챗봇 화면은 이후 문서 검색, 데이터 분석, 도구 호출과 모델 평가 기능을 연결하는 공통 테스트 화면으로 확장할 수 있다.
