import asyncio
from playwright.async_api import Page
from ..resilience.human_delays import HumanDelays
from ..utils.screenshot import ScreenshotManager
from ..config.settings import settings


class AudioGenerator:
    """Generates audio overviews."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.home_dir)
        
    async def generate_audio(self, instructions: str = "", audio_format: str = "deep-dive") -> dict:
        """
        Generate audio overview.
        
        Args:
            instructions: Custom instructions for audio generation
            audio_format: Audio format (deep-dive, brief, critique, debate)
            
        Returns:
            Dict with status and type
        """
        try:
            # Click generate audio
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate audio"), button:has-text("Audio")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            # Wait for dialog
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            # Select format if available
            try:
                await self.page.click(f'button:has-text("{audio_format}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass  # Format selection not available
            
            # Enter instructions if provided
            if instructions:
                try:
                    textarea = self.page.locator('textarea, input[placeholder*="instruction"]').first
                    await textarea.fill('')
                    await textarea.type(instructions, delay=30)
                except Exception:
                    pass  # Instructions field not available
            
            await self.delays.random_delay(0.5, 1.0)
            
            # Click generate
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            # Wait for generation to complete
            await self.page.wait_for_selector(
                'button:has-text("Download"), a:has-text("Download")',
                timeout=300000  # 5 minutes
            )
            
            return {'status': 'generated', 'type': 'audio', 'format': audio_format}
        except Exception as e:
            print(f"Error generating audio: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_audio_error")
            return {'status': 'error', 'error': str(e)}
    
    async def download_audio(self, output_path: str) -> str:
        """
        Download generated audio.
        
        Args:
            output_path: Path to save audio file
            
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
            print(f"Error downloading audio: {e}")
            return None
