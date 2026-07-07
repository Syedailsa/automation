"""
NotebookLM Playwright Automation Agent

A comprehensive automation agent for Google NotebookLM that uses browser-based
authentication (no API keys required) to manage notebooks, sources, and outputs.
"""

import asyncio
import argparse
from pathlib import Path

from .config.browser_config import BrowserConfig
from .config.settings import settings
from .auth.login_manager import LoginManager
from .auth.session_manager import SessionManager
from .auth.session_detector import SessionDetector
from .notebooks.notebook_manager import NotebookManager
from .notebooks.source_manager import SourceManager
from .notebooks.processing_monitor import ProcessingMonitor
from .outputs.audio_generator import AudioGenerator
from .outputs.video_generator import VideoGenerator
from .outputs.quiz_generator import QuizGenerator
from .outputs.flashcard_generator import FlashcardGenerator
from .outputs.slide_generator import SlideGenerator
from .outputs.download_manager import DownloadManager
from .resilience.retry_handler import RetryHandler
from .resilience.rate_limiter import RateLimiter
from .utils.logger import logger
from .utils.screenshot import ScreenshotManager


class NotebookLMAgent:
    """
    Main NotebookLM automation agent.
    
    Provides a unified interface for all NotebookLM operations including
    authentication, notebook management, source management, and output generation.
    """
    
    def __init__(self, profile_name: str = "default"):
        """
        Initialize the agent.
        
        Args:
            profile_name: Profile name for multi-account support
        """
        self.profile_name = profile_name
        self.browser_config = BrowserConfig(profile_name)
        self.session_manager = SessionManager(self.browser_config.storage_file)
        self.retry_handler = RetryHandler()
        self.rate_limiter = RateLimiter()
        self.screenshot_manager = ScreenshotManager()
        
        # Components will be initialized when context is created
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Managers will be initialized when page is available
        self.notebook_manager = None
        self.source_manager = None
        self.processing_monitor = None
        self.audio_generator = None
        self.video_generator = None
        self.quiz_generator = None
        self.flashcard_generator = None
        self.slide_generator = None
        self.download_manager = None
        
    async def start(self, headless: bool = False) -> bool:
        """
        Start the agent and create browser context.
        
        Args:
            headless: Whether to run browser in headless mode
            
        Returns:
            True if successful
        """
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )
            
            self.context = await self.browser_config.create_context(self.browser)
            self.page = await self.context.new_page()
            
            # Initialize managers
            self.notebook_manager = NotebookManager(self.page)
            self.source_manager = SourceManager(self.page)
            self.processing_monitor = ProcessingMonitor(self.page)
            self.audio_generator = AudioGenerator(self.page)
            self.video_generator = VideoGenerator(self.page)
            self.quiz_generator = QuizGenerator(self.page)
            self.flashcard_generator = FlashcardGenerator(self.page)
            self.slide_generator = SlideGenerator(self.page)
            self.download_manager = DownloadManager(self.page)
            
            logger.info(f"Agent started with profile: {self.profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent: {e}")
            return False
    
    async def stop(self):
        """Stop the agent and close browser."""
        try:
            if self.context:
                await self.browser_config.save_session(self.context)
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("Agent stopped")
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")
    
    async def login(self) -> bool:
        """
        Perform manual login.
        
        Returns:
            True if login successful
        """
        login_manager = LoginManager(self.browser_config)
        return await login_manager.manual_login()
    
    async def navigate_to_notebooklm(self) -> bool:
        """
        Navigate to NotebookLM.
        
        Returns:
            True if successful
        """
        try:
            await self.page.goto(settings.notebooklm_base_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Check if authenticated
            session_detector = SessionDetector(self.page)
            state = await session_detector.get_current_state()
            
            if state == 'authenticated':
                logger.info("Successfully navigated to NotebookLM")
                return True
            else:
                logger.warning(f"Not authenticated. Current state: {state}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to navigate to NotebookLM: {e}")
            return False
    
    async def create_notebook(self, title: str) -> str:
        """
        Create a new notebook.
        
        Args:
            title: Notebook title
            
        Returns:
            Notebook ID
        """
        await self.rate_limiter.acquire()
        return await self.retry_handler.execute_with_retry(
            self.notebook_manager.create_notebook,
            title
        )
    
    async def list_notebooks(self) -> list[dict]:
        """List all notebooks."""
        await self.rate_limiter.acquire()
        return await self.notebook_manager.list_notebooks()
    
    async def add_url_source(self, url: str) -> dict:
        """
        Add a URL source.
        
        Args:
            url: URL to add
            
        Returns:
            Result dict
        """
        await self.rate_limiter.acquire()
        return await self.retry_handler.execute_with_retry(
            self.source_manager.add_url_source,
            url
        )
    
    async def add_text_source(self, title: str, content: str) -> dict:
        """
        Add a text source.
        
        Args:
            title: Source title
            content: Text content
            
        Returns:
            Result dict
        """
        await self.rate_limiter.acquire()
        return await self.retry_handler.execute_with_retry(
            self.source_manager.add_text_source,
            title,
            content
        )
    
    async def add_file_source(self, file_path: str) -> dict:
        """
        Add a file source.
        
        Args:
            file_path: Path to file
            
        Returns:
            Result dict
        """
        await self.rate_limiter.acquire()
        return await self.retry_handler.execute_with_retry(
            self.source_manager.add_file_source,
            file_path
        )
    
    async def add_youtube_source(self, youtube_url: str) -> dict:
        """
        Add a YouTube source.
        
        Args:
            youtube_url: YouTube URL
            
        Returns:
            Result dict
        """
        await self.rate_limiter.acquire()
        return await self.retry_handler.execute_with_retry(
            self.source_manager.add_youtube_source,
            youtube_url
        )
    
    async def generate_audio(self, instructions: str = "") -> dict:
        """
        Generate audio overview.
        
        Args:
            instructions: Custom instructions
            
        Returns:
            Result dict
        """
        await self.rate_limiter.acquire()
        return await self.audio_generator.generate_audio(instructions)
    
    async def generate_video(self, style: str = "explainer") -> dict:
        """
        Generate video overview.
        
        Args:
            style: Video style
            
        Returns:
            Result dict
        """
        await self.rate_limiter.acquire()
        return await self.video_generator.generate_video(style)
    
    async def generate_quiz(self, num_questions: int = 10) -> dict:
        """
        Generate quiz.
        
        Args:
            num_questions: Number of questions
            
        Returns:
            Result dict
        """
        await self.rate_limiter.acquire()
        return await self.quiz_generator.generate_quiz(num_questions)
    
    async def generate_flashcards(self, num_cards: int = 20) -> dict:
        """
        Generate flashcards.
        
        Args:
            num_cards: Number of flashcards
            
        Returns:
            Result dict
        """
        await self.rate_limiter.acquire()
        return await self.flashcard_generator.generate_flashcards(num_cards)
    
    async def generate_slides(self, format: str = "detailed") -> dict:
        """
        Generate slides.
        
        Args:
            format: Slide format
            
        Returns:
            Result dict
        """
        await self.rate_limiter.acquire()
        return await self.slide_generator.generate_slides(format)
    
    async def download_artifact(self, artifact_type: str, output_path: str = None) -> str:
        """
        Download artifact.
        
        Args:
            artifact_type: Type of artifact
            output_path: Output path
            
        Returns:
            Path to downloaded file
        """
        return await self.download_manager.download_artifact(artifact_type, output_path)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='NotebookLM Playwright Agent')
    parser.add_argument('--profile', default='default', help='Profile name')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--login', action='store_true', help='Perform login')
    parser.add_argument('--list', action='store_true', help='List notebooks')
    parser.add_argument('--create', type=str, help='Create notebook with title')
    parser.add_argument('--add-url', type=str, help='Add URL source')
    parser.add_argument('--add-text', nargs=2, help='Add text source (title content)')
    parser.add_argument('--add-file', type=str, help='Add file source')
    parser.add_argument('--generate-audio', action='store_true', help='Generate audio')
    parser.add_argument('--generate-video', action='store_true', help='Generate video')
    parser.add_argument('--generate-quiz', action='store_true', help='Generate quiz')
    
    args = parser.parse_args()
    
    agent = NotebookLMAgent(args.profile)
    
    try:
        if args.login:
            await agent.login()
            return
        
        if not await agent.start(args.headless):
            print("Failed to start agent")
            return
        
        if not await agent.navigate_to_notebooklm():
            print("Failed to navigate to NotebookLM")
            return
        
        if args.list:
            notebooks = await agent.list_notebooks()
            print(f"Found {len(notebooks)} notebooks:")
            for nb in notebooks:
                print(f"  - {nb['title']} ({nb['id']})")
        
        elif args.create:
            nb_id = await agent.create_notebook(args.create)
            print(f"Created notebook: {nb_id}")
        
        elif args.add_url:
            result = await agent.add_url_source(args.add_url)
            print(f"Added URL source: {result}")
        
        elif args.add_text:
            result = await agent.add_text_source(args.add_text[0], args.add_text[1])
            print(f"Added text source: {result}")
        
        elif args.add_file:
            result = await agent.add_file_source(args.add_file)
            print(f"Added file source: {result}")
        
        elif args.generate_audio:
            result = await agent.generate_audio()
            print(f"Generated audio: {result}")
        
        elif args.generate_video:
            result = await agent.generate_video()
            print(f"Generated video: {result}")
        
        elif args.generate_quiz:
            result = await agent.generate_quiz()
            print(f"Generated quiz: {result}")
        
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
