import asyncio
from playwright.async_api import Page
from .browser_manager import HumanDelays, ScreenshotManager
from .selectors import settings


class NotebookManager:
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()

    async def create_notebook(self, title: str) -> str:
        await self.delays.click_delay()
        await self.page.click('button:has-text("New Notebook")')
        await self.page.wait_for_selector('input[placeholder*="title"], input[type="text"]')
        title_input = self.page.locator('input[placeholder*="title"], input[type="text"]').first
        await title_input.fill('')
        await title_input.type(title, delay=50)
        await self.delays.random_delay(0.5, 1.0)
        await self.page.click('button:has-text("Create")')
        await asyncio.sleep(2)
        try:
            notebook_element = await self.page.wait_for_selector(f'[data-notebook-title="{title}"]', timeout=10000)
            notebook_id = await notebook_element.get_attribute('data-notebook-id')
            if notebook_id:
                return notebook_id
        except Exception:
            pass
        return title.lower().replace(' ', '_')

    async def list_notebooks(self) -> list[dict]:
        await asyncio.sleep(1)
        notebooks = await self.page.query_selector_all('[data-notebook-id]')
        result = []
        for nb in notebooks:
            nb_id = await nb.get_attribute('data-notebook-id')
            title_elem = await nb.query_selector('h3, h4, [role="heading"]')
            title_text = await title_elem.inner_text() if title_elem else "Untitled"
            result.append({'id': nb_id, 'title': title_text})
        return result

    async def open_notebook(self, notebook_id: str) -> bool:
        try:
            await self.page.click(f'[data-notebook-id="{notebook_id}"]')
            await self.page.wait_for_load_state('networkidle')
            await self.delays.random_delay(1.0, 2.0)
            return True
        except Exception as e:
            print(f"Error opening notebook: {e}")
            return False

    async def delete_notebook(self, notebook_id: str) -> bool:
        try:
            await self.page.click(f'[data-notebook-id="{notebook_id}"]', button='right')
            await self.delays.random_delay(0.3, 0.5)
            await self.page.click('button:has-text("Delete")')
            await self.delays.random_delay(0.3, 0.5)
            await self.page.click('button:has-text("Confirm"), button:has-text("Yes")')
            await asyncio.sleep(1)
            return True
        except Exception as e:
            print(f"Error deleting notebook: {e}")
            return False


class SourceManager:
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)

    async def add_url_source(self, url: str) -> dict:
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

    async def list_sources(self) -> list[dict]:
        await asyncio.sleep(1)
        sources = await self.page.query_selector_all('[data-source-id]')
        result = []
        for src in sources:
            src_id = await src.get_attribute('data-source-id')
            title_elem = await src.query_selector('h3, h4, [role="heading"], span')
            title_text = await title_elem.inner_text() if title_elem else "Untitled"
            result.append({'id': src_id, 'title': title_text})
        return result


class ProcessingMonitor:
    PROCESSING_INDICATORS = ['[data-status="processing"]', 'div:has-text("Processing")', 'div:has-text("Loading")']
    READY_INDICATORS = ['[data-status="ready"]', '[data-status="completed"]']

    def __init__(self, page: Page):
        self.page = page

    async def wait_for_source_ready(self, source_id: str = None, timeout: int = 60) -> bool:
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            if source_id:
                source = await self.page.query_selector(f'[data-source-id="{source_id}"]')
                if source:
                    status = await source.get_attribute('data-status')
                    if status in ['ready', 'completed']:
                        return True
                    elif status == 'error':
                        return False
            processing = False
            for indicator in self.PROCESSING_INDICATORS:
                if await self.page.locator(indicator).count() > 0:
                    processing = True
                    break
            if not processing:
                for indicator in self.READY_INDICATORS:
                    if await self.page.locator(indicator).count() > 0:
                        return True
            await asyncio.sleep(1)
        return False
