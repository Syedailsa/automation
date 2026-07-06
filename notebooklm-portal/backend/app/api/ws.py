from fastapi import APIRouter, WebSocket

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/agent/{execution_id}")
async def agent_websocket(websocket: WebSocket, execution_id: str):
    await websocket.accept()
    await websocket.send_json({"message": "WebSocket connected - to be implemented by P4"})
    await websocket.close()


@router.websocket("/ws/notebooks/{notebook_id}/sources")
async def sources_websocket(websocket: WebSocket, notebook_id: str):
    await websocket.accept()
    await websocket.send_json({"message": "WebSocket connected - to be implemented by P4"})
    await websocket.close()
