import os
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key


BASE_DIR = Path(__file__).resolve().parent.parent


def load_local_env(path):
    """Load simple KEY=VALUE entries without overriding shell variables."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


load_local_env(BASE_DIR / ".env")


def clean_environment_value(name):
    """Return a trimmed value and tolerate a pasted ``NAME=value`` line."""
    value = os.environ.get(name, "").strip()
    prefix = f"{name}="
    if value.startswith(prefix):
        value = value[len(prefix) :].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1].strip()
    return value


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}


PRODUCTION = env_bool("DJANGO_PRODUCTION")
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if PRODUCTION:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY is required in production")
    SECRET_KEY = get_random_secret_key()

DEBUG = env_bool("DJANGO_DEBUG", default=not PRODUCTION)
if PRODUCTION and DEBUG:
    raise ImproperlyConfigured("DJANGO_DEBUG must be false in production")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost" if not PRODUCTION else RENDER_EXTERNAL_HOSTNAME,
    ).split(",")
    if host.strip()
]
if PRODUCTION and not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS is required in production")

SITE_URL = (
    os.environ.get("SITE_URL", "")
    or os.environ.get("RENDER_EXTERNAL_URL", "")
    or (f"https://{RENDER_EXTERNAL_HOSTNAME}" if RENDER_EXTERNAL_HOSTNAME else "")
).strip().rstrip("/")
if PRODUCTION and not SITE_URL:
    raise ImproperlyConfigured("SITE_URL is required in production")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
if PRODUCTION and SITE_URL and SITE_URL not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(SITE_URL)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tracker",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "tracker.middleware.RefreshRateLimitMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "priority_poke.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "priority_poke.wsgi.application"

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    parsed_database_url = urlparse(DATABASE_URL)
    if parsed_database_url.scheme not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured("DATABASE_URL must be a PostgreSQL URL")
    if not parsed_database_url.hostname or not parsed_database_url.path.strip("/"):
        raise ImproperlyConfigured("DATABASE_URL is missing a host or database name")
    database_options = dict(parse_qsl(parsed_database_url.query))
    if parsed_database_url.hostname.endswith(".neon.tech"):
        database_options.setdefault("sslmode", "require")
        database_options.setdefault("channel_binding", "require")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(parsed_database_url.path.lstrip("/")),
            "USER": unquote(parsed_database_url.username or ""),
            "PASSWORD": unquote(parsed_database_url.password or ""),
            "HOST": parsed_database_url.hostname,
            "PORT": str(parsed_database_url.port or 5432),
            "OPTIONS": database_options,
            "CONN_MAX_AGE": 60,
            "CONN_HEALTH_CHECKS": True,
        }
    }
elif PRODUCTION:
    raise ImproperlyConfigured("DATABASE_URL is required in production")
else:
    # 로컬 개발은 별도 DB 서버 없이 SQLite를 사용합니다. 나중에
    # DATABASE_URL을 설정하면 위의 PostgreSQL 설정으로 자동 전환됩니다.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if PRODUCTION
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        )
    },
}

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "10"))
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "").strip() or (
    f"우선콕 <{EMAIL_HOST_USER}>" if EMAIL_HOST_USER else "우선콕 <noreply@example.com>"
)
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

WEBPUSH_VAPID_PRIVATE_KEY = clean_environment_value("WEBPUSH_VAPID_PRIVATE_KEY")
WEBPUSH_VAPID_PUBLIC_KEY = clean_environment_value("WEBPUSH_VAPID_PUBLIC_KEY")
WEBPUSH_VAPID_SUBJECT = os.environ.get("WEBPUSH_VAPID_SUBJECT", "").strip() or (
    f"mailto:{EMAIL_HOST_USER}" if EMAIL_HOST_USER else "mailto:contact@example.com"
)

if PRODUCTION:
    missing_service_settings = [
        name
        for name, value in {
            "EMAIL_HOST_USER": EMAIL_HOST_USER,
            "EMAIL_HOST_PASSWORD": EMAIL_HOST_PASSWORD,
        }.items()
        if not value
    ]
    if missing_service_settings:
        raise ImproperlyConfigured(
            "Missing production settings: " + ", ".join(missing_service_settings)
        )

REFRESH_RATE_LIMIT_REQUESTS = int(os.environ.get("REFRESH_RATE_LIMIT_REQUESTS", "20"))
REFRESH_RATE_LIMIT_WINDOW_SECONDS = int(
    os.environ.get("REFRESH_RATE_LIMIT_WINDOW_SECONDS", "10")
)
REFRESH_RATE_LIMIT_BLOCK_SECONDS = int(
    os.environ.get("REFRESH_RATE_LIMIT_BLOCK_SECONDS", "30")
)
SENSITIVE_POST_RATE_LIMIT_REQUESTS = int(
    os.environ.get("SENSITIVE_POST_RATE_LIMIT_REQUESTS", "10")
)
SENSITIVE_POST_RATE_LIMIT_WINDOW_SECONDS = int(
    os.environ.get("SENSITIVE_POST_RATE_LIMIT_WINDOW_SECONDS", "60")
)
EMAIL_VERIFICATION_MAX_AGE_SECONDS = int(
    os.environ.get("EMAIL_VERIFICATION_MAX_AGE_SECONDS", "86400")
)
RUN_NOTIFICATION_SCHEDULER = env_bool("RUN_NOTIFICATION_SCHEDULER", False)
NOTIFICATION_SCHEDULER_INTERVAL_SECONDS = max(
    60, int(os.environ.get("NOTIFICATION_SCHEDULER_INTERVAL_SECONDS", "600"))
)

if PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "3600"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
        "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", False
    )
    SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "landing"
