import asyncio
from playwright.async_api import Page
from ..resilience.human_delays import HumanDelays
from ..utils.screenshot import ScreenshotManager
from ..config.settings import settings


class VideoGenerator:
    """Generates video overviews."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.home_dir)
        
    async def generate_video(self, style: str = "explainer", custom_prompt: str = "") -> dict:
        """
        Generate video overview.
        
        Args:
            style: Video style (explainer, brief, cinematic, short)
            custom_prompt: Custom prompt for video generation
            
        Returns:
            Dict with status and type
        """
        try:
            # Click generate video
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate video"), button:has-text("Video")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            # Wait for dialog
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            # Select style if available
            try:
                await self.page.click(f'button:has-text("{style}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass  # Style selection not available
            
            # Enter custom prompt if provided
            if custom_prompt:
                try:
                    textarea = self.page.locator('textarea, input[placeholder*="prompt"]').first
                    await textarea.fill('')
                    await textarea.type(custom_prompt, delay=30)
                except Exception:
                    pass  # Prompt field not available
            
            await self.delays.random_delay(0.5, 1.0)
            
            # Click generate
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            # Wait for generation (videos take longer)
            await self.page.wait_for_selector(
                'button:has-text("Download"), a:has-text("Download")',
                timeout=600000  # 10 minutes
            )
            
            return {'status': 'generated', 'type': 'video', 'style': style}
        except Exception as e:
            print(f"Error generating video: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_video_error")
            return {'status': 'error', 'error': str(e)}
    
    async def download_video(self, output_path: str) -> str:
        """
        Download generated video.
        
        Args:
            output_path: Path to save video file
            
        Returns:
            Path to downloaded file
        """
        try:
            async with self.page.expect_download() as download_info:
                await self.page.click('button:has-text("Download"), a:has-text("Download")')
            
            download = await download_info.value
            await download.save_as(output_path)
            
            return output_path
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None
