"""Agent API client for NotebookLM automation."""
from typing import Dict, Any, Optional
import httpx


class AgentAPI:
    """API client for agent operations."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def refine(self, token: str, input_text: str) -> Dict[str, Any]:
        """Refine user input using the agent."""
        response = await self.client.post(
            f"{self.base_url}/api/agent/refine",
            headers={"Authorization": f"Bearer {token}"},
            json={"input": input_text}
        )
        return response.json()
    
    async def execute(self, token: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent action."""
        response = await self.client.post(
            f"{self.base_url}/api/agent/execute",
            headers={"Authorization": f"Bearer {token}"},
            json={"action": action, "params": params}
        )
        return response.json()
    
    async def get_status(self, token: str, execution_id: str) -> Dict[str, Any]:
        """Get execution status."""
        response = await self.client.get(
            f"{self.base_url}/api/agent/status/{execution_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
