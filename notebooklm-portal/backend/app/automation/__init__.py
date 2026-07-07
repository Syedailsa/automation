"""Playwright automation module for NotebookLM."""
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from pathlib import Path
from datetime import datetime
import asyncio
import json
import random
import logging
from typing import Optional, Dict, List, Any
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('notebooklm')


class Settings:
    """Application settings."""
    
    # Paths
    HOME_DIR = Path.home() / ".notebooklm"
    PROFILES_DIR = HOME_DIR / "profiles"
    SCREENSHOTS_DIR = HOME_DIR / "screenshots"
    VIDEOS_DIR = HOME_DIR / "videos"
    LOGS_DIR = HOME_DIR / "logs"
    
    # Browser settings
    HEADLESS = False
    SLOW_MO = 0
    VIEWPORT_WIDTH = 1280
    VIEWPORT_HEIGHT = 720
    
    # Timeouts
    NAVIGATION_TIMEOUT = 60000
    ACTION_TIMEOUT = 30000
    LOGIN_TIMEOUT = 300000
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 10
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    RETRY_BACKOFF = 2.0
    
    # Delays
    MIN_TYPING_DELAY = 0.05
    MAX_TYPING_DELAY = 0.15
    MIN_CLICK_DELAY = 0.5
    MAX_CLICK_DELAY = 1.5
    
    # NotebookLM
    NOTEBOOKLM_BASE_URL = "https://notebooklm.google.com"


settings = Settings()


