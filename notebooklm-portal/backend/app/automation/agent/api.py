import httpx
from typing import Optional, Dict, Any, List


class AgentAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def execute_action(self, token: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.base_url}/api/agent/execute",
            headers={"Authorization": f"Bearer {token}"},
            json={"action": action, "params": params}
        )
        return response.json()

    async def get_status(self, token: str, execution_id: str) -> Dict[str, Any]:
        response = await self.client.get(
            f"{self.base_url}/api/agent/status/{execution_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

    async def get_history(self, token: str) -> List[Dict[str, Any]]:
        response = await self.client.get(
            f"{self.base_url}/api/agent/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

    async def format_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": result.get("status") == "success",
            "data": result.get("data"),
            "error": result.get("error"),
            "timestamp": result.get("timestamp")
        }

    async def close(self):
        await self.client.aclose()
