# 과제신호등

같은 과목을 듣는 학생들이 과제 정보를 함께 관리하고, 마감까지 남은 시간과 개인 진행 상태를 기준으로 급한 과제를 먼저 확인하는 Django 웹 서비스입니다.

> 현재 상태: 주요 기능 구현 및 테스트 완료 · Neon PostgreSQL 연결 지원 · Render 배포 직전 구성

## Day 2 학습 내용

- 클라우드 컴퓨팅과 서비스 배포 구조를 학습하고 Docker의 이미지·컨테이너 개념을 실습했습니다.
- Django 웹 서비스에 PostgreSQL·Neon, Gunicorn, WhiteNoise, Render 배포 구성을 연결했습니다.
- 과제 우선순위, 사용자별 진행 상태, 브라우저 푸시 알림을 결합한 '과제신호등' 프로토타입을 구현했습니다.
- Day 3에서는 이 프로젝트를 '우선콕'으로 개선하고 로컬 개발·배포 흐름을 다듬었습니다. 최신 버전은 [Week 06 · Day 03](../Week06-Day03/README.md)에서 확인할 수 있습니다.

## 프로젝트 목적과 의도

- **문제:** 과제 공지를 확인하고도 자주 잊거나, 개인 일정에 기록하지 못해 제출 기한을 놓치는 학생들이 있습니다.
- **목적:** 같은 수업을 듣는 친구들이 과제 정보를 함께 입력하고 공유하여, 과제를 자주 잊는 친구도 제시간에 확인하고 제출하도록 돕습니다.
- **의도:** 주변 친구들의 공동 입력에 남은 시간과 개인 진행 상태 분석을 더하고, 필요하면 서로의 진행 현황을 확인해 직접 찌르기 알림을 보내며 과제를 잊지 않도록 돕습니다.

## 사용자 역할

| 기능 | 구성원 | 관리자 |
| --- | --- | --- |
| 과제 조회 및 개인 진행 상태 변경 | 가능 | 가능 |
| 과제 등록 및 자신이 등록한 과제 수정·삭제 | 가능 | 가능 |
| 다른 사용자가 등록한 과제 수정 | 불가 | 가능 |
| 다른 사용자가 등록한 과제 삭제 | 불가 | 가능 |
| 그룹 정보 수정 | 불가 | 가능 |
| 관리자 지정·해제 및 구성원 내보내기 | 불가 | 가능 |
| 그룹 삭제 | 불가 | 가능 |
| 그룹 나가기 | 가능 | 가능하나 단독 관리자는 제한 |
| 공개 옵션이 켜진 그룹의 구성원 현황 확인·찌르기 | 가능 | 가능 |

모든 그룹 관리 기능은 화면 표시뿐 아니라 Django 뷰에서도 권한을 다시 검사합니다.

## 구현 기능

### 회원과 계정

- 이메일을 입력하는 회원가입과 24시간 유효한 이메일 인증
- 이메일 기반 로그인 및 로그아웃
- 로그인 5회 실패 시 이메일·IP 조합을 30초 동안 잠금
- 비밀번호 변경과 이메일 기반 비밀번호 재설정
- 마이페이지에서 참여 그룹 수, 진행할 과제 수, 알림 등록 기기 수 확인
- 회원 탈퇴 시 개인 진행 상태·그룹 참여·푸시 구독 삭제 및 계정 익명화
- 단독 관리자인 그룹이 있으면 다른 관리자를 지정하거나 그룹을 삭제하기 전까지 탈퇴 제한

### 공유 그룹

- 그룹 이름을 입력하고 설명을 선택적으로 추가해 그룹 생성
- 무작위 8자리 초대 코드로 그룹 참여
- 참여 중인 그룹을 카드형 또는 목록형으로 전환하고 선택 상태를 브라우저에 저장
- 그룹 정보 수정과 그룹 이름 확인을 거친 그룹 삭제
- 관리자 지정·해제와 구성원 내보내기
- 그룹 나가기 시 해당 그룹의 개인 진행 상태 삭제
- 그룹에는 항상 최소 한 명의 관리자가 남도록 제한
- 그룹 생성·수정 시 `구성원 진행 상태 공개` 선택 가능

### 과제와 진행 상태

- 그룹 구성원의 공동 과제 등록
- 과제 제목·설명·마감 시간 저장
- 과제 등록자는 자신이 등록한 과제를 수정·삭제 가능
- 그룹 관리자는 등록자와 관계없이 모든 과제를 수정·삭제 가능
- 사용자별 `시작 전`·`진행 중`·`완료` 상태 저장
- 같은 과제를 보더라도 각 사용자의 진행 상태는 서로 독립적으로 유지
- 대시보드에서 위험도와 마감 시간 순으로 자동 정렬
- 완료한 과제는 대시보드 우선순위 목록에서 제외
- 과목 상세 화면에서 과제와 그룹 구성원 확인
- 공개 옵션이 켜진 그룹에서는 과제별 구성원 진행 상태 확인
- `내 그룹`에서 그룹을 연 뒤 `미완료 구성원 보기`를 펼쳐 사람별 미완료 과제와 현재 상태 확인

