# Windows 로컬 AI 인프라 구축

Python, Ollama, WSL2, Docker Desktop, Open WebUI를 연결해 클라우드 API 없이 내 PC에서 AI 모델과 대화하는 환경을 구축한다.

## 학습 목표

- Python 3.10 가상환경을 구성한다.
- Ollama에 EXAONE 모델을 설치하고 로컬 API를 확인한다.
- Python과 LangChain에서 Ollama 모델을 호출한다.
- WSL2와 Docker Desktop을 설치하고 컨테이너 실행 환경을 검증한다.
- Open WebUI를 통해 브라우저에서 로컬 모델과 대화한다.

## 전체 구성

```text
브라우저
   |
   | http://localhost:3000
   v
Open WebUI (Docker 컨테이너, 내부 포트 8080)
   |
   | http://host.docker.internal:11434
   v
Ollama (Windows, API 포트 11434)
   |
   v
EXAONE 3.5 7.8B Instruct
```

설치는 다음 순서로 진행한다.

1. Python 3.10
2. Ollama와 EXAONE
3. WSL2
4. Docker Desktop
5. Open WebUI

## 사전 요구 사항

- Windows 10 22H2 또는 Windows 11
- 64비트 CPU
- BIOS/UEFI 가상화 기능 활성화
- 메모리 8GB 이상 권장
- 모델을 저장할 충분한 디스크 공간

EXAONE의 Q4_K_M 모델만 약 4.8GB이므로, Docker 이미지와 가상환경에 필요한 공간도 함께 고려한다.

---

## 1. Python 3.10 환경 구성

### Python 설치

강의 표준 버전은 Python 3.10.11이다. 공식 Windows installer(64-bit)를 사용하고 설치 화면에서 **Add python.exe to PATH**를 선택한다.

새 터미널을 열어 설치 결과를 확인한다.

```powershell
python --version
```

정상이라면 `Python 3.10.x`가 출력된다.

### 여러 Python 버전 확인

기존 Python을 삭제할 필요는 없다. Python Launcher로 설치된 버전을 확인한다.

```powershell
py --list
```

목록에 3.10이 있으면 `py -3.10`으로 해당 버전을 선택할 수 있다. 없다면 Python 3.10.11을 추가로 설치하면서 Python Launcher도 포함한다.

### 가상환경 생성 및 활성화

프로젝트 폴더에서 Python 3.10 전용 가상환경을 만든다.

```powershell
py -3.10 -m venv .venv
```

PowerShell에서 활성화한다.

```powershell
.\.venv\Scripts\Activate.ps1
python --version
```

프롬프트 앞에 `(.venv)`가 표시되고 `Python 3.10.x`가 출력되면 성공이다.

PowerShell이 `Activate.ps1` 실행을 차단할 때만 현재 사용자 범위의 실행 정책을 조정한다.

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

PowerShell을 다시 연 뒤 가상환경을 활성화한다.

---

## 2. Ollama와 EXAONE 설치

Ollama는 Windows에서 모델을 실행하고 `localhost:11434`에 API 서버를 제공한다. Python의 `ollama` 패키지는 이 서버를 호출하는 클라이언트이므로, Ollama Windows 앱을 먼저 설치해야 한다.

### Ollama 설치 확인

`OllamaSetup.exe`로 Windows 앱을 설치한 뒤 새 PowerShell을 연다.

```powershell
ollama --version
```

버전이 표시되면 PATH 등록이 완료된 것이다.

Ollama 앱을 실행한 상태에서 API를 확인한다.

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

설치된 모델 목록이 JSON으로 반환되면 서버가 정상적으로 실행 중이다.

### 강의 표준 모델

강의에서는 LG AI Research의 한국어·영어 지시형 모델인 **EXAONE 3.5 7.8B Instruct**를 사용한다.

| 형식 | 대략적인 크기 | 특징 |
| --- | ---: | --- |
| Q4_K_M | 4.8GB | 실습 PC에 권장, 용량과 품질의 균형 |
| Q8_0 | 8.3GB | 더 큰 메모리와 디스크 필요 |
| FP16 | 16GB | 가장 큰 용량 필요 |

### 방법 A: Ollama 공식 모델 실행

가장 간단한 설치 방법이다.

