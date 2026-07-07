import asyncio
from functools import wraps
from typing import Callable, Any


class RetryHandler:
    """Handles retry logic for failed operations."""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
    
    def retry(self, func: Callable) -> Callable:
        """Decorator to retry function on failure."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    delay = self.delay * (self.backoff ** attempt)
                    print(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                    print(f"Retrying in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
            
            print(f"All {self.max_retries} attempts failed")
            raise last_exception
        
        return wrapper
