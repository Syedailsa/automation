from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright
from .settings import settings


class BrowserConfig:
    """Browser configuration and context management."""
    
    def __init__(self, profile_name: str = "default"):
        self.profile_name = profile_name
        self.storage_dir = settings.profiles_dir / profile_name
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.storage_file = self.storage_dir / "storage_state.json"
        self.browser_profile_dir = self.storage_dir / "browser_profile"
        self.browser_profile_dir.mkdir(parents=True, exist_ok=True)
        
    async def create_playwright(self) -> Playwright:
        """Create playwright instance."""
        return await async_playwright().start()
    
    async def create_browser(self, playwright: Playwright) -> Browser:
        """Create a new browser instance."""
        browser = await playwright.chromium.launch(
            headless=settings.headless,
            slow_mo=settings.slow_mo,
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
                'width': settings.viewport_width,
                'height': settings.viewport_height
            },
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'locale': 'en-US',
            'timezone_id': 'America/New_York',
        }
        
        # Load existing storage state if available
        if self.storage_file.exists():
            context_args['storage_state'] = str(self.storage_file)
        
        context = await browser.new_context(**context_args)
        context.set_default_timeout(settings.action_timeout)
        context.set_default_navigation_timeout(settings.navigation_timeout)
        
        return context
    
    async def save_session(self, context: BrowserContext) -> None:
        """Save session storage state."""
        await context.storage_state(path=str(self.storage_file))
        
    def is_authenticated(self) -> bool:
        """Check if session file exists and is valid."""
        return self.storage_file.exists()
