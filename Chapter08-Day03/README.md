# Qwen2.5 0.5B CPU LoRA 학습 및 결과 조회

`Qwen/Qwen2.5-0.5B-Instruct`를 CPU에서 LoRA 방식으로 미세 조정하는 예제다. 기본 모델 가중치는 고정하고 약 0.88%의 어댑터 파라미터만 학습한다.

## 학습 결과 데이터

실행이 완료되면 어댑터 폴더에 `training_results.json`이 생성된다. 이 저장소에는 예제 4건을 1 epoch 학습한 결과가 [outputs/training_results.json](outputs/training_results.json)으로 포함되어 있다.

```powershell
python .\view_training_results.py
```

원본 JSON 전체를 보려면 다음을 실행한다.

```powershell
python .\view_training_results.py --json
```

## CPU 의존성 설치

```powershell
.\install_cpu_deps.ps1
```

CUDA가 아닌 `torch==2.7.0+cpu`를 설치한다.

## LoRA 학습

`data/sample_train.jsonl`은 UTF-8 JSONL 형식의 `prompt`, `response` 예제다.

```powershell
python .\train_cpu_lora.py `
  --train-file .\data\sample_train.jsonl `
  --output-dir .\outputs\my_lora `
  --epochs 3 --batch-size 1 --gradient-accumulation 8 --max-length 256 --cpu-threads 4
```

메모리가 부족하면 `--max-length 128` 또는 `--lora-r 4`로 낮춘다.

## 가중치 테스트

기본 모델:

```powershell
python .\test_weights_cpu.py
```

학습한 어댑터:

```powershell
python .\test_weights_cpu.py --model-id .\outputs\my_lora
```

## 공개 저장소 보안 규칙

- `outputs/`의 가중치·토크나이저·학습 설정은 Git에서 제외된다. 예제 결과 요약인 `outputs/training_results.json`만 공개한다.
- 실제 학습 데이터는 `data/*.jsonl`로 저장소에서 제외된다. 공개 가능한 예제 파일은 `data/sample_train.jsonl`만 유지한다.
- 기본 원격 모델은 검토한 `Qwen/Qwen2.5-0.5B-Instruct`만 허용한다. 다른 원격 모델은 출처를 검증한 뒤 `--allow-remote-model`을 명시해야 한다.
- API 키, 토큰, 개인정보를 학습 데이터·명령줄 인자·결과 JSON에 넣지 않는다.

## 파일 구성

- `train_cpu_lora.py`: CPU 전용 LoRA 학습 및 결과 JSON 생성
- `view_training_results.py`: 결과 JSON 콘솔 조회
- `test_weights_cpu.py`: 기본/어댑터 가중치 생성 테스트
- `outputs/training_results.json`: 실제 예제 학습 결과
