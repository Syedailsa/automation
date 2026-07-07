import json
from typing import Any, Dict, List, Optional

from .llm_provider import LLMProvider
from .prompt_templates import ExecutionPlan, PromptTemplates


class ActionPlanner:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.templates = PromptTemplates()

    async def plan_actions(self, user_input: str) -> List[Dict[str, Any]]:
        prompt = self.templates.ACTION_PLANNER_PROMPT.format(user_input=user_input)

        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=self.templates.SYSTEM_PROMPT,
        )

        try:
            result = json.loads(response)
            actions = result.get("actions", [])
            if not actions and isinstance(result, list):
                actions = result
            return actions
        except (json.JSONDecodeError, KeyError):
            return [{"action": "unknown", "params": {"raw_input": user_input}}]

    async def plan_with_reasoning(self, user_input: str) -> ExecutionPlan:
        prompt = self.templates.ACTION_PLANNER_PROMPT.format(user_input=user_input)

        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=self.templates.SYSTEM_PROMPT,
        )

        try:
            result = json.loads(response)
            from .prompt_templates import ActionStep
            steps = []
            for a in result.get("actions", []):
                steps.append(ActionStep(
                    action=a.get("action", "unknown"),
                    params=a.get("params", {}),
                    description=a.get("description"),
                ))
            return ExecutionPlan(
                steps=steps,
                reasoning=result.get("reasoning"),
            )
        except (json.JSONDecodeError, KeyError):
            return ExecutionPlan(
                steps=[],
                reasoning="Failed to parse LLM response",
            )

    async def translate_roman_urdu(self, text: str) -> str:
        prompt = self.templates.ROMAN_URDU_TRANSLATOR.format(input=text)
        return await self.llm.generate(prompt=prompt)
