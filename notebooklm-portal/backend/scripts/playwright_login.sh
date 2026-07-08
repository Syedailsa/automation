#!/bin/bash
# playwright_login.sh
# Logs into Google using Playwright's chromium (compatible with the server).
# Opens with remote debugging so you can log in from your local Chrome.

PROFILE_DIR="/home/hermes/project1/notebooklm-portal/backend/browser-profile"
VENV="/home/hermes/project1/notebooklm-portal/backend/venv/bin"

echo "============================================"
echo "  Playwright Chromium Login"
echo "============================================"
echo ""
echo "Starting Playwright chromium on port 9222..."
echo ""

# Clean old lock files
rm -f "$PROFILE_DIR/SingletonLock" "$PROFILE_DIR/SingletonSocket" "$PROFILE_DIR/SingletonCookie" 2>/dev/null

# Use Python to launch Playwright chromium with remote debugging
$VENV/python3 -c "
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--remote-debugging-port=9222',
                '--remote-debugging-address=0.0.0.0',
                '--disable-blink-features=AutomationControlled',
            ],
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )
        page = await context.new_page()
        await page.goto('https://accounts.google.com/signin')
        print('Chromium is running on port 9222')
        print('Waiting for you to complete login...')
        
        # Wait for signal file or timeout (10 minutes)
        import time
        for i in range(300):
            await asyncio.sleep(2)
            try:
                with open('/tmp/pw_login_done.signal') as f:
                    break
            except FileNotFoundError:
                continue
        
        # Check if logged in
        url = page.url
        if 'accounts.google.com' not in url:
            # Save session
            storage = await context.storage_state()
            import json
            from pathlib import Path
            from datetime import datetime, timedelta
            
            session_data = {
                'storage_state': storage,
                'saved_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat(),
            }
            Path('$PROFILE_DIR/server_session.json').write_text(json.dumps(session_data, indent=2))
            print('Session saved!')
        else:
            print('Login not completed')
        
        await browser.close()

asyncio.run(main())
" &

CHROME_PID=$!
echo "PID: $CHROME_PID"
echo ""
echo "On your LOCAL machine:"
echo "  1. Open Chrome → chrome://inspect/#devices"
echo "  2. Configure → add: 23.94.206.104:9222"
echo "  3. Click 'inspect' on the remote page"
echo "  4. Log into syedailsaubaid@gmail.com"
echo "  5. Go to notebooklm.google.com"
echo "  6. Once on dashboard, run:"
echo "     touch /tmp/pw_login_done.signal"
echo ""
echo "Waiting for login..."

wait $CHROME_PID
