"""Playwright session service — now wraps the single server session.

All NotebookLM operations go through ONE Google account managed by
ServerSessionService. Users never log into Google directly.
"""
import logging
from typing import Optional

from playwright.async_api import Page

from app.services.server_session import server_session

logger = logging.getLogger(__name__)


class PlaywrightSessionService:
    """Thin wrapper that delegates to the server-wide session.

    Kept for backward compatibility with existing imports.
    """

    async def get_authenticated_page(self, user_id: str = "shared") -> Optional[Page]:
        """Get a Playwright page logged into NotebookLM.

        The page uses the server's single Google account.
        Caller MUST close the page's context when done.
        """
        page = await server_session.get_page()
        if page:
            logger.info(f"Providing NotebookLM page for request (user={user_id})")
        else:
            logger.warning(f"Could not get NotebookLM page (user={user_id})")
        return page

    async def close(self):
        await server_session.close()


# Singleton — same API as before, backed by server session
session_service = PlaywrightSessionService()
