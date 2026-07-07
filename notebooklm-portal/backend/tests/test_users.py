import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client: AsyncClient):
    response = await client.get("/api/users/profile")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_get_settings_unauthorized(client: AsyncClient):
    response = await client.get("/api/users/settings")
    assert response.status_code in [401, 403, 422]
