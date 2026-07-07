from typing import Dict, Any, Callable, List
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Alert:
    alert_id: str
    severity: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


class AlertingSystem:
    def __init__(self):
        self.alerts: List[Alert] = []
        self.rules: Dict[str, Callable] = {}
        self.handlers: List[Callable] = []

    def add_rule(self, name: str, condition: Callable):
        self.rules[name] = condition

    def add_handler(self, handler: Callable):
        self.handlers.append(handler)

    async def check_alerts(self, metrics: Dict[str, Any]):
        for rule_name, condition in self.rules.items():
            try:
                if await condition(metrics):
                    alert = Alert(
                        alert_id=f"alert_{rule_name}_{datetime.now().timestamp()}",
                        severity="warning",
                        message=f"Alert triggered: {rule_name}"
                    )
                    self.alerts.append(alert)
                    await self._notify_handlers(alert)
            except Exception as e:
                print(f"Error checking rule {rule_name}: {e}")

    async def _notify_handlers(self, alert: Alert):
        for handler in self.handlers:
            try:
                await handler(alert)
            except Exception as e:
                print(f"Error notifying handler: {e}")

    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [{
            "alert_id": a.alert_id,
            "severity": a.severity,
            "message": a.message,
            "timestamp": a.timestamp.isoformat(),
            "acknowledged": a.acknowledged
        } for a in self.alerts[-limit:]]
