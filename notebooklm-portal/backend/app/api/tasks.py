from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.services.task_manager import task_manager, TaskStatus


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskResponse(BaseModel):
    task_id: str
    name: str
    status: str
    result: dict | None = None
    error: str | None = None
    progress: int = 0
    created_at: float
    started_at: float | None = None
    completed_at: float | None = None
    retries: int = 0


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: str | None = None,
    current_user: User = Depends(get_current_user),
):
    task_status = None
    if status:
        try:
            task_status = TaskStatus(status)
        except ValueError:
            pass
    tasks = task_manager.list_tasks(status=task_status)
    return TaskListResponse(
        tasks=[TaskResponse(
            task_id=t.task_id,
            name=t.name,
            status=t.status.value,
            result=t.result if isinstance(t.result, dict) else {"output": str(t.result)} if t.result else None,
            error=t.error,
            progress=t.progress,
            created_at=t.created_at,
            started_at=t.started_at,
            completed_at=t.completed_at,
            retries=t.retries,
        ) for t in tasks],
        total=len(tasks),
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    task = task_manager.get_task(task_id)
    if not task:
        raise NotFoundException("Task not found")
    return TaskResponse(
        task_id=task.task_id,
        name=task.name,
        status=task.status.value,
        result=task.result if isinstance(task.result, dict) else {"output": str(task.result)} if task.result else None,
        error=task.error,
        progress=task.progress,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        retries=task.retries,
    )


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    cancelled = await task_manager.cancel_task(task_id)
    if not cancelled:
        raise NotFoundException("Task not found or already completed")
    return {"message": "Task cancelled successfully"}
