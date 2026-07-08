#!/usr/bin/env python3
"""Google login with device verification support.

Keeps browser open on port 9222 after entering credentials.
Device verification happens externally. Once approved, run this
script again or the session will be saved.

Usage:
  cd /home/hermes/project1/notebooklm-portal/backend
  source venv/bin/activate
  DISPLAY=:99 python scripts/pw_google_login_interactive.py
"""
import asyncio
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright

PROFILE_DIR = "/home/hermes/project1/notebooklm-portal/backend/browser-pw-profile"
GOOGLE_EMAIL = "YOUR_EMAIL_HERE"
GOOGLE_PASSWORD = "YOUR_PASSWORD_HERE"

# Set to True to skip login if already logged in
SKIP_IF_LOGGED_IN = True


async def main():
    Path(PROFILE_DIR).mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--remote-debugging-port=9222",
                "--remote-debugging-address=127.0.0.1",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        print("Step 1: Navigating to NotebookLM to check session...")
        await page.goto("https://notebooklm.google.com", wait_until="networkidle", timeout=30000)

        # Check if already logged in
        if "accounts.google.com" not in page.url:
            print("ALREADY LOGGED IN! Saving session...")
            state_file = Path(PROFILE_DIR) / "storage_state.json"
            await context.storage_state(path=str(state_file))
            print(f"Session saved to {state_file}")
            await browser.close()
            return True

        print("Not logged in. Starting login flow...")

        # Navigate to Google sign-in
        print("Step 2: Navigating to Google sign-in...")
        await page.goto("https://accounts.google.com/signin", wait_until="networkidle", timeout=30000)

        # Enter email
        print("Step 3: Entering email...")
        email_input = await page.wait_for_selector('input[name="identifier"]', timeout=10000)
        await email_input.fill(GOOGLE_EMAIL)
        await page.click("#identifierNext")
        await asyncio.sleep(4)

        if "rejected" in page.url:
            print("ERROR: Google blocked the login. Try again later.")
            await browser.close()
            return False

        # Enter password
        print("Step 4: Entering password...")
        pw_input = await page.wait_for_selector('input[type="password"]', timeout=10000)
        await pw_input.fill(GOOGLE_PASSWORD)
        await page.click("#passwordNext")
        await asyncio.sleep(5)

        print(f"Current URL: {page.url}")

        # Check if device verification is needed
        if "challenge" in page.url:
            print("\n=== DEVICE VERIFICATION REQUIRED ===")
            print("Google is asking to verify this device.")
            print("Check your phone for a prompt from Google.")
            print("Approve the prompt, then re-run this script.")
            print("The browser will stay open for 5 minutes.")
            print("=====================================\n")
            print("Browser accessible at: http://127.0.0.1:9222")

            # Keep browser open for 5 minutes
            await asyncio.sleep(300)
            print("Timeout reached. Closing browser.")
            await browser.close()
            return False

        # If we're not on Google login, we're good
        if "accounts.google.com" not in page.url:
            print("LOGIN SUCCESSFUL!")
            await page.goto("https://notebooklm.google.com", wait_until="networkidle", timeout=30000)
            print(f"NotebookLM loaded: {page.url}")

            state_file = Path(PROFILE_DIR) / "storage_state.json"
            await context.storage_state(path=str(state_file))
            print(f"Session saved to {state_file}")
            await browser.close()
            return True
        else:
            print(f"Login may have failed. URL: {page.url}")
            await browser.close()
            return False


if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
