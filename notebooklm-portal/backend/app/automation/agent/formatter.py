from typing import Dict, Any, Optional
from datetime import datetime


class ResultFormatter:
    def format_success(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

    def format_error(self, error: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "error": error,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

    def format_partial(self, data: Dict[str, Any], completed: list, failed: list) -> Dict[str, Any]:
        return {
            "status": "partial",
            "data": data,
            "completed": completed,
            "failed": failed,
            "timestamp": datetime.now().isoformat()
        }
