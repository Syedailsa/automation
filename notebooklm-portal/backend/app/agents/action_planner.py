import json
from typing import List, Dict, Any
from .llm_provider import LLMProvider
from .prompt_templates import PromptTemplates


class ActionPlanner:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.templates = PromptTemplates()
    
    async def plan_actions(self, user_input: str) -> List[Dict[str, Any]]:
        prompt = self.templates.ACTION_PLANNER_PROMPT.format(user_input=user_input)
        
        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=self.templates.SYSTEM_PROMPT
        )
        
        try:
            result = json.loads(response)
            return result.get("actions", [])
        except json.JSONDecodeError:
            return [{"action": "unknown", "params": {"raw_input": user_input}}]
    
    async def translate_roman_urdu(self, text: str) -> str:
        prompt = self.templates.ROMAN_URDU_TRANSLATOR.format(input=text)
        return await self.llm.generate(prompt=prompt)
