import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Optional

from playwright.async_api import Page, async_playwright

from .browser_manager import HumanDelays, ScreenshotManager
from .selectors import settings


class LoginManager:
    def __init__(self, browser_config):
        self.config = browser_config
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)

    async def manual_login(self, timeout: int = None) -> bool:
        if timeout is None:
            timeout = settings.LOGIN_TIMEOUT
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


class SessionManager:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path

    def save_session(self, storage_state: dict, expires_days: int = 7) -> None:
        data = {
            'storage_state': storage_state,
            'saved_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=expires_days)).isoformat()
        }
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_session(self) -> Optional[dict]:
        if not self.storage_path.exists():
            return None
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            expires_at = datetime.fromisoformat(data['expires_at'])
            if datetime.now() > expires_at:
                print("Session expired, please re-login")
                return None
            return data.get('storage_state')
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading session: {e}")
            return None

    def is_session_valid(self) -> bool:
        session = self.load_session()
        return session is not None


class SessionDetector:
    LOGIN_PAGE_INDICATORS = ['input[type="email"]', 'input[name="identifier"]', '#identifierId']
    AUTHENTICATED_INDICATORS = ['[data-notebook-id]', 'button:has-text("New Notebook")', '[role="main"]']
    CAPTCHA_INDICATORS = ['div.recaptcha', 'iframe[src*="recaptcha"]', 'div.g-recaptcha']

    def __init__(self, page: Page):
        self.page = page

    async def check_session_valid(self) -> bool:
        try:
            if 'accounts.google.com' in self.page.url:
                return False
            for selector in self.AUTHENTICATED_INDICATORS:
                if await self.page.locator(selector).count() > 0:
                    return True
            return False
        except Exception:
            return False

    async def detect_login_page(self) -> bool:
        if 'accounts.google.com' in self.page.url:
            return True
        for selector in self.LOGIN_PAGE_INDICATORS:
            if await self.page.locator(selector).count() > 0:
                return True
        return False

    async def detect_captcha(self) -> bool:
        for indicator in self.CAPTCHA_INDICATORS:
            if await self.page.locator(indicator).count() > 0:
                return True
        return False

    async def get_current_state(self) -> str:
        if await self.detect_captcha():
            return 'captcha'
        elif await self.detect_login_page():
            return 'login_page'
        elif await self.check_session_valid():
            return 'authenticated'
        else:
            return 'unknown'
