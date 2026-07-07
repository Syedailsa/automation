from typing import Dict, Any, List
from .action_planner import ActionPlanner
from .action_executor import ActionExecutor
from .llm_provider import LLMProvider
from .prompt_templates import PromptTemplates


class NotebookLMAgent:
    def __init__(self, page, provider: str = "openai"):
        self.page = page
        self.llm = LLMProvider(provider)
        self.planner = ActionPlanner(self.llm)
        self.executor = ActionExecutor(page)
        self.templates = PromptTemplates()
    
    async def refine_input(self, user_input: str) -> str:
        return await self.planner.translate_roman_urdu(user_input)
    
    async def execute_workflow(self, user_input: str) -> Dict[str, Any]:
        actions = await self.planner.plan_actions(user_input)
        results = await self.executor.execute_actions(actions)
        
        formatted = await self.llm.generate(
            prompt=self.templates.OUTPUT_FORMATTER.format(results=str(results)),
            system_prompt=self.templates.SYSTEM_PROMPT
        )
        
        return {
            "input": user_input,
            "actions": actions,
            "results": results,
            "message": formatted
        }
