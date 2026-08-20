from .settings import *  # noqa: F403


# PostgreSQL 서버 없이 도메인 로직을 검증하기 위한 테스트 전용
# 메모리 데이터베이스입니다. 실제 실행 설정은 PostgreSQL을 사용합니다.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

REFRESH_RATE_LIMIT_REQUESTS = 10000
SENSITIVE_POST_RATE_LIMIT_REQUESTS = 10000
