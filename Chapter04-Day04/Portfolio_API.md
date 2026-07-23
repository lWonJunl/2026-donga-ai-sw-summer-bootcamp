# 🔐 Django Portfolio Text API

> 기존 개인 포트폴리오에 텍스트 파일 기반 JSON API와 이메일 인증을 포함한 Django 계정 시스템을 연결한 프로젝트입니다.

본 프로젝트는 **2026 DongA AI·SW Summer Bootcamp**의 Django API 실습으로 제작했습니다.

포트폴리오 화면은 기존 구조를 유지하면서 `data/projects.txt`를 API 데이터 원본으로 사용합니다. 회원가입 또는 로그인한 사용자만 프로젝트 및 포트폴리오 API를 조회할 수 있으며, API 페이지에서 검색·분류·언어 필터와 JSON 응답을 직접 확인할 수 있습니다.

<br>

## 📂 Overview

| Item | Description |
| :-- | :-- |
| **Project** | Authenticated Portfolio Text API |
| **Program** | 2026 DongA AI·SW Summer Bootcamp |
| **Framework** | Django 4.2 |
| **Data Source** | UTF-8 tab-separated text file |
| **API Format** | JSON |
| **Authentication** | Django Session Authentication, django-allauth |
| **Database** | SQLite for user accounts and sessions |
| **Frontend** | HTML, CSS, Vanilla JavaScript Fetch API |
| **Environment** | Rocky Linux |

<br>

## 📂 Project Structure

```text
Chapter04-Day04
├── manage.py
├── Portfolio_API.md
├── db.sqlite3                  # local user/session database
├── data
│   └── projects.txt            # API source data
├── portfolio
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── forms.py                # secure signup and profile forms
│   ├── security.py             # browser security headers
│   ├── tests.py                # authentication and security tests
│   ├── asgi.py
│   └── wsgi.py
├── templates
│   ├── home.html
│   ├── api.html
│   ├── auth
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   └── account                 # django-allauth account pages
└── static
    ├── css
    │   ├── style.css
    │   ├── api.css
    │   └── auth.css
    └── js
        ├── main.js
        └── api.js
```

백업파일과 Python 캐시는 위 구조에서 생략했습니다.

<br>

## ✨ Core Features

### Text File Data

* `projects.txt`는 탭으로 열을 구분한 UTF-8 텍스트 파일입니다.
* Django의 `csv.DictReader`가 각 행을 읽어 Python 딕셔너리로 변환합니다.
* 별도 프로젝트 테이블 없이 텍스트 파일을 읽어 JSON 응답을 생성합니다.

### JSON API

* 프로젝트 전체 목록과 ID 기반 상세 조회를 제공합니다.
* `category`, `q`, `lang` 쿼리 매개변수로 분류·검색·언어 필터를 적용합니다.
* 한국어와 영어 제목·설명을 하나의 데이터 원본에서 선택해 반환합니다.
* 기존 포트폴리오의 프로필, 기술, Journey와 프로젝트 데이터도 JSON으로 제공합니다.

### Authentication

* Django 기본 사용자 모델, 세션 인증과 `django-allauth`를 사용합니다.
* 회원가입 후 확인 메일을 발송하며 이메일 인증을 마쳐야 로그인을 완료할 수 있습니다.
* 사용자명은 유니코드 정규화와 대소문자 중복 검사를 거치며 시스템 예약어 사용을 차단합니다.
* 인증되지 않은 JSON 요청에는 HTTP `401`과 로그인·회원가입 URL을 반환합니다.
* 인증되지 않은 브라우저의 HTML 요청은 로그인 필요 안내가 있는 로그인 페이지로 이동합니다.
* 사용자가 회원가입을 명시적으로 선택한 경우에만 가입 화면을 열어 기존 사용자와 신규 사용자의 흐름을 구분합니다.
* 마이페이지에서 사용자 정보를 수정하고 이메일 관리와 비밀번호 변경 화면으로 이동할 수 있습니다.
* 비밀번호 재설정과 Google·GitHub·Kakao·Naver 소셜 로그인 설정을 지원합니다.
* 반복된 로그인 실패는 캐시 기반 요청 제한으로 차단합니다.
* 로그아웃은 POST 요청으로 처리합니다.

