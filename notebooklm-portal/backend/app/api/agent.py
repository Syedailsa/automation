from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.agent import (
    AgentExecuteRequest,
    AgentExecuteResponse,
    AgentRefineRequest,
    AgentRefineResponse,
    ExecutionLogResponse,
)

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/refine", response_model=AgentRefineResponse)
async def refine_input(
    body: AgentRefineRequest,
    current_user: User = Depends(get_current_user),
):
    detected_language = body.language or "en"
    return AgentRefineResponse(
        refined_input=body.input_text,
        detected_language=detected_language,
        original_input=body.input_text,
    )


@router.post("/execute", response_model=AgentExecuteResponse)
async def execute_workflow(
    body: AgentExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import uuid

    execution_id = str(uuid.uuid4())
    return AgentExecuteResponse(
        execution_id=execution_id,
        status="pending",
    )


@router.get("/status/{execution_id}")
async def get_status(
    execution_id: str,
    current_user: User = Depends(get_current_user),
):
    return {"execution_id": execution_id, "status": "completed"}


@router.get("/history", response_model=list[ExecutionLogResponse])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return []
