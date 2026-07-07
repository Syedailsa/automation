import asyncio
from playwright.async_api import Page


class ProcessingMonitor:
    """Monitors source processing status."""
    
    PROCESSING_INDICATORS = [
        '[data-status="processing"]',
        'div:has-text("Processing")',
        'div:has-text("Loading")',
    ]
    
    READY_INDICATORS = [
        '[data-status="ready"]',
        '[data-status="completed"]',
    ]
    
    def __init__(self, page: Page):
        self.page = page
    
    async def wait_for_source_ready(self, source_id: str = None, timeout: int = 60) -> bool:
        """Wait for source to finish processing."""
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
