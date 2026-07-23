# 💻 Django Personal Portfolio

> 컴퓨터공학 학습 과정과 프로젝트, 연구 경험을 한 페이지에 정리한 개인 포트폴리오입니다.

본 프로젝트는 **2026 DongA AI·SW Summer Bootcamp**의 포트폴리오 미니 프로젝트로 제작했습니다.

Python과 Django로 콘텐츠를 구성하고 HTML, CSS, JavaScript를 연결해 반응형 웹사이트로 구현했습니다. 한국어·영어 전환, 프로젝트 분류 필터, 다크 모드 등의 기능을 제공하며 Rocky Linux의 Django 환경에서 실행할 수 있습니다.

<br>

## 📂 Overview

| Item | Description |
| :-- | :-- |
| **Project** | Django Personal Portfolio |
| **Program** | 2026 DongA AI·SW Summer Bootcamp |
| **Type** | Portfolio Mini Project |
| **Framework** | Django |
| **Frontend** | HTML, CSS, Vanilla JavaScript |
| **Environment** | Rocky Linux |
| **Theme Color** | `#aee1ff` |

<br>

## 📂 Project Structure

```text
Chapter04-Day03
├── manage.py
├── Portfolio.md
├── portfolio
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── templates
│   └── home.html
└── static
    ├── css
    │   └── style.css
    └── js
        └── main.js
```

<br>

## ✨ Core Features

### Portfolio Content

* 자기소개, 기술 스택, Journey, 대표 프로젝트, 프로젝트 아카이브, 학습 영역과 연락처를 한 페이지에 구성했습니다.
* 프로필과 프로젝트 데이터를 `views.py`에서 구조화하고 Django 템플릿에 전달합니다.
* 대표 프로젝트와 규모 있는 학습 결과를 분리해 핵심 경험을 빠르게 확인할 수 있도록 구성했습니다.

### Korean & English

* `?lang=ko`와 `?lang=en` 요청값에 따라 한국어 또는 영어 콘텐츠를 렌더링합니다.
* 언어 전환 버튼을 누르면 홈의 맨 위로 이동해 기존 해시나 스크롤 위치가 남지 않도록 처리했습니다.
* 메뉴와 기술명처럼 번역이 불필요한 표현은 영문 표기를 유지합니다.

### Project Archive Filter

* 프로젝트를 연구, AI·데이터, 웹 등의 간단한 분류 버튼으로 탐색할 수 있습니다.
* JavaScript가 선택된 분류에 맞는 항목만 표시하고 현재 결과 수를 함께 갱신합니다.
* 프로젝트 문서가 연결된 항목과 소논문처럼 별도 링크가 없는 항목을 구분합니다.

### Responsive UI

* 데스크톱과 모바일 화면에 맞춰 레이아웃, 글자 크기와 줄바꿈을 조정했습니다.
* 모바일에서는 메뉴 버튼으로 내비게이션을 열고 닫을 수 있습니다.
* `IntersectionObserver`를 사용해 섹션 진입 애니메이션과 기술 수준 표시를 실행합니다.

### Theme & Navigation

* 라이트·다크 테마를 전환하고 선택한 값을 `localStorage`에 저장합니다.
* 상단 고정 메뉴와 섹션 앵커를 이용해 원하는 콘텐츠로 이동합니다.
* 맨 위로 이동 버튼은 사용자의 모션 감소 설정을 고려해 스크롤 방식을 선택합니다.

<br>

## 🔄 Rendering Flow

```text
Browser Request
      │
      ▼
portfolio/urls.py
      │
      ▼
portfolio/views.py
  ├─ language selection
  ├─ portfolio data
  └─ template context
      │
      ▼
templates/home.html
  ├─ static/css/style.css
  └─ static/js/main.js
      │
      ▼
Rendered Portfolio Page
```

<br>

## 🛠️ Tech Stack

| Category | Stack |
| :-- | :-- |
| **Language** | Python |
| **Web Framework** | Django |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Template Engine** | Django Templates |
| **UI Features** | Responsive Design, Dark Mode, Intersection Observer |
| **Server Environment** | Rocky Linux |
| **Version Control** | Git, GitHub |
| **AI-Assisted Development** | OpenAI Codex |

<br>

## ▶️ Run on Rocky Linux

프로젝트 디렉터리에서 가상환경을 만들고 Django를 설치합니다.

```bash
cd /home/portfolio-project/protfolio
python3 -m venv .venv
source .venv/bin/activate
python -m pip install django
python manage.py runserver 0.0.0.0:8000
```

브라우저에서 `http://서버주소:8000`으로 접속합니다.

> `runserver`는 개발과 실습을 위한 서버입니다. 현재의 `DEBUG=True`와 `ALLOWED_HOSTS=['*']` 설정은 공개 운영 환경에 그대로 사용하지 않습니다.

<br>

## 🗂️ Key Files

| File | Role |
| :-- | :-- |
| [`portfolio/views.py`](portfolio/views.py) | 프로필, 프로젝트, Journey, 번역 데이터와 렌더링 로직 |
| [`portfolio/urls.py`](portfolio/urls.py) | 홈 화면과 Django 관리자 URL 연결 |
| [`portfolio/settings.py`](portfolio/settings.py) | 템플릿, 정적 파일, 언어와 시간대 등 프로젝트 설정 |
| [`templates/home.html`](templates/home.html) | 포트폴리오 페이지의 HTML 구조와 Django 템플릿 출력 |
| [`static/css/style.css`](static/css/style.css) | 색상, 타이포그래피, 반응형 레이아웃과 테마 |
| [`static/js/main.js`](static/js/main.js) | 테마, 모바일 메뉴, 필터, 애니메이션과 맨 위 이동 기능 |

<br>

## 🤖 AI-Assisted Development

본 프로젝트는 부트캠프의 **AI 기반 개발(Vibe Coding)** 과제로 시작했습니다.

개발 과정에서 **OpenAI Codex**를 활용해 코드 작성, 디자인 개선, 디버깅과 문서화를 진행했으며, 생성된 결과는 직접 확인하고 요구사항에 맞게 수정했습니다.

<br>

## 💡 What I Learned

* Django view가 준비한 데이터를 템플릿으로 전달하고 HTML로 렌더링하는 흐름을 이해했습니다.
* HTML은 콘텐츠 구조, CSS는 화면 디자인, JavaScript는 사용자 상호작용을 담당한다는 역할을 실제 프로젝트에서 연결했습니다.
* 하나의 콘텐츠를 한국어와 영어로 제공하기 위한 데이터 분리와 번역 처리 방식을 경험했습니다.
* Rocky Linux에서 Django 프로젝트를 구성하고 외부 접속이 가능한 개발 서버로 실행하는 과정을 실습했습니다.
* AI 도구가 생성한 코드를 그대로 사용하는 것이 아니라 직접 검토하고 개선하는 과정의 중요성을 배웠습니다.

<br>

## 📌 Notes

* 포트폴리오 내용은 학습과 프로젝트 진행 상황에 따라 계속 업데이트합니다.
* 개인 정보나 외부 공개가 제한된 활동의 세부 내용은 문서에 포함하지 않습니다.
* 배포 환경을 구성할 때는 비밀 키, 디버그 설정, 허용 호스트와 정적 파일 제공 방식을 별도로 점검해야 합니다.