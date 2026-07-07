import asyncio
from playwright.async_api import Page

from ..resilience import HumanDelays
from ..utils import ScreenshotManager
from ..config import settings


class SourceManager:
    """Manages NotebookLM source operations."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
    
    async def add_url_source(self, url: str) -> dict:
        """Add a URL as a source."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Add source")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Website"), button:has-text("URL")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            url_input = self.page.locator('input[type="url"], input[placeholder*="url"]').first
            await url_input.fill('')
            await url_input.type(url, delay=30)
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Insert"), button:has-text("Add")')
            
            await asyncio.sleep(2)
            
            return {'status': 'added', 'url': url}
        except Exception as e:
            print(f"Error adding URL source: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def add_text_source(self, title: str, content: str) -> dict:
        """Add text as a source."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Add source")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Text"), button:has-text("Paste")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            title_input = self.page.locator('input[placeholder*="title"], input[type="text"]').first
            await title_input.fill('')
            await title_input.type(title, delay=50)
            
            content_area = self.page.locator('textarea, div[contenteditable="true"]').first
            await content_area.fill('')
            await content_area.type(content, delay=20)
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Insert"), button:has-text("Add")')
            
            await asyncio.sleep(2)
            
            return {'status': 'added', 'title': title}
        except Exception as e:
            print(f"Error adding text source: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def add_youtube_source(self, youtube_url: str) -> dict:
        """Add a YouTube video as a source."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Add source")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("YouTube")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            url_input = self.page.locator('input[type="url"], input[placeholder*="youtube"]').first
            await url_input.fill('')
            await url_input.type(youtube_url, delay=30)
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Insert"), button:has-text("Add")')
            
            await asyncio.sleep(2)
            
            return {'status': 'added', 'url': youtube_url}
        except Exception as e:
            print(f"Error adding YouTube source: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def add_file_source(self, file_path: str) -> dict:
        """Upload a file as a source."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Add source")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Upload"), button:has-text("File")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            async with self.page.expect_file_chooser() as fc_info:
                await self.page.click('button:has-text("Choose file"), button:has-text("Browse")')
            
            file_chooser = await fc_info.value
            await file_chooser.set_files(file_path)
            
            await asyncio.sleep(3)
            
            return {'status': 'uploaded', 'file': file_path}
        except Exception as e:
            print(f"Error uploading file source: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def list_sources(self) -> list[dict]:
        """List all sources in current notebook."""
        await asyncio.sleep(1)
        
        sources = await self.page.query_selector_all('[data-source-id]')
        
        result = []
        for src in sources:
            src_id = await src.get_attribute('data-source-id')
            title_elem = await src.query_selector('h3, h4, [role="heading"], span')
            title_text = await title_elem.inner_text() if title_elem else "Untitled"
            result.append({'id': src_id, 'title': title_text})
        
        return result
