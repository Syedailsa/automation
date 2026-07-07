import asyncio
import random

from ..selectors import settings


class HumanDelays:
    """Simulates human-like delays to avoid detection."""
    
    @staticmethod
    async def typing_delay(text: str, min_delay: float = None, max_delay: float = None):
        """Simulate typing delay."""
        if min_delay is None:
            min_delay = settings.MIN_TYPING_DELAY
        if max_delay is None:
            max_delay = settings.MAX_TYPING_DELAY
        
        for _ in text:
            await asyncio.sleep(random.uniform(min_delay, max_delay))
    
    @staticmethod
    async def click_delay():
        """Random delay before click."""
        delay = random.uniform(settings.MIN_CLICK_DELAY, settings.MAX_CLICK_DELAY)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Random delay."""
        await asyncio.sleep(random.uniform(min_seconds, max_seconds))
