from typing import List, Dict, Any
from ..browser_manager import BrowserManager


class BatchSourceAddition:
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager

    async def add_multiple_sources(self, notebook_id: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        for source in sources:
            result = await self.browser.add_source(notebook_id, source)
            results.append(result)
        
        return {
            "total": len(sources),
            "successful": sum(1 for r in results if r.get("status") == "success"),
            "failed": sum(1 for r in results if r.get("status") == "error"),
            "results": results
        }