### Security

* 운영 모드에서는 비밀키, 호스트와 이메일 서버 설정을 환경변수로 읽습니다.
* HTTPS 리다이렉트, HSTS, 보안 쿠키와 프록시 HTTPS 전달 설정을 운영 환경에서 활성화할 수 있습니다.
* CSP, Permissions Policy, 클릭재킹 방지와 MIME 스니핑 방지 헤더를 적용합니다.
* 인증된 API 응답에는 `private, no-store` 캐시 정책과 `Vary: Cookie`를 설정합니다.
* 민감한 비밀번호 필드는 오류 보고에서 숨기고 `next` 주소는 같은 호스트인지 검증합니다.

### Interactive API Page

* API 페이지가 JavaScript `fetch()`로 JSON 엔드포인트를 호출합니다.
* 카테고리, 언어와 검색어를 선택해 요청 URL과 응답 본문을 확인할 수 있습니다.
* 원본 JSON과 프로젝트 카드 결과를 함께 표시합니다.
* 미인증 상태의 최초 요청은 `401` 응답을 표시하고, 사용자가 요청 버튼을 누르면 안내 후 로그인 화면으로 이동합니다.

<br>

## 🔄 Request Flow

```text
Browser
   │
   ├─ login warning / explicit register
   │              │
   │              ▼
   │      django-allauth ──→ email verification
   │              │
   │              ▼
   │       Django Auth ──→ SQLite
   │
   └─ API request
          │
          ▼
   Session authentication
          │
          ▼
   data/projects.txt
          │ csv.DictReader
          ▼
   filter & localization
          │
          ▼
      JsonResponse
```

<br>

## 🔗 Endpoints

| Method | URL | Authentication | Description |
| :--: | :-- | :--: | :-- |
| `GET` | `/` | No | 기존 개인 포트폴리오 |
| `GET` | `/api/` | No | API 요청 및 응답 확인 페이지 |
| `GET` | `/api/health/` | No | 텍스트 데이터 파일 상태와 레코드 수 |
| `GET` | `/api/projects/` | Required | 전체 프로젝트 목록 |
| `GET` | `/api/projects/1/` | Required | ID가 1인 프로젝트 |
| `GET` | `/api/portfolio/` | Required | 포트폴리오 전체 데이터 |
| `GET/POST` | `/accounts/register/` | No | 회원가입 |
| `GET/POST` | `/accounts/login/` | No | 로그인 |
| `POST` | `/accounts/logout/` | Required | 로그아웃 |
| `GET/POST` | `/accounts/profile/` | Required | 사용자명·이름 수정 및 계정 관리 |
| `GET/POST` | `/accounts/password/reset/` | No | 비밀번호 재설정 메일 요청 |
| `GET/POST` | `/accounts/password/change/` | Required | 비밀번호 변경 |
| `GET/POST` | `/accounts/email/` | Required | 이메일 변경 및 인증 관리 |

### Query Parameters

```text
/api/projects/?lang=ko
/api/projects/?lang=en
/api/projects/?category=Web
/api/projects/?q=Python
/api/portfolio/?lang=en
```

<br>

## ✅ Authentication Tests

`portfolio/tests.py`에는 다음 인증·보안 동작을 검사하는 16개의 테스트가 있습니다.

* 회원가입 후 이메일 인증 요구 및 확인 처리
* 미인증 사용자의 로그인 차단
* 예약 사용자명 차단
* 익명 JSON 요청의 HTTP `401` 응답
* 익명 HTML 요청의 로그인 안내 페이지 이동
* API 페이지의 공개 접근
* 보호 URL에서 기존 회원가입 경로를 호출했을 때 로그인 안내로 전환
* 사용자가 명시적으로 선택한 회원가입 화면 접근
* CSP·프레임·권한 정책 보안 헤더 적용
* 인증 API 응답의 브라우저 캐시 방지
* 반복된 로그인 실패 요청 제한
* 로그아웃 이후 API 재잠금
* GET 로그아웃 차단 및 POST 전용 처리
* 마이페이지 사용자 정보 수정
* 계정 노출 없이 비밀번호 재설정 메일 발송

