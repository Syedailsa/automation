import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .action_planner import ActionPlanner
from .action_executor import ActionExecutor
from .llm_provider import LLMProvider
from .prompt_templates import PromptTemplates


THINKING_STATES = [
    "thinking",
    "calling_tool",
    "fetching_data",
    "collecting_data",
    "formatting_output",
    "completed",
    "failed",
]


@dataclass
class ExecutionEvent:
    type: str
    description: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ExecutionHub:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, execution_id: str, callback: Callable):
        if execution_id not in self._subscribers:
            self._subscribers[execution_id] = []
        self._subscribers[execution_id].append(callback)

    def unsubscribe(self, execution_id: str, callback: Callable):
        if execution_id in self._subscribers:
            self._subscribers[execution_id] = [
                cb for cb in self._subscribers[execution_id] if cb != callback
            ]
            if not self._subscribers[execution_id]:
                del self._subscribers[execution_id]

    async def publish(self, execution_id: str, event: ExecutionEvent):
        if execution_id in self._subscribers:
            for callback in self._subscribers[execution_id]:
                try:
                    await callback(event)
                except Exception:
                    pass

    def cleanup(self, execution_id: str):
        self._subscribers.pop(execution_id, None)


execution_hub = ExecutionHub()


class NotebookLMAgent:
    def __init__(self, provider: Optional[str] = None):
        self.llm = LLMProvider(provider)
        self.planner = ActionPlanner(self.llm)
        self.executor = ActionExecutor()
        self.templates = PromptTemplates()
        self.execution_id: Optional[str] = None

    async def refine_input(
        self,
        user_input: str,
        detected_language: str = "en",
        on_event: Optional[Callable] = None,
    ) -> str:
        self.execution_id = str(uuid.uuid4())
        if on_event:
            execution_hub.subscribe(self.execution_id, on_event)

        await self._emit("thinking", "Detecting language and refining input")

        if detected_language in ("roman_urdu", "ur"):
            await self._emit("calling_tool", "Translating Roman Urdu to English")
            refined = await self.planner.translate_roman_urdu(user_input)
        else:
            refined = user_input

        await self._emit("formatting_output", "Input refined successfully")
        return refined

    async def execute_workflow(
        self,
        user_input: str,
        notebook_id: Optional[str] = None,
        on_event: Optional[Callable] = None,
        conversation_context: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        self.execution_id = str(uuid.uuid4())
        if on_event:
            execution_hub.subscribe(self.execution_id, on_event)

        start_time = time.time()
        events: List[Dict[str, Any]] = []

        try:
            await self._emit("thinking", "Analyzing user request and planning actions")
            actions = await self.planner.plan_actions(
                user_input,
                conversation_context=conversation_context,
            )
            events.append({
                "type": "plan_created",
                "actions": actions,
                "timestamp": datetime.utcnow().isoformat(),
            })

            if notebook_id:
                for action in actions:
                    if "params" not in action:
                        action["params"] = {}
                    action["params"]["notebook_id"] = notebook_id

            results = []
            for i, action in enumerate(actions):
                action_name = action.get("action", "unknown")
                await self._emit(
                    "calling_tool",
                    f"Executing step {i + 1}/{len(actions)}: {action_name}",
                    {"action": action, "step": i + 1, "total": len(actions)},
                )

                try:
                    result = await self.executor.execute_single(action)
                    results.append({
                        "action": action_name,
                        "status": "success",
                        "result": result,
                    })
                    events.append({
                        "type": "action_completed",
                        "action": action_name,
                        "status": "success",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                except Exception as e:
                    results.append({
                        "action": action_name,
                        "status": "error",
                        "error": str(e),
                    })
                    events.append({
                        "type": "action_failed",
                        "action": action_name,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            await self._emit("formatting_output", "Generating response")
            formatted = await self.llm.generate(
                prompt=self.templates.OUTPUT_FORMATTER.format(
                    results=json.dumps(results, indent=2)
                ),
                system_prompt=self.templates.SYSTEM_PROMPT,
            )

            duration_ms = int((time.time() - start_time) * 1000)
            await self._emit("completed", "Workflow completed successfully", {
                "duration_ms": duration_ms,
            })

            return {
                "input": user_input,
                "actions": actions,
                "results": results,
                "message": formatted,
                "execution_id": self.execution_id,
                "events": events,
                "duration_ms": duration_ms,
                "status": "completed",
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            await self._emit("failed", str(e), {"duration_ms": duration_ms})
            return {
                "input": user_input,
                "error": str(e),
                "execution_id": self.execution_id,
                "events": events,
                "duration_ms": duration_ms,
                "status": "failed",
            }
        finally:
            execution_hub.cleanup(self.execution_id)

    async def _emit(self, state: str, description: str, data: Optional[Dict] = None):
        if self.execution_id:
            event = ExecutionEvent(type=state, description=description, data=data)
            await execution_hub.publish(self.execution_id, event)
