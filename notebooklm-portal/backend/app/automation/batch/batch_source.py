import logging
from typing import List, Dict, Any
from ..browser_manager import BrowserManager
from ..operations.source_operations import SourceOperations

logger = logging.getLogger(__name__)


class BatchSourceAddition:
    """Batch add multiple sources using real SourceOperations."""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.ops = SourceOperations(browser_manager)

    async def add_multiple_sources(self, notebook_id: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        for source in sources:
            source_type = source.get("type", "text")
            try:
                if source_type == "url":
                    result = await self.ops.add_url_source(notebook_id, source.get("url", ""))
                elif source_type == "text":
                    result = await self.ops.add_text_source(
                        notebook_id, source.get("title", ""), source.get("content", "")
                    )
                elif source_type == "youtube":
                    result = await self.ops.add_youtube_source(notebook_id, source.get("url", ""))
                elif source_type == "file":
                    result = await self.ops.add_file_source(notebook_id, source.get("file_path", ""))
                else:
                    result = {"status": "error", "error": f"Unknown source type: {source_type}"}
            except Exception as e:
                logger.error(f"Batch source error: {e}")
                result = {"status": "error", "error": str(e)}
            results.append({"source": source, "result": result})
        
        return {
            "total": len(sources),
            "successful": sum(1 for r in results if r.get("result", {}).get("status") == "success"),
            "failed": sum(1 for r in results if r.get("result", {}).get("status") == "error"),
            "results": results
        }
