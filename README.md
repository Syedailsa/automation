# NotebookLM Playwright Agent

A comprehensive automation agent for Google NotebookLM that uses browser-based authentication (no API keys required).

## Features

- **No API Keys Required** - Uses browser cookies for authentication
- **Multi-Account Support** - Manage multiple Google accounts via profiles
- **Notebook Management** - Create, list, open, delete notebooks
- **Source Management** - Add URLs, text, files, and YouTube videos
- **Output Generation** - Generate audio, video, quizzes, flashcards, slides
- **Resilience** - Retry logic, rate limiting, human-like delays
- **Error Handling** - Screenshots on error, video recording option

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd notebooklm-playwright

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium chrome
playwright install-deps  # System dependencies (Linux)
```

## Configuration

Copy `.env.example` to `.env` and modify settings:

```bash
cp .env.example .env
```

## Usage

### First Time Setup (Login)

```bash
python -m src.main --login
```

This will open a browser window for you to complete Google login.

### Basic Commands

```bash
# List notebooks
python -m src.main --list

# Create a notebook
python -m src.main --create "My Research"

# Add URL source
python -m src.main --add-url "https://example.com/article"

# Add text source
python -m src.main --add-text "My Notes" "Content of the notes..."

# Add file source
python -m src.main --add-file ./document.pdf

# Generate audio
python -m src.main --generate-audio

# Generate video
python -m src.main --generate-video

# Generate quiz
python -m src.main --generate-quiz
```

### Using in Code

```python
import asyncio
from src.main import NotebookLMAgent

async def main():
    agent = NotebookLMAgent(profile_name="default")
    
    try:
        # Start the agent
        await agent.start(headless=False)
        
        # Navigate to NotebookLM
        await agent.navigate_to_notebooklm()
        
        # Create notebook
        notebook_id = await agent.create_notebook("My Research")
        
        # Add sources
        await agent.add_url_source("https://example.com/article")
        await agent.add_text_source("Notes", "My research notes")
        
        # Generate audio
        await agent.generate_audio("Create an engaging overview")
        
    finally:
        await agent.stop()

asyncio.run(main())
```

## Project Structure

```
notebooklm-playwright/
├── src/
│   ├── config/          # Configuration settings
│   ├── auth/            # Authentication management
│   ├── notebooks/       # Notebook operations
│   ├── outputs/         # Output generation
│   ├── resilience/      # Retry, rate limiting, delays
│   ├── utils/           # Utilities (logging, screenshots)
│   └── main.py          # Main entry point
├── tests/               # Test suite
├── config/              # Configuration files
├── storage/             # Persistent storage
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## Authentication

The agent uses browser-based authentication. When you run `--login`, it will:

1. Open a Chromium browser window
2. Navigate to NotebookLM
3. Wait for you to complete Google sign-in
4. Save session cookies for future use

Session cookies are stored in `~/.notebooklm/profiles/<profile>/storage_state.json`.

## Multi-Account Support

Use the `--profile` flag to manage multiple Google accounts:

```bash
# Login with work account
python -m src.main --profile work --login

# Login with personal account
python -m src.main --profile personal --login

# Use specific profile
python -m src.main --profile work --list
```

## Error Handling

- **Screenshots**: Error screenshots are saved to `~/.notebooklm/screenshots/`
- **Logs**: Detailed logs are saved to `~/.notebooklm/logs/`
- **Retry**: Failed operations are automatically retried
- **Rate Limiting**: Requests are throttled to avoid detection

## Testing

```bash
# Run unit tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run integration tests (requires valid session)
pytest tests/test_integration.py -v -m integration
```

## License

MIT License
