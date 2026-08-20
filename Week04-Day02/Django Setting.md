# Django 설치 및 실행 설정

Linux 환경에서 Django를 설치하고 외부에서 접속할 수 있도록 개발 서버를 실행하는 방법을 정리한다.

## 1. Python 설치 확인

설치된 Python 패키지를 확인한다.

```bash
rpm -qa | grep 'python*'
```

`pip`가 설치되어 있지 않다면 다음 명령으로 설치한다.

```bash
python3 -m ensurepip --default-pip
```

## 2. Django 설치

현재 사용 중인 Python3 환경에 Django를 설치한다.

```bash
python3 -m pip install django
```

설치 여부와 버전을 확인한다.

```bash
python3 -m django --version
```

## 3. 프로젝트 생성

작업 디렉터리를 만들고 Django 프로젝트를 생성한다.

```bash
cd /home
mkdir test
cd test

django-admin startproject testproject
cd testproject
```

프로젝트는 다음과 같은 구조로 생성된다.

```text
testproject/
├── manage.py
└── testproject/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

## 4. 개발 서버 실행

먼저 로컬 접속 전용으로 서버가 정상 실행되는지 확인한다.

```bash
python3 manage.py runserver
```

기본 접속 주소는 다음과 같다.

```text
http://127.0.0.1:8000
```

서버를 종료하려면 터미널에서 `Ctrl+C`를 누른다.

## 5. 외부 접속 설정

### 5.1 방화벽 포트 열기

8000번 TCP 포트를 영구적으로 허용한 뒤 방화벽 설정을 다시 불러온다.

```bash
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload
```

권한 오류가 발생하면 관리자 권한으로 실행한다.

```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 5.2 `ALLOWED_HOSTS` 설정

Django 설정 디렉터리로 이동한 뒤 원본 파일을 백업한다.

```bash
cd testproject
cp settings.py settings.py.bak.2026.07.21
vi settings.py
```

`settings.py`에서 `ALLOWED_HOSTS`에 접속을 허용할 서버의 IP 주소 또는 도메인을 입력한다.

```python
ALLOWED_HOSTS = ["서버_IP_또는_도메인"]
```

실습 환경에서 모든 호스트의 접속을 임시로 허용하려면 다음과 같이 설정할 수 있다.

```python
ALLOWED_HOSTS = ["*"]
```

> `ALLOWED_HOSTS = ["*"]`는 모든 호스트를 허용하므로 운영 환경에서는 사용하지 않는다.

`vi` 편집 방법은 다음과 같다.

1. 수정할 위치로 이동한 뒤 `a`를 눌러 입력 모드로 전환한다.
2. 편집이 끝나면 `Esc`를 눌러 명령 모드로 돌아간다.
3. `:wq`를 입력하고 `Enter`를 눌러 저장한 뒤 종료한다.

상위 디렉터리로 돌아간다.

```bash
cd ..
```

### 5.3 외부 접속 허용 상태로 실행

모든 네트워크 인터페이스의 8000번 포트에서 개발 서버를 실행한다.

```bash
python3 manage.py runserver 0.0.0.0:8000
```

다른 컴퓨터의 브라우저에서 다음 주소로 접속한다.

```text
http://서버_IP:8000
```

> Django의 `runserver`는 개발용 서버이다. 운영 환경에서는 별도의 WSGI/ASGI 서버와 웹 서버를 사용해야 한다.
