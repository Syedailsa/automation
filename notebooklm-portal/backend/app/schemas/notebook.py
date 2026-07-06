from datetime import datetime

from pydantic import BaseModel


class NotebookCreate(BaseModel):
    title: str
    description: str | None = None


class NotebookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


class NotebookResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str | None = None
    notebooklm_id: str | None = None
    status: str = "active"
    source_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotebookListResponse(BaseModel):
    notebooks: list[NotebookResponse]
    total: int
