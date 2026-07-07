import pytest
import asyncio
from app.services.cache_service import MemoryCache, cache


def test_cache_set_and_get():
    c = MemoryCache()
    c.set("key1", "value1", ttl=60)
    assert c.get("key1") == "value1"


def test_cache_expired():
    c = MemoryCache()
    c.set("key1", "value1", ttl=0)
    import time
    time.sleep(0.01)
    assert c.get("key1") is None


def test_cache_delete():
    c = MemoryCache()
    c.set("key1", "value1", ttl=60)
    c.delete("key1")
    assert c.get("key1") is None


def test_cache_delete_pattern():
    c = MemoryCache()
    c.set("notebooks:list:1", "data1", ttl=60)
    c.set("notebooks:list:2", "data2", ttl=60)
    c.set("users:1", "userdata", ttl=60)
    c.delete_pattern("notebooks:list")
    assert c.get("notebooks:list:1") is None
    assert c.get("notebooks:list:2") is None
    assert c.get("users:1") == "userdata"


def test_cache_clear():
    c = MemoryCache()
    c.set("a", 1, ttl=60)
    c.set("b", 2, ttl=60)
    c.clear()
    assert c.size() == 0


def test_cache_size():
    c = MemoryCache()
    c.set("a", 1, ttl=60)
    c.set("b", 2, ttl=60)
    assert c.size() == 2
