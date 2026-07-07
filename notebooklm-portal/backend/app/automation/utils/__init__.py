from .logger import get_logger
from .screenshot import ScreenshotManager
from .video_recorder import VideoRecorder
from .selector_registry import SelectorRegistry
from .screenshot_comparator import ScreenshotComparator, ScreenshotUploader
from .selector_manager import SelectorAutoDetector, SelectorTester, SelectorVersionManager
from .memory_optimizer import MemoryOptimizer, CacheManager, CachedBrowserOperation
