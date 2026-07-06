import asyncio
from functools import wraps
from typing import Callable, Any


class RetryHandler:
    """Handles retry logic for failed operations."""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries (seconds)
            backoff: Backoff multiplier for delay
        """
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
    
    def retry(self, func: Callable) -> Callable:
        """
        Decorator to retry function on failure.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function with retry logic
        """
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
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
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
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
