"""Request queue for NotebookLM operations.

Multiple users send requests → queue holds them → worker processes one at a time
through the single server-side Google account.
"""
import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Optional

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class NotebookLMTask:
    task_id: str
    user_id: str
    operation: str  # "chat", "create_notebook", "list_notebooks", "add_source", etc.
    params: dict
    status: TaskStatus = TaskStatus.QUEUED
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    position: int = 0  # queue position


class NotebookLMQueue:
    """Async queue that processes one NotebookLM operation at a time.

    Why one at a time?
    - All requests share ONE Google account / browser session
    - Running concurrent operations on the same NotebookLM account causes conflicts
    - Sequential processing is reliable and avoids Google rate-limit detection
    """

    def __init__(self, max_size: int = 50, timeout_seconds: int = 300):
        self.max_size = max_size
        self.timeout_seconds = timeout_seconds
        self._queue: asyncio.Queue[NotebookLMTask] = asyncio.Queue(maxsize=max_size)
        self._tasks: dict[str, NotebookLMTask] = {}
        self._processing = False
        self._worker_task: Optional[asyncio.Task] = None
        self._handler: Optional[Callable[..., Coroutine]] = None

    def set_handler(self, handler: Callable[..., Coroutine]):
        """Set the function that processes each task.

        Handler signature: async def handler(task: NotebookLMTask) -> str
        Must return the result string.
        """
        self._handler = handler

    async def start(self):
        """Start the background worker."""
        if self._worker_task and not self._worker_task.done():
            return
        self._worker_task = asyncio.create_task(self._worker_loop())
        logger.info("NotebookLM queue worker started")

    async def stop(self):
        """Stop the worker gracefully."""
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("NotebookLM queue worker stopped")

    async def enqueue(
        self, user_id: str, operation: str, params: dict | None = None
    ) -> NotebookLMTask:
        """Add a task to the queue. Returns the task with queue position."""
        task = NotebookLMTask(
            task_id=str(uuid.uuid4()),
            user_id=user_id,
            operation=operation,
            params=params or {},
        )

        if self._queue.qsize() >= self.max_size:
            raise RuntimeError("NotebookLM queue is full. Try again later.")

        task.position = self._queue.qsize() + 1
        self._tasks[task.task_id] = task
        await self._queue.put(task)
        logger.info(
            f"Task {task.task_id} queued (pos={task.position}, op={operation}, user={user_id})"
        )
        return task

    def get_task(self, task_id: str) -> Optional[NotebookLMTask]:
        return self._tasks.get(task_id)

    def get_queue_size(self) -> int:
        return self._queue.qsize()

    def get_user_position(self, task_id: str) -> int:
        """Get position in queue for a specific task."""
        task = self._tasks.get(task_id)
        if not task:
            return -1
        if task.status != TaskStatus.QUEUED:
            return 0
        return task.position

    async def _worker_loop(self):
        """Background loop that processes tasks one at a time."""
        while True:
            try:
                task = await self._queue.get()
            except asyncio.CancelledError:
                break

            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.utcnow()
            self._processing = True

            logger.info(f"Processing task {task.task_id} (op={task.operation})")

            try:
                if not self._handler:
                    raise RuntimeError("No handler set for queue")

                result = await asyncio.wait_for(
                    self._handler(task),
                    timeout=self.timeout_seconds,
                )
                task.result = result
                task.status = TaskStatus.COMPLETED
                logger.info(f"Task {task.task_id} completed")

            except asyncio.TimeoutError:
                task.error = f"Operation timed out after {self.timeout_seconds}s"
                task.status = TaskStatus.TIMEOUT
                logger.warning(f"Task {task.task_id} timed out")

            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                logger.error(f"Task {task.task_id} failed: {e}")

            finally:
                task.completed_at = datetime.utcnow()
                self._processing = False
                self._queue.task_done()

                # Update positions for remaining tasks
                pos = 1
                for t in list(self._tasks.values()):
                    if t.status == TaskStatus.QUEUED:
                        t.position = pos
                        pos += 1

    @property
    def is_processing(self) -> bool:
        return self._processing


# Singleton
notebooklm_queue = NotebookLMQueue()
