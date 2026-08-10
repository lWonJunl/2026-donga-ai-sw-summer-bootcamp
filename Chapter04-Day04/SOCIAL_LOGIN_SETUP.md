# 소셜 로그인 설정

각 개발자 콘솔에서 OAuth 앱을 만든 뒤 `.env.example`의 환경변수를 서버 실행 환경에 등록합니다.

로컬 콜백 주소:

- Google: `http://localhost:8000/accounts/google/login/callback/`
- GitHub: `http://localhost:8000/accounts/github/login/callback/`
- Kakao: `http://localhost:8000/accounts/kakao/login/callback/`
- Naver: `http://localhost:8000/accounts/naver/login/callback/`

Vercel 배포에서는 위 호스트를 실제 프로덕션 주소로 교체합니다. 예를 들어 프로젝트 주소가 `https://my-project.vercel.app`이라면 GitHub 콜백은 `https://my-project.vercel.app/accounts/github/login/callback/`입니다.

OAuth Client ID와 Secret은 Vercel Project Settings의 Environment Variables에 Production과 Preview 환경별로 등록합니다. 값을 변경한 뒤에는 다시 배포해야 로그인 화면의 해당 버튼에 새 설정이 적용됩니다.
