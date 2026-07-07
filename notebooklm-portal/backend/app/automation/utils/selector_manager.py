"""Selector auto-detection, testing, and versioning module."""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SelectorAutoDetector:
    """Auto-detects selectors on a page."""
    
    def __init__(self):
        self.detected_selectors: Dict[str, List[str]] = {}
    
    async def detect_selectors(self, page, element_type: str = "button") -> List[str]:
        """Detect available selectors for an element type."""
        selectors = []
        
        common_selectors = {
            "button": [
                'button',
                'button[type="submit"]',
                'button[type="button"]',
                '[role="button"]',
                'a.button',
                'input[type="submit"]',
                'input[type="button"]',
            ],
            "input": [
                'input[type="text"]',
                'input[type="email"]',
                'input[type="password"]',
                'input[type="url"]',
                'input[type="number"]',
                'textarea',
                '[contenteditable="true"]',
            ],
            "link": [
                'a[href]',
                'a[role="link"]',
                '[data-link]',
            ],
            "dialog": [
                '[role="dialog"]',
                '.modal',
                '.dialog',
                '[data-modal]',
            ],
        }
        
        for selector in common_selectors.get(element_type, []):
            try:
                count = await page.locator(selector).count()
                if count > 0:
                    selectors.append(selector)
            except Exception:
                pass
        
        self.detected_selectors[element_type] = selectors
        return selectors
    
    async def find_best_selector(self, page, element_description: str) -> Optional[str]:
        """Find the best selector for an element based on description."""
        element_type = "button"
        
        if "input" in element_description.lower() or "field" in element_description.lower():
            element_type = "input"
        elif "link" in element_description.lower():
            element_type = "link"
        elif "dialog" in element_description.lower() or "modal" in element_description.lower():
            element_type = "dialog"
        
        selectors = await self.detect_selectors(page, element_type)
        
        for selector in selectors:
            try:
                count = await page.locator(selector).count()
                if count > 0:
                    return selector
            except Exception:
                pass
        
        return None
    
    def get_detected_selectors(self) -> Dict[str, List[str]]:
        """Get all detected selectors."""
        return self.detected_selectors


class SelectorTester:
    """Tests selectors for validity and reliability."""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
    
    async def test_selector(self, page, selector: str, timeout: int = 5000) -> Dict[str, Any]:
        """Test if a selector works on the page."""
        start_time = datetime.now()
        
        try:
            count = await page.locator(selector).count()
            elapsed = (datetime.now() - start_time).total_seconds()
            
            result = {
                "selector": selector,
                "valid": count > 0,
                "count": count,
                "elapsed_time": elapsed,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            result = {
                "selector": selector,
                "valid": False,
                "count": 0,
                "error": str(e),
                "elapsed_time": elapsed,
                "timestamp": datetime.now().isoformat()
            }
        
        self.test_results.append(result)
        return result
    
    async def test_selectors_batch(self, page, selectors: List[str]) -> List[Dict[str, Any]]:
        """Test multiple selectors."""
        results = []
        for selector in selectors:
            result = await self.test_selector(page, selector)
            results.append(result)
        return results
    
    def get_test_report(self) -> Dict[str, Any]:
        """Get a report of all selector tests."""
        total = len(self.test_results)
        valid = sum(1 for r in self.test_results if r["valid"])
        
        return {
            "total_tested": total,
            "valid": valid,
            "invalid": total - valid,
            "results": self.test_results
        }


class SelectorVersionManager:
    """Manages selector versions for different UI versions."""
    
    def __init__(self, versions_dir: str = "~/.notebooklm/selector_versions"):
        self.versions_dir = Path(versions_dir).expanduser()
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.current_version: Optional[str] = None
    
    def save_version(self, version_name: str, selectors: Dict[str, str]) -> str:
        """Save a selector version."""
        version_file = self.versions_dir / f"{version_name}.json"
        
        data = {
            "version": version_name,
            "selectors": selectors,
            "created_at": datetime.now().isoformat()
        }
        
        with open(version_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.current_version = version_name
        logger.info(f"Selector version saved: {version_name}")
        return str(version_file)
    
    def load_version(self, version_name: str) -> Optional[Dict[str, str]]:
        """Load a selector version."""
        version_file = self.versions_dir / f"{version_name}.json"
        
        if not version_file.exists():
            return None
        
        with open(version_file, 'r') as f:
            data = json.load(f)
        
        self.current_version = version_name
        return data.get("selectors", {})
    
    def list_versions(self) -> List[str]:
        """List all saved versions."""
        versions = []
        for file in self.versions_dir.glob("*.json"):
            versions.append(file.stem)
        return sorted(versions)
    
    def get_current_version(self) -> Optional[str]:
        """Get current version name."""
        return self.current_version
    
    def delete_version(self, version_name: str) -> bool:
        """Delete a selector version."""
        version_file = self.versions_dir / f"{version_name}.json"
        
        if version_file.exists():
            version_file.unlink()
            return True
        return False
