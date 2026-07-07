from typing import List, Dict, Any
from ..browser_manager import BrowserManager


class BatchOutputGeneration:
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager

    async def generate_multiple_outputs(self, notebook_id: str, output_types: List[str]) -> Dict[str, Any]:
        results = []
        for output_type in output_types:
            result = await self.browser.generate_output(notebook_id, output_type)
            results.append({"type": output_type, "result": result})
        
        return {
            "total": len(output_types),
            "successful": sum(1 for r in results if r.get("result", {}).get("status") == "success"),
            "failed": sum(1 for r in results if r.get("result", {}).get("status") == "error"),
            "results": results
        }
