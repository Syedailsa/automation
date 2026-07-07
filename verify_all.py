#!/usr/bin/env python3
"""
NotebookLM Playwright Agent - Complete Verification Script
Tests all modules and functions to ensure everything works properly.
"""

import asyncio
import sys
import os
import traceback
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class VerificationRunner:
    """Runs comprehensive verification tests."""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "PASS": "✅", "FAIL": "❌", "ERROR": "💥", "TEST": "🧪"}
        icon = icons.get(level, "•")
        print(f"[{timestamp}] {icon} {message}")
        
    def record_result(self, test_name: str, passed: bool, error: str = None):
        """Record test result."""
        self.results.append({
            "name": test_name,
            "passed": passed,
            "error": error,
            "timestamp": datetime.now()
        })
        if passed:
            self.passed += 1
            self.log(f"{test_name}", "PASS")
        else:
            self.failed += 1
            self.errors.append({"test": test_name, "error": error})
            self.log(f"{test_name}: {error}", "FAIL")
            
    def print_summary(self):
        """Print verification summary."""
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        
        if self.errors:
            print("\nFAILED TESTS:")
            for err in self.errors:
                print(f"  ❌ {err['test']}: {err['error']}")
        print("=" * 70)
        

async def test_imports(runner: VerificationRunner):
    """Test all module imports."""
    runner.log("Testing Module Imports", "TEST")
    
    imports_to_test = [
        ("Config Module", "from src.config import BrowserConfig, Settings"),
        ("Auth Module", "from src.auth import LoginManager, SessionManager, SessionDetector"),
        ("Notebooks Module", "from src.notebooks import NotebookManager, SourceManager, ProcessingMonitor"),
        ("Outputs Module", "from src.outputs import AudioGenerator, VideoGenerator, QuizGenerator, FlashcardGenerator, SlideGenerator, DownloadManager"),
        ("Resilience Module", "from src.resilience import RetryHandler, RateLimiter, HumanDelays"),
        ("Utils Module", "from src.utils import Logger, ScreenshotManager, VideoRecorder, Selectors"),
        ("Main Module", "from src.main import NotebookLMAgent"),
    ]
    
    for name, import_statement in imports_to_test:
        try:
            exec(import_statement)
            runner.record_result(name, True)
        except Exception as e:
            runner.record_result(name, False, str(e))


def test_settings(runner: VerificationRunner):
    """Test Settings configuration."""
    runner.log("Testing Settings Configuration", "TEST")
    
    try:
        from src.config.settings import settings
        
        # Test default values
        tests = [
            ("Home directory exists", settings.home_dir.exists()),
            ("Profiles directory exists", settings.profiles_dir.exists()),
            ("Screenshots directory exists", settings.screenshots_dir.exists()),
            ("Videos directory exists", settings.videos_dir.exists()),
            ("Base URL correct", settings.notebooklm_base_url == "https://notebooklm.google.com"),
            ("Max retries set", settings.max_retries == 3),
            ("Viewport configured", settings.viewport_width == 1280),
            ("Rate limit set", settings.max_requests_per_minute == 10),
        ]
        
        for name, result in tests:
            runner.record_result(f"Settings: {name}", result)
            
    except Exception as e:
        runner.record_result("Settings Configuration", False, str(e))


def test_browser_config(runner: VerificationRunner):
    """Test BrowserConfig initialization."""
    runner.log("Testing BrowserConfig", "TEST")
    
    try:
        from src.config.browser_config import BrowserConfig
        
        # Test initialization
        config = BrowserConfig("test_verification")
        runner.record_result("BrowserConfig: Initialization", True)
        
        # Test storage directory
        runner.record_result("BrowserConfig: Storage dir created", config.storage_dir.exists())
        
        # Test storage file path
        runner.record_result("BrowserConfig: Storage file path", 
                           config.storage_file.name == "storage_state.json")
        
        # Test profile directory
        runner.record_result("BrowserConfig: Browser profile dir", 
                           config.browser_profile_dir.exists())
        
        # Cleanup test profile
        import shutil
        if config.storage_dir.exists():
            shutil.rmtree(config.storage_dir)
            
    except Exception as e:
        runner.record_result("BrowserConfig", False, str(e))


