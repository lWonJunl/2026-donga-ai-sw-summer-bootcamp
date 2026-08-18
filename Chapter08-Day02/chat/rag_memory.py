from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from django.conf import settings
import redis


class RAGMemory:
    def __init__(self, user_id: int, conversation_id: int):
        self.user_id = int(user_id)
        self.conversation_id = int(conversation_id)
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.history_key = f"rag:chat:{self.user_id}:{self.conversation_id}"
        self.context_key = f"rag:context:{self.user_id}:{self.conversation_id}"
        self.profile_key = f"rag:profile:{self.user_id}"
        self.log_path = (
            Path(settings.RAG_CHAT_LOG_DIR)
            / str(self.user_id)
            / f"{self.conversation_id}.jsonl"
        )

    def save_profile(self, profile: dict[str, str]):
        clean = {key: str(value)[:1000] for key, value in profile.items() if value}
        if clean:
            self.client.hset(self.profile_key, mapping=clean)

    def load_profile(self):
        return self.client.hgetall(self.profile_key)

    def add_message(self, role: str, content: str):
        if role not in {"user", "assistant"}:
            raise ValueError("지원하지 않는 메시지 역할입니다.")
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content[: settings.CHAT_MESSAGE_MAX_LENGTH],
        }
        payload = json.dumps(record, ensure_ascii=False)
        # The local audit log remains available even when Redis is temporarily down.
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(payload + "\n")
        pipe = self.client.pipeline()
        pipe.rpush(self.history_key, payload)
        pipe.ltrim(self.history_key, -(settings.RAG_MAX_HISTORY_TURNS * 2), -1)
        pipe.expire(self.history_key, settings.RAG_MEMORY_TTL)
        pipe.execute()

    def save_last_context(self, context: str):
        self.client.set(self.context_key, context[: settings.RAG_MAX_CONTEXT_CHARS], ex=settings.RAG_MEMORY_TTL)

    def load_last_context(self):
        return self.client.get(self.context_key) or ""

    def clear(self):
        self.client.delete(self.history_key, self.context_key)
