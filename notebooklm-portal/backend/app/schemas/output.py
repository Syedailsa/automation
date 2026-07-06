from datetime import datetime

from pydantic import BaseModel


class OutputResponse(BaseModel):
    id: str
    user_id: str
    notebook_id: str | None = None
    output_type: str
    file_path: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    metadata_: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class OutputListResponse(BaseModel):
    outputs: list[OutputResponse]
    total: int
