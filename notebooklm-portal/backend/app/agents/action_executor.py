from typing import Any, Dict, List, Optional


class NullToolExecutor:
    async def execute_single(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": action.get("action", "unknown"),
            "status": "simulated",
            "note": "No browser page available. Running in headless/API mode.",
        }

    async def execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
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
        return results


class ActionExecutor:
    def __init__(self, page=None):
        self.page = page
        self._managers = None

    def _lazy_init(self):
        if self._managers is not None:
            return
        if self.page is None:
            self._managers = None
            return
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
            self._managers = {
                "notebook": NotebookManager(self.page),
                "source": SourceManager(self.page),
                "audio": AudioGenerator(self.page),
                "video": VideoGenerator(self.page),
                "quiz": QuizGenerator(self.page),
                "flashcard": FlashcardGenerator(self.page),
                "slide": SlideGenerator(self.page),
            }
        except ImportError:
            self._managers = None

    async def execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
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
        return results

    async def execute_single(self, action: Dict[str, Any]) -> Any:
        self._lazy_init()
        if self._managers is None:
            return NullToolExecutor().execute_single(action)

        action_type = action.get("action")
        params = action.get("params", {})

        if action_type == "create_notebook":
            return await self._managers["notebook"].create_notebook(
                params.get("title", "Untitled")
            )
        elif action_type == "add_source":
            source_type = params.get("type", "url")
            if source_type == "url":
                return await self._managers["source"].add_url_source(params.get("url"))
            elif source_type == "text":
                return await self._managers["source"].add_text_source(
                    params.get("title"), params.get("content")
                )
            elif source_type == "youtube":
                return await self._managers["source"].add_youtube_source(
                    params.get("url")
                )
        elif action_type == "generate_audio":
            return await self._managers["audio"].generate_audio(
                params.get("instructions")
            )
        elif action_type == "generate_video":
            return await self._managers["video"].generate_video(
                params.get("style")
            )
        elif action_type == "generate_quiz":
            return await self._managers["quiz"].generate_quiz(
                params.get("num_questions")
            )
        elif action_type == "generate_flashcards":
            return await self._managers["flashcard"].generate_flashcards(
                params.get("num_cards")
            )
        elif action_type == "generate_slides":
            return await self._managers["slide"].generate_slides(
                params.get("format")
            )
        elif action_type == "list_notebooks":
            return await self._managers["notebook"].list_notebooks()
        else:
            raise ValueError(f"Unknown action: {action_type}")
