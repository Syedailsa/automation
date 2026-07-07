from typing import List, Dict, Any
from ..browser_manager import BrowserManager


class BatchNotebookCreation:
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager

    async def create_multiple_notebooks(self, notebooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        for notebook in notebooks:
            result = await self.browser.create_notebook(notebook.get("title", "Untitled"))
            results.append({"title": notebook.get("title"), "result": result})
        
        return {
            "total": len(notebooks),
            "successful": sum(1 for r in results if r.get("result", {}).get("status") == "success"),
            "failed": sum(1 for r in results if r.get("result", {}).get("status") == "error"),
            "results": results
        }
