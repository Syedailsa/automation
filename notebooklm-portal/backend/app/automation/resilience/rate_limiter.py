import asyncio
from datetime import datetime, timedelta
from collections import deque


class RateLimiter:
    """Handles rate limiting for API calls."""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    async def acquire(self) -> bool:
        """
        Acquire rate limit token.
        
        Returns:
            True if token acquired, False if rate limited
        """
        now = datetime.now()
        
        # Remove old requests outside the time window
        while self.requests and self.requests[0] < now - timedelta(seconds=self.time_window):
            self.requests.popleft()
        
        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            oldest = self.requests[0]
            wait_time = (oldest + timedelta(seconds=self.time_window) - now).total_seconds()
            print(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)
        
        self.requests.append(datetime.now())
        return True
    
    def detect_rate_limit(self, status_code: int) -> bool:
        """
        Detect if status code indicates rate limiting.
        
        Args:
            status_code: HTTP status code
            
        Returns:
            True if rate limited
        """
        return status_code == 429
    
    def get_remaining_requests(self) -> int:
        """
        Get number of remaining requests in current window.
        
        Returns:
            Number of remaining requests
        """
        now = datetime.now()
        
        # Remove old requests
        while self.requests and self.requests[0] < now - timedelta(seconds=self.time_window):
            self.requests.popleft()
        
        return max(0, self.max_requests - len(self.requests))
    
    def reset(self):
        """Reset rate limiter."""
        self.requests.clear()
