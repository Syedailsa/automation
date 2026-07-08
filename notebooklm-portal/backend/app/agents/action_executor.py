"""Action executor — executes NotebookLM actions via the server session.

Uses the single server-side Google account to drive all operations.
"""
from typing import Any, Dict, List

from app.services.playwright_session import session_service


class ActionExecutor:
    """Executes NotebookLM actions using the server's shared browser session."""

    def __init__(self):
        self._managers = None
        self._page = None

    async def _get_page(self):
        """Get a page from the server session."""
        if self._page is None:
            self._page = await session_service.get_authenticated_page()
        return self._page

    async def _init_managers(self, page):
        """Initialize automation managers with the page."""
        try:
            from ..automation import (
                NotebookManager,
                SourceManager,
                AudioGenerator,
                VideoGenerator,
                QuizGenerator,
                FlashcardGenerator,
                SlideGenerator,
            )
            return {
                "notebook": NotebookManager(page),
                "source": SourceManager(page),
                "audio": AudioGenerator(page),
                "video": VideoGenerator(page),
                "quiz": QuizGenerator(page),
                "flashcard": FlashcardGenerator(page),
                "slide": SlideGenerator(page),
            }
        except ImportError:
            return None

    async def execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a list of actions and return results."""
        results = []
        page = await self._get_page()
        if not page:
            return [
                {
                    "action": a.get("action", "unknown"),
                    "status": "error",
                    "error": "Could not connect to NotebookLM",
                }
                for a in actions
            ]

        try:
            self._managers = await self._init_managers(page)
            for action in actions:
                try:
                    result = await self.execute_single(action)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "action": action.get("action", "unknown"),
                        "status": "error",
                        "error": str(e),
                    })
        finally:
            await page.close()
            self._page = None
            self._managers = None

        return results

    async def execute_single(self, action: Dict[str, Any]) -> Any:
        """Execute a single action."""
        if self._managers is None:
            return {
                "action": action.get("action", "unknown"),
                "status": "error",
                "error": "Automation managers not initialized",
            }

        action_type = action.get("action")
        params = action.get("params", {})

        if action_type == "create_notebook":
            result = await self._managers["notebook"].create_notebook(
                params.get("title", "Untitled")
            )
            return {"action": action_type, "status": "success", "result": result}

        elif action_type == "add_source":
            source_type = params.get("type", "url")
            if source_type == "url":
                result = await self._managers["source"].add_url_source(params.get("url"))
            elif source_type == "text":
                result = await self._managers["source"].add_text_source(
                    params.get("title"), params.get("content")
                )
            elif source_type == "youtube":
                result = await self._managers["source"].add_youtube_source(params.get("url"))
            else:
                return {"action": action_type, "status": "error", "error": f"Unknown source type: {source_type}"}
            return {"action": action_type, "status": "success", "result": result}

        elif action_type == "generate_audio":
            result = await self._managers["audio"].generate_audio(params.get("instructions"))
            return {"action": action_type, "status": "success", "result": result}

        elif action_type == "generate_video":
            result = await self._managers["video"].generate_video(params.get("style"))
            return {"action": action_type, "status": "success", "result": result}

        elif action_type == "generate_quiz":
            result = await self._managers["quiz"].generate_quiz(params.get("num_questions"))
            return {"action": action_type, "status": "success", "result": result}

        elif action_type == "generate_flashcards":
            result = await self._managers["flashcard"].generate_flashcards(params.get("num_cards"))
            return {"action": action_type, "status": "success", "result": result}

        elif action_type == "generate_slides":
            result = await self._managers["slide"].generate_slides(params.get("format"))
            return {"action": action_type, "status": "success", "result": result}

        elif action_type == "list_notebooks":
            result = await self._managers["notebook"].list_notebooks()
            return {"action": action_type, "status": "success", "result": result}

        else:
            return {"action": action_type, "status": "error", "error": f"Unknown action: {action_type}"}
