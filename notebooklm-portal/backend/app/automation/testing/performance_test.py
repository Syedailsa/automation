import time
from typing import Dict, Any, List
from ..browser_manager import BrowserManager


class PerformanceTest:
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.metrics = []

    async def measure_operation_time(self, operation_name: str, operation_func) -> Dict[str, Any]:
        start_time = time.time()
        try:
            result = await operation_func()
            end_time = time.time()
            duration = end_time - start_time
            
            self.metrics.append({
                "operation": operation_name,
                "duration": duration,
                "status": "success"
            })
            
            return {
                "operation": operation_name,
                "duration": duration,
                "status": "success"
            }
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            self.metrics.append({
                "operation": operation_name,
                "duration": duration,
                "status": "error",
                "error": str(e)
            })
            
            return {
                "operation": operation_name,
                "duration": duration,
                "status": "error",
                "error": str(e)
            }

    async def run_performance_test(self, num_iterations: int = 10) -> Dict[str, Any]:
        results = []
        for i in range(num_iterations):
            result = await self.measure_operation_time(
                f"test_operation_{i}",
                self.browser.test_operation
            )
            results.append(result)
        
        avg_duration = sum(r["duration"] for r in results) / len(results)
        
        return {
            "total_iterations": num_iterations,
            "average_duration": avg_duration,
            "results": results
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        if not self.metrics:
            return {"total_operations": 0}
        
        durations = [m["duration"] for m in self.metrics]
        return {
            "total_operations": len(self.metrics),
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations)
        }
