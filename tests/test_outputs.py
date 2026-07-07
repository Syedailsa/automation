import pytest
import asyncio
from src.utils.screenshot import ScreenshotManager
from src.utils.video_recorder import VideoRecorder
from src.utils.selector_registry import Selectors
from src.config.settings import settings


def test_screenshot_manager_initialization():
    """Test ScreenshotManager initialization."""
    manager = ScreenshotManager()
    assert manager.storage_dir.exists()


def test_screenshot_list():
    """Test ScreenshotManager list."""
    manager = ScreenshotManager()
    screenshots = manager.list_screenshots()
    assert isinstance(screenshots, list)


def test_video_recorder_initialization():
    """Test VideoRecorder initialization."""
    recorder = VideoRecorder()
    assert recorder.storage_dir.exists()


def test_video_recorder_path():
    """Test VideoRecorder path generation."""
    recorder = VideoRecorder()
    path = recorder.get_video_path("test_session")
    assert "test_session" in path
    assert path.endswith(".webm")


def test_selectors():
    """Test Selectors registry."""
    assert Selectors.SIGN_IN_BUTTON is not None
    assert Selectors.NOTEBOOK_LIST is not None
    assert Selectors.ADD_SOURCE_BUTTON is not None
    assert Selectors.GENERATE_AUDIO is not None
    assert Selectors.DOWNLOAD_BUTTON is not None


def test_settings_home_dir():
    """Test Settings home directory."""
    assert settings.home_dir.exists()
    assert settings.profiles_dir.exists()
    assert settings.screenshots_dir.exists()
    assert settings.videos_dir.exists()
