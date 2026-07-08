#!/usr/bin/env python3
"""Login to Google via Playwright and save session state.

Run this once to establish the Google session for NotebookLM.
After login, the session is saved to browser-pw-profile/storage_state.json
and the server will use it for all NotebookLM operations.

Usage:
  cd /home/hermes/project1/notebooklm-portal/backend
  source venv/bin/activate
  python scripts/pw_google_login.py
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright

PROFILE_DIR = "/home/hermes/project1/notebooklm-portal/backend/browser-pw-profile"
GOOGLE_EMAIL = "YOUR_EMAIL_HERE"
GOOGLE_PASSWORD = "YOUR_PASSWORD_HERE"


async def main():
    Path(PROFILE_DIR).mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        print("Navigating to Google sign-in...")
        await page.goto("https://accounts.google.com/signin", wait_until="networkidle", timeout=30000)
        print(f"Current URL: {page.url}")

        # Enter email
        print("Entering email...")
        try:
            # Wait for the page to fully render
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            
            # Try multiple selectors
            selectors = [
                'input[type="email"]',
                'input[name="identifier"]',
                '#identifierId',
            ]
            email_input = None
            for sel in selectors:
                try:
                    email_input = await page.wait_for_selector(sel, timeout=5000)
                    if email_input:
                        print(f"Found email input with selector: {sel}")
                        break
                except:
                    continue
            
            if not email_input:
                print("Could not find email input field")
                print(f"Page title: {await page.title()}")
                content = await page.content()
                print(f"Content length: {len(content)}")
                # Try to find any input
                inputs = await page.query_selector_all("input")
                print(f"Found {len(inputs)} input elements")
                for i, inp in enumerate(inputs):
                    inp_type = await inp.get_attribute("type")
                    inp_name = await inp.get_attribute("name")
                    inp_id = await inp.get_attribute("id")
                    print(f"  Input {i}: type={inp_type}, name={inp_name}, id={inp_id}")
                await browser.close()
                return False
            
            await email_input.fill(GOOGLE_EMAIL)
            await page.click('#identifierNext')
            await asyncio.sleep(4)
            print(f"After email: {page.url}")
        except Exception as e:
            print(f"Email step failed: {e}")
            print(f"Page content snippet: {(await page.content())[:500]}")
            await browser.close()
            return False

        # Enter password
        print("Entering password...")
        try:
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            
            # Try multiple selectors
            selectors = [
                'input[type="password"]',
                'input[name="Passwd"]',
                '#password',
            ]
            pw_input = None
            for sel in selectors:
                try:
                    pw_input = await page.wait_for_selector(sel, timeout=5000)
                    if pw_input:
                        print(f"Found password input with selector: {sel}")
                        break
                except:
                    continue
            
            if not pw_input:
                print("Could not find password input field")
                print(f"Current URL: {page.url}")
                await browser.close()
                return False
            
            await pw_input.fill(GOOGLE_PASSWORD)
            await page.click('#passwordNext')
            await asyncio.sleep(5)
            print(f"After password: {page.url}")
        except Exception as e:
            print(f"Password step failed: {e}")
            # Maybe there's a CAPTCHA or different page
            content = await page.content()
            print(f"Page content snippet: {content[:500]}")
            await browser.close()
            return False

        # Check if we need 2FA
        if "challenge" in page.url or "signin/v2" in page.url:
            print("WARNING: 2FA or additional verification required.")
            print("This script cannot handle 2FA automatically.")
            print("Please log in manually via the server session.")
            await browser.close()
            return False

        # Check if login succeeded
        if "accounts.google.com" not in page.url:
            print("Login successful!")

            # Navigate to NotebookLM to verify
            print("Navigating to NotebookLM...")
            await page.goto("https://notebooklm.google.com", wait_until="networkidle", timeout=30000)
            print(f"NotebookLM URL: {page.url}")

            # Save session state
            state_file = Path(PROFILE_DIR) / "storage_state.json"
            await context.storage_state(path=str(state_file))
            print(f"Session saved to {state_file}")
            await browser.close()
            return True
        else:
            print(f"Login may have failed. URL: {page.url}")
            content = await page.content()
            print(f"Page content snippet: {content[:500]}")
            await browser.close()
            return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
