from datetime import datetime

from pydantic import BaseModel


class SourceCreate(BaseModel):
    title: str
    source_type: str
    url: str | None = None
    content: str | None = None


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
