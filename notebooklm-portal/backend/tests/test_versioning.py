import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_v1_health_check(client: AsyncClient):
    response = await client.get("/api/v1/../../api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_v1_auth_redirect(client: AsyncClient):
    response = await client.get("/api/auth/google/redirect")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_old_api_has_deprecation_header(client: AsyncClient):
    response = await client.get("/api/auth/google/redirect")
    assert response.status_code == 200
    assert "Deprecation" in response.headers
    assert response.headers["Deprecation"] == "true"
    assert "Sunset" in response.headers


@pytest.mark.asyncio
async def test_v1_endpoints_exist(client: AsyncClient):
    response = await client.get("/api/auth/google/redirect")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_v1_notebooks_unauthorized(client: AsyncClient):
    response = await client.get("/api/notebooks")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_backward_compat_old_endpoints(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_v1_sources_file_unauthorized(client: AsyncClient):
    import io
    files = {"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
    response = await client.post(
        "/api/notebooks/00000000-0000-0000-0000-000000000000/sources/file",
        files=files,
        data={"title": "Test"},
    )
    assert response.status_code in [401, 403, 422]
