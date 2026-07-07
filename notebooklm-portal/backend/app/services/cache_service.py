import time
import hashlib
import json
from typing import Any
from functools import wraps

"""In-memory caching with TTL support."""


class MemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        if key in self._store:
            value, expires_at = self._store[key]
            if time.time() < expires_at:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        expires_at = time.time() + ttl
        self._store[key] = (value, expires_at)

    def delete(self, key: str):
        self._store.pop(key, None)

    def delete_pattern(self, pattern: str):
        keys_to_delete = [k for k in self._store if pattern in k]
        for key in keys_to_delete:
            del self._store[key]

    def clear(self):
        self._store.clear()

    def size(self) -> int:
        now = time.time()
        return sum(1 for _, (_, exp) in self._store.items() if now < exp)


cache = MemoryCache()


def make_cache_key(*args, **kwargs) -> str:
    raw = json.dumps({"args": str(args), "kwargs": str(kwargs)}, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def cached(ttl: int = 300, prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{make_cache_key(*args, **kwargs)}"
            result = cache.get(key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
