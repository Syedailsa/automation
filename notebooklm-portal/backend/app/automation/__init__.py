"""NotebookLM automation module."""
from .config import BrowserConfig, Settings, settings
from .browser_manager import BrowserManager
from .auth import LoginManager, SessionManager, SessionDetector
from .notebooks import NotebookManager, SourceManager, ProcessingMonitor
from .outputs import AudioGenerator, VideoGenerator, QuizGenerator, FlashcardGenerator, SlideGenerator, DownloadManager
from .resilience import RetryHandler, RateLimiter, HumanDelays
from .utils import get_logger, ScreenshotManager, VideoRecorder, SelectorRegistry
from .api import NotebookLMAPI, AgentAPI, StatusAPI
from .agent import AgentIntegration, ActionExecutor, ResultFormatter
from .operations import SourceOperations, GenerationOperations, StatusTracker
from .parallel import SessionPool, ParallelSessionManager, SessionHealthMonitor
from .batch import BatchSourceAddition, BatchNotebookCreation, BatchOutputGeneration, BatchDownload
from .monitoring import OperationLogger, HealthCheck, StatusDashboard, AlertingSystem
from .testing import ReliabilityTest, PerformanceTest, IntegrationTest
from .main import NotebookLMAgent

__all__ = [
    "BrowserConfig", "Settings", "settings",
    "BrowserManager",
    "LoginManager", "SessionManager", "SessionDetector",
    "NotebookManager", "SourceManager", "ProcessingMonitor",
    "AudioGenerator", "VideoGenerator", "QuizGenerator", "FlashcardGenerator", "SlideGenerator", "DownloadManager",
    "RetryHandler", "RateLimiter", "HumanDelays",
    "get_logger", "ScreenshotManager", "VideoRecorder", "SelectorRegistry",
    "NotebookLMAPI", "AgentAPI", "StatusAPI",
    "AgentIntegration", "ActionExecutor", "ResultFormatter",
    "SourceOperations", "GenerationOperations", "StatusTracker",
    "SessionPool", "ParallelSessionManager", "SessionHealthMonitor",
    "BatchSourceAddition", "BatchNotebookCreation", "BatchOutputGeneration", "BatchDownload",
    "OperationLogger", "HealthCheck", "StatusDashboard", "AlertingSystem",
    "ReliabilityTest", "PerformanceTest", "IntegrationTest",
    "NotebookLMAgent",
]
