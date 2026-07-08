#!/usr/bin/env python3
"""NotebookLM Server Session Setup

Three ways to set up the server session:

1. ON A MACHINE WITH DISPLAY (local dev, X11 forwarding):
   python3 scripts/setup_notebooklm_session.py

2. ON A HEADLESS SERVER (import from file):
   Step A: Run on your LOCAL machine:
     python3 scripts/setup_notebooklm_session.py --export cookies.json
   Step B: Copy cookies.json to server, then:
     python3 scripts/setup_notebooklm_session.py --import cookies.json

3. ON A HEADLESS SERVER (via SSH X11 forwarding):
   ssh -X root@your-server
   cd /home/hermes/project1/notebooklm-portal/backend
   venv/bin/python3 scripts/setup_notebooklm_session.py
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

SESSION_DIR = Path(__file__).parent.parent / "storage" / "sessions"


async def interactive_login(output_file: str = None):
    """Open a visible browser for manual Google login."""
    from playwright.async_api import async_playwright

    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  NotebookLM Server Session Setup")
    print("=" * 60)
    print()
    print("A browser window will open.")
    print("Log into the Google account you want to use for NotebookLM.")
    print("Once you see the NotebookLM dashboard, come back here.")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
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
        await page.goto("https://notebooklm.google.com")

        print("Waiting for you to log in... (max 5 minutes)")
        print()

        try:
            await page.wait_for_selector(
                '[data-notebook-id], [role="main"], button:has-text("New notebook")',
                timeout=300000,
            )

            storage_state = await context.storage_state()
            session_data = {
                "storage_state": storage_state,
                "saved_at": datetime.utcnow().isoformat(),
                "expires_at": (
                    datetime.utcnow() + timedelta(days=7)
                ).isoformat(),
            }

            if output_file:
                # Export mode: save to user-specified file
                out_path = Path(output_file)
                out_path.write_text(json.dumps(session_data, indent=2))
                print()
                print("=" * 60)
                print("  SUCCESS! Cookies exported.")
                print(f"  Location: {out_path}")
                print()
                print("  Next steps:")
                print(f"  1. Copy this file to your server:")
                print(f"     scp {output_file} root@your-server:/home/hermes/project1/notebooklm-portal/backend/storage/sessions/server_session.json")
                print(f"  2. On the server, verify:")
                print(f"     curl http://localhost:8000/api/health")
                print("=" * 60)
            else:
                # Direct mode: save to server session
                session_file = SESSION_DIR / "server_session.json"
                session_file.write_text(json.dumps(session_data, indent=2))
                print()
                print("=" * 60)
                print("  SUCCESS! Server session saved.")
                print(f"  Location: {session_file}")
                print("  Expires in 7 days.")
                print()
                print("  You can now start the server.")
                print("=" * 60)

        except Exception as e:
            print()
            print(f"ERROR: Login timed out or failed: {e}")
            print("Please try again.")

        finally:
            await context.close()
            await browser.close()


def import_cookies(input_file: str):
    """Import cookies from a JSON file into the server session."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_file = SESSION_DIR / "server_session.json"

    source = Path(input_file)
    if not source.exists():
        print(f"ERROR: File not found: {input_file}")
        sys.exit(1)

    try:
        data = json.loads(source.read_text())
        # Validate structure
        if "storage_state" not in data:
            print("ERROR: Invalid cookie file. Missing 'storage_state' key.")
            sys.exit(1)

        session_file.write_text(json.dumps(data, indent=2))
        print()
        print("=" * 60)
        print("  SUCCESS! Session imported.")
        print(f"  Location: {session_file}")
        print(f"  Saved at: {data.get('saved_at', 'unknown')}")
        print(f"  Expires: {data.get('expires_at', 'unknown')}")
        print()
        print("  You can now start the server.")
        print("=" * 60)

    except json.JSONDecodeError:
        print("ERROR: Invalid JSON file.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="NotebookLM Server Session Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # On a machine with display (opens browser):
  python3 scripts/setup_notebooklm_session.py

  # Export cookies to file (run on local machine):
  python3 scripts/setup_notebooklm_session.py --export cookies.json

  # Import cookies on headless server:
  python3 scripts/setup_notebooklm_session.py --import cookies.json

  # Via SSH X11 forwarding:
  ssh -X root@server
  venv/bin/python3 scripts/setup_notebooklm_session.py
""",
    )
    parser.add_argument(
        "--export",
        metavar="FILE",
        help="Export cookies to a file (for copying to server)",
    )
    parser.add_argument(
        "--import",
        dest="import_file",
        metavar="FILE",
        help="Import cookies from a file (for headless servers)",
    )

    args = parser.parse_args()

    if args.import_file:
        import_cookies(args.import_file)
    else:
        asyncio.run(interactive_login(output_file=args.export))


if __name__ == "__main__":
    main()