```powershell
ollama run exaone3.5:7.8b
```

Q4_K_M 모델 다운로드가 끝난 뒤 `>>>` 프롬프트가 나타나면 성공이다. 종료 명령은 `/bye`이다.

설치된 모델명을 확인한다.

```powershell
ollama list
```

`NAME` 열에 `exaone3.5:7.8b`가 표시되어야 한다. 이후 Python, LangChain, Open WebUI에서도 같은 모델명을 사용한다.

### 방법 B: Hugging Face의 공식 GGUF 직접 실행

Ollama가 Hugging Face의 Q4_K_M GGUF를 직접 내려받도록 할 수 있다.

```powershell
ollama run hf.co/LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct-GGUF:Q4_K_M
```

### 방법 C: GGUF 수동 다운로드 및 등록

Hugging Face CLI를 설치한다.

```powershell
python -m pip install -U huggingface_hub
hf --help
```

CMD에서 Q4_K_M 파일 하나만 내려받는다.

```bat
hf download LGAI-EXAONE/^
EXAONE-3.5-7.8B-Instruct-GGUF ^
EXAONE-3.5-7.8B-Instruct-Q4_K_M.gguf ^
--local-dir ./models/exaone
```

다운로드가 끝나면 `./models/exaone`에 약 4.77GB의 GGUF 파일이 생성된다.

프로젝트 루트에 확장자 없이 `Modelfile`을 만든다.

```dockerfile
FROM ./models/exaone/EXAONE-3.5-7.8B-Instruct-Q4_K_M.gguf
PARAMETER stop "[|endofturn|]"
PARAMETER repeat_penalty 1.0
TEMPLATE """{{- range $i, $_ := .Messages }}
{{- $last := eq (len (slice $.Messages $i)) 1 -}}
{{ if eq .Role "system" }}[|system|]{{ .Content }}[|endofturn|]
{{ continue }}
{{ else if eq .Role "user" }}[|user|]{{ .Content }}
{{ else if eq .Role "assistant" }}[|assistant|]{{ .Content }}[|endofturn|]
{{ end }}
{{- if and (ne .Role "assistant") $last }}[|assistant|]{{ end }}
{{- end -}}"""
SYSTEM """You are EXAONE model from LG AI Research, a helpful assistant."""
```

`FROM`의 상대 경로는 `Modelfile` 위치를 기준으로 해석된다. 모델을 강의용 이름으로 등록하고 실행한다.

```powershell
ollama create exaone-3.5-7.8b-instruct -f Modelfile
ollama run exaone-3.5-7.8b-instruct
```

`ollama create`에서 `success`가 표시되고 한국어 질문에 응답하면 성공이다. 이 모델명은 직접 등록한 경우에만 사용한다.

> EXAONE 모델 카드에는 `EXAONE AI Model License Agreement 1.1 - NC`가 명시되어 있다. 강의·연구 외 배포나 상업적 이용을 계획한다면 사용 시점의 최신 라이선스 원문을 반드시 확인한다.

---

## 3. Python에서 Ollama 호출

### 연동 패키지 설치

활성화된 가상환경에서 패키지를 설치한다.

```powershell
python -m pip install -U pip
python -m pip install -U ollama langchain langchain-ollama
pip show ollama langchain langchain-ollama
```

### Ollama Python 클라이언트

다음 코드를 `ollama_test.py`로 저장한다.

```python
from ollama import Client

client = Client(host="http://127.0.0.1:11434")
response = client.chat(
    model="exaone3.5:7.8b",
    messages=[
        {
            "role": "user",
            "content": "가상환경의 장점을 한 문장으로 설명해줘",
        }
    ],
)

print(response.message.content)
```

### LangChain의 ChatOllama

다음 코드를 `langchain_test.py`로 저장한다.

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="exaone3.5:7.8b",
    base_url="http://127.0.0.1:11434",
    temperature=0,
)

answer = llm.invoke("Windows에서 가상환경을 쓰는 이유는?")
print(answer.content)
```

API를 먼저 확인한 뒤 두 예제를 실행한다.

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
python ollama_test.py
python langchain_test.py
```

API의 모델 목록과 두 Python 파일의 EXAONE 응답이 모두 출력되면 연동에 성공한 것이다.

---

## 4. WSL2 설치

