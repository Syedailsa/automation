from playwright.async_api import Page


class SessionDetector:
    """Detects session state and authentication status."""
    
    # Selectors for detecting login page
    LOGIN_PAGE_INDICATORS = [
        'input[type="email"]',
        'input[name="identifier"]',
        '#identifierId',
    ]
    
    # Selectors for detecting authenticated state
    AUTHENTICATED_INDICATORS = [
        '[data-notebook-id]',
        'button:has-text("New Notebook")',
        '[role="main"]',
    ]
    
    # CAPTCHA indicators
    CAPTCHA_INDICATORS = [
        'div.recaptcha',
        'iframe[src*="recaptcha"]',
        'div.g-recaptcha',
        '#captcha-container',
    ]
    
    def __init__(self, page: Page):
        self.page = page
        
    async def check_session_valid(self) -> bool:
        """
        Check if current session is still valid.
        
        Returns:
            True if session is valid
        """
        try:
            # Check if redirected to login
            if 'accounts.google.com' in self.page.url:
                return False
            
            # Check if notebook list is visible
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
    
    async def detect_error_page(self) -> bool:
        """Detect if on error page."""
        error_indicators = [
            'div:has-text("Something went wrong")',
            'div:has-text("Error")',
            'div:has-text("Not found")',
        ]
        
        for indicator in error_indicators:
            if await self.page.locator(indicator).count() > 0:
                return True
        return False
    
    async def get_current_state(self) -> str:
        """
        Get current page state.
        
        Returns:
            State string: 'authenticated', 'login_page', 'captcha', 'error', 'unknown'
        """
        if await self.detect_captcha():
            return 'captcha'
        elif await self.detect_login_page():
            return 'login_page'
        elif await self.detect_error_page():
            return 'error'
        elif await self.check_session_valid():
            return 'authenticated'
        else:
            return 'unknown'
