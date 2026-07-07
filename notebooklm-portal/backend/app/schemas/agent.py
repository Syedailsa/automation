from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AgentRefineRequest(BaseModel):
    input_text: str
    language: str | None = None


class AgentRefineResponse(BaseModel):
    refined_input: str
    detected_language: str
    original_input: str


class AgentExecuteRequest(BaseModel):
    input_text: str
    notebook_id: str | None = None


class AgentExecuteResponse(BaseModel):
    execution_id: str
    status: str = "pending"


class ExecutionEventSchema(BaseModel):
    type: str
    description: str
    data: Dict[str, Any] | None = None
    timestamp: str


class ExecutionLogResponse(BaseModel):
    id: str
    user_id: str
    original_input: str
    detected_language: str | None = None
    refined_input: str | None = None
    actions: dict | None = None
    result: dict | None = None
    status: str = "pending"
    error_message: str | None = None
    duration_ms: int | None = None
    created_at: datetime
    completed_at: datetime | None = None
    events: List[ExecutionEventSchema] | None = None

    class Config:
        from_attributes = True
