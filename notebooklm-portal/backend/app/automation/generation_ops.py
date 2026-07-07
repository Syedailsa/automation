import asyncio
import logging
from playwright.async_api import Page
from .browser_manager import HumanDelays, ScreenshotManager
from .selectors import settings

logger = logging.getLogger(__name__)


class AudioGenerator:
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)

    async def generate_audio(self, instructions: str = "", audio_format: str = "deep-dive") -> dict:
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate audio"), button:has-text("Audio")')
            await self.delays.random_delay(0.5, 1.0)
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            try:
                await self.page.click(f'button:has-text("{audio_format}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception as e:
                logger.debug(f"Could not click audio format button: {e}")
            if instructions:
                try:
                    textarea = self.page.locator('textarea, input[placeholder*="instruction"]').first
                    await textarea.fill('')
                    await textarea.type(instructions, delay=30)
                except Exception as e:
                    logger.debug(f"Could not fill instructions: {e}")
            await self.delays.random_delay(0.5, 1.0)
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            await self.page.wait_for_selector('button:has-text("Download"), a:has-text("Download")', timeout=300000)
            return {'status': 'generated', 'type': 'audio', 'format': audio_format}
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return {'status': 'error', 'error': str(e)}

    async def download_audio(self, output_path: str) -> str:
        try:
            async with self.page.expect_download() as download_info:
                await self.page.click('button:has-text("Download"), a:has-text("Download")')
            download = await download_info.value
            await download.save_as(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return None


class VideoGenerator:
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)

    async def generate_video(self, style: str = "explainer", custom_prompt: str = "") -> dict:
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
            await self.page.wait_for_selector('button:has-text("Download"), a:has-text("Download")', timeout=600000)
            return {'status': 'generated', 'type': 'video', 'style': style}
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return {'status': 'error', 'error': str(e)}


class QuizGenerator:
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)

    async def generate_quiz(self, num_questions: int = 10, difficulty: str = "medium") -> dict:
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate quiz"), button:has-text("Quiz")')
            await self.delays.random_delay(0.5, 1.0)
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            try:
                num_input = self.page.locator('input[type="number"], input[placeholder*="question"]').first
                await num_input.fill('')
                await num_input.type(str(num_questions), delay=50)
            except Exception as e:
                logger.debug(f"Could not set question count: {e}")
            await self.delays.random_delay(0.5, 1.0)
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            await self.page.wait_for_selector('button:has-text("Download"), [data-quiz-generated="true"]', timeout=120000)
            return {'status': 'generated', 'type': 'quiz'}
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return {'status': 'error', 'error': str(e)}


class FlashcardGenerator:
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)

    async def generate_flashcards(self, num_cards: int = 20, difficulty: str = "medium") -> dict:
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
            await self.delays.random_delay(0.5, 1.0)
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            await self.page.wait_for_selector('button:has-text("Download"), [data-flashcards-generated="true"]', timeout=120000)
            return {'status': 'generated', 'type': 'flashcards'}
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return {'status': 'error', 'error': str(e)}


class SlideGenerator:
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)

    async def generate_slides(self, format: str = "detailed", num_slides: int = None) -> dict:
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate slides"), button:has-text("Slides")')
            await self.delays.random_delay(0.5, 1.0)
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            try:
                await self.page.click(f'button:has-text("{format}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception as e:
                logger.debug(f"Could not click slide format button: {e}")
            if num_slides:
                try:
                    num_input = self.page.locator('input[type="number"], input[placeholder*="slide"]').first
                    await num_input.fill('')
                    await num_input.type(str(num_slides), delay=50)
                except Exception as e:
                    logger.debug(f"Could not set slide count: {e}")
            await self.delays.random_delay(0.5, 1.0)
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            await self.page.wait_for_selector('button:has-text("Download"), a:has-text("Download")', timeout=180000)
            return {'status': 'generated', 'type': 'slides', 'format': format}
        except Exception as e:
            logger.error(f"Error generating slides: {e}")
            return {'status': 'error', 'error': str(e)}
