import asyncio
from typing import Optional

from playwright.async_api import Page

from ..resilience import HumanDelays
from ..utils import ScreenshotManager
from ..config import settings


class LoginManager:
    """Handles manual Google login flow."""
    
    def __init__(self, browser_config):
        self.config = browser_config
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
    
    async def manual_login(self, timeout: int = None) -> bool:
        """Open browser for manual Google login."""
        if timeout is None:
            timeout = settings.LOGIN_TIMEOUT
        
        from playwright.async_api import async_playwright
        playwright = await async_playwright().start()
        browser = None
        
        try:
            browser = await playwright.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            
            context = await browser.new_context(
                viewport={'width': settings.VIEWPORT_WIDTH, 'height': settings.VIEWPORT_HEIGHT},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            await page.goto(settings.NOTEBOOKLM_BASE_URL)
            
            print("Please complete Google login in the browser window.")
            
            try:
                await page.wait_for_selector('[data-notebook-id], [role="main"]', timeout=timeout * 1000)
                await context.storage_state(path=str(self.config.storage_file))
                print("Login successful!")
                return True
            except Exception as e:
                print(f"Login timeout or failed: {e}")
                return False
            finally:
                await context.close()
                
        except Exception as e:
            print(f"Error during login: {e}")
            return False
        finally:
            if browser:
                await browser.close()
            await playwright.stop()
