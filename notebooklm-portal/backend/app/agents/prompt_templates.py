from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ActionStep:
    action: str
    params: dict = field(default_factory=dict)
    description: Optional[str] = None


@dataclass
class ExecutionPlan:
    steps: List[ActionStep] = field(default_factory=list)
    reasoning: Optional[str] = None


class PromptTemplates:
    SYSTEM_PROMPT = """You are a NotebookLM automation assistant.
You help users manage notebooks, sources, and generate outputs using natural language.
You can understand Roman Urdu and translate to English if needed.
Always respond with precise, structured output."""

    ACTION_PLANNER_PROMPT = """Analyze the user input and determine the actions to perform.

User Input: {user_input}

Available actions:
- create_notebook: Create a new notebook
- add_source: Add a source to notebook (types: url, text, youtube)
- generate_audio: Generate audio overview
- generate_video: Generate video overview
- generate_quiz: Generate quiz
- generate_flashcards: Generate flashcards
- generate_slides: Generate slide deck
- list_notebooks: List all notebooks

Return JSON with this structure:
{{
  "reasoning": "brief explanation of the plan",
  "actions": [
    {{"action": "action_name", "params": {{"key": "value"}}, "description": "what this step does"}}
  ]
}}"""

    ROMAN_URDU_TRANSLATOR = """Translate the following Roman Urdu text to English.

If the text is already in English, return it as-is.

Roman Urdu: {input}

English translation:"""

    OUTPUT_FORMATTER = """Format the following execution results as a clear, user-friendly message.

Results:
{results}

Write in a helpful, conversational tone. Include key details about what was done."""

    THINKING_STATE_PROMPT = """Current execution state: {state}
Description: {description}

Previous events:
{history}

Continue the execution workflow."""
