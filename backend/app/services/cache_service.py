import hashlib
import json
from typing import Any

from app.config import get_settings

settings = get_settings()


class CacheService:
    def __init__(self):
        self.client = None
        self.memory: dict[str, Any] = {}
        try:
            import redis
            self.client = redis.from_url(settings.redis_url, decode_responses=True)
            self.client.ping()
        except Exception:
            self.client = None

    def make_key(self, *parts: str) -> str:
        raw = "::".join(str(p) for p in parts)
        return "sentiment:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_json(self, key: str):
        try:
            if self.client:
                value = self.client.get(key)
                return json.loads(value) if value else None
            return self.memory.get(key)
        except Exception:
            return None

    def set_json(self, key: str, value, ttl_seconds: int = 300):
        try:
            if self.client:
                self.client.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))
            else:
                self.memory[key] = value
        except Exception:
            pass
