from typing import Dict, Any, List
from ..browser_manager import BrowserManager
from ..api.notebooklm_api import NotebookLMAPI
from ..agent.integration import AgentIntegration


class IntegrationTest:
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.api = NotebookLMAPI()
        self.agent = AgentIntegration(browser_manager)

    async def test_api_integration(self, token: str) -> Dict[str, Any]:
        try:
            status = await self.api.status(token)
            return {"test": "api_integration", "status": "success", "result": status}
        except Exception as e:
            return {"test": "api_integration", "status": "error", "error": str(e)}

    async def test_agent_integration(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = await self.agent.execute_action(action, params)
            return {"test": "agent_integration", "status": "success", "result": result}
        except Exception as e:
            return {"test": "agent_integration", "status": "error", "error": str(e)}

    async def test_browser_operations(self) -> Dict[str, Any]:
        try:
            result = await self.browser.test_operation()
            return {"test": "browser_operations", "status": "success", "result": result}
        except Exception as e:
            return {"test": "browser_operations", "status": "error", "error": str(e)}

    async def run_full_integration_test(self, token: str) -> Dict[str, Any]:
        results = []
        results.append(await self.test_api_integration(token))
        results.append(await self.test_agent_integration("test", {}))
        results.append(await self.test_browser_operations())
        
        return {
            "total_tests": len(results),
            "passed": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }
