# Security and production deployment

Do not deploy with `manage.py runserver`. Use a maintained Python runtime, a production WSGI/ASGI server, and HTTPS at the reverse proxy.

Required production environment:

```text
DJANGO_PRODUCTION=True
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<at least 50 random characters>
DJANGO_ALLOWED_HOSTS=portfolio.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://portfolio.example.com
DJANGO_BEHIND_HTTPS_PROXY=True
```

`DJANGO_HSTS_INCLUDE_SUBDOMAINS` and `DJANGO_HSTS_PRELOAD` intentionally default to false. Enable them only when every subdomain is permanently HTTPS-ready. HSTS is otherwise enabled for one year in production.

OAuth client secrets and `.env` must never be committed. Restrict every provider's callback URL to the exact HTTPS URL documented in `SOCIAL_LOGIN_SETUP.md`. Rotate any secret that has been exposed.

Signup requires email verification and enables django-allauth's account-enumeration prevention. Login and registration POST bodies are marked sensitive so usernames, email addresses, and passwords are excluded from Django error reports. Generic username validation messages avoid directly confirming whether a particular username is registered.

Email verification and password reset require a working SMTP service in production. Configure every `DJANGO_EMAIL_*` value in `.env.example`; production startup fails when `DJANGO_EMAIL_HOST` is missing.

The local SQLite database can contain usernames, password hashes, sessions, and OAuth account metadata. It is ignored by Git and should remain readable only by the service account. Use encrypted backups and a production database for deployment.

The Django admin login is not covered by django-allauth's rate limits. In production, restrict `/admin/` at the reverse proxy or private network and monitor failed login attempts.

The in-process login limiter is suitable for a single application process. A multi-process deployment must configure Django `CACHES` with a shared Redis or Memcached backend so limits are shared across workers.
