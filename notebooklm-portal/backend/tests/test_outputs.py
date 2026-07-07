import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_delete_output_unauthorized(client: AsyncClient):
    response = await client.delete("/api/outputs/00000000-0000-0000-0000-000000000000")
    assert response.status_code in [401, 403, 422]
