import httpx
from typing import Optional, Dict, Any


class NotebookLMAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def connect(self, token: str) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.base_url}/api/notebooklm/connect",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

    async def disconnect(self, token: str) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.base_url}/api/notebooklm/disconnect",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

    async def status(self, token: str) -> Dict[str, Any]:
        response = await self.client.get(
            f"{self.base_url}/api/notebooklm/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

    async def close(self):
        await self.client.aclose()
