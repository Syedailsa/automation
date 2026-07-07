import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    """Application settings."""
    
    # Paths
    home_dir: Path = Path(os.getenv("NOTEBOOKLM_HOME", Path.home() / ".notebooklm"))
    profiles_dir: Path = home_dir / "profiles"
    screenshots_dir: Path = home_dir / "screenshots"
    videos_dir: Path = home_dir / "videos"
    
    # Browser settings
    headless: bool = os.getenv("HEADLESS", "false").lower() == "true"
    slow_mo: int = int(os.getenv("SLOW_MO", "0"))
    viewport_width: int = int(os.getenv("VIEWPORT_WIDTH", "1280"))
    viewport_height: int = int(os.getenv("VIEWPORT_HEIGHT", "720"))
    
    # Timeouts
    navigation_timeout: int = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))
    action_timeout: int = int(os.getenv("ACTION_TIMEOUT", "30000"))
    login_timeout: int = int(os.getenv("LOGIN_TIMEOUT", "300000"))
    
    # Rate limiting
    max_requests_per_minute: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10"))
    
    # Retry settings
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    retry_delay: float = float(os.getenv("RETRY_DELAY", "1.0"))
    retry_backoff: float = float(os.getenv("RETRY_BACKOFF", "2.0"))
    
    # Delays
    min_typing_delay: float = float(os.getenv("MIN_TYPING_DELAY", "0.05"))
    max_typing_delay: float = float(os.getenv("MAX_TYPING_DELAY", "0.15"))
    min_click_delay: float = float(os.getenv("MIN_CLICK_DELAY", "0.5"))
    max_click_delay: float = float(os.getenv("MAX_CLICK_DELAY", "1.5"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # NotebookLM
    notebooklm_base_url: str = "https://notebooklm.google.com"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