WSL2는 실제 Linux 커널을 가벼운 가상 머신에서 실행하며, Docker의 Linux 컨테이너가 동작할 기반을 제공한다.

관리자 PowerShell에서 설치한다.

```powershell
wsl --install
```

명령이 필요한 Windows 기능과 기본 Ubuntu 배포판을 설치한다. 설치가 끝나면 가상화 기능과 커널 구성이 완전히 적용되도록 **Windows를 재부팅**한다.

재부팅 후 상태를 확인한다.

```powershell
wsl --list --verbose
```

Ubuntu 행의 `VERSION` 열이 `2`이면 성공이다.

---

## 5. Docker Desktop 설치

Docker Desktop을 기본 설정으로 설치하고 WSL2 기반 엔진을 사용한다.

Docker Desktop의 **Settings > General**에서 **Use the WSL 2 based engine**이 활성화되어 있는지 확인한다.

첫 컨테이너를 실행해 Docker 클라이언트, 데몬, 이미지 다운로드, 컨테이너 실행 흐름을 한 번에 검증한다.

```powershell
docker run hello-world
```

`Hello from Docker!`가 출력되면 정상이다.

---

## 6. Open WebUI 실행

Open WebUI는 로컬 AI를 브라우저 대화 화면으로 제공한다. Docker 컨테이너로 실행하면 UI와 데이터를 분리해 관리할 수 있다.

### CLI로 실행

다음 명령은 CMD의 줄 연속 기호 `^`를 사용한다.

```bat
docker run -d -p 3000:8080 ^
--add-host=host.docker.internal:host-gateway ^
-v open-webui:/app/backend/data ^
--name open-webui --restart always ^
ghcr.io/open-webui/open-webui:main
```

옵션의 의미는 다음과 같다.

| 옵션 | 의미 |
| --- | --- |
| `-d` | 컨테이너를 백그라운드에서 실행 |
| `-p 3000:8080` | Windows의 3000번 포트를 컨테이너의 8080번 포트에 연결 |
| `--add-host=...` | 컨테이너에서 Windows 호스트에 접근할 주소 추가 |
| `-v open-webui:/app/backend/data` | 설정과 대화 데이터를 Docker 볼륨에 보존 |
| `--name open-webui` | 컨테이너 이름 고정 |
| `--restart always` | Docker 재시작 후 컨테이너 자동 실행 |

브라우저에서 `http://localhost:3000`으로 접속한다.

### Docker Desktop GUI로 실행

Docker Desktop의 **Images**에서 `ghcr.io/open-webui/open-webui:main` 이미지의 **Run**을 누르고 **Optional settings**를 설정한다.

| 항목 | 값 |
| --- | --- |
| Container name | `open-webui` |
| Host port | `3000` |
| Container port | `8080/tcp` |
| Host path | `C:\Users\사용자명\open-webui-data` |
| Container path | `/app/backend/data` |
| Environment variable | `OLLAMA_BASE_URL` |
| Environment value | `http://host.docker.internal:11434` |

Host path로 사용할 폴더는 먼저 만든 뒤 **Browse**에서 선택한다. GUI에서 설정하기 어려운 `--restart always` 같은 고급 옵션은 CLI나 Docker Compose를 사용한다.

### 실행 상태 확인

- **Containers**에서 `open-webui`가 `Running`인지 확인한다.
- 포트에 `3000:8080`이 표시되는지 확인한다.
- 브라우저에서 `http://localhost:3000`에 접속한다.
- 모델 목록과 입력창이 나타나는지 확인한다.

### Ollama 연결 및 모델 선택

컨테이너에서 Windows의 Ollama에 접근할 때는 `localhost` 대신 다음 주소를 사용한다.

```text
http://host.docker.internal:11434
```

Open WebUI의 **Admin Settings > Connections > Ollama**에 이 주소를 입력한다.

EXAONE을 설치하거나 선택하는 방법은 다음과 같다.

1. **Admin Settings > Connections > Ollama > Manage**에서 `exaone3.5:7.8b`를 입력해 다운로드한다.
2. 새 대화의 모델 선택기에 `exaone3.5:7.8b`를 입력한다. 미설치 상태라면 다운로드 제안이 나타난다.
3. 공식 GGUF를 직접 가져오려면 다음 모델 경로를 입력한다.

