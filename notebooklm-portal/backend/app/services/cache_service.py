import time
import hashlib
import json
import logging
from typing import Any
from functools import wraps

from app.config import settings

logger = logging.getLogger(__name__)


class MemoryCache:
    """In-memory cache with TTL support (fallback when Redis unavailable)."""

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

    def health_check(self) -> bool:
        return True


class RedisCache:
    """Redis-backed cache with automatic JSON serialization."""

    def __init__(self, redis_url: str):
        import redis.asyncio as aioredis

        self._redis = aioredis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        self._connected = True

    async def get(self, key: str) -> Any | None:
        if not self._connected:
            return None
        try:
            raw = await self._redis.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Redis GET failed for {key}: {e}")
            self._connected = False
            return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        if not self._connected:
            return
        try:
            serialized = json.dumps(value, default=str)
            await self._redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.warning(f"Redis SET failed for {key}: {e}")
            self._connected = False

    async def delete(self, key: str):
        if not self._connected:
            return
        try:
            await self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis DELETE failed for {key}: {e}")
            self._connected = False

    async def delete_pattern(self, pattern: str):
        if not self._connected:
            return
        try:
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(
                    cursor=cursor, match=f"*{pattern}*", count=100
                )
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            logger.warning(f"Redis DELETE_PATTERN failed for {pattern}: {e}")
            self._connected = False

    async def clear(self):
        if not self._connected:
            return
        try:
            await self._redis.flushdb()
        except Exception as e:
            logger.warning(f"Redis CLEAR failed: {e}")
            self._connected = False

    async def health_check(self) -> bool:
        if not self._connected:
            return False
        try:
            await self._redis.ping()
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    async def close(self):
        if self._connected:
            try:
                await self._redis.close()
            except Exception:
                pass


class CacheService:
    """Unified cache with Redis primary + MemoryCache fallback.

    All methods are async for consistency. The synchronous MemoryCache
    is wrapped in async where needed.
    """

    def __init__(self):
        self._redis: RedisCache | None = None
        self._memory = MemoryCache()
        self._use_redis = False

    async def initialize(self):
        """Try to connect to Redis. Falls back to memory if unavailable."""
        try:
            self._redis = RedisCache(settings.REDIS_URL)
            if await self._redis.health_check():
                self._use_redis = True
                logger.info("Cache: Connected to Redis")
            else:
                self._use_redis = False
                logger.warning("Cache: Redis unavailable, using in-memory fallback")
        except Exception as e:
            self._use_redis = False
            logger.warning(f"Cache: Redis init failed ({e}), using in-memory fallback")

    async def get(self, key: str) -> Any | None:
        if self._use_redis:
            result = await self._redis.get(key)
            if result is not None:
                return result
            # Check memory fallback
            return self._memory.get(key)
        return self._memory.get(key)

    async def set(self, key: str, value: Any, ttl: int = 300):
        if self._use_redis:
            await self._redis.set(key, value, ttl)
        self._memory.set(key, value, ttl)

    async def delete(self, key: str):
        if self._use_redis:
            await self._redis.delete(key)
        self._memory.delete(key)

    async def delete_pattern(self, pattern: str):
        if self._use_redis:
            await self._redis.delete_pattern(pattern)
        self._memory.delete_pattern(pattern)

    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a specific user."""
        await self.delete_pattern(f"user:{user_id}")
        await self.delete_pattern(f"notebooks:{user_id}")

    async def invalidate_notebook_cache(self, notebook_id: str, user_id: str):
        """Invalidate cache entries for a specific notebook."""
        await self.delete(f"notebook:{notebook_id}")
        await self.delete_pattern(f"notebooks:{user_id}")

    async def clear(self):
        if self._use_redis:
            await self._redis.clear()
        self._memory.clear()

    async def health_check(self) -> dict:
        if self._use_redis:
            redis_ok = await self._redis.health_check()
            return {"backend": "redis", "healthy": redis_ok}
        return {"backend": "memory", "healthy": True}

    async def close(self):
        if self._redis:
            await self._redis.close()


cache = CacheService()


def make_cache_key(*args, **kwargs) -> str:
    raw = json.dumps({"args": str(args), "kwargs": str(kwargs)}, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def cached(ttl: int = 300, prefix: str = ""):
    """Decorator for caching async function results."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{make_cache_key(*args, **kwargs)}"
            result = await cache.get(key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(key, result, ttl=ttl)
            return result

        return wrapper

    return decorator
