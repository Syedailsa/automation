class Selectors:
    """Central registry of UI selectors for NotebookLM."""
    
    # Authentication
    SIGN_IN_BUTTON = 'button:has-text("Sign in")'
    GOOGLE_ACCOUNT_SELECTOR = 'div[data-email]'
    LOGIN_INPUT = 'input[type="email"], input[name="identifier"]'
    
    # Notebook Operations
    NOTEBOOK_LIST = '[data-notebook-id]'
    NEW_NOTEBOOK_BUTTON = 'button:has-text("New Notebook")'
    NOTEBOOK_TITLE = 'h1.notebook-title, h2.notebook-title'
    NOTEBOOK_CARD = '[data-notebook-id]'
    
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
    DOWNLOAD_MENU = '[role="menu"]'
    
    # Common Elements
    DIALOG = '[role="dialog"]'
    TEXTAREA = 'textarea'
    INPUT = 'input[type="text"]'
    BUTTON = 'button'
    
    # Status Indicators
    PROCESSING = '[data-status="processing"]'
    READY = '[data-status="ready"]'
    ERROR = '[data-status="error"]'
