import pytest
import asyncio
from pathlib import Path
from src.config.browser_config import BrowserConfig
from src.config.settings import settings
from src.auth.session_manager import SessionManager


def test_browser_config_initialization():
    """Test BrowserConfig initialization."""
    config = BrowserConfig("test_profile")
    assert config.profile_name == "test_profile"
    assert config.storage_dir.exists()
    assert config.browser_profile_dir.exists()


def test_session_manager_save_load():
    """Test SessionManager save and load."""
    storage_path = settings.profiles_dir / "test" / "storage_state.json"
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    manager = SessionManager(storage_path)
    
    # Test save
    test_state = {"cookies": [{"name": "test", "value": "test"}]}
    manager.save_session(test_state)
    assert storage_path.exists()
    
    # Test load
    loaded = manager.load_session()
    assert loaded is not None
    assert loaded == test_state
    
    # Cleanup
    manager.delete_session()


def test_session_manager_expired():
    """Test SessionManager with expired session."""
    storage_path = settings.profiles_dir / "test_expired" / "storage_state.json"
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    manager = SessionManager(storage_path)
    
    # Create expired session
    from datetime import datetime, timedelta
    data = {
        'storage_state': {"cookies": []},
        'saved_at': (datetime.now() - timedelta(days=10)).isoformat(),
        'expires_at': (datetime.now() - timedelta(days=3)).isoformat()
    }
    
    with open(storage_path, 'w') as f:
        import json
        json.dump(data, f)
    
    # Test load expired
    loaded = manager.load_session()
    assert loaded is None
    
    # Cleanup
    manager.delete_session()


def test_settings_defaults():
    """Test Settings defaults."""
    assert settings.home_dir.exists()
    assert settings.notebooklm_base_url == "https://notebooklm.google.com"
    assert settings.max_retries == 3
    assert settings.viewport_width == 1280
