# Qwen2.5-0.5B 파이썬 기초 문법 파인튜닝

`Qwen/Qwen2.5-0.5B-Instruct`를 CPU에서 직접 전체 파인튜닝하는 예제입니다.
CSV에는 질문이나 모델이 생성한 답변을 넣지 않고, 파이썬 기초 문법 정보만 저장합니다. 학습할 때만 코드가 `concept`를 이용해 일반적인 질문 형식을 만들고 `content`를 정답으로 학습합니다.

## 학습 데이터

[`data/python_basics_knowledge.csv`](data/python_basics_knowledge.csv)는 다음 열로 구성된 UTF-8 CSV입니다.

- `id`: 자료 번호
- `category`: 문법 분류
- `concept`: 문법 이름
- `content`: 학습할 설명과 예제
- `source_url`: 확인에 사용한 Python 공식 문서 주소

현재 숫자, 문자열, 조건문, 반복문, 함수, 리스트·튜플·딕셔너리와 예외 처리에 관한 핵심 자료 10건이 들어 있습니다. CSV 파일 자체에는 질문 열이 없습니다.

## 설치

PowerShell에서 다음 명령을 실행합니다.

```powershell
cd C:\Users\user\Documents\Ollama2
.\install_cpu_deps.ps1
```

CUDA가 아닌 `torch==2.7.0+cpu`를 사용합니다.

## 전체 파인튜닝

```powershell
cd C:\Users\user\Documents\Ollama2
.\.venv\Scripts\python.exe .\train_cpu_full_finetune.py `
  --train-file .\data\python_basics_knowledge.csv `
  --output-dir .\outputs\python_basics_knowledge_model `
  --epochs 5 --batch-size 1 --gradient-accumulation 4 `
  --max-length 160 --cpu-threads 4
```

모델의 모든 파라미터를 학습하므로 LoRA보다 느리고 메모리를 더 사용합니다. 완성된 전체 가중치와 `training_results.json`은 `C:\Users\user\Documents\Ollama2\outputs\python_basics_knowledge_model`에 저장됩니다.

이번 실제 학습 결과의 공개 가능한 요약은 [`outputs/full_finetune_results.json`](outputs/full_finetune_results.json)에 저장했습니다.

## 사용자 질문 실행

```powershell
cd C:\Users\user\Documents\Ollama2
.\.venv\Scripts\python.exe .\chat_finetuned_cpu.py
```

콘솔에 파이썬 기초 질문을 입력하면 답변합니다. CSV에 있는 핵심 문법은 검증된 `content`를 그대로 답해 작은 0.5B 모델의 숫자·문법 왜곡을 막고, CSV에서 찾지 못한 질문은 파인튜닝 모델이 생성합니다. `종료`, `exit`, `quit` 중 하나를 입력하면 끝납니다.

질문 한 건만 실행하고 종료할 수도 있습니다.

```powershell
.\.venv\Scripts\python.exe .\chat_finetuned_cpu.py `
  --question "range 함수는 어떻게 사용해?"
```

## 기존 LoRA 예제

기존의 작은 LoRA 학습 예제도 비교용으로 유지합니다.

```powershell
.\.venv\Scripts\python.exe .\train_cpu_lora.py `
  --train-file .\data\sample_train.jsonl `
  --output-dir .\outputs\my_lora
```

## 공개 저장소 보안

- 전체 모델 가중치, 체크포인트, 캐시와 로컬 실행 결과는 Git에서 제외합니다.
- 검토 가능한 소스 코드와 기초 문법 CSV만 GitHub 복사본에 보관합니다.
- 기본 원격 모델은 검토한 `Qwen/Qwen2.5-0.5B-Instruct`로 제한합니다.
- API 키, 토큰, 개인정보는 CSV나 결과 파일에 넣지 않습니다.

## 파일 구성

- `data/python_basics_knowledge.csv`: 질문이 없는 파이썬 기초 문법 학습 자료
- `train_cpu_full_finetune.py`: CSV의 문법명과 설명으로 질문-응답 학습 예제를 메모리에서 구성해 전체 파라미터를 CPU 학습
- `chat_finetuned_cpu.py`: CSV의 검증 답변과 학습된 로컬 모델을 사용하는 대화 프로그램
- `train_cpu_lora.py`: 비교용 LoRA 학습
- `test_weights_cpu.py`: 기본 모델과 학습 가중치 생성 테스트
- `view_training_results.py`: 학습 결과 JSON 조회
- `outputs/full_finetune_results.json`: 실제 전체 파인튜닝 결과 요약
