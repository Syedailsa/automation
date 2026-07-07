import logging
from typing import List, Dict, Any
from ..browser_manager import BrowserManager
from ..notebooks.notebook_manager import NotebookManager

logger = logging.getLogger(__name__)


class BatchNotebookCreation:
    """Batch create multiple notebooks using real NotebookManager."""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.manager = NotebookManager(browser_manager)

    async def create_multiple_notebooks(self, notebooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        for notebook in notebooks:
            title = notebook.get("title", "Untitled")
            try:
                result = await self.manager.create_notebook(title)
            except Exception as e:
                logger.error(f"Batch notebook creation error: {e}")
                result = {"status": "error", "error": str(e)}
            results.append({"title": title, "result": result})
        
        return {
            "total": len(notebooks),
            "successful": sum(1 for r in results if r.get("result", {}).get("status") == "success"),
            "failed": sum(1 for r in results if r.get("result", {}).get("status") == "error"),
            "results": results
        }
