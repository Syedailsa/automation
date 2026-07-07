import asyncio
import logging
from typing import Dict, Any, List
from ..browser_manager import BrowserManager
from ..utils.selector_registry import selector_registry
from ..resilience import HumanDelays

logger = logging.getLogger(__name__)


class SourceOperations:
    """Handles source operations using BrowserManager and SelectorRegistry."""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.delays = HumanDelays()
        self.selectors = selector_registry

    async def add_url_source(self, notebook_id: str, url: str) -> Dict[str, Any]:
        """Add a URL source using registered selectors with fallbacks."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            await self.delays.click_delay()
            
            add_btn = self.selectors.get_selector("add_source_button")
            await page.click(add_btn)
            await self.delays.random_delay(0.5, 1.0)
            
            url_opt = self.selectors.get_selector("url_source_option")
            await page.click(url_opt)
            await self.delays.random_delay(0.5, 1.0)
            
            url_input = self.selectors.get_selector("url_input")
            input_elem = page.locator(url_input).first
            await input_elem.fill('')
            await input_elem.type(url, delay=30)
            
            await self.delays.random_delay(0.5, 1.0)
            await page.click('button:has-text("Insert"), button:has-text("Add")')
            await asyncio.sleep(2)
            
            return {"status": "success", "source_type": "url", "url": url}
        except Exception as e:
            logger.error(f"Error adding URL source: {e}")
            return {"status": "error", "error": str(e)}

    async def add_text_source(self, notebook_id: str, title: str, content: str) -> Dict[str, Any]:
        """Add a text source using registered selectors."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            await self.delays.click_delay()
            
            add_btn = self.selectors.get_selector("add_source_button")
            await page.click(add_btn)
            await self.delays.random_delay(0.5, 1.0)
            
            text_opt = self.selectors.get_selector("text_source_option")
            await page.click(text_opt)
            await self.delays.random_delay(0.5, 1.0)
            
            title_input = page.locator('input[placeholder*="title"], input[type="text"]').first
            await title_input.fill('')
            await title_input.type(title, delay=50)
            
            textarea = self.selectors.get_selector("textarea")
            content_area = page.locator(textarea).first
            await content_area.fill('')
            await content_area.type(content, delay=20)
            
            await self.delays.random_delay(0.5, 1.0)
            await page.click('button:has-text("Insert"), button:has-text("Add")')
            await asyncio.sleep(2)
            
            return {"status": "success", "source_type": "text", "title": title}
        except Exception as e:
            logger.error(f"Error adding text source: {e}")
            return {"status": "error", "error": str(e)}

    async def add_youtube_source(self, notebook_id: str, url: str) -> Dict[str, Any]:
        """Add a YouTube source using registered selectors."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            await self.delays.click_delay()
            
            add_btn = self.selectors.get_selector("add_source_button")
            await page.click(add_btn)
            await self.delays.random_delay(0.5, 1.0)
            
            yt_opt = self.selectors.get_selector("youtube_source_option")
            await page.click(yt_opt)
            await self.delays.random_delay(0.5, 1.0)
            
            url_input = self.selectors.get_selector("url_input")
            input_elem = page.locator(url_input).first
            await input_elem.fill('')
            await input_elem.type(url, delay=30)
            
            await self.delays.random_delay(0.5, 1.0)
            await page.click('button:has-text("Insert"), button:has-text("Add")')
            await asyncio.sleep(2)
            
            return {"status": "success", "source_type": "youtube", "url": url}
        except Exception as e:
            logger.error(f"Error adding YouTube source: {e}")
            return {"status": "error", "error": str(e)}

    async def add_file_source(self, notebook_id: str, file_path: str) -> Dict[str, Any]:
        """Upload a file source using registered selectors."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            await self.delays.click_delay()
            
            add_btn = self.selectors.get_selector("add_source_button")
            await page.click(add_btn)
            await self.delays.random_delay(0.5, 1.0)
            
            file_opt = self.selectors.get_selector("file_source_option")
            await page.click(file_opt)
            await self.delays.random_delay(0.5, 1.0)
            
            async with page.expect_file_chooser() as fc_info:
                await page.click('button:has-text("Choose file"), button:has-text("Browse")')
            
            file_chooser = await fc_info.value
            await file_chooser.set_files(file_path)
            await asyncio.sleep(3)
            
            return {"status": "success", "source_type": "file", "file_path": file_path}
        except Exception as e:
            logger.error(f"Error uploading file source: {e}")
            return {"status": "error", "error": str(e)}

    async def get_processing_status(self, notebook_id: str, source_id: str) -> Dict[str, Any]:
        """Get source processing status."""
        try:
            page = await self.browser.get_page()
            if not page:
                return {"status": "error", "error": "No page available"}
            
            ready_ind = self.selectors.get_selector("ready_indicator")
            proc_ind = self.selectors.get_selector("processing_indicator")
            
            if await page.locator(ready_ind).count() > 0:
                return {"status": "ready", "source_id": source_id}
            elif await page.locator(proc_ind).count() > 0:
                return {"status": "processing", "source_id": source_id}
            else:
                return {"status": "unknown", "source_id": source_id}
        except Exception as e:
            logger.error(f"Error getting processing status: {e}")
            return {"status": "error", "error": str(e)}

    async def list_sources(self, notebook_id: str) -> List[Dict[str, Any]]:
        """List all sources in the current notebook."""
        try:
            page = await self.browser.get_page()
            if not page:
                return []
            
            sources = await page.query_selector_all('[data-source-id]')
            result = []
            for src in sources:
                src_id = await src.get_attribute('data-source-id')
                title_elem = await src.query_selector('h3, h4, [role="heading"], span')
                title_text = await title_elem.inner_text() if title_elem else "Untitled"
                result.append({'id': src_id, 'title': title_text})
            return result
        except Exception as e:
            logger.error(f"Error listing sources: {e}")
            return []
