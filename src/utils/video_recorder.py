from playwright.async_api import BrowserContext, Page
from pathlib import Path
from datetime import datetime
from ..config.settings import settings


class VideoRecorder:
    """Manages video recording for debugging."""
    
    def __init__(self, storage_dir: Path = None):
        if storage_dir is None:
            storage_dir = settings.home_dir
        
        self.storage_dir = storage_dir / "videos"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def get_video_path(self, session_name: str) -> str:
        """
        Get video recording path.
        
        Args:
            session_name: Name/identifier for the session
            
        Returns:
            Path for video recording
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{session_name}_{timestamp}.webm"
        return str(self.storage_dir / filename)
    
    async def start_recording(self, context: BrowserContext, session_name: str) -> str:
        """
        Start video recording.
        
        Args:
            context: Browser context
            session_name: Name/identifier for the session
            
        Returns:
            Path for video recording
        """
        video_path = self.get_video_path(session_name)
        # Video recording is configured at context creation
        # This method returns the path for reference
        return video_path
    
    async def stop_recording(self, page: Page) -> str:
        """
        Stop video recording.
        
        Args:
            page: Playwright page
            
        Returns:
            Status message
        """
        await page.close()
        return "Recording stopped"
    
    def list_recordings(self) -> list[str]:
        """List all video recordings."""
        return [str(f) for f in self.storage_dir.glob("*.webm")]
    
    def cleanup_old_recordings(self, days: int = 7):
        """Delete recordings older than specified days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for filepath in self.storage_dir.glob("*.webm"):
            if filepath.stat().st_mtime < cutoff:
                filepath.unlink()
                print(f"Deleted old recording: {filepath}")