실행 명령:

```bash
python manage.py test portfolio
```

<br>

## 🛠️ Tech Stack

| Category | Stack |
| :-- | :-- |
| **Language** | Python |
| **Web Framework** | Django 4.2 |
| **API Response** | Django `JsonResponse` |
| **Text Parser** | Python `csv.DictReader` |
| **Authentication** | Django Auth, django-allauth, Session, CSRF |
| **Database** | SQLite |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Client Request** | Fetch API |
| **Server Environment** | Rocky Linux |

<br>

## ▶️ Run on Rocky Linux

```bash
cd /path/to/Chapter04-Day04
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "Django==4.2.30" django-allauth

python manage.py migrate
python manage.py check
python manage.py test portfolio
python manage.py runserver 0.0.0.0:8000
```

개발 환경에서는 콘솔에 출력되는 이메일 인증 링크를 열어 계정을 인증한 뒤 `http://서버주소:8000/api/`에서 API를 호출합니다.

> `runserver`는 개발 실습용입니다. 실제 공개 배포 전에는 운영 환경변수, Gunicorn, Nginx, HTTPS와 SMTP 설정이 필요합니다.

### Production Environment Variables

```bash
export DJANGO_PRODUCTION=true
export DJANGO_SECRET_KEY='충분히 길고 무작위인 운영용 키'
export DJANGO_ALLOWED_HOSTS='portfolio.example.com'
export DJANGO_CSRF_TRUSTED_ORIGINS='https://portfolio.example.com'
export DJANGO_BEHIND_HTTPS_PROXY=true
export DJANGO_EMAIL_HOST='smtp.example.com'
export DJANGO_EMAIL_PORT=587
export DJANGO_EMAIL_HOST_USER='smtp-user'
export DJANGO_EMAIL_HOST_PASSWORD='smtp-password'
export DJANGO_DEFAULT_FROM_EMAIL='no-reply@example.com'
```

소셜 로그인을 사용할 때는 각 서비스의 OAuth Client ID와 Secret도 환경변수로 설정합니다. 실제 비밀값은 문서나 저장소에 기록하지 않습니다.

<br>

## 🔒 Security & Publication

* `db.sqlite3`에는 가입한 사용자 정보가 저장되므로 GitHub에 올리지 않습니다.
* Django 코드, 텍스트 데이터, HTML/CSS/JavaScript와 백업파일도 공개 저장소에서 제외합니다.
* GitHub에는 구현 설명 문서인 `Portfolio_API.md`만 공개합니다.
* 운영용 `SECRET_KEY`는 환경변수로 분리하고 공개된 키는 사용하지 않습니다.
* 운영 환경에서는 `DEBUG=False`와 제한된 `ALLOWED_HOSTS`를 사용합니다.
* SMTP 비밀번호와 OAuth Client Secret도 환경변수로 관리합니다.

<br>

## 🤖 AI-Assisted Development

개발 과정에서 **OpenAI Codex**를 활용해 API 구조 설계, 텍스트 파싱, 인증 흐름, UI 구성, 디버깅과 문서화를 진행했으며 결과를 직접 검토하고 수정했습니다.

<br>

## 💡 What I Learned

* 텍스트 데이터를 Python 자료구조로 변환하고 JSON API로 제공하는 흐름을 이해했습니다.
* HTTP 상태 코드와 목록·상세 API, 쿼리 필터를 구현했습니다.
* Django 세션 인증, CSRF 보호와 이메일 인증이 API 및 폼 요청에 적용되는 방식을 학습했습니다.
* 안전한 `next` URL 검증, 요청 제한과 로그인·회원가입·계정 관리 흐름을 테스트로 확인했습니다.
* 환경변수 기반 운영 설정과 브라우저 보안 헤더를 구성했습니다.
* JavaScript Fetch API로 서버 응답을 호출하고 화면에 렌더링했습니다.
* 공개 저장소에서 소스 코드, 사용자 DB와 비밀 설정을 분리하는 과정을 경험했습니다.
