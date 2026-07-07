"""Playwright session service — manages Google login for NotebookLM per user.

For headless servers: uses Google OAuth tokens to authenticate Playwright.
For local dev: opens visible browser for first-time login.
"""
import json
import logging
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

SESSION_DIR = Path(__file__).parent.parent.parent / "storage" / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

NOTEBOOKLM_URL = "https://notebooklm.google.com"
SESSION_EXPIRY_DAYS = 7

# Google OAuth scope needed for NotebookLM
GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


class PlaywrightSessionService:
    """Manages per-user Playwright browser sessions for NotebookLM."""

    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None

    async def _ensure_browser(self):
        if not self._playwright:
            self._playwright = await async_playwright().start()
        if not self._browser:
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )

    def _session_path(self, user_id: str) -> Path:
        return SESSION_DIR / f"{user_id}.json"

    def _load_session(self, user_id: str) -> Optional[dict]:
        path = self._session_path(user_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            expires_at = datetime.fromisoformat(data.get("expires_at", "2000-01-01"))
            if datetime.utcnow() > expires_at:
                path.unlink(missing_ok=True)
                return None
            return data
        except Exception:
            return None

    def _save_session(self, user_id: str, storage_state: dict):
        data = {
            "storage_state": storage_state,
            "saved_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat(),
        }
        self._session_path(user_id).write_text(json.dumps(data))

    async def get_authenticated_page(
        self,
        user_id: str,
        google_access_token: Optional[str] = None,
        google_refresh_token: Optional[str] = None,
    ) -> Optional[Page]:
        """Get a Playwright page logged into NotebookLM for this user.

        Strategy:
        1. Check for saved session cookies (reuse if valid)
        2. If no session, try to authenticate using Google OAuth tokens
        3. If still no auth, return None (user needs to log in via OAuth)
        """
        await self._ensure_browser()

        # 1. Try existing session
        session = self._load_session(user_id)
        if session:
            context = await self._browser.new_context(
                storage_state=session["storage_state"],
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = await context.new_page()
            try:
                await page.goto(NOTEBOOKLM_URL, wait_until="networkidle", timeout=30000)
                if "accounts.google.com" not in page.url:
                    logger.info(f"Session valid for user {user_id}")
                    return page
            except Exception as e:
                logger.warning(f"Session check failed: {e}")
            await context.close()

        # 2. Try Google OAuth token authentication
        if google_access_token:
            page = await self._authenticate_with_oauth(
                user_id, google_access_token, google_refresh_token
            )
            if page:
                return page

        # 3. No auth available
        logger.warning(f"No valid session for user {user_id}")
        return None

    async def _authenticate_with_oauth(
        self,
        user_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
    ) -> Optional[Page]:
        """Try to authenticate Playwright using Google OAuth tokens.

        Strategy: Navigate to Google OAuth with the token, which should
        set the necessary session cookies for NotebookLM.
        """
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        # Set Google auth cookies
        await context.add_cookies([
            {
                "name": "SID",
                "value": access_token[:50] if len(access_token) > 50 else access_token,
                "domain": ".google.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "None",
            },
            {
                "name": "HSID",
                "value": access_token[:25] if len(access_token) > 25 else access_token,
                "domain": ".google.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "None",
            },
            {
                "name": "SSID",
                "value": access_token[-20:] if len(access_token) > 20 else access_token,
                "domain": ".google.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "None",
            },
        ])

        page = await context.new_page()

        try:
            # Try navigating to NotebookLM
            await page.goto(NOTEBOOKLM_URL, wait_until="networkidle", timeout=30000)

            # Check if authenticated
            if "accounts.google.com" not in page.url and "notebooklm.google.com" in page.url:
                logger.info(f"OAuth auth successful for user {user_id}")
                storage_state = await context.storage_state()
                self._save_session(user_id, storage_state)
                return page

            # Try the OAuth consent flow
            logger.info(f"Trying OAuth consent flow for user {user_id}")

            # Navigate to Google OAuth with the token
            from app.config import settings
            oauth_url = (
                f"https://accounts.google.com/o/oauth2/v2/auth"
                f"?client_id={settings.GOOGLE_CLIENT_ID}"
                f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
                f"&response_type=code"
                f"&scope=openid email profile"
                f"&access_type=offline"
                f"&prompt=none"
            )

            await page.goto(oauth_url, wait_until="networkidle", timeout=30000)

            # If we got redirected back to our app, the auth worked
            if "notebooklm.google.com" in page.url or "novaai.8.jugaar.ai" in page.url:
                # Navigate to NotebookLM
                await page.goto(NOTEBOOKLM_URL, wait_until="networkidle", timeout=30000)
                if "accounts.google.com" not in page.url:
                    storage_state = await context.storage_state()
                    self._save_session(user_id, storage_state)
                    return page

        except Exception as e:
            logger.error(f"OAuth auth failed: {e}")

        await context.close()
        return None

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._playwright = None


# Singleton
session_service = PlaywrightSessionService()
