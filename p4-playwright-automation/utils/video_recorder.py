import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

from playwright.async_api import Page


class VideoRecorder:
    """Records browser sessions for debugging and review."""
    
    def __init__(self, page: Page, output_dir: str = "~/.notebooklm/videos"):
        self.page = page
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.is_recording = False
        self.current_video_path: Optional[Path] = None
        
    async def start_recording(self, filename: Optional[str] = None) -> str:
        """Start recording the browser session."""
        if filename is None:
            filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
        
        self.current_video_path = self.output_dir / filename
        self.is_recording = True
        
        return str(self.current_video_path)
    
    async def stop_recording(self) -> Optional[str]:
        """Stop recording and return the path to the recorded video."""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        return str(self.current_video_path) if self.current_video_path else None
    
    async def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take a screenshot of the current page state."""
        if filename is None:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        screenshot_path = self.output_dir / filename
        await self.page.screenshot(path=str(screenshot_path), full_page=True)
        
        return str(screenshot_path)
    
    async def take_element_screenshot(self, selector: str, filename: Optional[str] = None) -> str:
        """Take a screenshot of a specific element."""
        if filename is None:
            filename = f"element_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        screenshot_path = self.output_dir / filename
        element = self.page.locator(selector)
        await element.screenshot(path=str(screenshot_path))
        
        return str(screenshot_path)
    
    def get_recording_status(self) -> dict:
        """Get the current recording status."""
        return {
            "is_recording": self.is_recording,
            "output_path": str(self.current_video_path) if self.current_video_path else None,
            "output_dir": str(self.output_dir)
        }
