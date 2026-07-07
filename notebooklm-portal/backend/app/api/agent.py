import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import NotebookLMAgent, execution_hub, ExecutionEvent
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
from app.services.agent_service import get_agent_service
from app.services.ws_manager import ws_manager
from app.utils.language_detector import detect_language

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/refine", response_model=AgentRefineResponse)
async def refine_input(
    body: AgentRefineRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = get_agent_service(db)
    detected_language = body.language or detect_language(body.input_text)

    agent = NotebookLMAgent()
    refined = await agent.refine_input(body.input_text, detected_language)

    await svc.create_execution_log(
        user_id=current_user.id,
        original_input=body.input_text,
        detected_language=detected_language,
        refined_input=refined,
    )

    return AgentRefineResponse(
        refined_input=refined,
        detected_language=detected_language,
        original_input=body.input_text,
    )


@router.post("/execute", response_model=AgentExecuteResponse)
async def execute_workflow(
    body: AgentExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = get_agent_service(db)

    detected_language = detect_language(body.input_text)

    log = await svc.create_execution_log(
        user_id=current_user.id,
        original_input=body.input_text,
        detected_language=detected_language,
    )

    execution_id = str(log.id)

    async def on_event(event: ExecutionEvent):
        event_data = {
            "type": event.type,
            "description": event.description,
            "data": event.data,
            "timestamp": event.timestamp,
        }
        await ws_manager.broadcast_agent_status(execution_id, event_data)
        await svc.append_event(log.id, event_data)

    agent = NotebookLMAgent()
    result = await agent.execute_workflow(
        user_input=body.input_text,
        notebook_id=body.notebook_id,
        on_event=on_event,
    )

    await svc.update_execution_log(
        log.id,
        status=result.get("status", "completed"),
        actions=result.get("actions"),
        result={"events": result.get("events", []), "message": result.get("message")},
        error_message=result.get("error"),
        duration_ms=result.get("duration_ms"),
        refined_input=result.get("refined_input"),
    )

    return AgentExecuteResponse(
        execution_id=execution_id,
        status=result.get("status", "completed"),
    )


@router.get("/status/{execution_id}", response_model=ExecutionLogResponse)
async def get_status(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = get_agent_service(db)
    try:
        eid = uuid.UUID(execution_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")

    log = await svc.get_execution_log(eid)
    if not log:
        raise HTTPException(status_code=404, detail="Execution log not found")

    if str(log.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this execution")

    return ExecutionLogResponse(
        id=str(log.id),
        user_id=str(log.user_id),
        original_input=log.original_input,
        detected_language=log.detected_language,
        refined_input=log.refined_input,
        actions=log.actions,
        result=log.result,
        status=log.status,
        error_message=log.error_message,
        duration_ms=log.duration_ms,
        created_at=log.created_at,
        completed_at=log.completed_at,
    )


@router.get("/history", response_model=List[ExecutionLogResponse])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    svc = get_agent_service(db)
    logs = await svc.get_execution_logs_by_user(
        user_id=current_user.id,
        limit=min(limit, 100),
        offset=offset,
    )
    return [
        ExecutionLogResponse(
            id=str(log.id),
            user_id=str(log.user_id),
            original_input=log.original_input,
            detected_language=log.detected_language,
            refined_input=log.refined_input,
            actions=log.actions,
            result=log.result,
            status=log.status,
            error_message=log.error_message,
            duration_ms=log.duration_ms,
            created_at=log.created_at,
            completed_at=log.completed_at,
        )
        for log in logs
    ]
