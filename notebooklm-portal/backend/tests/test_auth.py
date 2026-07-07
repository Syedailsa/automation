import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_google_redirect(client: AsyncClient):
    response = await client.get("/api/auth/google/redirect")
    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "accounts.google.com" in data["authorization_url"]


@pytest.mark.asyncio
async def test_google_callback_invalid_code(client: AsyncClient):
    response = await client.post(
        "/api/auth/google/callback",
        json={"code": "invalid_code", "state": "test_state"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_logout_unauthorized(client: AsyncClient):
    response = await client.post("/api/auth/logout")
    assert response.status_code in [401, 403, 422]
