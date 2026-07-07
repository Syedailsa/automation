from typing import Dict, Any, Optional
from ..browser_manager import BrowserManager
from .executor import ActionExecutor
from .formatter import ResultFormatter


class AgentIntegration:
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.executor = ActionExecutor(browser_manager)
        self.formatter = ResultFormatter()

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = await self.executor.execute(action, params)
            return self.formatter.format_success(result)
        except Exception as e:
            return self.formatter.format_error(str(e))

    async def handle_concurrent_sessions(self, sessions: list) -> list:
        results = []
        for session in sessions:
            result = await self.execute_action(session["action"], session["params"])
            results.append(result)
        return results
