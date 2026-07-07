from typing import Dict, Any, List
from datetime import datetime
from .session_pool import SessionPool, BrowserSession


class SessionHealthMonitor:
    def __init__(self, session_pool: SessionPool):
        self.pool = session_pool
        self.health_checks: Dict[str, Dict[str, Any]] = {}

    async def check_health(self, session_id: str) -> Dict[str, Any]:
        session = self.pool.sessions.get(session_id)
        if not session:
            return {"status": "not_found"}
        
        return {
            "session_id": session_id,
            "is_active": session.is_active,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "health": "healthy" if session.is_active else "inactive"
        }

    async def get_pool_health(self) -> Dict[str, Any]:
        active_sessions = await self.pool.get_active_sessions()
        return {
            "total_sessions": len(self.pool.sessions),
            "active_sessions": len(active_sessions),
            "max_sessions": self.pool.max_sessions,
            "pool_health": "healthy" if len(active_sessions) < self.pool.max_sessions else "full"
        }

    async def monitor_sessions(self) -> List[Dict[str, Any]]:
        results = []
        for session_id in self.pool.sessions:
            health = await self.check_health(session_id)
            results.append(health)
        return results
