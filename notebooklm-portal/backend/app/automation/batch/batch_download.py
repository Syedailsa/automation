from typing import List, Dict, Any
from ..browser_manager import BrowserManager


class BatchDownload:
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager

    async def download_multiple_files(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        for file_info in files:
            result = await self.browser.download_file(file_info.get("url"), file_info.get("output_path"))
            results.append({"file": file_info.get("url"), "result": result})
        
        return {
            "total": len(files),
            "successful": sum(1 for r in results if r.get("result", {}).get("status") == "success"),
            "failed": sum(1 for r in results if r.get("result", {}).get("status") == "error"),
            "results": results
        }
