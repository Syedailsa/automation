from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class OutputType(str, Enum):
    summary = "summary"
    quiz = "quiz"
    study_guide = "study_guide"
    transcript = "transcript"
    mind_map = "mind_map"
    audio_overview = "audio_overview"


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

    model_config = ConfigDict(from_attributes=True)


class OutputListResponse(BaseModel):
    outputs: list[OutputResponse]
    total: int
