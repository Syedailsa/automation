#!/usr/bin/env python3
"""Quick Playwright login - saves cookies to server_session.json."""
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE = Path("/home/hermes/project1/notebooklm-portal/backend/browser-profile")
SIGNAL = Path("/tmp/pw_done.signal")

async def main():
    SIGNAL.unlink(missing_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--remote-debugging-port=9222", "--remote-debugging-address=0.0.0.0", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        await page.goto("https://accounts.google.com/signin")
        print("Chromium running on port 9222")
        print("Log in via Chrome DevTools, then run: touch /tmp/pw_done.signal")
        for i in range(600):
            await asyncio.sleep(2)
            if SIGNAL.exists():
                break
        storage = await context.storage_state()
        data = {
            "storage_state": storage,
            "saved_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        }
        (PROFILE / "server_session.json").write_text(json.dumps(data, indent=2))
        print("Session saved!")
        SIGNAL.unlink(missing_ok=True)
        await browser.close()

asyncio.run(main())
