import json
import logging

from django.conf import settings
from django.core.cache import caches


logger = logging.getLogger(__name__)


class UTF8StringSerializer:
    """Store context JSON as UTF-8 without Django's default pickle serializer."""

    def dumps(self, value):
        if not isinstance(value, str):
            raise TypeError("The context cache only accepts strings")
        return value.encode("utf-8")

    def loads(self, value):
        return value.decode("utf-8")


def _cache_key(conversation_id):
    return f"conversation:{conversation_id}:recent-messages"


def _context_cache():
    return caches["context"]


def _recent_messages_from_sqlite(conversation):
    limit = settings.CHAT_CONTEXT_MESSAGE_LIMIT
    content_limit = settings.CHAT_MESSAGE_MAX_LENGTH
    messages = list(
        conversation.messages.order_by("-created_at", "-id")
        .values("role", "content")[:limit]
    )
    messages.reverse()
    for message in messages:
        message["content"] = message["content"][:content_limit]
    return messages


def _parse_cached_messages(cached):
    messages = json.loads(cached)
    if not isinstance(messages, list) or len(messages) > settings.CHAT_CONTEXT_MESSAGE_LIMIT:
        raise ValueError("Invalid cached context")
    for message in messages:
        if (
            not isinstance(message, dict)
            or set(message) != {"role", "content"}
            or message["role"] not in {"user", "assistant"}
            or not isinstance(message["content"], str)
            or len(message["content"]) > settings.CHAT_MESSAGE_MAX_LENGTH
        ):
            raise ValueError("Invalid cached message")
    return messages


def refresh_conversation_context(conversation):
    """Replace the Redis entry with the latest context from SQLite."""
    messages = _recent_messages_from_sqlite(conversation)
    try:
        _context_cache().set(
            _cache_key(conversation.id),
            json.dumps(messages, ensure_ascii=False),
            timeout=settings.CHAT_CONTEXT_CACHE_TIMEOUT,
        )
    except Exception:
        logger.warning("Redis context cache write failed; continuing with SQLite")
    return messages


def recent_messages(conversation):
    """Return recent context from Redis, falling back to SQLite on any cache error."""
    key = _cache_key(conversation.id)
    try:
        cached = _context_cache().get(key)
        if cached is not None:
            return _parse_cached_messages(cached)
    except Exception:
        logger.warning("Redis context cache read failed; using SQLite")

    return refresh_conversation_context(conversation)


def invalidate_conversation_context(conversation_id):
    if not conversation_id:
        return
    try:
        _context_cache().delete(_cache_key(conversation_id))
    except Exception:
        logger.warning("Redis context cache invalidation failed")
