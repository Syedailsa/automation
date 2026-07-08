import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution_log import ExecutionLog


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_execution_log(
        self,
        user_id: uuid.UUID,
        original_input: str,
        detected_language: Optional[str] = None,
        refined_input: Optional[str] = None,
    ) -> ExecutionLog:
        log = ExecutionLog(
            user_id=user_id,
            original_input=original_input,
            detected_language=detected_language,
            refined_input=refined_input,
            status="pending",
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def update_execution_log(
        self,
        execution_id: uuid.UUID,
        **kwargs,
    ) -> Optional[ExecutionLog]:
        log = await self.get_execution_log(execution_id)
        if not log:
            return None

        for key, value in kwargs.items():
            if hasattr(log, key):
                setattr(log, key, value)

        if "status" in kwargs and kwargs["status"] in ("completed", "failed"):
            log.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def append_event(
        self,
        execution_id: uuid.UUID,
        event: Dict[str, Any],
    ) -> Optional[ExecutionLog]:
        log = await self.get_execution_log(execution_id)
        if not log:
            return None

        if log.result is None:
            log.result = {"events": []}

        if "events" not in log.result:
            log.result["events"] = []

        log.result["events"].append(event)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_execution_log(
        self, execution_id: uuid.UUID
    ) -> Optional[ExecutionLog]:
        result = await self.db.execute(
            select(ExecutionLog).where(ExecutionLog.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def get_execution_logs_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ExecutionLog]:
        result = await self.db.execute(
            select(ExecutionLog)
            .where(ExecutionLog.user_id == user_id)
            .order_by(desc(ExecutionLog.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_execution_logs_by_status(
        self,
        user_id: uuid.UUID,
        status: str,
        limit: int = 50,
    ) -> List[ExecutionLog]:
        result = await self.db.execute(
            select(ExecutionLog)
            .where(ExecutionLog.user_id == user_id)
            .where(ExecutionLog.status == status)
            .order_by(desc(ExecutionLog.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_execution_log(
        self, execution_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        log = await self.get_execution_log(execution_id)
        if not log or str(log.user_id) != str(user_id):
            return False
        await self.db.delete(log)
        await self.db.commit()
        return True

    async def get_conversation_context(
        self,
        user_id: uuid.UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get recent execution history for conversation memory."""
        logs = await self.get_execution_logs_by_user(user_id, limit=limit)
        context = []
        for log in reversed(logs):
            context.append({
                "input": log.original_input,
                "refined": log.refined_input,
                "status": log.status,
                "result_summary": (
                    log.result.get("message", "")[:200]
                    if log.result and isinstance(log.result, dict)
                    else ""
                ),
            })
        return context


class _AgentServiceProxy:
    def __init__(self):
        self._instances: dict = {}

    def __call__(self, db: AsyncSession) -> AgentService:
        key = id(db)
        if key not in self._instances:
            self._instances[key] = AgentService(db)
        return self._instances[key]


get_agent_service = _AgentServiceProxy()
