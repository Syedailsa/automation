import asyncio
from playwright.async_api import Page


class ProcessingMonitor:
    """Monitors source processing status."""
    
    # Status indicators
    PROCESSING_INDICATORS = [
        '[data-status="processing"]',
        'div:has-text("Processing")',
        'div:has-text("Loading")',
        'div:has-text("Indexing")',
    ]
    
    READY_INDICATORS = [
        '[data-status="ready"]',
        '[data-status="completed"]',
    ]
    
    ERROR_INDICATORS = [
        '[data-status="error"]',
        'div:has-text("Error")',
        'div:has-text("Failed")',
    ]
    
    def __init__(self, page: Page):
        self.page = page
        
    async def wait_for_source_ready(self, source_id: str = None, timeout: int = 60) -> bool:
        """
        Wait for source to finish processing.
        
        Args:
            source_id: Specific source ID to wait for
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if ready, False if error or timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            if source_id:
                # Check specific source
                source = await self.page.query_selector(f'[data-source-id="{source_id}"]')
                if source:
                    status = await source.get_attribute('data-status')
                    if status in ['ready', 'completed']:
                        return True
                    elif status == 'error':
                        return False
            
            # Check for any processing indicators
            processing = False
            for indicator in self.PROCESSING_INDICATORS:
                if await self.page.locator(indicator).count() > 0:
                    processing = True
                    break
            
            if not processing:
                # Check if any sources are ready
                for indicator in self.READY_INDICATORS:
                    if await self.page.locator(indicator).count() > 0:
                        return True
            
            await asyncio.sleep(1)
        
        return False
    
    async def wait_for_all_sources_ready(self, timeout: int = 120) -> bool:
        """
        Wait for all sources to finish processing.
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if all ready, False if any error or timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Check for any processing indicators
            processing = False
            for indicator in self.PROCESSING_INDICATORS:
                count = await self.page.locator(indicator).count()
                if count > 0:
                    processing = True
                    break
            
            if not processing:
                return True
            
            # Check for errors
            for indicator in self.ERROR_INDICATORS:
                if await self.page.locator(indicator).count() > 0:
                    return False
            
            await asyncio.sleep(2)
        
        return False
    
    async def get_source_status(self, source_id: str) -> str:
        """
        Get status of a specific source.
        
        Args:
            source_id: Source ID
            
        Returns:
            Status string: 'processing', 'ready', 'error', 'unknown'
        """
        source = await self.page.query_selector(f'[data-source-id="{source_id}"]')
        if source:
            status = await source.get_attribute('data-status')
            return status or 'unknown'
        return 'unknown'
