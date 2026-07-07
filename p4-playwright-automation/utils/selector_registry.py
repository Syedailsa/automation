from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Selector:
    """Represents a UI selector with fallback options."""
    name: str
    primary: str
    fallbacks: List[str]
    description: str = ""
    
    def get_all_selectors(self) -> List[str]:
        """Get all selector options (primary + fallbacks)."""
        return [self.primary] + self.fallbacks
    
    def get_first_match(self) -> str:
        """Get the primary selector."""
        return self.primary


class SelectorRegistry:
    """Central registry for all UI selectors with fallback support."""
    
    def __init__(self):
        self.selectors: Dict[str, Selector] = {}
        self._register_default_selectors()
    
    def _register_default_selectors(self):
        """Register default selectors for NotebookLM."""
        # Authentication
        self.register("login_button", Selector(
            name="login_button",
            primary='button:has-text("Sign in")',
            fallbacks=['button:has-text("Log in")', 'a:has-text("Sign in")'],
            description="Google sign-in button"
        ))
        
        self.register("email_input", Selector(
            name="email_input",
            primary='input[type="email"]',
            fallbacks=['input[name="identifier"]', '#identifierId'],
            description="Email input field"
        ))
        
        # Notebook operations
        self.register("new_notebook_button", Selector(
            name="new_notebook_button",
            primary='button:has-text("New Notebook")',
            fallbacks=['button:has-text("Create Notebook")', 'button:has-text("+ New")'],
            description="Button to create new notebook"
        ))
        
        self.register("notebook_list", Selector(
            name="notebook_list",
            primary='[data-notebook-id]',
            fallbacks=['div.notebook-item', 'li.notebook'],
            description="Notebook list container"
        ))
        
        # Source management
        self.register("add_source_button", Selector(
            name="add_source_button",
            primary='button:has-text("Add source")',
            fallbacks=['button:has-text("+ Source")', 'button:has-text("Add Source")'],
            description="Button to add source"
        ))
        
        self.register("url_source_option", Selector(
            name="url_source_option",
            primary='button:has-text("Website")',
            fallbacks=['button:has-text("URL")', 'button:has-text("Web")'],
            description="Website URL source option"
        ))
        
        self.register("text_source_option", Selector(
            name="text_source_option",
            primary='button:has-text("Text")',
            fallbacks=['button:has-text("Paste")', 'button:has-text("Copy")'],
            description="Text source option"
        ))
        
        self.register("youtube_source_option", Selector(
            name="youtube_source_option",
            primary='button:has-text("YouTube")',
            fallbacks=['button:has-text("Video")'],
            description="YouTube source option"
        ))
        
        self.register("file_source_option", Selector(
            name="file_source_option",
            primary='button:has-text("Upload")',
            fallbacks=['button:has-text("File")', 'button:has-text("Browse")'],
            description="File upload source option"
        ))
        
        self.register("url_input", Selector(
            name="url_input",
            primary='input[type="url"]',
            fallbacks=['input[placeholder*="url"]', 'input[placeholder*="URL"]'],
            description="URL input field"
        ))
        
        self.register("file_input", Selector(
            name="file_input",
            primary='input[type="file"]',
            fallbacks=[],
            description="File input field"
        ))
        
        # Output generation
        self.register("generate_audio_button", Selector(
            name="generate_audio_button",
            primary='button:has-text("Generate audio")',
            fallbacks=['button:has-text("Audio")', 'button:has-text("Audio Overview")'],
            description="Generate audio overview button"
        ))
        
        self.register("generate_video_button", Selector(
            name="generate_video_button",
            primary='button:has-text("Generate video")',
            fallbacks=['button:has-text("Video")', 'button:has-text("Video Overview")'],
            description="Generate video overview button"
        ))
        
        self.register("generate_quiz_button", Selector(
            name="generate_quiz_button",
            primary='button:has-text("Generate quiz")',
            fallbacks=['button:has-text("Quiz")'],
            description="Generate quiz button"
        ))
        
        self.register("generate_flashcards_button", Selector(
            name="generate_flashcards_button",
            primary='button:has-text("Generate flashcards")',
            fallbacks=['button:has-text("Flashcards")'],
            description="Generate flashcards button"
        ))
        
        self.register("generate_slides_button", Selector(
            name="generate_slides_button",
            primary='button:has-text("Generate slides")',
            fallbacks=['button:has-text("Slides")', 'button:has-text("Slide Deck")'],
            description="Generate slides button"
        ))
        
        self.register("download_button", Selector(
            name="download_button",
            primary='button:has-text("Download")',
            fallbacks=['a:has-text("Download")', 'button:has-text("Export")'],
            description="Download button"
        ))
        
        # Common UI elements
        self.register("dialog", Selector(
            name="dialog",
            primary='[role="dialog"]',
            fallbacks=['div.modal', 'div.overlay'],
            description="Dialog/modal container"
        ))
        
        self.register("textarea", Selector(
            name="textarea",
            primary='textarea',
            fallbacks=['div[contenteditable="true"]', 'input[type="text"]'],
            description="Text input area"
        ))
        
        self.register("processing_indicator", Selector(
            name="processing_indicator",
            primary='[data-status="processing"]',
            fallbacks=['div:has-text("Processing")', 'div:has-text("Loading")'],
            description="Processing status indicator"
        ))
        
        self.register("ready_indicator", Selector(
            name="ready_indicator",
            primary='[data-status="ready"]',
            fallbacks=['[data-status="completed"]'],
            description="Ready status indicator"
        ))
    
    def register(self, name: str, selector: Selector):
        """Register a selector."""
        self.selectors[name] = selector
    
    def get(self, name: str) -> Optional[Selector]:
        """Get a selector by name."""
        return self.selectors.get(name)
    
    def get_selector(self, name: str) -> str:
        """Get the primary selector string for a named selector."""
        selector = self.selectors.get(name)
        return selector.primary if selector else None
    
    def get_all_selectors(self, name: str) -> List[str]:
        """Get all selector options for a named selector."""
        selector = self.selectors.get(name)
        return selector.get_all_selectors() if selector else []
    
    def list_selectors(self) -> List[str]:
        """List all registered selector names."""
        return list(self.selectors.keys())
    
    def update_selector(self, name: str, primary: str, fallbacks: List[str] = None):
        """Update an existing selector."""
        if name in self.selectors:
            self.selectors[name].primary = primary
            if fallbacks is not None:
                self.selectors[name].fallbacks = fallbacks


# Global instance
selector_registry = SelectorRegistry()