```text
hf.co/LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct-GGUF:Q4_K_M
```

모델 선택기에서 `exaone3.5:7.8b`를 선택하고 첫 질문에 응답하면 전체 설치가 완료된 것이다.

---

## 문제 해결

### `python` 명령을 찾지 못하는 경우

증상:

```text
'python' is not recognized
```

Python 설치 폴더와 `Scripts` 폴더를 사용자 `Path`에 추가한 뒤 새 터미널을 연다.

### `ollama` 명령을 찾지 못하는 경우

기본 설치 경로에 실행 파일이 있는지 확인한다.

```powershell
$ollamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
Test-Path $ollamaExe
```

- `True`: 현재 PowerShell의 PATH 문제이다.
- `False`: Ollama Windows 앱이 설치되지 않은 상태이다.

`True`라면 현재 세션의 PATH를 복구한다.

```powershell
$env:Path += ";$env:LOCALAPPDATA\Programs\Ollama"
ollama --version
```

버전이 표시되면 PowerShell과 VS Code를 완전히 종료했다가 다시 연다. `False`라면 `OllamaSetup.exe`를 설치하고 시작 메뉴에서 Ollama를 실행한 뒤 새 터미널에서 다시 확인한다.

### Ollama 연결 오류

증상:

```text
Failed to connect to Ollama
```

시작 메뉴에서 Ollama 앱을 실행하고 API부터 확인한다.

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

`pip install ollama`는 Python 클라이언트만 설치하며 Ollama 서버를 설치하지 않는다.

### WSL2 설치가 불완전한 경우

증상:

```text
WSL 2 installation is incomplete
```

관리자 PowerShell에서 업데이트한다.

```powershell
wsl --update
```

Microsoft Store가 차단된 환경에서는 `--web-download` 옵션이나 공식 MSI 배포본을 사용한다.

### 3000번 포트가 충돌하는 경우

기존 컨테이너를 제거한 뒤 호스트 포트만 다른 값으로 바꾼다. 예를 들어 `-p 8080:8080`으로 실행했다면 브라우저에서 `http://localhost:8080`으로 접속한다.

포트 매핑은 `호스트 포트:컨테이너 포트` 순서라는 점에 주의한다.

### 가상화가 비활성화된 경우

증상:

```text
Virtualization is disabled
```

작업 관리자에서 가상화 상태를 확인하고 BIOS/UEFI에서 다음 항목 중 해당하는 기능을 활성화한다.

- Intel Virtualization Technology
- AMD SVM

---

## 최종 검증 체크리스트

- [ ] `(.venv) python --version`에서 `Python 3.10.x`가 출력된다.
- [ ] `ollama run exaone3.5:7.8b`에서 `>>>` 프롬프트가 나타난다.
- [ ] Ollama API 11434에서 모델 목록을 확인할 수 있다.
- [ ] Python과 LangChain 예제에서 EXAONE 응답이 출력된다.
- [ ] `wsl --list --verbose`에서 Ubuntu의 `VERSION`이 `2`이다.
- [ ] `docker run hello-world`에서 `Hello from Docker!`가 출력된다.
- [ ] Docker Desktop에서 `open-webui` 컨테이너가 `Running` 상태이다.
- [ ] `http://localhost:3000`에서 EXAONE을 선택하고 질문할 수 있다.

## 핵심 정리

- 설치 순서는 **Python → Ollama/EXAONE → WSL2 → Docker Desktop → Open WebUI**이다.
- Ollama 서버가 먼저 실행되어야 Python 클라이언트와 Open WebUI가 연결될 수 있다.
- Windows에서 Ollama API 주소는 `127.0.0.1:11434`, Docker 컨테이너에서는 `host.docker.internal:11434`를 사용한다.
- Docker 볼륨을 사용하면 컨테이너를 다시 만들어도 Open WebUI의 설정과 대화 데이터를 유지할 수 있다.
- 각 단계를 설치 직후 검증하면 PATH, 가상화, 포트, 서버 연결 문제를 빠르게 분리할 수 있다.

다음 단계에서는 이 환경을 이용해 모델 비교, 프롬프트 실험, 문서 기반 질의, API 연동을 진행할 수 있다.
