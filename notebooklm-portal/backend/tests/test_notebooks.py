import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_notebooks_unauthorized(client: AsyncClient):
    response = await client.get("/api/notebooks")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_create_notebook_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/notebooks",
        json={"title": "Test Notebook", "description": "A test notebook"},
    )
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_get_notebook_invalid_id(client: AsyncClient):
    response = await client.get("/api/notebooks/not-a-uuid")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_update_notebook_unauthorized(client: AsyncClient):
    response = await client.put(
        "/api/notebooks/00000000-0000-0000-0000-000000000000",
        json={"title": "Updated"},
    )
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_delete_notebook_unauthorized(client: AsyncClient):
    response = await client.delete("/api/notebooks/00000000-0000-0000-0000-000000000000")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_list_notebook_sources_unauthorized(client: AsyncClient):
    response = await client.get("/api/notebooks/00000000-0000-0000-0000-000000000000/sources")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_list_notebook_outputs_unauthorized(client: AsyncClient):
    response = await client.get("/api/notebooks/00000000-0000-0000-0000-000000000000/outputs")
    assert response.status_code in [401, 403, 422]
