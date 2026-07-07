from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class OperationLog:
    operation_id: str
    operation_type: str
    status: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    details: Dict[str, Any] = field(default_factory=dict)


class OperationLogger:
    def __init__(self, log_file: str = "automation_logs.json"):
        self.log_file = log_file
        self.logs: list = []

    def log_operation(self, operation_id: str, operation_type: str, status: str, details: Dict[str, Any] = None):
        log = OperationLog(
            operation_id=operation_id,
            operation_type=operation_type,
            status=status,
            details=details or {}
        )
        self.logs.append(log)
        self._save_logs()

    def _save_logs(self):
        with open(self.log_file, 'w') as f:
            json.dump([{
                "operation_id": log.operation_id,
                "type": log.operation_type,
                "status": log.status,
                "start_time": log.start_time.isoformat(),
                "end_time": log.end_time.isoformat() if log.end_time else None,
                "details": log.details
            } for log in self.logs], f, indent=2)

    def get_logs(self, limit: int = 100) -> list:
        return self.logs[-limit:]
