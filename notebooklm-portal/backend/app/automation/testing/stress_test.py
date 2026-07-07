"""Stress testing module for P4 automation."""
import asyncio
import time
from typing import Dict, Any, List, Callable
import logging

logger = logging.getLogger(__name__)


class StressTester:
    """Performs stress testing on browser operations."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    async def run_stress_test(self, operation_func: Callable, num_iterations: int = 100, concurrency: int = 10) -> Dict[str, Any]:
        """Run stress test on an operation."""
        start_time = time.time()
        successful = 0
        failed = 0
        errors: List[str] = []
        
        semaphore = asyncio.Semaphore(concurrency)
        
        async def run_single_operation(index: int):
            nonlocal successful, failed
            async with semaphore:
                try:
                    await operation_func()
                    successful += 1
                except Exception as e:
                    failed += 1
                    errors.append(str(e))
        
        tasks = [run_single_operation(i) for i in range(num_iterations)]
        await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        result = {
            "total_iterations": num_iterations,
            "concurrency": concurrency,
            "successful": successful,
            "failed": failed,
            "elapsed_time": round(elapsed, 2),
            "operations_per_second": round(num_iterations / elapsed, 2),
            "unique_errors": list(set(errors))
        }
        
        self.results.append(result)
        return result
    
    async def run_memory_stress_test(self, browser_manager, num_operations: int = 50) -> Dict[str, Any]:
        """Run stress test monitoring memory usage."""
        from .memory_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer()
        memory_readings: List[Dict[str, Any]] = []
        
        for i in range(num_operations):
            try:
                await browser_manager.test_operation()
                
                memory_info = await optimizer.check_memory_usage()
                memory_readings.append({
                    "iteration": i,
                    "memory_mb": memory_info.get("current_mb", 0)
                })
                
                if memory_info.get("needs_cleanup"):
                    await optimizer.cleanup_memory()
            except Exception as e:
                logger.error(f"Stress test iteration {i} failed: {e}")
        
        memory_values = [r["memory_mb"] for r in memory_readings]
        
        return {
            "total_operations": num_operations,
            "memory_readings": memory_readings,
            "avg_memory_mb": round(sum(memory_values) / len(memory_values), 2) if memory_values else 0,
            "max_memory_mb": round(max(memory_values), 2) if memory_values else 0,
            "min_memory_mb": round(min(memory_values), 2) if memory_values else 0
        }
    
    def get_stress_test_report(self) -> Dict[str, Any]:
        """Get stress test report."""
        if not self.results:
            return {"status": "no_tests_run"}
        
        total_operations = sum(r["total_iterations"] for r in self.results)
        total_successful = sum(r["successful"] for r in self.results)
        total_failed = sum(r["failed"] for r in self.results)
        
        return {
            "total_tests": len(self.results),
            "total_operations": total_operations,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "overall_success_rate": round((total_successful / total_operations * 100), 2) if total_operations > 0 else 0,
            "results": self.results
        }


class LoadTester:
    """Performs load testing with increasing concurrency."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    async def run_load_test(self, operation_func: Callable, max_concurrency: int = 50, step: int = 5) -> Dict[str, Any]:
        """Run load test with increasing concurrency."""
        stress_tester = StressTester()
        
        for concurrency in range(step, max_concurrency + 1, step):
            result = await stress_tester.run_stress_test(
                operation_func,
                num_iterations=concurrency * 2,
                concurrency=concurrency
            )
            
            self.results.append({
                "concurrency": concurrency,
                "result": result
            })
            
            logger.info(f"Load test at concurrency {concurrency}: {result['operations_per_second']} ops/sec")
        
        return {
            "max_concurrency": max_concurrency,
            "step": step,
            "results": self.results
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.results:
            return {"status": "no_tests_run"}
        
        ops_per_second = [r["result"]["operations_per_second"] for r in self.results]
        
        return {
            "total_concurrency_levels": len(self.results),
            "avg_ops_per_second": round(sum(ops_per_second) / len(ops_per_second), 2),
            "max_ops_per_second": round(max(ops_per_second), 2),
            "min_ops_per_second": round(min(ops_per_second), 2)
        }
