from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class OperationStatus:
    operation_id: str
    operation_type: str
    status: str = "pending"
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class StatusTracker:
    def __init__(self):
        self.operations: Dict[str, OperationStatus] = {}

    def create_operation(self, operation_id: str, operation_type: str) -> OperationStatus:
        op = OperationStatus(operation_id=operation_id, operation_type=operation_type)
        self.operations[operation_id] = op
        return op

    def update_status(self, operation_id: str, status: str, progress: float = None):
        if operation_id in self.operations:
            op = self.operations[operation_id]
            op.status = status
            if progress is not None:
                op.progress = progress
            op.updated_at = datetime.now()

    def set_result(self, operation_id: str, result: Dict[str, Any]):
        if operation_id in self.operations:
            self.operations[operation_id].result = result
            self.operations[operation_id].status = "completed"

    def set_error(self, operation_id: str, error: str):
        if operation_id in self.operations:
            self.operations[operation_id].error = error
            self.operations[operation_id].status = "failed"

    def get_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        if operation_id in self.operations:
            op = self.operations[operation_id]
            return {
                "operation_id": op.operation_id,
                "type": op.operation_type,
                "status": op.status,
                "progress": op.progress,
                "result": op.result,
                "error": op.error,
                "created_at": op.created_at.isoformat(),
                "updated_at": op.updated_at.isoformat()
            }
        return None
