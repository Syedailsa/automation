from pathlib import Path
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings."""
    # Paths
    HOME_DIR: Path = Path.home() / ".notebooklm"
    PROFILES_DIR: Path = Path.home() / ".notebooklm" / "profiles"
    SCREENSHOTS_DIR: Path = Path.home() / ".notebooklm" / "screenshots"
    VIDEOS_DIR: Path = Path.home() / ".notebooklm" / "videos"
    LOGS_DIR: Path = Path.home() / ".notebooklm" / "logs"
    
    # Browser settings
    HEADLESS: bool = False
    SLOW_MO: int = 0
    VIEWPORT_WIDTH: int = 1280
    VIEWPORT_HEIGHT: int = 720
    
    # Timeouts
    NAVIGATION_TIMEOUT: int = 60000
    ACTION_TIMEOUT: int = 30000
    LOGIN_TIMEOUT: int = 300000
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 10
    
    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    RETRY_BACKOFF: float = 2.0
    
    # Delays
    MIN_TYPING_DELAY: float = 0.05
    MAX_TYPING_DELAY: float = 0.15
    MIN_CLICK_DELAY: float = 0.5
    MAX_CLICK_DELAY: float = 1.5
    
    # NotebookLM
    NOTEBOOKLM_BASE_URL: str = "https://notebooklm.google.com"


# Global settings instance
settings = Settings()