async def test_retry_handler(runner: VerificationRunner):
    """Test RetryHandler functionality."""
    runner.log("Testing RetryHandler", "TEST")
    
    try:
        from src.resilience.retry_handler import RetryHandler
        
        handler = RetryHandler(max_retries=3, delay=0.1)
        runner.record_result("RetryHandler: Initialization", True)
        
        # Test successful function
        async def success_func():
            return "success"
        
        result = await handler.execute_with_retry(success_func)
        runner.record_result("RetryHandler: Successful execution", result == "success")
        
        # Test retry on failure
        call_count = 0
        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Test error")
            return "recovered"
        
        result = await handler.execute_with_retry(fail_then_succeed)
        runner.record_result("RetryHandler: Recovery after retries", 
                           result == "recovered" and call_count == 3)
        
        # Test max retries exceeded
        async def always_fail():
            raise ValueError("Always fails")
        
        try:
            await handler.execute_with_retry(always_fail)
            runner.record_result("RetryHandler: Max retries exceeded", False, "Should have raised")
        except ValueError:
            runner.record_result("RetryHandler: Max retries exceeded", True)
            
    except Exception as e:
        runner.record_result("RetryHandler", False, str(e))


async def test_rate_limiter(runner: VerificationRunner):
    """Test RateLimiter functionality."""
    runner.log("Testing RateLimiter", "TEST")
    
    try:
        from src.resilience.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_requests=3, time_window=1)
        runner.record_result("RateLimiter: Initialization", True)
        
        # Test acquiring tokens
        result1 = await limiter.acquire()
        result2 = await limiter.acquire()
        result3 = await limiter.acquire()
        
        runner.record_result("RateLimiter: Token acquisition", 
                           all([result1, result2, result3]))
        
        # Test remaining requests
        remaining = limiter.get_remaining_requests()
        runner.record_result("RateLimiter: Remaining requests", remaining == 0)
        
        # Test rate limit detection
        runner.record_result("RateLimiter: Detect 429", limiter.detect_rate_limit(429))
        runner.record_result("RateLimiter: Detect 200", not limiter.detect_rate_limit(200))
        
        # Test reset
        limiter.reset()
        runner.record_result("RateLimiter: Reset", limiter.get_remaining_requests() == 3)
        
    except Exception as e:
        runner.record_result("RateLimiter", False, str(e))


async def test_human_delays(runner: VerificationRunner):
    """Test HumanDelays functionality."""
    runner.log("Testing HumanDelays", "TEST")
    
    try:
        from src.resilience.human_delays import HumanDelays
        
        delays = HumanDelays()
        runner.record_result("HumanDelays: Initialization", True)
        
        # Test random delay (non-blocking)
        start = asyncio.get_event_loop().time()
        await delays.random_delay(0.05, 0.1)
        elapsed = asyncio.get_event_loop().time() - start
        runner.record_result("HumanDelays: Random delay", 0.05 <= elapsed <= 0.2)
        
        # Test click delay
        start = asyncio.get_event_loop().time()
        await delays.click_delay()
        elapsed = asyncio.get_event_loop().time() - start
        runner.record_result("HumanDelays: Click delay", 0.3 <= elapsed <= 2.0)
        
        # Test between actions delay
        start = asyncio.get_event_loop().time()
        await delays.between_actions_delay()
        elapsed = asyncio.get_event_loop().time() - start
        runner.record_result("HumanDelays: Between actions delay", 0.2 <= elapsed <= 1.0)
        
    except Exception as e:
        runner.record_result("HumanDelays", False, str(e))


def test_screenshot_manager(runner: VerificationRunner):
    """Test ScreenshotManager functionality."""
    runner.log("Testing ScreenshotManager", "TEST")
    
    try:
        from src.utils.screenshot import ScreenshotManager
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ScreenshotManager(Path(tmpdir))
            runner.record_result("ScreenshotManager: Initialization", True)
            
            # Test storage directory
            runner.record_result("ScreenshotManager: Storage dir exists", 
                               manager.storage_dir.exists())
            
            # Test list screenshots
            screenshots = manager.list_screenshots()
            runner.record_result("ScreenshotManager: List screenshots", 
                               isinstance(screenshots, list))
            
    except Exception as e:
        runner.record_result("ScreenshotManager", False, str(e))


def test_video_recorder(runner: VerificationRunner):
    """Test VideoRecorder functionality."""
    runner.log("Testing VideoRecorder", "TEST")
    
    try:
        from src.utils.video_recorder import VideoRecorder
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            recorder = VideoRecorder(Path(tmpdir))
            runner.record_result("VideoRecorder: Initialization", True)
            
            # Test path generation
            path = recorder.get_video_path("test_session")
            runner.record_result("VideoRecorder: Path generation", 
                               "test_session" in path and path.endswith(".webm"))
            
            # Test list recordings
            recordings = recorder.list_recordings()
            runner.record_result("VideoRecorder: List recordings", 
                               isinstance(recordings, list))
            
    except Exception as e:
        runner.record_result("VideoRecorder", False, str(e))


