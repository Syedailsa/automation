import asyncio
from playwright.async_api import Page

from ..browser_manager import HumanDelays, ScreenshotManager
from ..selectors import settings


class SlideGenerator:
    """Generates slide decks from notebook content."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
    
    async def generate_slides(self, format: str = "detailed", num_slides: int = None) -> dict:
        """Generate slide deck."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate slides"), button:has-text("Slides")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                await self.page.click(f'button:has-text("{format}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass
            
            if num_slides:
                try:
                    num_input = self.page.locator('input[type="number"], input[placeholder*="slide"]').first
                    await num_input.fill('')
                    await num_input.type(str(num_slides), delay=50)
                except Exception:
                    pass
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await self.page.wait_for_selector(
                'button:has-text("Download"), a:has-text("Download")',
                timeout=180000
            )
            
            return {'status': 'generated', 'type': 'slides', 'format': format}
        except Exception as e:
            print(f"Error generating slides: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_slides_error")
            return {'status': 'error', 'error': str(e)}
