import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


class SessionManager:
    """Manages session storage and persistence."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
    
    def save_session(self, storage_state: dict, expires_days: int = 7) -> None:
        """Save session to file with metadata."""
        data = {
            'storage_state': storage_state,
            'saved_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=expires_days)).isoformat()
        }
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_session(self) -> Optional[dict]:
        """Load session from file if valid."""
        if not self.storage_path.exists():
            return None
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            expires_at = datetime.fromisoformat(data['expires_at'])
            if datetime.now() > expires_at:
                print("Session expired, please re-login")
                return None
            
            return data.get('storage_state')
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading session: {e}")
            return None
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid."""
        session = self.load_session()
        return session is not None
