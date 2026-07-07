from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class NotebookStatus(str, Enum):
    active = "active"
    archived = "archived"
    processing = "processing"


class NotebookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)


class NotebookUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    status: NotebookStatus | None = None


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

    model_config = ConfigDict(from_attributes=True)


class NotebookListResponse(BaseModel):
    notebooks: list[NotebookResponse]
    total: int
