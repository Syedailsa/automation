from typing import Dict, Any
from datetime import datetime


class HealthCheck:
    def __init__(self):
        self.checks = {}

    def register_check(self, name: str, check_func):
        self.checks[name] = check_func

    async def run_checks(self) -> Dict[str, Any]:
        results = {}
        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = {"status": "healthy", "result": result}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if all(r["status"] == "healthy" for r in results.values()) else "unhealthy",
            "checks": results
        }

    def get_health(self) -> Dict[str, Any]:
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "checks_registered": len(self.checks)
        }
