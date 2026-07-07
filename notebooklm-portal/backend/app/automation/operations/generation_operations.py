import asyncio
import logging
from typing import Dict, Any
from ..browser_manager import BrowserManager
from ..utils.selector_registry import selector_registry
from ..resilience import HumanDelays

logger = logging.getLogger(__name__)


class GenerationOperations:
    """Handles generation operations using BrowserManager and SelectorRegistry."""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.delays = HumanDelays()
        self.selectors = selector_registry

    async def generate_audio(self, notebook_id: str, instructions: str = "") -> Dict[str, Any]:
        """Generate audio overview using registered selectors."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            await self.delays.click_delay()
            
            audio_btn = self.selectors.get_selector("generate_audio_button")
            await page.click(audio_btn)
            await self.delays.random_delay(0.5, 1.0)
            
            await page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            if instructions:
                try:
                    textarea = self.selectors.get_selector("textarea")
                    input_elem = page.locator(textarea).first
                    await input_elem.fill('')
                    await input_elem.type(instructions, delay=30)
                except Exception as e:
                    logger.debug(f"Could not fill instructions: {e}")
            
            await self.delays.random_delay(0.5, 1.0)
            await page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await page.wait_for_selector('button:has-text("Download"), a:has-text("Download")', timeout=300000)
            
            return {"status": "success", "type": "audio", "notebook_id": notebook_id}
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return {"status": "error", "error": str(e)}

    async def generate_video(self, notebook_id: str, style: str = "explainer") -> Dict[str, Any]:
        """Generate video overview using registered selectors."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            await self.delays.click_delay()
            
            video_btn = self.selectors.get_selector("generate_video_button")
            await page.click(video_btn)
            await self.delays.random_delay(0.5, 1.0)
            
            await page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            await self.delays.random_delay(0.5, 1.0)
            await page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await page.wait_for_selector('button:has-text("Download"), a:has-text("Download")', timeout=600000)
            
            return {"status": "success", "type": "video", "notebook_id": notebook_id}
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return {"status": "error", "error": str(e)}

    async def generate_quiz(self, notebook_id: str, num_questions: int = 10) -> Dict[str, Any]:
        """Generate quiz using registered selectors."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            await self.delays.click_delay()
            
            quiz_btn = self.selectors.get_selector("generate_quiz_button")
            await page.click(quiz_btn)
            await self.delays.random_delay(0.5, 1.0)
            
            await page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                num_input = page.locator('input[type="number"], input[placeholder*="question"]').first
                await num_input.fill('')
                await num_input.type(str(num_questions), delay=50)
            except Exception as e:
                logger.debug(f"Could not set question count: {e}")
            
            await self.delays.random_delay(0.5, 1.0)
            await page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await page.wait_for_selector('button:has-text("Download"), [data-quiz-generated="true"]', timeout=120000)
            
            return {"status": "success", "type": "quiz", "notebook_id": notebook_id}
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return {"status": "error", "error": str(e)}

    async def generate_flashcards(self, notebook_id: str, num_cards: int = 20) -> Dict[str, Any]:
        """Generate flashcards using registered selectors."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            await self.delays.click_delay()
            
            flashcard_btn = self.selectors.get_selector("generate_flashcards_button")
            await page.click(flashcard_btn)
            await self.delays.random_delay(0.5, 1.0)
            
            await page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                num_input = page.locator('input[type="number"], input[placeholder*="card"]').first
                await num_input.fill('')
                await num_input.type(str(num_cards), delay=50)
            except Exception as e:
                logger.debug(f"Could not set card count: {e}")
            
            await self.delays.random_delay(0.5, 1.0)
            await page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await page.wait_for_selector('button:has-text("Download"), [data-flashcards-generated="true"]', timeout=120000)
            
            return {"status": "success", "type": "flashcards", "notebook_id": notebook_id}
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return {"status": "error", "error": str(e)}

    async def generate_slides(self, notebook_id: str, format: str = "detailed") -> Dict[str, Any]:
        """Generate slides using registered selectors."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            await self.delays.click_delay()
            
            slides_btn = self.selectors.get_selector("generate_slides_button")
            await page.click(slides_btn)
            await self.delays.random_delay(0.5, 1.0)
            
            await page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            await self.delays.random_delay(0.5, 1.0)
            await page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await page.wait_for_selector('button:has-text("Download"), a:has-text("Download")', timeout=180000)
            
            return {"status": "success", "type": "slides", "notebook_id": notebook_id}
        except Exception as e:
            logger.error(f"Error generating slides: {e}")
            return {"status": "error", "error": str(e)}

    async def get_generation_status(self, notebook_id: str, output_type: str) -> Dict[str, Any]:
        """Get generation status."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            ready_ind = self.selectors.get_selector("ready_indicator")
            proc_ind = self.selectors.get_selector("processing_indicator")
            
            if await page.locator(ready_ind).count() > 0:
                return {"status": "ready", "type": output_type, "notebook_id": notebook_id}
            elif await page.locator(proc_ind).count() > 0:
                return {"status": "processing", "type": output_type, "notebook_id": notebook_id}
            else:
                return {"status": "unknown", "type": output_type, "notebook_id": notebook_id}
        except Exception as e:
            logger.error(f"Error getting generation status: {e}")
            return {"status": "error", "error": str(e)}
