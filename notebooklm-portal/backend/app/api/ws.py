from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import execution_hub, ExecutionEvent, THINKING_STATES
from app.core.security import verify_ws_token
from app.database import async_session_factory
from app.models.user import User
from app.services.ws_manager import ws_manager

router = APIRouter(tags=["websocket"])


async def get_user_from_ws_token(token: str) -> User | None:
    payload = verify_ws_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


@router.websocket("/ws/agent/{execution_id}")
async def agent_websocket(
    websocket: WebSocket,
    execution_id: str,
    token: str = Query(...),
):
    user = await get_user_from_ws_token(token)
    if not user:
        await websocket.accept()
        await websocket.close(code=4001, reason="Invalid or missing token")
        return

    await ws_manager.connect_agent(websocket, execution_id)

    async def forward_event(event: ExecutionEvent):
        try:
            await websocket.send_json({
                "type": event.type,
                "description": event.description,
                "data": event.data,
                "timestamp": event.timestamp,
            })
        except Exception:
            pass

    execution_hub.subscribe(execution_id, forward_event)

    try:
        await websocket.send_json({
            "type": "connected",
            "execution_id": execution_id,
            "user_id": str(user.id),
            "states": THINKING_STATES,
            "message": "Connected to agent execution stream",
        })

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await ws_manager.broadcast_agent_status(execution_id, {
                    "type": "client_message",
                    "message": data,
                })
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        execution_hub.unsubscribe(execution_id, forward_event)
        await ws_manager.disconnect_agent(websocket, execution_id)


@router.websocket("/ws/notebooks/{notebook_id}/sources")
async def sources_websocket(
    websocket: WebSocket,
    notebook_id: str,
    token: str = Query(...),
):
    user = await get_user_from_ws_token(token)
    if not user:
        await websocket.accept()
        await websocket.close(code=4001, reason="Invalid or missing token")
        return

    await ws_manager.connect_source(websocket, notebook_id)
    try:
        await websocket.send_json({
            "type": "connected",
            "notebook_id": notebook_id,
            "user_id": str(user.id),
            "message": "Connected to source status stream",
        })
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await ws_manager.broadcast_source_status(notebook_id, {
                    "type": "client_message",
                    "message": data,
                })
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await ws_manager.disconnect_source(websocket, notebook_id)
