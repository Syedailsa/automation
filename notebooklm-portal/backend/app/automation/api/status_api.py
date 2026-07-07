from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BrowserStatus:
    is_connected: bool = False
    session_active: bool = False
    last_activity: Optional[datetime] = None
    memory_usage: float = 0.0
    active_sessions: int = 0


class StatusAPI:
    def __init__(self):
        self.status = BrowserStatus()

    def update_status(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.status, key):
                setattr(self.status, key, value)
        self.status.last_activity = datetime.now()

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_connected": self.status.is_connected,
            "session_active": self.status.session_active,
            "last_activity": self.status.last_activity.isoformat() if self.status.last_activity else None,
            "memory_usage": self.status.memory_usage,
            "active_sessions": self.status.active_sessions
        }

    def is_healthy(self) -> bool:
        return self.status.is_connected and self.status.session_active
