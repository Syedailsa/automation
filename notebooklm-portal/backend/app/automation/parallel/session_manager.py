import asyncio
import logging
from typing import Dict, Any, List
from .session_pool import SessionPool
from ..browser_manager import BrowserManager

logger = logging.getLogger(__name__)


class ParallelSessionManager:
    """Manages parallel browser sessions with proper lifecycle."""
    
    def __init__(self, session_pool: SessionPool):
        self.pool = session_pool
        self.browsers: Dict[str, BrowserManager] = {}

    async def execute_parallel(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tasks = []
        for op in operations:
            user_id = op.get("user_id", "default")
            session_id = await self.pool.acquire_session(user_id)
            if session_id:
                tasks.append(self._execute_with_session(session_id, op))
            else:
                tasks.append(asyncio.coroutine(lambda: {"status": "error", "error": "No sessions available"})())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def _execute_with_session(self, session_id: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        browser = None
        try:
            browser = BrowserManager()
            initialized = await browser.initialize()
            if not initialized:
                return {"session_id": session_id, "status": "error", "error": "Failed to initialize browser"}
            
            self.browsers[session_id] = browser
            result = await browser.execute_operation(operation)
            return {"session_id": session_id, "status": "success", "result": result}
        except Exception as e:
            logger.error(f"Session {session_id} execution error: {e}")
            return {"session_id": session_id, "status": "error", "error": str(e)}
        finally:
            if session_id in self.browsers:
                await self.browsers[session_id].close()
                del self.browsers[session_id]
            await self.pool.release_session(session_id)

    async def shutdown_all(self):
        """Gracefully close all active browser sessions."""
        for session_id in list(self.browsers.keys()):
            try:
                await self.browsers[session_id].close()
            except Exception as e:
                logger.error(f"Error closing session {session_id}: {e}")
        self.browsers.clear()
