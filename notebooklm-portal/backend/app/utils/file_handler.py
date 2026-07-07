import os
import uuid
from pathlib import Path

from app.config import settings


ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "text/plain": "txt",
    "text/markdown": "md",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/csv": "csv",
    "application/json": "json",
}

MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE


def get_allowed_extensions() -> set[str]:
    return {ext.strip() for ext in settings.ALLOWED_FILE_TYPES.split(",")}


def validate_file(filename: str, content_type: str | None, size: int) -> tuple[bool, str]:
    if size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        return False, f"File size exceeds maximum limit of {max_mb}MB"

    ext = Path(filename).suffix.lower().lstrip(".")
    allowed = get_allowed_extensions()
    if ext not in allowed:
        return False, f"File type '.{ext}' is not allowed. Allowed types: {', '.join(sorted(allowed))}"

    if content_type and content_type not in ALLOWED_MIME_TYPES:
        if not content_type.startswith("text/") and content_type != "application/octet-stream":
            return False, f"Content type '{content_type}' is not allowed"

    return True, "OK"


def safe_filename(filename: str) -> str:
    name = Path(filename).stem
    ext = Path(filename).suffix.lower()
    name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name)
    name = name.strip().replace(" ", "_")
    if not name:
        name = "file"
    unique_id = uuid.uuid4().hex[:8]
    return f"{name}_{unique_id}{ext}"


def cleanup_file(file_path: str | Path) -> bool:
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except OSError:
        return False
