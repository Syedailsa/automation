#!/bin/bash
# persistent_login.sh
# Opens Chrome with a persistent profile for manual Google login.
# After login, the profile is saved and reused by the server.
#
# Usage:
#   bash scripts/persistent_login.sh
#
# Then:
#   1. Chrome opens with the persistent profile
#   2. Log into nova.ai.project@gmail.com
#   3. Navigate to notebooklm.google.com
#   4. Once logged in, close Chrome
#   5. The profile is saved automatically

PROFILE_DIR="/home/hermes/project1/notebooklm-portal/backend/browser-profile"
PORT=9222

echo "============================================"
echo "  Persistent Browser Login"
echo "============================================"
echo ""
echo "Profile directory: $PROFILE_DIR"
echo "Remote debugging: port $PORT"
echo ""
echo "Chrome will open with a persistent profile."
echo "Log into your Google account, then close Chrome."
echo "The profile will be saved automatically."
echo ""

# Kill any existing Chrome instances
pkill -f "chrome.*browser-profile" 2>/dev/null
sleep 1

# Launch Chrome with persistent profile
snap run chromium \
  --no-sandbox \
  --disable-gpu \
  --remote-debugging-port=$PORT \
  --remote-debugging-address=0.0.0.0 \
  --user-data-dir="$PROFILE_DIR" \
  --disable-blink-features=AutomationControlled \
  --window-size=1280,720 \
  "https://accounts.google.com/signin" &

CHROME_PID=$!
echo "Chrome started (PID: $CHROME_PID)"
echo ""
echo "On your LOCAL machine:"
echo "  1. Open Chrome → go to chrome://inspect/#devices"
echo "  2. Click 'Configure' → add: YOUR_SERVER_IP:$PORT"
echo "  3. Click 'inspect' on the remote page"
echo "  4. Log into nova.ai.project@gmail.com"
echo "  5. Navigate to notebooklm.google.com"
echo "  6. Once on NotebookLM dashboard, close Chrome on the server"
echo ""
echo "To close Chrome on server: kill $CHROME_PID"
echo "Or: pkill -f 'chrome.*browser-profile'"
echo ""
echo "Waiting for Chrome to close..."
wait $CHROME_PID
echo ""
echo "Chrome closed. Profile saved to: $PROFILE_DIR"
echo "You can now start the server."
