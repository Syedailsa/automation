import asyncio
import argparse
from typing import Optional
from pathlib import Path

from playwright.async_api import async_playwright

from .config import BrowserConfig, settings
from .auth import LoginManager, SessionManager, SessionDetector
from .notebooks import NotebookManager, SourceManager, ProcessingMonitor
from .outputs import AudioGenerator, VideoGenerator, QuizGenerator, FlashcardGenerator, SlideGenerator, DownloadManager
from .utils.logger import get_logger
from .utils.selector_registry import selector_registry

logger = get_logger("notebooklm.main")


class NotebookLMAgent:
    """Main entry point for NotebookLM automation."""
    
    def __init__(self, profile_name: str = "default"):
        self.profile_name = profile_name
        self.browser_config = BrowserConfig(profile_name)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    async def initialize(self) -> bool:
        """Initialize the browser and load session."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.browser_config.create_browser(self.playwright)
            self.context = await self.browser_config.create_context(self.browser)
            self.page = await self.context.new_page()
            
            # Check if we have an existing session
            if self.browser_config.is_authenticated():
                session_manager = SessionManager(self.browser_config.storage_file)
                if session_manager.is_session_valid():
                    logger.info("Existing session found, attempting to restore...")
                    return True
            
            logger.info("No valid session found, login required")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def login(self) -> bool:
        """Perform manual login."""
        login_manager = LoginManager(self.browser_config)
        return await login_manager.manual_login()
    
    async def create_notebook(self, title: str) -> str:
        """Create a new notebook."""
        notebook_manager = NotebookManager(self.page)
        return await notebook_manager.create_notebook(title)
    
    async def list_notebooks(self) -> list:
        """List all notebooks."""
        notebook_manager = NotebookManager(self.page)
        return await notebook_manager.list_notebooks()
    
    async def add_source(self, source_type: str, **kwargs) -> dict:
        """Add a source to the current notebook."""
        source_manager = SourceManager(self.page)
        
        if source_type == "url":
            return await source_manager.add_url_source(kwargs.get("url"))
        elif source_type == "text":
            return await source_manager.add_text_source(kwargs.get("title"), kwargs.get("content"))
        elif source_type == "youtube":
            return await source_manager.add_youtube_source(kwargs.get("url"))
        elif source_type == "file":
            return await source_manager.add_file_source(kwargs.get("file_path"))
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    async def generate_audio(self, instructions: str = "", audio_format: str = "deep-dive") -> dict:
        """Generate audio overview."""
        audio_generator = AudioGenerator(self.page)
        return await audio_generator.generate_audio(instructions, audio_format)
    
    async def generate_video(self, style: str = "explainer", custom_prompt: str = "") -> dict:
        """Generate video overview."""
        video_generator = VideoGenerator(self.page)
        return await video_generator.generate_video(style, custom_prompt)
    
    async def generate_quiz(self, num_questions: int = 10, difficulty: str = "medium") -> dict:
        """Generate quiz."""
        quiz_generator = QuizGenerator(self.page)
        return await quiz_generator.generate_quiz(num_questions, difficulty)
    
    async def generate_flashcards(self, num_cards: int = 20, difficulty: str = "medium") -> dict:
        """Generate flashcards."""
        flashcard_generator = FlashcardGenerator(self.page)
        return await flashcard_generator.generate_flashcards(num_cards, difficulty)
    
    async def generate_slides(self, format: str = "detailed", num_slides: int = None) -> dict:
        """Generate slides."""
        slide_generator = SlideGenerator(self.page)
        return await slide_generator.generate_slides(format, num_slides)
    
    async def download_output(self, artifact_type: str, output_path: str = None) -> str:
        """Download generated output."""
        download_manager = DownloadManager(self.page)
        return await download_manager.download_artifact(artifact_type, output_path)
    
    async def close(self):
        """Close browser and cleanup."""
        try:
            if self.context:
                await self.browser_config.save_session(self.context)
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="NotebookLM Automation Agent")
    parser.add_argument("--login", action="store_true", help="Perform manual login")
    parser.add_argument("--list", action="store_true", help="List all notebooks")
    parser.add_argument("--create", type=str, help="Create a new notebook with title")
    parser.add_argument("--profile", type=str, default="default", help="Profile name")
    
    args = parser.parse_args()
    
    agent = NotebookLMAgent(args.profile)
    
    try:
        await agent.initialize()
        
        if args.login:
            await agent.login()
        elif args.list:
            notebooks = await agent.list_notebooks()
            for nb in notebooks:
                print(f"- {nb.get('title', 'Untitled')} (ID: {nb.get('id')})")
        elif args.create:
            notebook_id = await agent.create_notebook(args.create)
            print(f"Created notebook: {notebook_id}")
        else:
            print("NotebookLM Automation Agent")
            print("Use --help for available commands")
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
