from playwright.async_api import Page
from pathlib import Path
from datetime import datetime
from ..config.settings import settings


class ScreenshotManager:
    """Manages screenshots for error handling and debugging."""
    
    def __init__(self, storage_dir: Path = None):
        if storage_dir is None:
            storage_dir = settings.home_dir
        
        self.storage_dir = storage_dir / "screenshots"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    async def capture_error_screenshot(self, page: Page, error_name: str) -> str:
        """
        Capture screenshot on error.
        
        Args:
            page: Playwright page
            error_name: Name/identifier for the error
            
        Returns:
            Path to saved screenshot
        """
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
    
    async def capture_state_screenshot(self, page: Page, state_name: str) -> str:
        """
        Capture current state screenshot.
        
        Args:
            page: Playwright page
            state_name: Name/identifier for the state
            
        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"state_{state_name}_{timestamp}.png"
        filepath = self.storage_dir / filename
        
        try:
            await page.screenshot(path=str(filepath))
            print(f"State screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None
    
    async def capture_full_page_screenshot(self, page: Page, name: str) -> str:
        """
        Capture full page screenshot.
        
        Args:
            page: Playwright page
            name: Name/identifier for the screenshot
            
        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fullpage_{name}_{timestamp}.png"
        filepath = self.storage_dir / filename
        
        try:
            await page.screenshot(path=str(filepath), full_page=True)
            print(f"Full page screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None
    
    def list_screenshots(self) -> list[str]:
        """List all saved screenshots."""
        return [str(f) for f in self.storage_dir.glob("*.png")]
    
    def cleanup_old_screenshots(self, days: int = 30):
        """Delete screenshots older than specified days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for filepath in self.storage_dir.glob("*.png"):
            if filepath.stat().st_mtime < cutoff:
                filepath.unlink()
                print(f"Deleted old screenshot: {filepath}")