### 브라우저 푸시 알림

- 서비스 워커 등록
- 브라우저 푸시 구독 등록·해제
- 마이페이지와 대시보드에서 알림 켜기
- 등록된 브라우저로 테스트 알림 발송
- 사용자별 진행 상태와 마감 시각을 기준으로 자동 알림 발송
- 사용자·과제·알림 시각별 발송 기록으로 중복 알림 방지
- 만료된 푸시 구독이 404 또는 410을 반환하면 자동 삭제
- VAPID 공개키·개인키가 설정되지 않은 환경에서는 알림 버튼 또는 발송을 안전하게 제한
- 공개 옵션이 켜진 그룹에서 미완료 구성원에게 `누군가가 당신에게 ‘과제명’을 하라고 찔렀습니다.` 푸시 발송
- 같은 과제에서 같은 구성원을 찌르는 알림은 보낸 사람별로 30분에 한 번으로 제한

수동 테스트 알림과 자동 마감 알림을 모두 지원합니다. 자동 발송 명령은 한 번 실행한 뒤 종료되므로 운영 환경의 Cron에서 10분마다 호출합니다.

### 자동 알림 방식

| 과제 상태 | 남은 시간 | 알림 시점 |
| --- | --- | --- |
| 안전 | 72시간 초과 | 알림 없음 |
| 주의 진입 | 72시간 전 | 즉시 1회 발송 |
| 위험 진입 | 24시간 전 | 즉시 1회 발송 |
| 위험 반복 | 12시간·6시간·3시간·2시간·1시간·30분 전 | 마감이 가까워질수록 간격을 줄여 발송 |
| 마감 초과 진입 | 제출 기한 경과 시점 | 즉시 1회 발송 |
| 마감 초과 반복 | 제출 기한 경과 후 | 미완료 상태이면 6시간마다 발송 |
| 완료 | 완료 처리 | 이후 알림 즉시 중단 |

핵심 원칙은 **주의와 위험 단계에 들어갈 때 반드시 알리고, 이후 12시간·6시간·3시간·2시간·1시간·30분 전에 반복하며, 마감 초과 시 한 번 더 알린 뒤 미완료 과제는 6시간마다 알리는 것**입니다. 과제를 완료하면 알림을 즉시 중단합니다. Cron 실행이 늦어져도 지나간 알림을 몰아서 보내지 않고 현재 구간의 알림만 발송합니다.

### 보안과 안정성

- Django CSRF 보호와 로그인 필요 페이지 제한
- 그룹 참여 여부와 관리자 역할에 따른 객체 접근 권한 검사
- 일반 조회 요청이 10초 동안 20회를 초과하면 30초 동안 제한
- 로그인·회원가입·비밀번호 재설정·그룹 참여 요청이 60초 동안 10회를 초과하면 제한
- 운영 환경에서 HTTPS 리다이렉트, 보안 쿠키, HSTS, 프록시 HTTPS 헤더 적용
- 실제 비밀값은 `.env` 또는 Render 환경변수에서만 관리

## 위험도 기준

| 조건 | 표시 | 정렬 순서 |
| --- | --- | --- |
| 완료 | 대시보드에서 제외 | - |
| 마감 시간이 지남 | 마감 초과 | 1 |
| 마감까지 24시간 이내 | 위험 | 2 |
| 마감까지 24시간 초과, 72시간 이내 | 주의 | 3 |
| 마감까지 72시간 초과 | 안전 | 4 |

같은 위험도에서는 마감 시간이 빠른 과제가 먼저 표시됩니다.

## 주요 데이터 구조

| 모델 | 역할 |
| --- | --- |
| `User` | Django 기본 사용자 계정 |
| `ClassGroup` | 그룹 이름·설명·초대 코드·진행 상태 공개 옵션 |
| `GroupMembership` | 사용자와 그룹 연결 및 관리자/구성원 역할 |
| `Assignment` | 그룹에 공유되는 과제와 마감 시간 |
| `AssignmentProgress` | 사용자별 과제 진행 상태 |
| `PushSubscription` | 사용자별 브라우저 푸시 구독 |
| `AssignmentNotification` | 사용자·과제·알림 시각별 자동 푸시 발송 기록 |
| `PeerReminder` | 과제·보낸 사람·받는 사람별 찌르기 알림 발송 기록 |
| `EmailVerification` | 회원가입 이메일 인증 토큰 |
| `LoginAttempt` | 로그인 실패 횟수와 잠금 시간 |

## 기술 구성

| 구분 | 기술 |
| --- | --- |
| Backend | Python 3.10+, Django 5.2 LTS, Gunicorn |
| Database | PostgreSQL, Neon, psycopg2 |
| Frontend | Django Template, HTML, CSS, JavaScript |
| Push | Service Worker, Web Push API, pywebpush, VAPID |
| Static files | WhiteNoise, Brotli |
| Deployment | Render Web Service |
| Test | Django TestCase, 테스트용 SQLite 메모리 DB |

## 프로젝트 구조

