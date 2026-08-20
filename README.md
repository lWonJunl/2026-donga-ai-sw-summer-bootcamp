# 📚 2026 Dong-A AI·SW Summer Bootcamp

> 2026 동아대학교 AI·SW Summer Bootcamp에서 학습한 내용을 정리한 저장소입니다.

본 저장소는 **2026 Dong-A AI·SW Summer Bootcamp**의 학습 과정과 실습 결과를 기록하기 위해 제작되었습니다.

8주 동안 Python을 중심으로 프로그래밍, 데이터 처리, 생성형 AI 활용 및 프로젝트 개발을 학습했으며, 주차별 실습 코드와 프로젝트 결과물을 체계적으로 기록했습니다.

<br>

## 📂 Overview

| Item             | Description                                                   |
| :--------------- | :------------------------------------------------------------ |
| **Organization** | Dong-A University National Center of Excellence in Software   |
| **Program**      | 2026 DongA AI·SW Summer Bootcamp                              |
| **Period**       | 2026.06.29 ~ 2026.08.21 (8 Weeks)                             |
| **Status**       | ✅ Completed                                                 |
<br>

## 📂 Repository Structure

```text
2026-donga-ai-sw-summer-bootcamp
├── Chapter01-Day01
├── Chapter01-Day02
├── Chapter01-Day03
├── Chapter01-Day04
├── Chapter01-Day05
├── Chapter02-Day01
├── Chapter02-Day02
├── Chapter02-Day03
├── Chapter02-Day04
├── Chapter03-Day03
├── Chapter03-Day04
├── Chapter04-Day02
├── Chapter04-Day03
├── Chapter04-Day04
├── Chapter06-Day02
├── Chapter06-Day03
├── Chapter07-Day03
├── Chapter07-Day04
├── Chapter08-Day02
├── Chapter08-Day03
└── Report
```

<br>

## 📖 Contents

| Chapter | Day | Topic | Note |
| :-----: | :--: | ----- | ---- |
| 01 | 01 | Dynamic Programming |  |
| 01 | 02 | Greedy Algorithm | |
| 01 | 03 | Graph Algorithm | |
| 01 | 04 | Dijkstra Algorithm |  |
| 01 | 05 | July Project(4 Weeks) Planning | 📚 Dong-A Univ. Campus Navigation |
| 02 | 01 | Database Fundamentals |  |
| 02 | 02 | SQL Join & Union |  |
| 02 | 03 | DBMS in Modern Services | |
| 02 | 04 | 📚  Dong-A Univ. Campus Navigation Project |  |
| 03 | 02 | Frontend & Backend Fundamentals | ❌ No hands-on coding |
| 03 | 03 | 📚  Dong-A Univ. Campus Navigation Project | |
| 03 | 04 | Web Service | |
| 04 | 02 | Django Fundamentals & Server Setup |  |
| 04 | 03 | 📚 Portfolio project | 💻 Online |
| 04 | 04 | Django Portfolio API & Authentication | 🍽️ Networking |
| 06 | 02 | Cloud Computing, Deployment & Docker Basics | 📚 Assignment Signal Project |
| 06 | 03 | Priority Poke Project Enhancement | 📚 Assignment Signal → Priority Poke |
| 07 | 02 | Generative AI & LLM Fundamentals | ❌ No hands-on coding |
| 07 | 03 | Local AI Infrastructure & EXAONE Django Chatbot | |
| 07 | 04 | Personalized RAG Web Chatbot | |
| 08 | 02 | RAG Preprocessing Enhancement with LangGraph | |
| 08 | 03 | CPU Fine-Tuning of Qwen2.5-0.5B | |
| 08 | 04 | Bootcamp Wrap-up | 🏁 Bootcamp Completed |
<br>

## 🛠️ Tech Stack

