#!/bin/bash
# Quick login helper - opens Chromium with remote debugging
# Run this on the server, then connect from your local Chrome

echo "============================================"
echo "  NotebookLM Login Helper"
echo "============================================"
echo ""
echo "Starting Chromium on port 9222..."
echo ""
echo "On your LOCAL machine:"
echo "  1. Open Chrome"
echo "  2. Go to: chrome://inspect/#devices"
echo "  3. Click 'Configure' → add: YOUR_SERVER_IP:9222"
echo "  4. Click 'inspect' on the remote page"
echo "  5. Log into cooddder@gmail.com"
echo "  6. Once on NotebookLM dashboard, run:"
echo "     touch /tmp/notebooklm_login_done.signal"
echo ""
echo "Waiting for login..."

# Create signal file handler
rm -f /tmp/notebooklm_login_done.signal

# Start Chromium with remote debugging
snap run chromium \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --user-data-dir=/tmp/chrome_profile \
  "https://notebooklm.google.com" &

CHROME_PID=$!

# Wait for signal file (check every 2 seconds, max 10 minutes)
for i in $(seq 1 300); do
  if [ -f /tmp/notebooklm_login_done.signal ]; then
    echo ""
    echo "Login signal received! Saving cookies..."
    
    # Use playwright to capture the session from the running chrome
    cd /home/hermes/project1/notebooklm-portal/backend
    /home/hermes/project1/notebooklm-portal/backend/venv/bin/python3 -c "
import asyncio, json
from pathlib import Path
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

async def save():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        contexts = browser.contexts
        if contexts:
            storage = await contexts[0].storage_state()
            data = {
                'storage_state': storage,
                'saved_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            Path('storage/sessions/server_session.json').write_text(json.dumps(data, indent=2))
            print('Session saved!')
        await browser.close()

asyncio.run(save())
"
    rm -f /tmp/notebooklm_login_done.signal
    kill $CHROME_PID 2>/dev/null
    echo "Done! You can close this window."
    exit 0
  fi
  sleep 2
done

echo "Timeout waiting for login."
kill $CHROME_PID 2>/dev/null
