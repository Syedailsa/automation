"""Manual intervention triggers and graceful degradation module."""
import asyncio
from typing import Optional, Dict, Any, Callable, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class InterventionType(Enum):
    """Types of manual intervention."""
    CAPTCHA = "captcha"
    LOGIN_REQUIRED = "login_required"
    RATE_LIMITED = "rate_limited"
    UI_CHANGED = "ui_changed"
    ERROR_OCCURRED = "error_occurred"
    SESSION_EXPIRED = "session_expired"


class ManualInterventionTrigger:
    """Triggers manual intervention when needed."""
    
    def __init__(self):
        self.triggers: Dict[InterventionType, Callable] = {}
        self.intervention_history: List[Dict[str, Any]] = []
    
    def register_trigger(self, intervention_type: InterventionType, handler: Callable):
        """Register a handler for an intervention type."""
        self.triggers[intervention_type] = handler
        logger.info(f"Trigger registered for {intervention_type.value}")
    
    async def trigger_intervention(self, intervention_type: InterventionType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger manual intervention."""
        handler = self.triggers.get(intervention_type)
        
        if not handler:
            logger.warning(f"No handler registered for {intervention_type.value}")
            return {"status": "no_handler", "type": intervention_type.value}
        
        try:
            result = await handler(context)
            
            self.intervention_history.append({
                "type": intervention_type.value,
                "context": context,
                "result": result,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            return result
        except Exception as e:
            logger.error(f"Intervention handler failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_intervention_history(self) -> List[Dict[str, Any]]:
        """Get history of interventions."""
        return self.intervention_history


class GracefulDegradation:
    """Handles graceful degradation when operations fail."""
    
    def __init__(self):
        self.fallback_strategies: Dict[str, Callable] = {}
        self.degradation_log: List[Dict[str, Any]] = []
    
    def register_fallback(self, operation_name: str, fallback_func: Callable):
        """Register a fallback function for an operation."""
        self.fallback_strategies[operation_name] = fallback_func
        logger.info(f"Fallback registered for {operation_name}")
    
    async def execute_with_fallback(self, operation_name: str, primary_func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute operation with fallback on failure."""
        try:
            result = await primary_func(*args, **kwargs)
            return {"status": "success", "result": result, "used_fallback": False}
        except Exception as e:
            logger.warning(f"Primary operation failed: {e}")
            
            fallback = self.fallback_strategies.get(operation_name)
            if fallback:
                try:
                    fallback_result = await fallback(*args, **kwargs)
                    
                    self.degradation_log.append({
                        "operation": operation_name,
                        "primary_error": str(e),
                        "fallback_used": True,
                        "timestamp": asyncio.get_event_loop().time()
                    })
                    
                    return {"status": "degraded", "result": fallback_result, "used_fallback": True}
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
            
            return {"status": "error", "error": str(e), "used_fallback": False}
    
    def get_degradation_log(self) -> List[Dict[str, Any]]:
        """Get log of degradation events."""
        return self.degradation_log
    
    def get_degradation_stats(self) -> Dict[str, Any]:
        """Get statistics about degradation."""
        total = len(self.degradation_log)
        fallback_used = sum(1 for log in self.degradation_log if log.get("fallback_used"))
        
        return {
            "total_events": total,
            "fallback_used": fallback_used,
            "fallback_rate": (fallback_used / total * 100) if total > 0 else 0
        }


class FallbackScenarioTester:
    """Tests fallback scenarios."""
    
    def __init__(self, degradation: GracefulDegradation):
        self.degradation = degradation
        self.test_results: List[Dict[str, Any]] = []
    
    async def test_fallback_scenario(self, operation_name: str, primary_should_fail: bool = True) -> Dict[str, Any]:
        """Test a fallback scenario."""
        async def mock_primary():
            if primary_should_fail:
                raise Exception("Mock primary failure")
            return "primary_success"
        
        async def mock_fallback():
            return "fallback_success"
        
        self.degradation.register_fallback(operation_name, mock_fallback)
        
        result = await self.degradation.execute_with_fallback(operation_name, mock_primary)
        
        self.test_results.append({
            "operation": operation_name,
            "expected_primary_failure": primary_should_fail,
            "result": result,
            "test_passed": result.get("used_fallback") == primary_should_fail
        })
        
        return result
    
    async def run_fallback_tests(self, operations: List[str]) -> Dict[str, Any]:
        """Run fallback tests for multiple operations."""
        results = []
        
        for operation in operations:
            result = await self.test_fallback_scenario(operation, primary_should_fail=True)
            results.append(result)
        
        total = len(results)
        passed = sum(1 for r in self.test_results if r.get("test_passed"))
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "results": results
        }
