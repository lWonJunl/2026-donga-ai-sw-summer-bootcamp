from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit, urlunsplit


URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
TRAILING_PUNCTUATION = ".,!?;:)]}〉》」』’”"


def normalize_url(url: str) -> str:
    candidate = url.strip().rstrip(TRAILING_PUNCTUATION)
    if len(candidate) > 2048:
        raise ValueError("URL은 2,048자 이하여야 합니다.")
    parsed = urlsplit(candidate)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("http 또는 https URL만 사용할 수 있습니다.")
    if parsed.username or parsed.password:
        raise ValueError("인증정보가 포함된 URL은 사용할 수 없습니다.")
    host = parsed.hostname.lower()
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError as error:
        raise ValueError("URL 호스트 형식이 올바르지 않습니다.") from error
    if ":" in host:
        host = f"[{host}]"
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("URL 포트 형식이 올바르지 않습니다.") from error
    if port and not ((parsed.scheme.lower() == "http" and port == 80) or (parsed.scheme.lower() == "https" and port == 443)):
        host = f"{host}:{port}"
    return urlunsplit((parsed.scheme.lower(), host, parsed.path or "/", parsed.query, ""))


def extract_urls(text: str, limit: int = 3) -> tuple[list[str], bool]:
    urls = []
    seen = set()
    matches = URL_PATTERN.findall(text or "")
    for match in matches:
        try:
            normalized = normalize_url(match)
        except ValueError:
            continue
        if normalized not in seen:
            seen.add(normalized)
            urls.append(normalized)
    return urls[:limit], len(urls) > limit


def url_fingerprint(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()
