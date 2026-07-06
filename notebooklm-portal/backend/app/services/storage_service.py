import os
from pathlib import Path

from app.config import settings


def get_user_storage_path(user_id: str) -> Path:
    base = Path(settings.NOTEBOOKLM_STORAGE_BASE)
    user_path = base / user_id
    user_path.mkdir(parents=True, exist_ok=True)
    return user_path


def get_user_outputs_path(user_id: str) -> Path:
    path = get_user_storage_path(user_id) / "outputs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_user_notebooklm_path(user_id: str) -> Path:
    path = get_user_storage_path(user_id) / "notebooklm"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_file(user_id: str, filename: str, content: bytes) -> str:
    outputs_path = get_user_outputs_path(user_id)
    file_path = outputs_path / filename
    file_path.write_bytes(content)
    return str(file_path)


def delete_file(file_path: str) -> bool:
    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        return False
