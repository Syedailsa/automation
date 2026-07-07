import asyncio
from playwright.async_api import Page
from ..resilience.human_delays import HumanDelays
from ..utils.screenshot import ScreenshotManager
from ..config.settings import settings


class SlideGenerator:
    """Generates slide decks from notebook content."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.home_dir)
        
    async def generate_slides(self, format: str = "detailed", num_slides: int = None) -> dict:
        """
        Generate slide deck.
        
        Args:
            format: Slide format (detailed, presenter)
            num_slides: Number of slides (optional)
            
        Returns:
            Dict with status and type
        """
        try:
            # Click generate slides
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate slides"), button:has-text("Slides")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            # Wait for dialog
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            # Select format
            try:
                await self.page.click(f'button:has-text("{format}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass  # Format selection not available
            
            # Set number of slides if provided
            if num_slides:
                try:
                    num_input = self.page.locator('input[type="number"], input[placeholder*="slide"]').first
                    await num_input.fill('')
                    await num_input.type(str(num_slides), delay=50)
                except Exception:
                    pass  # Number input not available
            
            await self.delays.random_delay(0.5, 1.0)
            
            # Click generate
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            # Wait for generation
            await self.page.wait_for_selector(
                'button:has-text("Download"), a:has-text("Download")',
                timeout=180000  # 3 minutes
            )
            
            return {'status': 'generated', 'type': 'slides', 'format': format}
        except Exception as e:
            print(f"Error generating slides: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_slides_error")
            return {'status': 'error', 'error': str(e)}
    
    async def download_slides(self, output_path: str, format: str = "pdf") -> str:
        """
        Download slides.
        
        Args:
            output_path: Path to save slides file
            format: Output format (pdf, pptx)
            
        Returns:
            Path to downloaded file
        """
        try:
            # Click download button
            await self.page.click('button:has-text("Download")')
            
            await self.delays.random_delay(0.3, 0.5)
            
            # Select format
            try:
                await self.page.click(f'button:has-text("{format}")')
            except Exception:
                pass  # Format selection not available
            
            async with self.page.expect_download() as download_info:
                await self.page.click('button:has-text("Download")')
            
            download = await download_info.value
            await download.save_as(output_path)
            
            return output_path
        except Exception as e:
            print(f"Error downloading slides: {e}")
            return None
