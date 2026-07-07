import asyncio
import logging
from playwright.async_api import Page

from ..resilience import HumanDelays
from ..utils import ScreenshotManager
from ..config import settings

logger = logging.getLogger(__name__)


class FlashcardGenerator:
    """Generates flashcards from notebook content."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
    
    async def generate_flashcards(self, num_cards: int = 20, difficulty: str = "medium") -> dict:
        """Generate flashcards."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate flashcards"), button:has-text("Flashcards")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                num_input = self.page.locator('input[type="number"], input[placeholder*="card"]').first
                await num_input.fill('')
                await num_input.type(str(num_cards), delay=50)
            except Exception as e:
                logger.debug(f"Could not set card count: {e}")
            
            try:
                await self.page.click(f'button:has-text("{difficulty}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception as e:
                logger.debug(f"Could not click difficulty button: {e}")
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await self.page.wait_for_selector(
                'button:has-text("Download"), [data-flashcards-generated="true"]',
                timeout=120000
            )
            
            return {'status': 'generated', 'type': 'flashcards'}
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_flashcards_error")
            return {'status': 'error', 'error': str(e)}
