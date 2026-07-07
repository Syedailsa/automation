from typing import Dict, Any, List
from datetime import datetime


class StatusDashboard:
    def __init__(self):
        self.metrics = {}

    def update_metric(self, name: str, value: Any):
        self.metrics[name] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

    def get_dashboard(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "summary": {
                "total_metrics": len(self.metrics),
                "last_updated": max([m["timestamp"] for m in self.metrics.values()], default=None)
            }
        }

    def get_metric(self, name: str) -> Dict[str, Any]:
        return self.metrics.get(name, {"value": None, "timestamp": None})
