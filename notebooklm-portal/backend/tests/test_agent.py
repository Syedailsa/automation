import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_refine_input_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/agent/refine",
        json={"input_text": "Hello world", "language": "en"},
    )
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_execute_workflow_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/agent/execute",
        json={"input_text": "Test input"},
    )
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_get_status_unauthorized(client: AsyncClient):
    response = await client.get("/api/agent/status/test-execution-id")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_get_history_unauthorized(client: AsyncClient):
    response = await client.get("/api/agent/history")
    assert response.status_code in [401, 403, 422]