| Category | Stack |
| :-- | :-- |
| **Languages & Markup** | Python, SQL, HTML, CSS, JavaScript |
| **Algorithms & Visualization** | Dynamic Programming, Greedy, BFS, DFS, Dijkstra, OpenCV, NumPy, NetworkX, Matplotlib |
| **Web Application** | Django 5.2 LTS, django-allauth, Django `JsonResponse`, Fetch API |
| **Database & Cache** | MySQL, SQLite, PostgreSQL, Redis |
| **Push & Browser** | Web Push API, Service Worker, pywebpush, VAPID |
| **External Integration** | Feedparser, Google News RSS, Kakao Maps JavaScript API |
| **Web Server & Deployment** | Python `http.server`, Gunicorn, WhiteNoise, Docker, Vercel, Render, Neon |
| **Linux & Virtualization** | Rocky Linux 9.8 Minimal, VMware |
| **Remote Access & File Transfer** | PuTTY, WinSCP |
| **Testing & Security** | Django TestCase, CSRF, CSP, HSTS, Rate Limiting |
| **Local LLM** | Ollama, EXAONE 3.5 7.8B, Qwen2.5-0.5B-Instruct |
| **RAG & Document Processing** | LangChain, LangGraph, Sentence Transformers, Milvus, Beautiful Soup, python-docx, python-pptx, pypdf, PyMuPDF, pytesseract |
| **Fine-Tuning** | PyTorch 2.7 (CPU), Transformers, PEFT (LoRA), Safetensors, SentencePiece |
| **AI-assisted Development** | Codex, Gemini |
| **Development Tools** | Visual Studio Code, Git, GitHub, Docker Desktop |

<br>

## 💡 Learning & Project Highlights

### Algorithms & Data Foundations

* 동적 계획법, 그리디, BFS, DFS, 다익스트라를 Python으로 구현하고, IDA* 탐색을 이용한 3×3 루빅스 큐브 풀이를 실습했습니다.
* OpenCV·NumPy로 미로 이미지를 처리하고, NetworkX·Matplotlib으로 그래프를 시각화했으며, Feedparser로 Google News RSS 추천기를 만들었습니다.
* MySQL의 조회·집계·조인·합집합을 실습하고, 캠퍼스 길찾기에 필요한 장소·도로·경유지 데이터를 관계형 테이블과 SQL 시드 데이터로 모델링했습니다.
* 자세한 결과는 [Google News RSS 추천기](Chapter01-Day02/README_Google_News_RSS.md), [IDA* 루빅스 큐브 풀이](Chapter01-Day03/README_IDA_Star_Rubiks_Cube.md), [이미지 기반 미로 탐색](Chapter01-Day04/README_Image_Maze_Solver.md)에서 확인할 수 있습니다.

### Web Applications, Authentication & Deployment

* VMware의 Rocky Linux 9.8 Minimal 환경에서 Django 서버를 구성하고, `ALLOWED_HOSTS`와 방화벽 설정을 통해 외부 접속을 실습했습니다.
* Django 템플릿·정적 파일로 반응형 포트폴리오를 만들고, JSON API의 목록·상세·검색·분류·언어 필터를 구현했습니다.
* 세션 인증과 `django-allauth`를 연결해 회원가입, 이메일 인증, 비밀번호 재설정, 계정 관리와 소셜 로그인을 구성했습니다.
* Vercel, Render, Gunicorn·WhiteNoise 배포 흐름을 학습하고, 인증·API 접근·보안 헤더·요청 제한·캐시 정책을 Django 테스트로 검증했습니다.
* 구현·보안·배포 방법은 [`Portfolio.md`](Chapter04-Day03/Portfolio.md), [`Portfolio_API.md`](Chapter04-Day04/Portfolio_API.md), [`SECURITY.md`](Chapter04-Day04/SECURITY.md), [`SOCIAL_LOGIN_SETUP.md`](Chapter04-Day04/SOCIAL_LOGIN_SETUP.md)에 정리했습니다.

### Priority Poke Mini Project

* Day 2에서 과제와 마감 시간을 공유하는 Django 웹 서비스 '과제신호등'을 구현하고, Day 3에서 '우선콕'으로 확장했습니다.
* 초대 코드 기반 공유 그룹, 관리자 권한, 공동 과제 등록과 사용자별 독립적인 진행 상태를 구성했습니다.
* 마감까지 남은 시간으로 위험도를 계산하고, Service Worker와 Web Push API로 자동 마감 알림과 구성원 '찌르기' 알림을 발송하도록 구현했습니다.
* 로컬에서는 SQLite를 사용하고, 운영 환경에서는 PostgreSQL·Neon과 Render Web Service를 사용하도록 배포 구성을 분리했습니다.
* 인증, 요청 제한, 그룹·과제 권한, 개인 진행 상태, 자동 알림과 찌르기 중복 방지를 Django 테스트로 검증했습니다.
* 개발 과정은 [Day 2 · 과제신호등](Chapter06-Day02/README.md), 최신 구현과 배포 방법은 [Day 3 · 우선콕](Chapter06-Day03/README.md)에서 확인할 수 있습니다.

### Local AI, RAG & Fine-Tuning Projects

