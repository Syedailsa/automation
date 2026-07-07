from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/agent", tags=["agent"])


class RefineRequest(BaseModel):
    input: str


class ExecuteRequest(BaseModel):
    input: str
    notebook_id: Optional[str] = None


@router.post("/refine")
async def refine_input(
    request: RefineRequest,
    current_user: User = Depends(get_current_user),
):
    return {"refined_input": request.input, "message": "Input refined"}


@router.post("/execute")
async def execute_workflow(
    request: ExecuteRequest,
    current_user: User = Depends(get_current_user),
):
    return {
        "status": "executed",
        "input": request.input,
        "notebook_id": request.notebook_id,
        "message": "Workflow executed successfully"
    }


@router.get("/status/{execution_id}")
async def get_status(
    execution_id: str,
    current_user: User = Depends(get_current_user),
):
    return {"execution_id": execution_id, "status": "completed"}


@router.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user),
):
    return {"executions": []}
