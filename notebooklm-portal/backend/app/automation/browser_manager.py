"""Browser manager module for NotebookLM automation."""
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import logging

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .config import BrowserConfig, settings

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser instances and sessions for NotebookLM automation."""
    
    def __init__(self, profile_name: str = "default"):
        self.profile_name = profile_name
        self.config = BrowserConfig(profile_name)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize browser and load session."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.config.create_browser(self.playwright)
            self.context = await self.config.create_context(self.browser)
            self.page = await self.context.new_page()
            self._is_initialized = True
            logger.info(f"Browser initialized for profile: {self.profile_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def close(self):
        """Close browser and cleanup resources."""
        try:
            if self.context:
                await self.config.save_session(self.context)
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self._is_initialized = False
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    @property
    def is_initialized(self) -> bool:
        return self._is_initialized
    
    async def navigate(self, url: str) -> bool:
        """Navigate to a URL."""
        try:
            if not self.page:
                logger.error("No page available")
                return False
            await self.page.goto(url, timeout=settings.NAVIGATION_TIMEOUT)
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    async def get_page(self) -> Optional[Page]:
        """Get current page instance."""
        return self.page
    
    async def take_screenshot(self, name: str = None) -> Optional[str]:
        """Take a screenshot of current page."""
        try:
            if not self.page:
                return None
            if name is None:
                name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = settings.SCREENSHOTS_DIR / name
            await self.page.screenshot(path=str(screenshot_path))
            return str(screenshot_path)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    async def execute_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a browser operation."""
        try:
            op_type = operation.get("type")
            if op_type == "navigate":
                url = operation.get("url")
                success = await self.navigate(url)
                return {"status": "success" if success else "error", "url": url}
            elif op_type == "screenshot":
                path = await self.take_screenshot(operation.get("name"))
                return {"status": "success" if path else "error", "path": path}
            else:
                return {"status": "error", "message": f"Unknown operation type: {op_type}"}
        except Exception as e:
            logger.error(f"Operation execution failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def test_operation(self) -> Dict[str, Any]:
        """Test a basic browser operation."""
        try:
            if not self.page:
                return {"status": "error", "message": "No page available"}
            await self.page.goto("about:blank")
            return {"status": "success", "message": "Test operation completed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
