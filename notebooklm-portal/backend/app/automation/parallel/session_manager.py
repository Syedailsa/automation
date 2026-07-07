import asyncio
from typing import Dict, Any, List
from .session_pool import SessionPool
from ..browser_manager import BrowserManager


class ParallelSessionManager:
    def __init__(self, session_pool: SessionPool):
        self.pool = session_pool
        self.browsers: Dict[str, BrowserManager] = {}

    async def execute_parallel(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tasks = []
        for op in operations:
            session_id = await self.pool.acquire_session(op.get("user_id", "default"))
            if session_id:
                tasks.append(self._execute_with_session(session_id, op))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def _execute_with_session(self, session_id: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        try:
            browser = BrowserManager()
            self.browsers[session_id] = browser
            result = await browser.execute_operation(operation)
            return {"session_id": session_id, "status": "success", "result": result}
        except Exception as e:
            return {"session_id": session_id, "status": "error", "error": str(e)}
        finally:
            await self.pool.release_session(session_id)
            if session_id in self.browsers:
                del self.browsers[session_id]