class BrowserConfig:
    """Browser configuration and context management."""
    
    def __init__(self, profile_name: str = "default"):
        self.profile_name = profile_name
        self.storage_dir = settings.PROFILES_DIR / profile_name
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.storage_file = self.storage_dir / "storage_state.json"
        self.browser_profile_dir = self.storage_dir / "browser_profile"
        self.browser_profile_dir.mkdir(parents=True, exist_ok=True)
        
    async def create_playwright(self):
        """Create playwright instance."""
        return await async_playwright().start()
    
    async def create_browser(self, playwright):
        """Create a new browser instance."""
        browser = await playwright.chromium.launch(
            headless=settings.HEADLESS,
            slow_mo=settings.SLOW_MO,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        return browser
    
    async def create_context(self, browser: Browser) -> BrowserContext:
        """Create a new browser context with persistent profile."""
        context_args = {
            'viewport': {
                'width': settings.VIEWPORT_WIDTH,
                'height': settings.VIEWPORT_HEIGHT
            },
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'locale': 'en-US',
            'timezone_id': 'America/New_York',
        }
        
        # Load existing storage state if available
        if self.storage_file.exists():
            context_args['storage_state'] = str(self.storage_file)
        
        context = await browser.new_context(**context_args)
        context.set_default_timeout(settings.ACTION_TIMEOUT)
        context.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
        
        return context
    
    async def save_session(self, context: BrowserContext) -> None:
        """Save session storage state."""
        await context.storage_state(path=str(self.storage_file))
        
    def is_authenticated(self) -> bool:
        """Check if session file exists and is valid."""
        return self.storage_file.exists()


class ScreenshotManager:
    """Manages screenshots for error handling and debugging."""
    
    def __init__(self, storage_dir: Path = None):
        if storage_dir is None:
            storage_dir = settings.HOME_DIR
        
        self.storage_dir = storage_dir / "screenshots"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    async def capture_error_screenshot(self, page: Page, error_name: str) -> str:
        """Capture screenshot on error."""
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


class RetryHandler:
    """Handles retry logic for failed operations."""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
    
    def retry(self, func):
        """Decorator to retry function on failure."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    delay = self.delay * (self.backoff ** attempt)
                    print(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                    print(f"Retrying in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
            
            print(f"All {self.max_retries} attempts failed")
            raise last_exception
        
        return wrapper


class RateLimiter:
    """Handles rate limiting for API calls."""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self) -> bool:
        """Acquire rate limit token."""
        now = datetime.now()
        
        # Remove old requests
        self.requests = [r for r in self.requests if r > now - asyncio.timedelta(seconds=self.time_window)]
        
        if len(self.requests) >= self.max_requests:
            wait_time = (self.requests[0] + asyncio.timedelta(seconds=self.time_window) - now).total_seconds()
            print(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)
        
        self.requests.append(now)
        return True


class HumanDelays:
    """Simulates human-like delays to avoid detection."""
    
    @staticmethod
    async def typing_delay(text: str, min_delay: float = None, max_delay: float = None):
        """Simulate typing delay."""
        if min_delay is None:
            min_delay = settings.MIN_TYPING_DELAY
        if max_delay is None:
            max_delay = settings.MAX_TYPING_DELAY
            
        for _ in text:
            await asyncio.sleep(random.uniform(min_delay, max_delay))
    
    @staticmethod
    async def click_delay():
        """Random delay before click."""
        delay = random.uniform(settings.MIN_CLICK_DELAY, settings.MAX_CLICK_DELAY)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Random delay."""
        await asyncio.sleep(random.uniform(min_seconds, max_seconds))


class Selectors:
    """Central registry of UI selectors for NotebookLM."""
    
    # Authentication
    SIGN_IN_BUTTON = 'button:has-text("Sign in")'
    LOGIN_INPUT = 'input[type="email"], input[name="identifier"]'
    
    # Notebook Operations
    NOTEBOOK_LIST = '[data-notebook-id]'
    NEW_NOTEBOOK_BUTTON = 'button:has-text("New Notebook")'
    
    # Source Management
    ADD_SOURCE_BUTTON = 'button:has-text("Add source")'
    URL_SOURCE_OPTION = 'button:has-text("Website")'
    TEXT_SOURCE_OPTION = 'button:has-text("Text")'
    FILE_SOURCE_OPTION = 'button:has-text("Upload")'
    YOUTUBE_SOURCE_OPTION = 'button:has-text("YouTube")'
    URL_INPUT = 'input[type="url"]'
    FILE_INPUT = 'input[type="file"]'
    SOURCE_LIST = '[data-source-id]'
    
    # Output Generation
    GENERATE_AUDIO = 'button:has-text("Generate audio")'
    GENERATE_VIDEO = 'button:has-text("Generate video")'
    GENERATE_QUIZ = 'button:has-text("Generate quiz")'
    GENERATE_FLASHCARDS = 'button:has-text("Generate flashcards")'
    GENERATE_SLIDES = 'button:has-text("Generate slides")'
    
    # Downloads
    DOWNLOAD_BUTTON = 'button:has-text("Download")'
    
    # Common Elements
    DIALOG = '[role="dialog"]'
    TEXTAREA = 'textarea'
    INPUT = 'input[type="text"]'
    
    # Status Indicators
    PROCESSING = '[data-status="processing"]'
    READY = '[data-status="ready"]'
    ERROR = '[data-status="error"]'


class LoginManager:
    """Handles manual Google login flow."""
    
    def __init__(self, browser_config: BrowserConfig):
        self.config = browser_config
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
        
    async def manual_login(self, timeout: int = None) -> bool:
        """Open browser for manual Google login."""
        if timeout is None:
            timeout = settings.LOGIN_TIMEOUT
            
        playwright = await async_playwright().start()
        browser = None
        
        try:
            browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': settings.VIEWPORT_WIDTH, 'height': settings.VIEWPORT_HEIGHT},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Navigate to NotebookLM
            await page.goto(settings.NOTEBOOKLM_BASE_URL)
            
            print("=" * 60)
            print("Please complete Google login in the browser window.")
            print("Waiting for login completion...")
            print("=" * 60)
            
            try:
                # Wait for successful login
                await page.wait_for_selector(
                    '[data-notebook-id], [role="main"]',
                    timeout=timeout * 1000
                )
                
                # Save storage state
                await context.storage_state(path=str(self.config.storage_file))
                print("Login successful! Storage state saved.")
                return True
                
            except Exception as e:
                print(f"Login timeout or failed: {e}")
                await self.screenshot_manager.capture_error_screenshot(page, "login_failed")
                return False
            finally:
                await context.close()
                
        except Exception as e:
            print(f"Error during login: {e}")
            return False
        finally:
            if browser:
                await browser.close()
            await playwright.stop()


class SessionManager:
    """Manages session storage and persistence."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        
    def save_session(self, storage_state: dict, expires_days: int = 7) -> None:
        """Save session to file with metadata."""
        data = {
            'storage_state': storage_state,
            'saved_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=expires_days)).isoformat()
        }
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_session(self) -> Optional[dict]:
        """Load session from file if valid."""
        if not self.storage_path.exists():
            return None
            
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            expires_at = datetime.fromisoformat(data['expires_at'])
            if datetime.now() > expires_at:
                print("Session expired, please re-login")
                return None
                
            return data.get('storage_state')
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading session: {e}")
            return None
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid."""
        session = self.load_session()
        return session is not None


class SessionDetector:
    """Detects session state and authentication status."""
    
    LOGIN_PAGE_INDICATORS = [
        'input[type="email"]',
        'input[name="identifier"]',
        '#identifierId',
    ]
    
    AUTHENTICATED_INDICATORS = [
        '[data-notebook-id]',
        'button:has-text("New Notebook")',
        '[role="main"]',
    ]
    
    CAPTCHA_INDICATORS = [
        'div.recaptcha',
        'iframe[src*="recaptcha"]',
        'div.g-recaptcha',
    ]
    
    def __init__(self, page: Page):
        self.page = page
        
    async def check_session_valid(self) -> bool:
        """Check if current session is still valid."""
        try:
            if 'accounts.google.com' in self.page.url:
                return False
            
            for selector in self.AUTHENTICATED_INDICATORS:
                if await self.page.locator(selector).count() > 0:
                    return True
            
            return False
        except Exception:
            return False
    
    async def detect_login_page(self) -> bool:
        """Detect if on login page."""
        if 'accounts.google.com' in self.page.url:
            return True
        
        for selector in self.LOGIN_PAGE_INDICATORS:
            if await self.page.locator(selector).count() > 0:
                return True
        
        return False
    
    async def detect_captcha(self) -> bool:
        """Detect if CAPTCHA is present."""
        for indicator in self.CAPTCHA_INDICATORS:
            if await self.page.locator(indicator).count() > 0:
                return True
        return False
    
    async def get_current_state(self) -> str:
        """Get current page state."""
        if await self.detect_captcha():
            return 'captcha'
        elif await self.detect_login_page():
            return 'login_page'
        elif await self.check_session_valid():
            return 'authenticated'
        else:
            return 'unknown'


class NotebookManager:
    """Manages NotebookLM notebook operations."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        
    async def create_notebook(self, title: str) -> str:
        """Create a new notebook and return its ID."""
        await self.delays.click_delay()
        await self.page.click('button:has-text("New Notebook")')
        
        await self.page.wait_for_selector('input[placeholder*="title"], input[type="text"]')
        
        title_input = self.page.locator('input[placeholder*="title"], input[type="text"]').first
        await title_input.fill('')
        await title_input.type(title, delay=50)
        
        await self.delays.random_delay(0.5, 1.0)
        
        await self.page.click('button:has-text("Create")')
        
        await asyncio.sleep(2)
        
        try:
            notebook_element = await self.page.wait_for_selector(
                f'[data-notebook-title="{title}"], [aria-label*="{title}"]',
                timeout=10000
            )
            notebook_id = await notebook_element.get_attribute('data-notebook-id')
            if notebook_id:
                return notebook_id
        except Exception:
            pass
        
        return title.lower().replace(' ', '_')
    
    async def list_notebooks(self) -> list[dict]:
        """List all notebooks."""
        await asyncio.sleep(1)
        
        notebooks = await self.page.query_selector_all('[data-notebook-id]')
        
        result = []
        for nb in notebooks:
            nb_id = await nb.get_attribute('data-notebook-id')
            title_elem = await nb.query_selector('h3, h4, [role="heading"]')
            title_text = await title_elem.inner_text() if title_elem else "Untitled"
            result.append({'id': nb_id, 'title': title_text})
        
        return result
    
    async def open_notebook(self, notebook_id: str) -> bool:
        """Open a specific notebook."""
        try:
            await self.page.click(f'[data-notebook-id="{notebook_id}"]')
            await self.page.wait_for_load_state('networkidle')
            await self.delays.random_delay(1.0, 2.0)
            return True
        except Exception as e:
            print(f"Error opening notebook: {e}")
            return False
    
    async def delete_notebook(self, notebook_id: str) -> bool:
        """Delete a notebook."""
        try:
            await self.page.click(
                f'[data-notebook-id="{notebook_id}"]',
                button='right'
            )
            
            await self.delays.random_delay(0.3, 0.5)
            
            await self.page.click('button:has-text("Delete")')
            
            await self.delays.random_delay(0.3, 0.5)
            
            await self.page.click('button:has-text("Confirm"), button:has-text("Yes")')
            
            await asyncio.sleep(1)
            
            return True
        except Exception as e:
            print(f"Error deleting notebook: {e}")
            return False


class SourceManager:
    """Manages NotebookLM source operations."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
        
    async def add_url_source(self, url: str) -> dict:
        """Add a URL as a source."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Add source")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Website"), button:has-text("URL")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            url_input = self.page.locator('input[type="url"], input[placeholder*="url"]').first
            await url_input.fill('')
            await url_input.type(url, delay=30)
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Insert"), button:has-text("Add")')
            
            await asyncio.sleep(2)
            
            return {'status': 'added', 'url': url}
        except Exception as e:
            print(f"Error adding URL source: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "add_url_error")
            return {'status': 'error', 'error': str(e)}
    
    async def add_text_source(self, title: str, content: str) -> dict:
        """Add text as a source."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Add source")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Text"), button:has-text("Paste")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            title_input = self.page.locator('input[placeholder*="title"], input[type="text"]').first
            await title_input.fill('')
            await title_input.type(title, delay=50)
            
            content_area = self.page.locator('textarea, div[contenteditable="true"]').first
            await content_area.fill('')
            await content_area.type(content, delay=20)
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Insert"), button:has-text("Add")')
            
            await asyncio.sleep(2)
            
            return {'status': 'added', 'title': title}
        except Exception as e:
            print(f"Error adding text source: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "add_text_error")
            return {'status': 'error', 'error': str(e)}
    
    async def add_youtube_source(self, youtube_url: str) -> dict:
        """Add a YouTube video as a source."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Add source")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("YouTube")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            url_input = self.page.locator('input[type="url"], input[placeholder*="youtube"]').first
            await url_input.fill('')
            await url_input.type(youtube_url, delay=30)
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Insert"), button:has-text("Add")')
            
            await asyncio.sleep(2)
            
            return {'status': 'added', 'url': youtube_url}
        except Exception as e:
            print(f"Error adding YouTube source: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "add_youtube_error")
            return {'status': 'error', 'error': str(e)}
    
    async def add_file_source(self, file_path: str) -> dict:
        """Upload a file as a source."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Add source")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Upload"), button:has-text("File")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            async with self.page.expect_file_chooser() as fc_info:
                await self.page.click('button:has-text("Choose file"), button:has-text("Browse")')
            
            file_chooser = await fc_info.value
            await file_chooser.set_files(file_path)
            
            await asyncio.sleep(3)
            
            return {'status': 'uploaded', 'file': file_path}
        except Exception as e:
            print(f"Error uploading file source: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "upload_file_error")
            return {'status': 'error', 'error': str(e)}
    
    async def list_sources(self) -> list[dict]:
        """List all sources in current notebook."""
        await asyncio.sleep(1)
        
        sources = await self.page.query_selector_all('[data-source-id]')
        
        result = []
        for src in sources:
            src_id = await src.get_attribute('data-source-id')
            title_elem = await src.query_selector('h3, h4, [role="heading"], span')
            title_text = await title_elem.inner_text() if title_elem else "Untitled"
            result.append({'id': src_id, 'title': title_text})
        
        return result


class ProcessingMonitor:
    """Monitors source processing status."""
    
    PROCESSING_INDICATORS = [
        '[data-status="processing"]',
        'div:has-text("Processing")',
        'div:has-text("Loading")',
    ]
    
    READY_INDICATORS = [
        '[data-status="ready"]',
        '[data-status="completed"]',
    ]
    
    def __init__(self, page: Page):
        self.page = page
        
    async def wait_for_source_ready(self, source_id: str = None, timeout: int = 60) -> bool:
        """Wait for source to finish processing."""
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            if source_id:
                source = await self.page.query_selector(f'[data-source-id="{source_id}"]')
                if source:
                    status = await source.get_attribute('data-status')
                    if status in ['ready', 'completed']:
                        return True
                    elif status == 'error':
                        return False
            
            processing = False
            for indicator in self.PROCESSING_INDICATORS:
                if await self.page.locator(indicator).count() > 0:
                    processing = True
                    break
            
            if not processing:
                for indicator in self.READY_INDICATORS:
                    if await self.page.locator(indicator).count() > 0:
                        return True
            
            await asyncio.sleep(1)
        
        return False


class AudioGenerator:
    """Generates audio overviews."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
        
    async def generate_audio(self, instructions: str = "", audio_format: str = "deep-dive") -> dict:
        """Generate audio overview."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate audio"), button:has-text("Audio")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                await self.page.click(f'button:has-text("{audio_format}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass
            
            if instructions:
                try:
                    textarea = self.page.locator('textarea, input[placeholder*="instruction"]').first
                    await textarea.fill('')
                    await textarea.type(instructions, delay=30)
                except Exception:
                    pass
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await self.page.wait_for_selector(
                'button:has-text("Download"), a:has-text("Download")',
                timeout=300000
            )
            
            return {'status': 'generated', 'type': 'audio', 'format': audio_format}
        except Exception as e:
            print(f"Error generating audio: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_audio_error")
            return {'status': 'error', 'error': str(e)}
    
    async def download_audio(self, output_path: str) -> str:
        """Download generated audio."""
        try:
            async with self.page.expect_download() as download_info:
                await self.page.click('button:has-text("Download"), a:has-text("Download")')
            
            download = await download_info.value
            await download.save_as(output_path)
            
            return output_path
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None


class VideoGenerator:
    """Generates video overviews."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
        
    async def generate_video(self, style: str = "explainer", custom_prompt: str = "") -> dict:
        """Generate video overview."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate video"), button:has-text("Video")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                await self.page.click(f'button:has-text("{style}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass
            
            if custom_prompt:
                try:
                    textarea = self.page.locator('textarea, input[placeholder*="prompt"]').first
                    await textarea.fill('')
                    await textarea.type(custom_prompt, delay=30)
                except Exception:
                    pass
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await self.page.wait_for_selector(
                'button:has-text("Download"), a:has-text("Download")',
                timeout=600000
            )
            
            return {'status': 'generated', 'type': 'video', 'style': style}
        except Exception as e:
            print(f"Error generating video: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_video_error")
            return {'status': 'error', 'error': str(e)}
    
    async def download_video(self, output_path: str) -> str:
        """Download generated video."""
        try:
            async with self.page.expect_download() as download_info:
                await self.page.click('button:has-text("Download"), a:has-text("Download")')
            
            download = await download_info.value
            await download.save_as(output_path)
            
            return output_path
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None


class QuizGenerator:
    """Generates quizzes from notebook content."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
        
    async def generate_quiz(self, num_questions: int = 10, difficulty: str = "medium") -> dict:
        """Generate quiz."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate quiz"), button:has-text("Quiz")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                num_input = self.page.locator('input[type="number"], input[placeholder*="question"]').first
                await num_input.fill('')
                await num_input.type(str(num_questions), delay=50)
            except Exception:
                pass
            
            try:
                await self.page.click(f'button:has-text("{difficulty}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await self.page.wait_for_selector(
                'button:has-text("Download"), [data-quiz-generated="true"]',
                timeout=120000
            )
            
            return {'status': 'generated', 'type': 'quiz'}
        except Exception as e:
            print(f"Error generating quiz: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_quiz_error")
            return {'status': 'error', 'error': str(e)}


