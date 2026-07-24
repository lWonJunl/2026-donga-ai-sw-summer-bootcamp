# 소셜 로그인 설정

각 개발자 콘솔에서 OAuth 앱을 만든 뒤 `.env.example`의 환경변수를 서버 실행 환경에 등록합니다.

로컬 콜백 주소:

- Google: `http://localhost:8000/accounts/google/login/callback/`
- GitHub: `http://localhost:8000/accounts/github/login/callback/`
- Kakao: `http://localhost:8000/accounts/kakao/login/callback/`
- Naver: `http://localhost:8000/accounts/naver/login/callback/`

운영 배포 시에는 위 호스트를 실제 HTTPS 도메인으로 교체합니다. 환경변수 설정 후 Django 서버를 재시작하면 로그인 화면의 해당 버튼이 활성화됩니다.
