import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext
from ..config.browser_config import BrowserConfig
from ..config.settings import settings
from ..utils.screenshot import ScreenshotManager
from pathlib import Path


class LoginManager:
    """Handles manual Google login flow."""
    
    def __init__(self, browser_config: BrowserConfig):
        self.config = browser_config
        self.screenshot_manager = ScreenshotManager(settings.home_dir)
        
    async def manual_login(self, timeout: int = None) -> bool:
        """
        Open browser for manual Google login.
        Waits for user to complete login.
        
        Args:
            timeout: Maximum time to wait for login (seconds)
        
        Returns:
            bool: True if login successful
        """
        if timeout is None:
            timeout = settings.login_timeout
            
        playwright = await async_playwright().start()
        browser = None
        
        try:
            browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': settings.viewport_width, 'height': settings.viewport_height},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Navigate to NotebookLM
            await page.goto(settings.notebooklm_base_url)
            
            print("=" * 60)
            print("Please complete Google login in the browser window.")
            print("Waiting for login completion...")
            print("=" * 60)
            
            try:
                # Wait for successful login (notebook list appears)
                await page.wait_for_selector(
                    '[data-notebook-id], [role="main"]',
                    timeout=timeout * 1000
                )
                
                # Save storage state
                await context.storage_state(path=str(self.config.storage_file))
                print("Login successful! Storage state saved.")
                return True
                
            except Exception as e:
                print(f"Login timeout or failed: {e}")
                await self.screenshot_manager.capture_error_screenshot(page, "login_failed")
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
    
    async def re_login(self) -> bool:
        """Re-login when session expires."""
        print("Session expired. Starting re-login process...")
        
        # Delete old storage state
        if self.config.storage_file.exists():
            self.config.storage_file.unlink()
        
        return await self.manual_login()
