from pathlib import Path

class Settings:
    HOME_DIR = Path.home() / ".notebooklm"
    PROFILES_DIR = HOME_DIR / "profiles"
    SCREENSHOTS_DIR = HOME_DIR / "screenshots"
    VIDEOS_DIR = HOME_DIR / "videos"
    LOGS_DIR = HOME_DIR / "logs"
    HEADLESS = False
    SLOW_MO = 0
    VIEWPORT_WIDTH = 1280
    VIEWPORT_HEIGHT = 720
    NAVIGATION_TIMEOUT = 60000
    ACTION_TIMEOUT = 30000
    LOGIN_TIMEOUT = 300000
    MAX_REQUESTS_PER_MINUTE = 10
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    RETRY_BACKOFF = 2.0
    MIN_TYPING_DELAY = 0.05
    MAX_TYPING_DELAY = 0.15
    MIN_CLICK_DELAY = 0.5
    MAX_CLICK_DELAY = 1.5
    NOTEBOOKLM_BASE_URL = "https://notebooklm.google.com"

settings = Settings()
