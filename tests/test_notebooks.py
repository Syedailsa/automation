import pytest
import asyncio
from src.resilience.retry_handler import RetryHandler
from src.resilience.rate_limiter import RateLimiter
from src.resilience.human_delays import HumanDelays


@pytest.mark.asyncio
async def test_retry_handler_success():
    """Test RetryHandler with successful function."""
    handler = RetryHandler(max_retries=3, delay=0.1)
    
    async def success_func():
        return "success"
    
    result = await handler.execute_with_retry(success_func)
    assert result == "success"


@pytest.mark.asyncio
async def test_retry_handler_failure():
    """Test RetryHandler with failing function."""
    handler = RetryHandler(max_retries=2, delay=0.1)
    
    call_count = 0
    
    async def fail_func():
        nonlocal call_count
        call_count += 1
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        await handler.execute_with_retry(fail_func)
    
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_handler_eventual_success():
    """Test RetryHandler with function that succeeds after retries."""
    handler = RetryHandler(max_retries=3, delay=0.1)
    
    call_count = 0
    
    async def eventual_success():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Test error")
        return "success"
    
    result = await handler.execute_with_retry(eventual_success)
    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_rate_limiter():
    """Test RateLimiter."""
    limiter = RateLimiter(max_requests=2, time_window=1)
    
    # Should allow first two requests
    assert await limiter.acquire()
    assert await limiter.acquire()
    
    # Check remaining
    remaining = limiter.get_remaining_requests()
    assert remaining == 0


def test_rate_limiter_detect():
    """Test RateLimiter detection."""
    limiter = RateLimiter()
    
    assert limiter.detect_rate_limit(429) == True
    assert limiter.detect_rate_limit(200) == False
    assert limiter.detect_rate_limit(404) == False


@pytest.mark.asyncio
async def test_human_delays():
    """Test HumanDelays."""
    delays = HumanDelays()
    
    # Test random delay
    await delays.random_delay(0.1, 0.2)
    
    # Test click delay
    await delays.click_delay()
    
    # Test between actions delay
    await delays.between_actions_delay()
