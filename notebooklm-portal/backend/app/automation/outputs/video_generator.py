import asyncio
import logging
from playwright.async_api import Page

from ..resilience import HumanDelays
from ..utils import ScreenshotManager
from ..config import settings

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Generates video overviews."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
    
    async def generate_video(self, style: str = "explainer", custom_prompt: str = "") -> dict:
        """Generate video overview."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate video"), button:has-text("Video")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                await self.page.click(f'button:has-text("{style}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception as e:
                logger.debug(f"Could not click video style button: {e}")
            
            if custom_prompt:
                try:
                    textarea = self.page.locator('textarea, input[placeholder*="prompt"]').first
                    await textarea.fill('')
                    await textarea.type(custom_prompt, delay=30)
                except Exception as e:
                    logger.debug(f"Could not fill custom prompt: {e}")
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await self.page.wait_for_selector(
                'button:has-text("Download"), a:has-text("Download")',
                timeout=600000
            )
            
            return {'status': 'generated', 'type': 'video', 'style': style}
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_video_error")
            return {'status': 'error', 'error': str(e)}
    
    async def download_video(self, output_path: str) -> str:
        """Download generated video."""
        try:
            async with self.page.expect_download() as download_info:
                await self.page.click('button:has-text("Download"), a:has-text("Download")')
            
            download = await download_info.value
            await download.save_as(output_path)
            
            return output_path
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None
