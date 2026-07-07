import logging
from typing import List, Dict, Any
from ..browser_manager import BrowserManager
from ..operations.generation_operations import GenerationOperations

logger = logging.getLogger(__name__)


class BatchOutputGeneration:
    """Batch generate multiple outputs using real GenerationOperations."""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.ops = GenerationOperations(browser_manager)

    async def generate_multiple_outputs(self, notebook_id: str, output_types: List[str]) -> Dict[str, Any]:
        results = []
        for output_type in output_types:
            try:
                if output_type == "audio":
                    result = await self.ops.generate_audio(notebook_id)
                elif output_type == "video":
                    result = await self.ops.generate_video(notebook_id)
                elif output_type == "quiz":
                    result = await self.ops.generate_quiz(notebook_id)
                elif output_type == "flashcards":
                    result = await self.ops.generate_flashcards(notebook_id)
                elif output_type == "slides":
                    result = await self.ops.generate_slides(notebook_id)
                else:
                    result = {"status": "error", "error": f"Unknown output type: {output_type}"}
            except Exception as e:
                logger.error(f"Batch output error: {e}")
                result = {"status": "error", "error": str(e)}
            results.append({"type": output_type, "result": result})
        
        return {
            "total": len(output_types),
            "successful": sum(1 for r in results if r.get("result", {}).get("status") == "success"),
            "failed": sum(1 for r in results if r.get("result", {}).get("status") == "error"),
            "results": results
        }