class FlashcardGenerator:
    """Generates flashcards from notebook content."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
        
    async def generate_flashcards(self, num_cards: int = 20, difficulty: str = "medium") -> dict:
        """Generate flashcards."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate flashcards"), button:has-text("Flashcards")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                num_input = self.page.locator('input[type="number"], input[placeholder*="card"]').first
                await num_input.fill('')
                await num_input.type(str(num_cards), delay=50)
            except Exception:
                pass
            
            try:
                await self.page.click(f'button:has-text("{difficulty}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await self.page.wait_for_selector(
                'button:has-text("Download"), [data-flashcards-generated="true"]',
                timeout=120000
            )
            
            return {'status': 'generated', 'type': 'flashcards'}
        except Exception as e:
            print(f"Error generating flashcards: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_flashcards_error")
            return {'status': 'error', 'error': str(e)}


class SlideGenerator:
    """Generates slide decks from notebook content."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.screenshot_manager = ScreenshotManager(settings.HOME_DIR)
        
    async def generate_slides(self, format: str = "detailed", num_slides: int = None) -> dict:
        """Generate slide deck."""
        try:
            await self.delays.click_delay()
            await self.page.click('button:has-text("Generate slides"), button:has-text("Slides")')
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.wait_for_selector('[role="dialog"], div[role="dialog"]')
            
            try:
                await self.page.click(f'button:has-text("{format}")')
                await self.delays.random_delay(0.3, 0.5)
            except Exception:
                pass
            
            if num_slides:
                try:
                    num_input = self.page.locator('input[type="number"], input[placeholder*="slide"]').first
                    await num_input.fill('')
                    await num_input.type(str(num_slides), delay=50)
                except Exception:
                    pass
            
            await self.delays.random_delay(0.5, 1.0)
            
            await self.page.click('button:has-text("Generate"), button:has-text("Create")')
            
            await self.page.wait_for_selector(
                'button:has-text("Download"), a:has-text("Download")',
                timeout=180000
            )
            
            return {'status': 'generated', 'type': 'slides', 'format': format}
        except Exception as e:
            print(f"Error generating slides: {e}")
            await self.screenshot_manager.capture_error_screenshot(self.page, "generate_slides_error")
            return {'status': 'error', 'error': str(e)}


class DownloadManager:
    """Manages file downloads from NotebookLM."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.download_dir = settings.HOME_DIR / "downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    async def download_artifact(self, artifact_type: str, output_path: str = None) -> str:
        """Download any artifact type."""
        if output_path is None:
            output_path = str(self.download_dir / f"{artifact_type}_download")
        
        try:
            download_button = self.page.locator(
                f'button:has-text("Download"), a:has-text("Download")'
            ).first
            
            async with self.page.expect_download() as download_info:
                await download_button.click()
            
            download = await download_info.value
            
            suggested_filename = download.suggested_filename
            if suggested_filename:
                final_path = str(Path(output_path).parent / suggested_filename)
            else:
                final_path = output_path
            
            await download.save_as(final_path)
            
            return final_path
        except Exception as e:
            print(f"Error downloading artifact: {e}")
            return None
