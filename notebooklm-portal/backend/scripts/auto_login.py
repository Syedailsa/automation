#!/usr/bin/env python3
"""Automated Google Login for NotebookLM Server Session

Logs into Google automatically using email/password.
If 2FA or CAPTCHA is required, it pauses and gives you options.

Usage:
    # Basic (email + password):
    python3 scripts/auto_login.py --email you@gmail.com --password yourpassword

    # With 2FA code:
    python3 scripts/auto_login.py --email you@gmail.com --password yourpassword --totp 123456

    # Remote debugging mode (manual login via Chrome DevTools):
    python3 scripts/auto_login.py --remote-debug
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

SESSION_DIR = Path(__file__).parent.parent / "storage" / "sessions"
NOTEBOOKLM_URL = "https://notebooklm.google.com"
GOOGLE_LOGIN_URL = "https://accounts.google.com/signin"


async def auto_login(email: str, password: str, totp: str = None):
    """Automate Google login with email/password."""
    from playwright.async_api import async_playwright

    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_file = SESSION_DIR / "server_session.json"

    print("=" * 60)
    print("  Automated Google Login for NotebookLM")
    print("=" * 60)
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
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

        try:
            # Step 1: Go to Google login
            print("[1/5] Navigating to Google login...")
            await page.goto(GOOGLE_LOGIN_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Step 2: Enter email
            print("[2/5] Entering email...")
            email_input = page.locator('input[type="email"], input[name="identifier"], #identifierId')
            await email_input.wait_for(timeout=10000)
            await email_input.fill(email)
            await page.wait_for_timeout(500)

            # Click Next
            next_btn = page.locator('#identifierNext')
            await next_btn.click()
            await page.wait_for_timeout(3000)

            # Step 3: Enter password
            print("[3/5] Entering password...")
            password_input = page.locator('input[type="password"], input[name="password"]')
            
            # Wait for password field to appear (with timeout for potential CAPTCHA)
            try:
                await password_input.wait_for(timeout=10000)
            except Exception:
                # Check if we hit CAPTCHA or phone verification
                current_url = page.url
                page_text = await page.inner_text("body")
                
                if "verify" in page_text.lower() or "confirm" in page_text.lower():
                    print()
                    print("  ⚠ Google is asking for verification.")
                    print("  This usually means:")
                    print("  - 2FA is enabled on this account")
                    print("  - Google detected automated login")
                    print()
                    print("  Options:")
                    print("  1. Disable 2FA on this Google account temporarily")
                    print("  2. Use --remote-debug mode for manual login")
                    print("  3. Try a different Google account")
                    print()
                    await context.close()
                    await browser.close()
                    return False

                if "captcha" in page_text.lower() or "robot" in page_text.lower():
                    print()
                    print("  ⚠ Google CAPTCHA detected.")
                    print("  Automated login blocked by Google.")
                    print()
                    print("  Use --remote-debug mode for manual login:")
                    print("  python3 scripts/auto_login.py --remote-debug")
                    print()
                    await context.close()
                    await browser.close()
                    return False

                print(f"  Unexpected page: {current_url}")
                await context.close()
                await browser.close()
                return False

            await password_input.fill(password)
            await page.wait_for_timeout(500)

            # Click Next
            next_btn = page.locator('#passwordNext')
            await next_btn.click()
            await page.wait_for_timeout(5000)

            # Step 4: Handle 2FA if needed
            print("[4/5] Checking for 2FA...")
            page_text = await page.inner_text("body")
            
            if "verification code" in page_text.lower() or "authenticator" in page_text.lower():
                if totp:
                    print("  Entering 2FA code...")
                    code_input = page.locator('input[type="tel"], input[type="text"], input[name="totpPin"]')
                    await code_input.wait_for(timeout=5000)
                    await code_input.fill(totp)
                    await page.wait_for_timeout(500)
                    
                    verify_btn = page.locator('button:has-text("Verify"), button:has-text("Next")')
                    await verify_btn.click()
                    await page.wait_for_timeout(5000)
                else:
                    print()
                    print("  ⚠ 2FA is required for this account.")
                    print("  Run with --totp YOUR_CODE")
                    print("  Or disable 2FA temporarily.")
                    print()
                    await context.close()
                    await browser.close()
                    return False

            # Step 5: Navigate to NotebookLM
            print("[5/5] Navigating to NotebookLM...")
            await page.goto(NOTEBOOKLM_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            # Check if we're logged in
            current_url = page.url
            if "accounts.google.com" in current_url:
                print()
                print("  ✗ Login failed — still on Google login page.")
                print("  Check your email/password and try again.")
                print()
                await context.close()
                await browser.close()
                return False

            # Check for NotebookLM dashboard
            try:
                await page.wait_for_selector(
                    '[data-notebook-id], [role="main"], button:has-text("New notebook")',
                    timeout=15000,
                )
            except Exception:
                print("  ⚠ Could not confirm NotebookLM dashboard.")
                print("  Continuing anyway — cookies may still work.")

            # Save session
            storage_state = await context.storage_state()
            session_data = {
                "storage_state": storage_state,
                "saved_at": datetime.utcnow().isoformat(),
                "expires_at": (
                    datetime.utcnow() + timedelta(days=7)
                ).isoformat(),
            }
            session_file.write_text(json.dumps(session_data, indent=2))

            print()
            print("=" * 60)
            print("  ✓ SUCCESS! Logged in and session saved.")
            print(f"  Location: {session_file}")
            print("  Expires in 7 days.")
            print()
            print("  Start the server with:")
            print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
            print("=" * 60)

            await context.close()
            await browser.close()
            return True

        except Exception as e:
            print()
            print(f"  ✗ ERROR: {e}")
            print()
            print("  Use --remote-debug mode for manual login:")
            print("  python3 scripts/auto_login.py --remote-debug")
            print()
            await context.close()
            await browser.close()
            return False


async def remote_debug_login():
    """Start Chromium with remote debugging for manual login."""
    from playwright.async_api import async_playwright

    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_file = SESSION_DIR / "server_session.json"

    print("=" * 60)
    print("  Remote Debug Login Mode")
    print("=" * 60)
    print()
    print("Starting Chromium with remote debugging...")
    print()

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

        print("  Chromium is running with remote debugging on port 9222.")
        print()
        print("  To complete login:")
        print("  1. Open Chrome on your LOCAL machine")
        print("  2. Go to: chrome://inspect/#devices")
        print("  3. Click 'Configure' and add: your-server-ip:9222")
        print("  4. You should see the remote page — click 'inspect'")
        print("  5. Log into Google in the remote browser window")
        print("  6. Once on NotebookLM dashboard, come back here")
        print()
        print("  OR use SSH port forwarding:")
        print("  ssh -L 9222:localhost:9222 root@your-server")
        print("  Then open: chrome://inspect/#devices")
        print()
        input("  Press ENTER when you've completed login... ")

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

            print()
            print("=" * 60)
            print("  ✓ SUCCESS! Session saved.")
            print(f"  Location: {session_file}")
            print("=" * 60)
        else:
            print()
            print("  ✗ Login not completed. Try again.")

        await context.close()
        await browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Automated Google Login for NotebookLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic login (email + password):
  python3 scripts/auto_login.py --email you@gmail.com --password yourpassword

  # With 2FA code:
  python3 scripts/auto_login.py --email you@gmail.com --password yourpassword --totp 123456

  # Remote debugging (manual login via Chrome DevTools):
  python3 scripts/auto_login.py --remote-debug
""",
    )
    parser.add_argument("--email", help="Google account email")
    parser.add_argument("--password", help="Google account password")
    parser.add_argument("--totp", help="2FA/TOTP code (if 2FA is enabled)")
    parser.add_argument(
        "--remote-debug",
        action="store_true",
        help="Start Chromium with remote debugging for manual login",
    )

    args = parser.parse_args()

    if args.remote_debug:
        asyncio.run(remote_debug_login())
    elif args.email and args.password:
        asyncio.run(auto_login(args.email, args.password, args.totp))
    else:
        parser.print_help()
        print()
        print("ERROR: Provide --email and --password, or use --remote-debug")
        sys.exit(1)


if __name__ == "__main__":
    main()