```text
assignment_signal/
├── assignment_signal/       # Django 설정, URL, WSGI/ASGI
├── tracker/                 # 모델, 폼, 뷰, 권한, 위험도 로직, 테스트
├── tracker/migrations/      # PostgreSQL 스키마 변경 기록
├── templates/               # 서비스 및 계정 화면
├── static/tracker/          # CSS, 과목 보기 JS, 푸시 JS, 서비스 워커
├── .env.example             # 비밀값이 없는 환경변수 예시
├── build.sh                 # Render 빌드와 마이그레이션
├── manage.py
├── render.yaml              # Render Blueprint
└── requirements.txt
```

## 로컬 실행

Python 3.10 이상과 PostgreSQL이 필요합니다.

### 1. PostgreSQL 준비

```sql
CREATE USER assignment_user WITH PASSWORD 'replace_with_local_password';
CREATE DATABASE assignment_signal OWNER assignment_user;
```

### 2. 환경변수 파일 준비

Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

`.env`에서 `POSTGRES_PASSWORD`를 실제 로컬 DB 비밀번호로 변경합니다. `.env`는 Git에서 제외됩니다.

### 3. 설치와 실행

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

## 테스트

PostgreSQL이 실행 중이면 실제 설정으로 테스트합니다.

```bash
python manage.py test
```

PostgreSQL 없이 애플리케이션 로직을 검사하려면 테스트 전용 SQLite 메모리 DB를 사용합니다.

```bash
python manage.py test --settings=assignment_signal.test_settings
```

현재 테스트는 위험도, 인증, 로그인 잠금, 요청 제한, 그룹 권한, 과제 권한, 개인 진행 상태, 회원 탈퇴, 푸시 구독, 자동 알림 시각과 중복 방지, 구성원 현황 공개와 찌르기 알림의 30분 제한을 검사합니다.

자동 알림 명령을 직접 한 번 실행하려면 다음 명령을 사용합니다.

```bash
python manage.py send_assignment_notifications
```

## Render + Neon 배포 준비

이 폴더의 내용을 `assignment_signal` GitHub 저장소 루트에 올리는 구성을 기준으로 합니다. 따라서 `render.yaml`에는 `rootDir`이 없습니다.

### Neon

1. Neon에서 PostgreSQL 프로젝트를 생성합니다.
2. **Pooled connection** 문자열을 복사합니다.
3. 연결 문자열에 `sslmode=require&channel_binding=require`가 포함됐는지 확인합니다.
4. 문자열을 Render의 `DATABASE_URL`에만 저장합니다.

### Render

GitHub 저장소를 연결하고 **New > Blueprint**에서 `render.yaml`을 적용합니다.

| 환경변수 | 설명 |
| --- | --- |
| `DJANGO_PRODUCTION=true` | 운영 보안 설정 활성화 |
| `DJANGO_DEBUG=false` | 디버그 화면 비활성화 |
| `DJANGO_SECRET_KEY` | Render가 생성하는 무작위 비밀값 |
| `DATABASE_URL` | Neon pooled connection string |
| `EMAIL_HOST_USER` | SMTP 계정 |
| `EMAIL_HOST_PASSWORD` | SMTP 앱 비밀번호 |
| `DEFAULT_FROM_EMAIL` | SMTP에서 허용된 발신자 주소 |
| `WEBPUSH_VAPID_PUBLIC_KEY` | 브라우저 구독에 사용하는 공개키 |
| `WEBPUSH_VAPID_PRIVATE_KEY` | VAPID 개인키 또는 Render Secret File 경로 |
| `WEBPUSH_VAPID_SUBJECT` | `mailto:` 형식의 발신자 연락처 |

푸시 알림을 사용하려면 VAPID 키 쌍을 저장소 밖에서 생성합니다. 개인키 파일을 사용할 경우 Render Secret Files에 등록하고 `WEBPUSH_VAPID_PRIVATE_KEY=/etc/secrets/private_key.pem`처럼 경로만 환경변수에 입력합니다.

`build.sh`는 패키지 설치, 정적 파일 수집, Neon DB 마이그레이션을 실행합니다. Render 호스트명은 허용 호스트, 사이트 URL, CSRF 신뢰 출처에 자동 반영됩니다.

Blueprint에는 웹 서비스와 별도로 `assignment-signal-notifications` Cron Job이 포함됩니다. Cron에도 웹 서비스와 같은 `DATABASE_URL` 및 VAPID 키를 입력해야 하며, 10분마다 자동 알림 명령을 실행합니다. Render Cron Job은 무료 플랜이 없으므로 실제 Blueprint 적용 시 별도 비용이 발생합니다. 배포하지 않는 경우에는 로컬 또는 Linux 서버의 cron에서 위 관리 명령을 호출할 수 있습니다.

## GitHub 보안 주의사항

- `.env`, 실제 DB URL, SMTP 비밀번호, Django 비밀키, VAPID 개인키를 커밋하지 않습니다.
- `.env.example`과 `render.yaml`에는 변수 이름과 안전한 예시만 둡니다.
- VAPID 공개키는 공개 가능한 값이지만 현재 구성은 환경변수로 통일했습니다.
- 배포 전 `python manage.py check --deploy`와 전체 테스트를 다시 실행합니다.
