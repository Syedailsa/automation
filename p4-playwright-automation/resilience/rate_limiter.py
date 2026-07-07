import asyncio
from datetime import datetime, timedelta
from typing import List


class RateLimiter:
    """Handles rate limiting for API calls."""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[datetime] = []
    
    async def acquire(self) -> bool:
        """Acquire rate limit token."""
        now = datetime.now()
        
        # Remove old requests
        self.requests = [
            r for r in self.requests 
            if r > now - timedelta(seconds=self.time_window)
        ]
        
        if len(self.requests) >= self.max_requests:
            wait_time = (
                self.requests[0] + timedelta(seconds=self.time_window) - now
            ).total_seconds()
            print(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)
        
        self.requests.append(now)
        return True
