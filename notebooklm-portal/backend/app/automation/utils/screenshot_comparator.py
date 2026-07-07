"""Screenshot comparison and visual regression testing module."""
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ScreenshotComparator:
    """Compares screenshots for visual regression testing."""
    
    def __init__(self, baseline_dir: str = "~/.notebooklm/baselines"):
        self.baseline_dir = Path(baseline_dir).expanduser()
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.comparison_results: List[Dict[str, Any]] = []
    
    def calculate_hash(self, image_path: str) -> str:
        """Calculate MD5 hash of an image file."""
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    async def capture_baseline(self, page, name: str) -> str:
        """Capture a baseline screenshot."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"baseline_{name}_{timestamp}.png"
        filepath = self.baseline_dir / filename
        
        await page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Baseline captured: {filepath}")
        return str(filepath)
    
    async def compare_with_baseline(self, page, name: str, baseline_path: str) -> Dict[str, Any]:
        """Compare current page with baseline screenshot."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        current_filename = f"current_{name}_{timestamp}.png"
        current_path = self.baseline_dir / current_filename
        
        await page.screenshot(path=str(current_path), full_page=True)
        
        baseline_hash = self.calculate_hash(baseline_path)
        current_hash = self.calculate_hash(str(current_path))
        
        is_match = baseline_hash == current_hash
        
        result = {
            "name": name,
            "baseline": baseline_path,
            "current": str(current_path),
            "baseline_hash": baseline_hash,
            "current_hash": current_hash,
            "is_match": is_match,
            "timestamp": timestamp
        }
        
        self.comparison_results.append(result)
        
        if not is_match:
            logger.warning(f"Visual regression detected for {name}")
        
        return result
    
    def get_regression_report(self) -> Dict[str, Any]:
        """Get a report of all visual regressions."""
        total = len(self.comparison_results)
        passed = sum(1 for r in self.comparison_results if r["is_match"])
        failed = total - passed
        
        return {
            "total_comparisons": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "results": self.comparison_results
        }
    
    async def run_visual_regression_test(self, page, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run visual regression tests."""
        results = []
        
        for test_case in test_cases:
            name = test_case.get("name")
            url = test_case.get("url")
            baseline = test_case.get("baseline")
            
            if url:
                await page.goto(url)
            
            if baseline:
                result = await self.compare_with_baseline(page, name, baseline)
            else:
                baseline_path = await self.capture_baseline(page, name)
                result = {"name": name, "baseline": baseline_path, "status": "baseline_created"}
            
            results.append(result)
        
        return {
            "total_tests": len(test_cases),
            "results": results,
            "report": self.get_regression_report()
        }


class ScreenshotUploader:
    """Uploads screenshots to storage or external service."""
    
    def __init__(self, upload_dir: str = "~/.notebooklm/uploads"):
        self.upload_dir = Path(upload_dir).expanduser()
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.uploaded_files: List[Dict[str, Any]] = []
    
    async def upload_screenshot(self, screenshot_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Upload a screenshot."""
        source_path = Path(screenshot_path)
        
        if not source_path.exists():
            return {"status": "error", "message": "Screenshot file not found"}
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_filename = f"upload_{source_path.stem}_{timestamp}{source_path.suffix}"
        dest_path = self.upload_dir / dest_filename
        
        import shutil
        shutil.copy2(str(source_path), str(dest_path))
        
        upload_result = {
            "original_path": str(source_path),
            "uploaded_path": str(dest_path),
            "filename": dest_filename,
            "size": dest_path.stat().st_size,
            "metadata": metadata or {},
            "timestamp": timestamp
        }
        
        self.uploaded_files.append(upload_result)
        logger.info(f"Screenshot uploaded: {dest_path}")
        
        return upload_result
    
    def get_upload_history(self) -> List[Dict[str, Any]]:
        """Get history of uploaded screenshots."""
        return self.uploaded_files
