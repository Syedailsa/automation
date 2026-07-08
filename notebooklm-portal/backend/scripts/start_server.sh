#!/bin/bash
# start_server.sh
# Starts the NotebookLM Portal backend with persistent browser profile.
#
# Usage:
#   bash scripts/start_server.sh
#
# Prerequisites:
#   1. Browser profile must exist: browser-profile/
#   2. If not, run: bash scripts/persistent_login.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
VENV="$BACKEND_DIR/venv/bin"
PROFILE_DIR="$BACKEND_DIR/browser-profile"
PORT=8100
LOG_FILE="/tmp/notebooklm_v2.log"

echo "============================================"
echo "  NotebookLM Portal v2 - Starting"
echo "============================================"
echo ""

# Check if browser profile exists
if [ ! -d "$PROFILE_DIR" ] || [ -z "$(ls -A "$PROFILE_DIR" 2>/dev/null)" ]; then
    echo "ERROR: No browser profile found at $PROFILE_DIR"
    echo ""
    echo "Run this first to set up Google login:"
    echo "  bash scripts/persistent_login.sh"
    echo ""
    exit 1
fi

# Check if server is already running
if curl -s "http://localhost:$PORT/api/health" > /dev/null 2>&1; then
    echo "Server already running on port $PORT"
    echo "Health check:"
    curl -s "http://localhost:$PORT/api/health" | python3 -m json.tool
    exit 0
fi

echo "Starting backend on port $PORT..."
echo "Log file: $LOG_FILE"
echo ""

# Start the server
cd "$BACKEND_DIR"
$VENV/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level info \
    > "$LOG_FILE" 2>&1 &

SERVER_PID=$!
echo "Server started (PID: $SERVER_PID)"
echo ""

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in $(seq 1 30); do
    if curl -s "http://localhost:$PORT/api/health" > /dev/null 2>&1; then
        echo "Server is ready!"
        echo ""
        echo "Health check:"
        curl -s "http://localhost:$PORT/api/health" | python3 -m json.tool
        echo ""
        echo "============================================"
        echo "  Server running at: https://nova2.8.jugaar.ai"
        echo "  API docs: https://nova2.8.jugaar.ai/docs"
        echo "  Health: https://nova2.8.jugaar.ai/api/health"
        echo "============================================"
        exit 0
    fi
    sleep 1
done

echo "Server may still be starting. Check logs: $LOG_FILE"
echo "Or check: curl http://localhost:$PORT/api/health"