def test_selectors(runner: VerificationRunner):
    """Test Selectors registry."""
    runner.log("Testing Selectors Registry", "TEST")
    
    try:
        from src.utils.selector_registry import Selectors
        
        # Test all selector categories
        selector_tests = [
            ("Auth selectors", [Selectors.SIGN_IN_BUTTON, Selectors.LOGIN_INPUT]),
            ("Notebook selectors", [Selectors.NOTEBOOK_LIST, Selectors.NEW_NOTEBOOK_BUTTON]),
            ("Source selectors", [Selectors.ADD_SOURCE_BUTTON, Selectors.URL_INPUT]),
            ("Output selectors", [Selectors.GENERATE_AUDIO, Selectors.GENERATE_VIDEO]),
            ("Download selectors", [Selectors.DOWNLOAD_BUTTON]),
        ]
        
        for name, selectors in selector_tests:
            runner.record_result(f"Selectors: {name}", all(s is not None for s in selectors))
            
    except Exception as e:
        runner.record_result("Selectors", False, str(e))


def test_session_manager(runner: VerificationRunner):
    """Test SessionManager functionality."""
    runner.log("Testing SessionManager", "TEST")
    
    try:
        from src.auth.session_manager import SessionManager
        import tempfile
        import json
        
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_storage.json"
            manager = SessionManager(storage_path)
            runner.record_result("SessionManager: Initialization", True)
            
            # Test save session
            test_state = {"cookies": [{"name": "test", "value": "value"}]}
            manager.save_session(test_state)
            runner.record_result("SessionManager: Save session", storage_path.exists())
            
            # Test load session
            loaded = manager.load_session()
            runner.record_result("SessionManager: Load session", 
                               loaded is not None and loaded == test_state)
            
            # Test session validity
            runner.record_result("SessionManager: Session valid", manager.is_session_valid())
            
            # Test session age
            age = manager.get_session_age()
            runner.record_result("SessionManager: Session age", age is not None)
            
            # Test delete session
            manager.delete_session()
            runner.record_result("SessionManager: Delete session", not storage_path.exists())
            
    except Exception as e:
        runner.record_result("SessionManager", False, str(e))


def test_notebook_manager(runner: VerificationRunner):
    """Test NotebookManager (mock)."""
    runner.log("Testing NotebookManager", "TEST")
    
    try:
        from src.notebooks.notebook_manager import NotebookManager
        
        # Test class instantiation (without page - just verify class exists)
        runner.record_result("NotebookManager: Class exists", True)
        
        # Test methods exist
        methods = ['create_notebook', 'list_notebooks', 'open_notebook', 
                   'delete_notebook', 'rename_notebook']
        for method in methods:
            runner.record_result(f"NotebookManager: {method} exists", 
                               hasattr(NotebookManager, method))
            
    except Exception as e:
        runner.record_result("NotebookManager", False, str(e))


def test_source_manager(runner: VerificationRunner):
    """Test SourceManager (mock)."""
    runner.log("Testing SourceManager", "TEST")
    
    try:
        from src.notebooks.source_manager import SourceManager
        
        # Test class instantiation
        runner.record_result("SourceManager: Class exists", True)
        
        # Test methods exist
        methods = ['add_url_source', 'add_text_source', 'add_file_source', 
                   'add_youtube_source', 'list_sources', 'delete_source']
        for method in methods:
            runner.record_result(f"SourceManager: {method} exists", 
                               hasattr(SourceManager, method))
            
    except Exception as e:
        runner.record_result("SourceManager", False, str(e))


def test_output_generators(runner: VerificationRunner):
    """Test all output generators."""
    runner.log("Testing Output Generators", "TEST")
    
    try:
        from src.outputs.audio_generator import AudioGenerator
        from src.outputs.video_generator import VideoGenerator
        from src.outputs.quiz_generator import QuizGenerator
        from src.outputs.flashcard_generator import FlashcardGenerator
        from src.outputs.slide_generator import SlideGenerator
        from src.outputs.download_manager import DownloadManager
        
        generators = [
            ("AudioGenerator", AudioGenerator, ['generate_audio', 'download_audio']),
            ("VideoGenerator", VideoGenerator, ['generate_video', 'download_video']),
            ("QuizGenerator", QuizGenerator, ['generate_quiz', 'download_quiz']),
            ("FlashcardGenerator", FlashcardGenerator, ['generate_flashcards', 'download_flashcards']),
            ("SlideGenerator", SlideGenerator, ['generate_slides', 'download_slides']),
            ("DownloadManager", DownloadManager, ['download_artifact', 'download_all_artifacts']),
        ]
        
        for name, cls, methods in generators:
            runner.record_result(f"{name}: Class exists", True)
            for method in methods:
                runner.record_result(f"{name}: {method} exists", hasattr(cls, method))
                
    except Exception as e:
        runner.record_result("Output Generators", False, str(e))


