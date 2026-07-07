"""Playwright automation module for NotebookLM."""
from .config import BrowserConfig, Settings
from .auth import LoginManager, SessionManager, SessionDetector
from .notebooks import NotebookManager, SourceManager, ProcessingMonitor
from .outputs import (
    AudioGenerator,
    VideoGenerator,
    QuizGenerator,
    FlashcardGenerator,
    SlideGenerator,
    DownloadManager
)
from .resilience import RetryHandler, RateLimiter, HumanDelays
from .utils import Logger, ScreenshotManager, VideoRecorder, Selectors
from .main import NotebookLMAgent

__all__ = [
    'BrowserConfig',
    'Settings',
    'LoginManager',
    'SessionManager',
    'SessionDetector',
    'NotebookManager',
    'SourceManager',
    'ProcessingMonitor',
    'AudioGenerator',
    'VideoGenerator',
    'QuizGenerator',
    'FlashcardGenerator',
    'SlideGenerator',
    'DownloadManager',
    'RetryHandler',
    'RateLimiter',
    'HumanDelays',
    'Logger',
    'ScreenshotManager',
    'VideoRecorder',
    'Selectors',
    'NotebookLMAgent'
]
