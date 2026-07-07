import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BrowserSession:
    session_id: str
    user_id: str
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class SessionPool:
    def __init__(self, max_sessions: int = 10):
        self.max_sessions = max_sessions
        self.sessions: Dict[str, BrowserSession] = {}
        self.lock = asyncio.Lock()

    async def acquire_session(self, user_id: str) -> Optional[str]:
        async with self.lock:
            if len(self.sessions) >= self.max_sessions:
                return None
            
            session_id = f"session_{user_id}_{datetime.now().timestamp()}"
            session = BrowserSession(session_id=session_id, user_id=user_id, is_active=True)
            self.sessions[session_id] = session
            return session_id

    async def release_session(self, session_id: str):
        async with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]

    async def get_active_sessions(self) -> List[BrowserSession]:
        return [s for s in self.sessions.values() if s.is_active]

    async def rotate_session(self, session_id: str) -> Optional[str]:
        session = self.sessions.get(session_id)
        user_id = session.user_id if session else "default"
        await self.release_session(session_id)
        return await self.acquire_session(user_id)
