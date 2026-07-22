# Django 개인 포트폴리오

컴퓨터공학 학습 과정, 연구와 프로젝트를 한곳에 정리하고 Rocky Linux 환경에서 실행하도록 만든 반응형 포트폴리오 웹사이트입니다.

## 주요 기능

- Django view의 구조화된 데이터를 템플릿에 전달합니다.
- 대표 프로젝트, Journey, 학습 영역과 연락 채널을 한 페이지에 구성했습니다.
- 프로젝트 분류 필터, 다크 모드와 맨 위로 이동 기능을 JavaScript로 구현했습니다.
- `?lang=ko`, `?lang=en` 요청에 따라 한국어와 영어 콘텐츠를 렌더링합니다.
- 모바일 화면의 글자 크기와 줄바꿈을 별도로 조정했습니다.

## 기술

`Python` · `Django` · `HTML` · `CSS` · `JavaScript` · `Rocky Linux`

## 관련 파일

- [Django view와 콘텐츠](../../Chapter04-Day03/portfolio/views.py)
- [메인 템플릿](../../Chapter04-Day03/templates/home.html)
- [스타일시트](../../Chapter04-Day03/static/css/style.css)
- [인터랙션 스크립트](../../Chapter04-Day03/static/js/main.js)

## 배운 점

HTML·CSS·JavaScript가 담당하는 화면 역할과 Django가 데이터를 준비해 템플릿을 렌더링하는 흐름을 연결해 이해했습니다. 개발 과정에는 OpenAI Codex를 보조 도구로 활용하고 결과를 직접 검토했습니다.
