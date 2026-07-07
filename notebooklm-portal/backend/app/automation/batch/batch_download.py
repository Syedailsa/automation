import logging
from typing import List, Dict, Any
from ..browser_manager import BrowserManager
from ..outputs.download_manager import DownloadManager

logger = logging.getLogger(__name__)


class BatchDownload:
    """Batch download multiple files using real DownloadManager."""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager

    async def download_multiple_files(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        page = await self.browser.get_page()
        if not page:
            return {"total": len(files), "successful": 0, "failed": len(files), "results": []}
        
        dm = DownloadManager(page)
        results = []
        for file_info in files:
            try:
                artifact_type = file_info.get("type", "unknown")
                output_path = file_info.get("output_path")
                saved_path = await dm.download_artifact(artifact_type, output_path)
                if saved_path:
                    results.append({"file": file_info, "result": {"status": "success", "path": saved_path}})
                else:
                    results.append({"file": file_info, "result": {"status": "error", "error": "Download failed"}})
            except Exception as e:
                logger.error(f"Batch download error: {e}")
                results.append({"file": file_info, "result": {"status": "error", "error": str(e)}})
        
        return {
            "total": len(files),
            "successful": sum(1 for r in results if r.get("result", {}).get("status") == "success"),
            "failed": sum(1 for r in results if r.get("result", {}).get("status") == "error"),
            "results": results
        }
