import json
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        # execution_id -> list of WebSocket connections
        self._agent_connections: dict[str, list[WebSocket]] = {}
        # notebook_id -> list of WebSocket connections
        self._source_connections: dict[str, list[WebSocket]] = {}

    async def connect_agent(self, websocket: WebSocket, execution_id: str):
        await websocket.accept()
        if execution_id not in self._agent_connections:
            self._agent_connections[execution_id] = []
        self._agent_connections[execution_id].append(websocket)

    async def disconnect_agent(self, websocket: WebSocket, execution_id: str):
        if execution_id in self._agent_connections:
            self._agent_connections[execution_id] = [
                ws for ws in self._agent_connections[execution_id] if ws != websocket
            ]
            if not self._agent_connections[execution_id]:
                del self._agent_connections[execution_id]

    async def connect_source(self, websocket: WebSocket, notebook_id: str):
        await websocket.accept()
        if notebook_id not in self._source_connections:
            self._source_connections[notebook_id] = []
        self._source_connections[notebook_id].append(websocket)

    async def disconnect_source(self, websocket: WebSocket, notebook_id: str):
        if notebook_id in self._source_connections:
            self._source_connections[notebook_id] = [
                ws for ws in self._source_connections[notebook_id] if ws != websocket
            ]
            if not self._source_connections[notebook_id]:
                del self._source_connections[notebook_id]

    async def broadcast_agent_status(self, execution_id: str, data: dict[str, Any]):
        if execution_id in self._agent_connections:
            message = json.dumps(data)
            dead = []
            for ws in self._agent_connections[execution_id]:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self._agent_connections[execution_id].remove(ws)

    async def broadcast_source_status(self, notebook_id: str, data: dict[str, Any]):
        if notebook_id in self._source_connections:
            message = json.dumps(data)
            dead = []
            for ws in self._source_connections[notebook_id]:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self._source_connections[notebook_id].remove(ws)

    def get_agent_connections_count(self, execution_id: str) -> int:
        return len(self._agent_connections.get(execution_id, []))

    def get_source_connections_count(self, notebook_id: str) -> int:
        return len(self._source_connections.get(notebook_id, []))


ws_manager = ConnectionManager()
