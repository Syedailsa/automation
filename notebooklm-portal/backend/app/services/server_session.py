"""Server-side NotebookLM session — ONE Google account for all users.

Uses Playwright's own chromium with a persistent profile directory.
No snap chromium dependency. Browser launched lazily on first request.
"""
import logging
import time
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

PW_PROFILE = "/home/hermes/project1/notebooklm-portal/backend/browser-pw-profile"
NOTEBOOKLM_URL = "https://notebooklm.google.com"


class ServerSessionService:
    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """No-op on startup. Browser launched on first request."""
        Path(PW_PROFILE).mkdir(parents=True, exist_ok=True)
        self._initialized = True
        logger.info("Server session ready (lazy init)")
        return True

    async def _ensure_browser(self):
        if self._browser and self._browser.is_connected():
            return

        # Kill any leftover chromium processes
        import subprocess
        subprocess.run(["pkill", "-9", "-f", "chromium"], capture_output=True)
        time.sleep(1)

        # Start Playwright with persistent context
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        # Load persistent context with saved profile (50 Google cookies)
        storage_state = self._get_storage_state()
        if storage_state:
            logger.info(f"Loading storage state from {storage_state}")
        else:
            logger.warning("No storage state found - NotebookLM will require login")
        
        self._context = await self._browser.new_context(
            storage_state=storage_state,
            viewport={"width": 1280, "height": 720},
        )

        logger.info("Playwright browser launched (persistent profile)")

    def _get_storage_state(self) -> Optional[str]:
        """Load saved storage state if it exists."""
        state_file = Path(PW_PROFILE) / "storage_state.json"
        if state_file.exists():
            return str(state_file)
        return None

    async def _save_storage_state(self):
        """Save storage state for next launch."""
        if self._context:
            state_file = Path(PW_PROFILE) / "storage_state.json"
            await self._context.storage_state(path=str(state_file))
            logger.info("Saved storage state")

    async def get_page(self) -> Optional[Page]:
        try:
            await self._ensure_browser()
            page = await self._context.new_page()
            await page.goto(NOTEBOOKLM_URL, wait_until="networkidle", timeout=30000)

            if "accounts.google.com" not in page.url:
                logger.info("NotebookLM loaded successfully")
                return page

            logger.warning("Session expired or not logged in")
            await page.close()
            return None
        except Exception as e:
            logger.error(f"Failed to get page: {e}")
            self._browser = None
            return None

    async def is_session_valid(self) -> bool:
        """Check if we have a saved session."""
        state_file = Path(PW_PROFILE) / "storage_state.json"
        return state_file.exists()

    async def login_google(self, email: str, password: str) -> bool:
        """Login to Google account via Playwright. Call this once to establish session."""
        try:
            await self._ensure_browser()
            page = await self._context.new_page()

            # Navigate to Google login
            await page.goto("https://accounts.google.com/signin", wait_until="networkidle", timeout=30000)

            # Enter email
            await page.fill('input[type="email"]', email)
            await page.click('#identifierNext')
            time.sleep(3)

            # Enter password
            await page.fill('input[type="password"]', password)
            await page.click('#passwordNext')
            time.sleep(5)

            # Check if login succeeded
            if "accounts.google.com" not in page.url:
                logger.info("Google login successful")
                await self._save_storage_state()
                await page.close()
                return True
            else:
                logger.error("Google login failed - still on login page")
                await page.close()
                return False
        except Exception as e:
            logger.error(f"Google login failed: {e}")
            return False

    async def close(self):
        if self._browser:
            try:
                await self._save_storage_state()
                await self._browser.close()
            except Exception:
                pass
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
        self._browser = None
        self._context = None
        self._playwright = None


server_session = ServerSessionService()
