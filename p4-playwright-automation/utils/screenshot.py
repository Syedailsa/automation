from pathlib import Path
from datetime import datetime
from typing import Optional

from playwright.async_api import Page


class ScreenshotManager:
    """Manages screenshots for error handling and debugging."""
    
    def __init__(self, storage_dir: Path = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".notebooklm"
        
        self.storage_dir = storage_dir / "screenshots"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    async def capture_error_screenshot(self, page: Page, error_name: str) -> Optional[str]:
        """Capture screenshot on error."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"error_{error_name}_{timestamp}.png"
        filepath = self.storage_dir / filename
        
        try:
            await page.screenshot(path=str(filepath), full_page=True)
            print(f"Error screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None
