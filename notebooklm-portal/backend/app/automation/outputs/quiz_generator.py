import asyncio
from playwright.async_api import Page
from ..resilience.human_delays import HumanDelays
from ..utils.screenshot import ScreenshotManager
from ..config.settings import settings


class QuizGenerator:
    """Generates quizzes from notebook content."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.home_dir)
        
    async def generate_quiz(self, num_questions: int = 10, difficulty: str = "medium") -> dict:
        """
        Generate quiz.
        
        Args:
            num_questions: Number of questions to generate
            difficulty: Quiz difficulty (easy, medium, hard)
            
        Returns:
            Dict with status and content
        """
        try:
            # Click generate quiz
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate quiz"), button:has-text("Quiz")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            # Wait for dialog
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            # Set number of questions
            try:
                num_input = self.page.locator('input[type="number"], input[placeholder*="question"]').first
                await num_input.fill('')
                await num_input.type(str(num_questions), delay=50)
            except Exception:
                pass  # Number input not available
            
            # Select difficulty
            try:
                await self.page.click(f'button:has-text("{difficulty}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass  # Difficulty selection not available
            
            await self.delays.random_delay(0.5, 1.0)
            
            # Click generate
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            # Wait for generation
            await self.page.wait_for_selector(
                'button:has-text("Download"), [data-quiz-generated="true"]',
                timeout=120000  # 2 minutes
            )
            
            return {'status': 'generated', 'type': 'quiz'}
        except Exception as e:
            print(f"Error generating quiz: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_quiz_error")
            return {'status': 'error', 'error': str(e)}
    
    async def download_quiz(self, output_path: str, format: str = "json") -> str:
        """
        Download quiz in specified format.
        
        Args:
            output_path: Path to save quiz file
            format: Output format (json, markdown, html)
            
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
            print(f"Error downloading quiz: {e}")
            return None
