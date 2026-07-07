import asyncio
import random
from ..config.settings import settings


class HumanDelays:
    """Simulates human-like delays to avoid detection."""
    
    @staticmethod
    async def typing_delay(text: str, min_delay: float = None, max_delay: float = None):
        """
        Simulate typing delay.
        
        Args:
            text: Text being typed
            min_delay: Minimum delay between characters
            max_delay: Maximum delay between characters
        """
        if min_delay is None:
            min_delay = settings.min_typing_delay
        if max_delay is None:
            max_delay = settings.max_typing_delay
            
        for _ in text:
            await asyncio.sleep(random.uniform(min_delay, max_delay))
    
    @staticmethod
    async def click_delay():
        """Random delay before click."""
        delay = random.uniform(settings.min_click_delay, settings.max_click_delay)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def navigation_delay():
        """Delay after navigation."""
        await asyncio.sleep(random.uniform(2.0, 4.0))
    
    @staticmethod
    async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Random delay."""
        await asyncio.sleep(random.uniform(min_seconds, max_seconds))
    
    @staticmethod
    async def page_load_delay():
        """Delay for page load."""
        await asyncio.sleep(random.uniform(1.0, 2.0))
    
    @staticmethod
    async def processing_delay():
        """Delay for processing operations."""
        await asyncio.sleep(random.uniform(0.5, 1.5))
    
    @staticmethod
    async def between_actions_delay():
        """Delay between different actions."""
        await asyncio.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def get_random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> float:
        """Get random delay value without sleeping."""
        return random.uniform(min_seconds, max_seconds)
