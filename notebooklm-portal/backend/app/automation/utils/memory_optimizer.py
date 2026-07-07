"""Memory optimization and caching module."""
import asyncio
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
import logging
import gc

logger = logging.getLogger(__name__)


class MemoryOptimizer:
    """Optimizes memory usage for browser operations."""
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb
        self.cleanup_callbacks: list = []
    
    def register_cleanup_callback(self, callback: Callable):
        """Register a cleanup callback."""
        self.cleanup_callbacks.append(callback)
    
    async def check_memory_usage(self) -> Dict[str, Any]:
        """Check current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            return {
                "current_mb": round(memory_mb, 2),
                "max_mb": self.max_memory_mb,
                "usage_percent": round((memory_mb / self.max_memory_mb) * 100, 2),
                "needs_cleanup": memory_mb > self.max_memory_mb
            }
        except ImportError:
            return {"status": "psutil not available"}
    
    async def cleanup_memory(self) -> Dict[str, Any]:
        """Perform memory cleanup."""
        gc.collect()
        
        for callback in self.cleanup_callbacks:
            try:
                await callback()
            except Exception as e:
                logger.error(f"Cleanup callback failed: {e}")
        
        memory_info = await self.check_memory_usage()
        
        return {
            "status": "cleanup_completed",
            "memory_after": memory_info
        }
    
    async def monitor_memory(self, interval_seconds: int = 30) -> None:
        """Monitor memory usage in background."""
        while True:
            memory_info = await self.check_memory_usage()
            
            if memory_info.get("needs_cleanup"):
                logger.warning("Memory usage high, performing cleanup")
                await self.cleanup_memory()
            
            await asyncio.sleep(interval_seconds)


class CacheManager:
    """Manages caching for automation operations."""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry["expires_at"]:
                return entry["value"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache."""
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl),
            "created_at": datetime.now()
        }
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.now()
        valid_entries = sum(1 for entry in self.cache.values() if now < entry["expires_at"])
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self.cache) - valid_entries
        }
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        now = datetime.now()
        expired_keys = [key for key, entry in self.cache.items() if now >= entry["expires_at"]]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)


class CachedBrowserOperation:
    """Caches browser operation results."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    async def execute_cached(self, operation_name: str, operation_func: Callable, *args, cache_key: str = None, ttl: int = None) -> Any:
        """Execute operation with caching."""
        if cache_key is None:
            cache_key = f"{operation_name}:{hash(str(args))}"
        
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for {operation_name}")
            return cached_result
        
        result = await operation_func(*args)
        self.cache.set(cache_key, result, ttl)
        
        return result