def test_logger(runner: VerificationRunner):
    """Test Logger functionality."""
    runner.log("Testing Logger", "TEST")
    
    try:
        from src.utils.logger import Logger
        
        logger = Logger()
        runner.record_result("Logger: Initialization", True)
        
        # Test log methods
        log_methods = ['info', 'debug', 'warning', 'error', 'critical']
        for method in log_methods:
            runner.record_result(f"Logger: {method} method", hasattr(logger, method))
            
        # Test singleton pattern
        logger2 = Logger()
        runner.record_result("Logger: Singleton pattern", logger is logger2)
        
    except Exception as e:
        runner.record_result("Logger", False, str(e))


def test_processing_monitor(runner: VerificationRunner):
    """Test ProcessingMonitor (mock)."""
    runner.log("Testing ProcessingMonitor", "TEST")
    
    try:
        from src.notebooks.processing_monitor import ProcessingMonitor
        
        # Test class exists
        runner.record_result("ProcessingMonitor: Class exists", True)
        
        # Test methods exist
        methods = ['wait_for_source_ready', 'wait_for_all_sources_ready', 'get_source_status']
        for method in methods:
            runner.record_result(f"ProcessingMonitor: {method} exists", 
                               hasattr(ProcessingMonitor, method))
            
    except Exception as e:
        runner.record_result("ProcessingMonitor", False, str(e))


async def test_main_agent(runner: VerificationRunner):
    """Test main NotebookLMAgent."""
    runner.log("Testing NotebookLMAgent", "TEST")
    
    try:
        from src.main import NotebookLMAgent
        
        # Test initialization
        agent = NotebookLMAgent("test_verification")
        runner.record_result("NotebookLMAgent: Initialization", True)
        
        # Test profile name
        runner.record_result("NotebookLMAgent: Profile name", 
                           agent.profile_name == "test_verification")
        
        # Test browser config
        runner.record_result("NotebookLMAgent: Browser config", 
                           agent.browser_config is not None)
        
        # Test session manager
        runner.record_result("NotebookLMAgent: Session manager", 
                           agent.session_manager is not None)
        
        # Test retry handler
        runner.record_result("NotebookLMAgent: Retry handler", 
                           agent.retry_handler is not None)
        
        # Test rate limiter
        runner.record_result("NotebookLMAgent: Rate limiter", 
                           agent.rate_limiter is not None)
        
        # Test methods exist
        methods = ['start', 'stop', 'login', 'navigate_to_notebooklm',
                   'create_notebook', 'list_notebooks', 'add_url_source',
                   'add_text_source', 'add_file_source', 'add_youtube_source',
                   'generate_audio', 'generate_video', 'generate_quiz',
                   'generate_flashcards', 'generate_slides', 'download_artifact']
        
        for method in methods:
            runner.record_result(f"NotebookLMAgent: {method} method", 
                               hasattr(agent, method))
        
        # Cleanup test profile
        import shutil
        if agent.browser_config.storage_dir.exists():
            shutil.rmtree(agent.browser_config.storage_dir)
            
    except Exception as e:
        runner.record_result("NotebookLMAgent", False, str(e))


async def test_browser_initialization(runner: VerificationRunner):
    """Test actual browser initialization."""
    runner.log("Testing Browser Initialization", "TEST")
    
    try:
        from playwright.async_api import async_playwright
        from src.config.browser_config import BrowserConfig
        
        config = BrowserConfig("browser_test")
        
        playwright = await async_playwright().start()
        runner.record_result("Browser: Playwright started", True)
        
        browser = await playwright.chromium.launch(headless=True)
        runner.record_result("Browser: Chromium launched", True)
        
        context = await browser.new_context()
        runner.record_result("Browser: Context created", True)
        
        page = await context.new_page()
        runner.record_result("Browser: Page created", True)
        
        # Test navigation
        await page.goto("https://example.com")
        title = await page.title()
        runner.record_result("Browser: Navigation works", "Example" in title)
        
        # Cleanup
        await context.close()
        await browser.close()
        await playwright.stop()
        
        # Remove test directory
        import shutil
        if config.storage_dir.exists():
            shutil.rmtree(config.storage_dir)
            
    except Exception as e:
        runner.record_result("Browser Initialization", False, str(e))


async def main():
    """Run all verification tests."""
    print("=" * 70)
    print("NOTEBOOKLM PLAYWRIGHT AGENT - VERIFICATION SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    runner = VerificationRunner()
    
    # Run all tests
    await test_imports(runner)
    test_settings(runner)
    test_browser_config(runner)
    await test_retry_handler(runner)
    await test_rate_limiter(runner)
    await test_human_delays(runner)
    test_screenshot_manager(runner)
    test_video_recorder(runner)
    test_selectors(runner)
    test_session_manager(runner)
    test_notebook_manager(runner)
    test_source_manager(runner)
    test_output_generators(runner)
    test_logger(runner)
    test_processing_monitor(runner)
    await test_main_agent(runner)
    await test_browser_initialization(runner)
    
    # Print summary
    runner.print_summary()
    
    return runner.failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
