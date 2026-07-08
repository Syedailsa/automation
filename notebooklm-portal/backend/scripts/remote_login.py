#!/usr/bin/env python3
"""Background remote debug login - waits for a signal file."""
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

SESSION_DIR = Path(__file__).parent.parent / "storage" / "sessions"
SIGNAL_FILE = Path("/tmp/notebooklm_login_done.signal")
NOTEBOOKLM_URL = "https://notebooklm.google.com"


async def remote_debug_background():
    from playwright.async_api import async_playwright

    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_file = SESSION_DIR / "server_session.json"

    # Remove old signal file
    SIGNAL_FILE.unlink(missing_ok=True)

    print("Starting Chromium with remote debugging on port 9222...")
    print("Waiting for login completion signal...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--remote-debugging-port=9222",
                "--remote-debugging-address=0.0.0.0",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        page = await context.new_page()
        await page.goto(NOTEBOOKLM_URL)

        # Wait for signal file (check every 2 seconds, max 10 minutes)
        print("Polling for /tmp/notebooklm_login_done.signal ...")
        for i in range(300):  # 300 * 2 = 600 seconds = 10 minutes
            await asyncio.sleep(2)
            if SIGNAL_FILE.exists():
                print("Signal received! Saving session...")
                break
        else:
            print("Timeout waiting for login signal.")
            await context.close()
            await browser.close()
            return False

        # Check if logged in
        current_url = page.url
        if "accounts.google.com" not in current_url:
            storage_state = await context.storage_state()
            session_data = {
                "storage_state": storage_state,
                "saved_at": datetime.utcnow().isoformat(),
                "expires_at": (
                    datetime.utcnow() + timedelta(days=7)
                ).isoformat(),
            }
            session_file.write_text(json.dumps(session_data, indent=2))
            print(f"SUCCESS! Session saved to {session_file}")
            SIGNAL_FILE.unlink(missing_ok=True)
            await context.close()
            await browser.close()
            return True
        else:
            print("Login not completed - still on Google login page.")
            SIGNAL_FILE.unlink(missing_ok=True)
            await context.close()
            await browser.close()
            return False


if __name__ == "__main__":
    asyncio.run(remote_debug_background())
