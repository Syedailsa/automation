from typing import Dict, Any, List
from ..automation import NotebookManager, SourceManager, AudioGenerator, VideoGenerator, QuizGenerator, FlashcardGenerator, SlideGenerator


class ActionExecutor:
    def __init__(self, page):
        self.page = page
        self.notebook_manager = NotebookManager(page)
        self.source_manager = SourceManager(page)
        self.audio_generator = AudioGenerator(page)
        self.video_generator = VideoGenerator(page)
        self.quiz_generator = QuizGenerator(page)
        self.flashcard_generator = FlashcardGenerator(page)
        self.slide_generator = SlideGenerator(page)
    
    async def execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for action in actions:
            try:
                result = await self._execute_single(action)
                results.append({"action": action["action"], "status": "success", "result": result})
            except Exception as e:
                results.append({"action": action["action"], "status": "error", "error": str(e)})
        return results
    
    async def _execute_single(self, action: Dict[str, Any]) -> Any:
        action_type = action.get("action")
        params = action.get("params", {})
        
        if action_type == "create_notebook":
            return await self.notebook_manager.create_notebook(params.get("title", "Untitled"))
        elif action_type == "add_source":
            source_type = params.get("type", "url")
            if source_type == "url":
                return await self.source_manager.add_url_source(params.get("url"))
            elif source_type == "text":
                return await self.source_manager.add_text_source(params.get("title"), params.get("content"))
            elif source_type == "youtube":
                return await self.source_manager.add_youtube_source(params.get("url"))
        elif action_type == "generate_audio":
            return await self.audio_generator.generate_audio(params.get("instructions"))
        elif action_type == "generate_video":
            return await self.video_generator.generate_video(params.get("style"))
        elif action_type == "generate_quiz":
            return await self.quiz_generator.generate_quiz(params.get("num_questions"))
        elif action_type == "generate_flashcards":
            return await self.flashcard_generator.generate_flashcards(params.get("num_cards"))
        elif action_type == "generate_slides":
            return await self.slide_generator.generate_slides(params.get("format"))
        else:
            raise ValueError(f"Unknown action: {action_type}")
