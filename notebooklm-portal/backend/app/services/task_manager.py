import asyncio
import uuid
import time
import traceback
from enum import Enum
from typing import Any, Callable, Coroutine
from dataclasses import dataclass, field

"""Background task management with retry logic."""


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskInfo:
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
    progress: int = 0
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    retries: int = 0
    max_retries: int = 3


class BackgroundTaskManager:
    def __init__(self):
        self._tasks: dict[str, TaskInfo] = {}
        self._asyncio_tasks: dict[str, asyncio.Task] = {}
        self._max_concurrent: int = 5
        self._semaphore: asyncio.Semaphore | None = None

    def _get_semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self._max_concurrent)
        return self._semaphore

    async def submit(
        self,
        name: str,
        func: Callable[..., Coroutine[Any, Any, Any]],
        *args,
        max_retries: int = 3,
        **kwargs,
    ) -> str:
        task_id = str(uuid.uuid4())
        task_info = TaskInfo(task_id=task_id, name=name, max_retries=max_retries)
        self._tasks[task_id] = task_info

        async_task = asyncio.create_task(
            self._run_task(task_id, func, *args, **kwargs)
        )
        self._asyncio_tasks[task_id] = async_task
        return task_id

    async def _run_task(self, task_id: str, func: Callable, *args, **kwargs):
        task_info = self._tasks[task_id]
        sem = self._get_semaphore()

        async with sem:
            task_info.status = TaskStatus.RUNNING
            task_info.started_at = time.time()

            while task_info.retries <= task_info.max_retries:
                try:
                    task_info.result = await func(*args, **kwargs)
                    task_info.status = TaskStatus.COMPLETED
                    task_info.completed_at = time.time()
                    task_info.progress = 100
                    return
                except Exception as e:
                    task_info.retries += 1
                    if task_info.retries > task_info.max_retries:
                        task_info.status = TaskStatus.FAILED
                        task_info.error = f"{type(e).__name__}: {e}"
                        task_info.completed_at = time.time()
                        return
                    await asyncio.sleep(min(2 ** task_info.retries, 30))

    def get_task(self, task_id: str) -> TaskInfo | None:
        return self._tasks.get(task_id)

    def list_tasks(self, status: TaskStatus | None = None) -> list[TaskInfo]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    async def cancel_task(self, task_id: str) -> bool:
        task = self._asyncio_tasks.get(task_id)
        task_info = self._tasks.get(task_id)
        if task and not task.done():
            task.cancel()
            if task_info:
                task_info.status = TaskStatus.CANCELLED
                task_info.completed_at = time.time()
            return True
        return False

    def update_progress(self, task_id: str, progress: int):
        if task_id in self._tasks:
            self._tasks[task_id].progress = min(100, max(0, progress))


task_manager = BackgroundTaskManager()
