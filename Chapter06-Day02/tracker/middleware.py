import hashlib
import time

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render


class RefreshRateLimitMiddleware:
    sensitive_post_paths = {
        "/accounts/login/",
        "/accounts/signup/",
        "/accounts/password/reset/",
        "/groups/join/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path in self.sensitive_post_paths:
            response = self.check_sensitive_post(request)
            if response is not None:
                return response
        if request.method not in {"GET", "HEAD"} or self.is_excluded(request.path):
            return self.get_response(request)

        identity = self.identity_for(request)
        digest = hashlib.sha256(identity.encode()).hexdigest()
        block_key = f"refresh-limit:block:{digest}"
        block_seconds = settings.REFRESH_RATE_LIMIT_BLOCK_SECONDS

        if cache.get(block_key):
            return self.blocked_response(request, block_seconds)

        window_seconds = settings.REFRESH_RATE_LIMIT_WINDOW_SECONDS
        window = int(time.time() // window_seconds)
        count_key = f"refresh-limit:count:{digest}:{window}"
        if cache.add(count_key, 1, timeout=window_seconds + 1):
            count = 1
        else:
            count = cache.incr(count_key)

        if count > settings.REFRESH_RATE_LIMIT_REQUESTS:
            cache.set(block_key, True, timeout=block_seconds)
            return self.blocked_response(request, block_seconds)
        return self.get_response(request)

    def check_sensitive_post(self, request):
        identity = self.identity_for(request)
        digest = hashlib.sha256(f"{request.path}:{identity}".encode()).hexdigest()
        window_seconds = settings.SENSITIVE_POST_RATE_LIMIT_WINDOW_SECONDS
        window = int(time.time() // window_seconds)
        key = f"sensitive-post-limit:{digest}:{window}"
        if cache.add(key, 1, timeout=window_seconds + 1):
            count = 1
        else:
            count = cache.incr(key)
        if count > settings.SENSITIVE_POST_RATE_LIMIT_REQUESTS:
            return self.blocked_response(request, window_seconds)
        return None

    @staticmethod
    def identity_for(request):
        if request.user.is_authenticated:
            return f"user:{request.user.pk}"
        return f"ip:{request.META.get('REMOTE_ADDR', 'unknown')}"

    @staticmethod
    def is_excluded(path):
        static_path = f"/{settings.STATIC_URL.lstrip('/')}"
        return path.startswith(static_path) or path in {"/sw.js", "/favicon.ico"}

    @staticmethod
    def blocked_response(request, retry_after):
        response = render(
            request,
            "errors/rate_limited.html",
            {"retry_after": retry_after},
            status=429,
        )
        response["Retry-After"] = str(retry_after)
        return response
