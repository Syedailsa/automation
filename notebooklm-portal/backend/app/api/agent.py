from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/refine")
async def refine_input(
    current_user: User = Depends(get_current_user),
):
    return {"message": "Agent refine endpoint - to be implemented by P3"}


@router.post("/execute")
async def execute_workflow(
    current_user: User = Depends(get_current_user),
):
    return {"message": "Agent execute endpoint - to be implemented by P3"}
