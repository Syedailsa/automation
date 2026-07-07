import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.ws_manager import ConnectionManager


@pytest.fixture
def manager():
    return ConnectionManager()


def test_initial_state(manager):
    assert manager._agent_connections == {}
    assert manager._source_connections == {}


def test_get_connections_count_empty(manager):
    assert manager.get_agent_connections_count("exec-1") == 0
    assert manager.get_source_connections_count("nb-1") == 0


@pytest.mark.asyncio
async def test_connect_agent(manager):
    ws = AsyncMock()
    await manager.connect_agent(ws, "exec-1")
    assert manager.get_agent_connections_count("exec-1") == 1
    ws.accept.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_agent(manager):
    ws = AsyncMock()
    await manager.connect_agent(ws, "exec-1")
    assert manager.get_agent_connections_count("exec-1") == 1

    await manager.disconnect_agent(ws, "exec-1")
    assert manager.get_agent_connections_count("exec-1") == 0


@pytest.mark.asyncio
async def test_connect_source(manager):
    ws = AsyncMock()
    await manager.connect_source(ws, "nb-1")
    assert manager.get_source_connections_count("nb-1") == 1
    ws.accept.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_source(manager):
    ws = AsyncMock()
    await manager.connect_source(ws, "nb-1")
    assert manager.get_source_connections_count("nb-1") == 1

    await manager.disconnect_source(ws, "nb-1")
    assert manager.get_source_connections_count("nb-1") == 0


@pytest.mark.asyncio
async def test_broadcast_agent_status(manager):
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    await manager.connect_agent(ws1, "exec-1")
    await manager.connect_agent(ws2, "exec-1")

    await manager.broadcast_agent_status("exec-1", {"type": "status", "status": "running"})
    ws1.send_text.assert_called_once()
    ws2.send_text.assert_called_once()


@pytest.mark.asyncio
async def test_broadcast_source_status(manager):
    ws1 = AsyncMock()
    await manager.connect_source(ws1, "nb-1")

    await manager.broadcast_source_status("nb-1", {"type": "source_status", "status": "ready"})
    ws1.send_text.assert_called_once()


@pytest.mark.asyncio
async def test_broadcast_removes_dead_connections(manager):
    ws_dead = AsyncMock()
    ws_dead.send_text.side_effect = Exception("connection closed")
    ws_alive = AsyncMock()

    await manager.connect_agent(ws_dead, "exec-1")
    await manager.connect_agent(ws_alive, "exec-1")
    assert manager.get_agent_connections_count("exec-1") == 2

    await manager.broadcast_agent_status("exec-1", {"type": "test"})
    assert manager.get_agent_connections_count("exec-1") == 1


@pytest.mark.asyncio
async def test_multiple_executions_independent(manager):
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    await manager.connect_agent(ws1, "exec-1")
    await manager.connect_agent(ws2, "exec-2")

    assert manager.get_agent_connections_count("exec-1") == 1
    assert manager.get_agent_connections_count("exec-2") == 1

    await manager.disconnect_agent(ws1, "exec-1")
    assert manager.get_agent_connections_count("exec-1") == 0
    assert manager.get_agent_connections_count("exec-2") == 1
