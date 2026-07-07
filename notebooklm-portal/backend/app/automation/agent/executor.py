import logging
from typing import Dict, Any
from ..browser_manager import BrowserManager
from ..notebooks.notebook_manager import NotebookManager
from ..operations.source_operations import SourceOperations
from ..operations.generation_operations import GenerationOperations

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes agent actions using real automation classes."""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.notebooks = NotebookManager(browser_manager)
        self.source_ops = SourceOperations(browser_manager)
        self.generation_ops = GenerationOperations(browser_manager)

    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        action_map = {
            "create_notebook": self._create_notebook,
            "add_source": self._add_source,
            "generate_audio": self._generate_audio,
            "generate_video": self._generate_video,
            "generate_quiz": self._generate_quiz,
            "generate_flashcards": self._generate_flashcards,
            "generate_slides": self._generate_slides,
        }
        
        if action not in action_map:
            raise ValueError(f"Unknown action: {action}")
        
        return await action_map[action](params)

    async def _create_notebook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        title = params.get("title", "Untitled Notebook")
        result = await self.notebooks.create_notebook(title)
        if result.get("status") == "success":
            return {"status": "success", "notebook_id": result.get("notebook_id", title)}
        return {"status": "error", "error": result.get("error", "Failed to create notebook")}

    async def _add_source(self, params: Dict[str, Any]) -> Dict[str, Any]:
        notebook_id = params.get("notebook_id", "")
        source_type = params.get("source_type", "text")
        
        if source_type == "url":
            return await self.source_ops.add_url_source(notebook_id, params.get("url", ""))
        elif source_type == "text":
            return await self.source_ops.add_text_source(
                notebook_id, params.get("title", ""), params.get("content", "")
            )
        elif source_type == "youtube":
            return await self.source_ops.add_youtube_source(notebook_id, params.get("url", ""))
        elif source_type == "file":
            return await self.source_ops.add_file_source(notebook_id, params.get("file_path", ""))
        else:
            return {"status": "error", "error": f"Unknown source type: {source_type}"}

    async def _generate_audio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self.generation_ops.generate_audio(
            params.get("notebook_id", ""), params.get("instructions", "")
        )

    async def _generate_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self.generation_ops.generate_video(
            params.get("notebook_id", ""), params.get("style", "explainer")
        )

    async def _generate_quiz(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self.generation_ops.generate_quiz(
            params.get("notebook_id", ""), params.get("num_questions", 10)
        )

    async def _generate_flashcards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self.generation_ops.generate_flashcards(
            params.get("notebook_id", ""), params.get("num_cards", 20)
        )

    async def _generate_slides(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self.generation_ops.generate_slides(
            params.get("notebook_id", ""), params.get("format", "detailed")
        )
