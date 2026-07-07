import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_url_source_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/notebooks/00000000-0000-0000-0000-000000000000/sources/url",
        json={"title": "Test Source", "url": "https://example.com"},
    )
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_add_text_source_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/notebooks/00000000-0000-0000-0000-000000000000/sources/text",
        json={"title": "Test Source", "content": "Test content"},
    )
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_delete_source_unauthorized(client: AsyncClient):
    response = await client.delete(
        "/api/notebooks/00000000-0000-0000-0000-000000000000/sources/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_get_source_content_unauthorized(client: AsyncClient):
    response = await client.get(
        "/api/notebooks/00000000-0000-0000-0000-000000000000/sources/00000000-0000-0000-0000-000000000000/content"
    )
    assert response.status_code in [401, 403, 422]
