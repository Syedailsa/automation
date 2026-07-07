import pytest
import asyncio
from httpx import AsyncClient
from app.services.task_manager import BackgroundTaskManager, TaskStatus, TaskInfo


@pytest.fixture
def tm():
    return BackgroundTaskManager()


def test_task_initial_state(tm):
    assert tm.list_tasks() == []


@pytest.mark.asyncio
async def test_submit_and_complete(tm):
    async def dummy():
        return "done"

    task_id = await tm.submit("test_task", dummy)
    assert task_id is not None
    await asyncio.sleep(0.1)

    task = tm.get_task(task_id)
    assert task is not None
    assert task.status == TaskStatus.COMPLETED
    assert task.result == "done"


@pytest.mark.asyncio
async def test_submit_and_fail(tm):
    async def failing():
        raise ValueError("boom")

    task_id = await tm.submit("failing_task", failing, max_retries=0)
    await asyncio.sleep(0.1)

    task = tm.get_task(task_id)
    assert task is not None
    assert task.status == TaskStatus.FAILED
    assert "boom" in task.error


@pytest.mark.asyncio
async def test_retry_logic(tm):
    attempt = 0
    async def flaky():
        nonlocal attempt
        attempt += 1
        if attempt < 3:
            raise RuntimeError("not yet")
        return "success"

    task_id = await tm.submit("flaky_task", flaky, max_retries=3)
    await asyncio.sleep(10)

    task = tm.get_task(task_id)
    assert task is not None
    assert task.status == TaskStatus.COMPLETED
    assert task.result == "success"


@pytest.mark.asyncio
async def test_cancel_task(tm):
    async def slow():
        await asyncio.sleep(10)
        return "done"

    task_id = await tm.submit("slow_task", slow)
    await asyncio.sleep(0.05)

    cancelled = await tm.cancel_task(task_id)
    assert cancelled is True

    task = tm.get_task(task_id)
    assert task.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_list_tasks_filter(tm):
    async def ok():
        return 1

    await tm.submit("task1", ok)
    await tm.submit("task2", ok)
    await asyncio.sleep(0.1)

    all_tasks = tm.list_tasks()
    assert len(all_tasks) == 2

    completed = tm.list_tasks(status=TaskStatus.COMPLETED)
    assert len(completed) == 2


@pytest.mark.asyncio
async def test_update_progress(tm):
    async def working():
        return 42

    task_id = await tm.submit("progress_task", working)
    tm.update_progress(task_id, 50)
    task = tm.get_task(task_id)
    assert task.progress == 50


@pytest.mark.asyncio
async def test_task_api_unauthorized(client: AsyncClient):
    response = await client.get("/api/tasks")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_task_detail_api_unauthorized(client: AsyncClient):
    response = await client.get("/api/tasks/test-id")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_task_cancel_api_unauthorized(client: AsyncClient):
    response = await client.post("/api/tasks/test-id/cancel")
    assert response.status_code in [401, 403, 422]