* Ollama의 EXAONE 3.5 7.8B를 Django와 연결해 회원별 대화, 실시간 스트리밍 응답, 대화 제목·개인 설정 관리 기능을 갖춘 로컬 AI 채팅 서비스를 구현했습니다.
* SQLite에 대화와 설정을 저장하고 Redis에 최근 문맥을 캐시했으며, Redis를 사용할 수 없을 때 SQLite 기반 문맥으로 동작하도록 구성했습니다.
* URL·PPTX·DOCX 자료를 사용자별로 수집해 Milvus 벡터 검색과 연결하고, 검색 근거 표시·문서 격리·URL 자동 수집·Redis·JSONL 대화 메모리를 적용했습니다.
* LangGraph 기반 전처리로 문서를 분할·요약·키워드 추출·태깅하고, PDF/OCR 구조화와 키워드 가중 재정렬로 개인화 RAG 검색 품질을 개선했습니다.
* Qwen2.5-0.5B-Instruct를 CPU에서 파이썬 기초 문법 자료로 전체 파인튜닝하고, 비교용 LoRA 학습과 검증된 CSV 답변 기반 콘솔 챗봇을 구현했습니다.
* 상세 내용은 [Django EXAONE Chat](Chapter07-Day03/02_Django_EXAONE_Chat/README.md), [Personalized RAG Chatbot](Chapter07-Day04/02_Django_Personalized_RAG_Web_Chatbot/README.md), [RAG 전처리 고도화](Chapter08-Day02/README.md), [Qwen CPU 파인튜닝](Chapter08-Day03/Chapter08-Day03_Qwen2.5-0.5B_Fine-Tuning.md)에서 확인할 수 있습니다.

### Campus Navigation Mini Project

* 동아대학교 승학캠퍼스의 장소와 도로 데이터를 바탕으로 다익스트라 기반 경로 탐색 기능을 개발했습니다.
* 도보·차량 모드, 경유지, 계단 회피, 엘리베이터 우선 등의 경로 옵션을 구현했습니다.
* Python 표준 라이브러리 기반 HTTP 서버와 HTML/CSS/JavaScript UI를 연결했습니다.
* Kakao Maps JavaScript API를 활용해 장소, 현재 위치 및 탐색 경로를 지도에 표시했습니다.
* 거리·시간 우선 탐색, 실내 경로 우선, 차량 이동 후 주차장에서 도보로 전환하는 복합 경로를 지원합니다.
* 프로젝트의 진행 과정은 [Day 1](Chapter01-Day05/navDay01.md), [Day 2](Chapter02-Day04/navDay02.md), [Day 3](Chapter03-Day03/navDay03.md), [Day 4](Chapter03-Day04/navDay04.md) 문서에서 확인할 수 있습니다.

<br>

## 🤖 AI-Assisted Development

본 부트캠프는 **AI 기반 개발(Vibe Coding)** 방식을 바탕으로 진행되었습니다.

학습 과정에서는 주로 **ChatGPT(5.5 및 5.6) 기반 Codex**를 활용하여 문제 해결, 코드 작성, 디버깅 및 문서화를 수행하였으며, 결과물은 직접 검토하고 개선하는 과정을 거쳐 완성하였습니다.

AI가 생성한 결과는 실행, 테스트, 코드 검토를 통해 요구사항과 실제 동작이 일치하는지 확인하고, 비밀값과 개인정보가 저장소에 포함되지 않도록 점검했습니다.

<br>

## 🎯 Goal

* Python 기반 문제 해결 능력과 알고리즘 구현 역량 향상
* SQL과 관계형 데이터베이스의 핵심 개념 학습
* 데이터, 서버, Web UI가 연결된 프로젝트 개발 경험 축적
* AI 도구를 활용한 개발과 결과물 검증 과정 체득
* Git과 GitHub를 활용한 학습 기록 및 포트폴리오 관리

<br>

## 📌 Notes

* 학습 내용은 `ChapterXX-DayXX` 형식으로 체계적으로 관리합니다.
* 각 폴더에는 해당 일자의 실습 코드, SQL, 문서 및 프로젝트 결과물을 저장합니다.
* 캠퍼스 길찾기 실행 시 카카오 JavaScript 키는 공개된 소스 코드가 아닌 `.env` 파일에 설정합니다.
* Django 프로젝트의 비밀키, 이메일 및 OAuth 설정은 `.env.example`을 참고해 환경변수로 관리합니다.
* SQLite 사용자 데이터베이스, `.env`, 로그, 캐시 및 백업 파일은 Git에 포함하지 않습니다.
* 수료 후에도 학습 결과물을 포트폴리오용으로 보완할 수 있습니다.