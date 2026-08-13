import os
import secrets
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY is required when DEBUG is false")
    SECRET_KEY = secrets.token_urlsafe(64)
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "chat",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "exaone_site.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]
WSGI_APPLICATION = "exaone_site.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# SQLite remains the source of truth. Redis only caches the recent chat context.
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
CHAT_CONTEXT_MESSAGE_LIMIT = int(os.environ.get("CHAT_CONTEXT_MESSAGE_LIMIT", "12"))
CHAT_CONTEXT_CACHE_TIMEOUT = int(os.environ.get("CHAT_CONTEXT_CACHE_TIMEOUT", "3600"))
CHAT_MESSAGE_MAX_LENGTH = int(os.environ.get("CHAT_MESSAGE_MAX_LENGTH", "16000"))
SYSTEM_PROMPT_MAX_LENGTH = int(os.environ.get("SYSTEM_PROMPT_MAX_LENGTH", "1000"))
RAG_EMBED_MODEL = os.environ.get("RAG_EMBED_MODEL", "intfloat/multilingual-e5-small")
RAG_EMBED_DEVICE = os.environ.get("RAG_EMBED_DEVICE", "cpu")
RAG_MILVUS_URI = os.environ.get("RAG_MILVUS_URI", "http://127.0.0.1:19530")
RAG_MILVUS_COLLECTION = os.environ.get("RAG_MILVUS_COLLECTION", "exaone_personal_docs")
RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "4"))
RAG_MAX_HISTORY_TURNS = int(os.environ.get("RAG_MAX_HISTORY_TURNS", "8"))
RAG_MEMORY_TTL = int(os.environ.get("RAG_MEMORY_TTL", str(60 * 60 * 24 * 30)))
RAG_MAX_CONTEXT_CHARS = int(os.environ.get("RAG_MAX_CONTEXT_CHARS", "12000"))
RAG_MAX_UPLOAD_BYTES = int(os.environ.get("RAG_MAX_UPLOAD_BYTES", str(20 * 1024 * 1024)))
RAG_DATA_DIR = Path(os.environ.get("RAG_DATA_DIR", BASE_DIR / "data"))
RAG_UPLOAD_DIR = Path(os.environ.get("RAG_UPLOAD_DIR", RAG_DATA_DIR / "uploads"))
RAG_CHAT_LOG_DIR = Path(os.environ.get("RAG_CHAT_LOG_DIR", RAG_DATA_DIR / "chat_logs"))
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "exaone-default",
    },
    "context": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": "exaone-chat",
        "TIMEOUT": CHAT_CONTEXT_CACHE_TIMEOUT,
        "OPTIONS": {
            "serializer": "chat.context_cache.UTF8StringSerializer",
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ko-kr"
DEFAULT_CHARSET = "utf-8"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "chat"
LOGOUT_REDIRECT_URL = "login"
