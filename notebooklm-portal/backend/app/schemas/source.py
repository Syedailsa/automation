from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    url = "url"
    text = "text"
    file = "file"
    youtube = "youtube"
    google_doc = "google_doc"


class SourceStatus(str, Enum):
    processing = "processing"
    ready = "ready"
    error = "error"


class SourceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    source_type: SourceType | None = None
    url: str | None = Field(None, max_length=2000)
    content: str | None = Field(None, max_length=500000)


class SourceResponse(BaseModel):
    id: str
    notebook_id: str
    title: str
    source_type: str
    url: str | None = None
    file_path: str | None = None
    status: str = "processing"
    notebooklm_source_id: str | None = None
    metadata_: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class SourceListResponse(BaseModel):
    sources: list[SourceResponse]
    total: int
