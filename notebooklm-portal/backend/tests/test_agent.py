import json
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.agents import (
    NotebookLMAgent,
    ExecutionHub,
    ExecutionEvent,
    execution_hub,
    THINKING_STATES,
    ActionPlanner,
    ActionExecutor,
    NullToolExecutor,
    LLMProvider,
    PromptTemplates,
    ActionStep,
    ExecutionPlan,
)
from app.utils.language_detector import detect_language, contains_urdu_script, has_roman_urdu_vocabulary
from app.main import app


class TestLanguageDetector:
    def test_detect_english(self):
        assert detect_language("Hello, how are you?") == "en"
        assert detect_language("Create a new notebook about AI") == "en"

    def test_detect_urdu_script(self):
        assert detect_language("آپ کیسے ہیں؟") == "ur"

    def test_detect_roman_urdu(self):
        assert detect_language("mujhe ek notebook banana hai") == "roman_urdu"

    def test_detect_empty(self):
        assert detect_language("") == "unknown"
        assert detect_language("   ") == "unknown"

    def test_contains_urdu_script(self):
        assert contains_urdu_script("سلام") is True
        assert contains_urdu_script("Hello") is False

    def test_has_roman_urdu_vocabulary(self):
        assert has_roman_urdu_vocabulary("mujhe chahiye") is True
        assert has_roman_urdu_vocabulary("the quick brown fox") is False


class TestPromptTemplates:
    def test_system_prompt_exists(self):
        templates = PromptTemplates()
        assert "NotebookLM" in templates.SYSTEM_PROMPT

    def test_action_planner_prompt_format(self):
        templates = PromptTemplates()
        prompt = templates.ACTION_PLANNER_PROMPT.format(user_input="test input")
        assert "test input" in prompt

    def test_roman_urdu_translator_format(self):
        templates = PromptTemplates()
        prompt = templates.ROMAN_URDU_TRANSLATOR.format(input="mera naam")
        assert "mera naam" in prompt

    def test_output_formatter_format(self):
        templates = PromptTemplates()
        prompt = templates.OUTPUT_FORMATTER.format(results='{"key": "value"}')
        assert "key" in prompt

    def test_thinking_state_prompt_format(self):
        templates = PromptTemplates()
        prompt = templates.THINKING_STATE_PROMPT.format(
            state="thinking", description="test", history="[]"
        )
        assert "thinking" in prompt


class TestExecutionHub:
    def setup_method(self):
        execution_hub._subscribers = {}

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        callback = AsyncMock()
        execution_hub.subscribe("test-id", callback)
        event = ExecutionEvent(type="thinking", description="test")
        await execution_hub.publish("test-id", event)
        callback.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        callback = AsyncMock()
        execution_hub.subscribe("test-id", callback)
        execution_hub.unsubscribe("test-id", callback)
        event = ExecutionEvent(type="thinking", description="test")
        await execution_hub.publish("test-id", event)
        callback.assert_not_called()

    @pytest.mark.asyncio
    async def test_cleanup(self):
        callback = AsyncMock()
        execution_hub.subscribe("test-id", callback)
        execution_hub.cleanup("test-id")
        assert "test-id" not in execution_hub._subscribers

    @pytest.mark.asyncio
    async def test_publish_no_subscribers(self):
        event = ExecutionEvent(type="thinking", description="test")
        await execution_hub.publish("nonexistent", event)


class TestTHINKING_STATES:
    def test_has_all_states(self):
        assert "thinking" in THINKING_STATES
        assert "calling_tool" in THINKING_STATES
        assert "fetching_data" in THINKING_STATES
        assert "collecting_data" in THINKING_STATES
        assert "formatting_output" in THINKING_STATES
        assert "completed" in THINKING_STATES
        assert "failed" in THINKING_STATES
        assert len(THINKING_STATES) == 7


class TestNullToolExecutor:
    @pytest.mark.asyncio
    async def test_execute_single(self):
        executor = NullToolExecutor()
        result = await executor.execute_single({"action": "test", "params": {}})
        assert result["status"] == "simulated"
        assert result["action"] == "test"

    @pytest.mark.asyncio
    async def test_execute_actions(self):
        executor = NullToolExecutor()
        results = await executor.execute_actions([
            {"action": "action1", "params": {}},
            {"action": "action2", "params": {}},
        ])
        assert len(results) == 2
        assert results[0]["status"] == "simulated"


class TestNotebookLMAgent:
    @pytest.mark.asyncio
    async def test_refine_input_english(self):
        agent = NotebookLMAgent()
        with patch.object(agent.llm, "generate", new=AsyncMock(return_value="refined input")):
            result = await agent.refine_input("Hello world", "en")
            assert result == "refined input"

    @pytest.mark.asyncio
    async def test_refine_input_roman_urdu(self):
        agent = NotebookLMAgent()
        with patch.object(agent.llm, "generate", new=AsyncMock(return_value="translated input")):
            result = await agent.refine_input("mujhe kuch chahiye", "roman_urdu")
            assert result == "translated input"

    @pytest.mark.asyncio
    async def test_execute_workflow_with_events(self):
        agent = NotebookLMAgent()
        agent.executor = NullToolExecutor()

        mock_plan = [{"action": "create_notebook", "params": {"title": "Test"}}]
        mock_format = "Formatted output"

        with (
            patch.object(agent.planner, "plan_actions", new=AsyncMock(return_value=mock_plan)),
            patch.object(agent.llm, "generate", new=AsyncMock(return_value=mock_format)),
        ):
            result = await agent.execute_workflow("create a notebook")
            assert result["status"] == "completed"
            assert len(result["actions"]) == 1
            assert result["execution_id"] is not None

    @pytest.mark.asyncio
    async def test_execute_workflow_failure(self):
        agent = NotebookLMAgent()
        agent.executor = NullToolExecutor()

        with patch.object(agent.planner, "plan_actions", new=AsyncMock(side_effect=RuntimeError("fail"))):
            result = await agent.execute_workflow("do something")
            assert result["status"] == "failed"
            assert "error" in result


class TestActionPlanner:
    @pytest.mark.asyncio
    async def test_plan_actions(self):
        llm = LLMProvider()
        planner = ActionPlanner(llm)

        mock_response = json.dumps({
            "reasoning": "test",
            "actions": [{"action": "create_notebook", "params": {"title": "Test"}}],
        })

        with patch.object(llm, "generate", new=AsyncMock(return_value=mock_response)):
            actions = await planner.plan_actions("create a notebook")
            assert len(actions) == 1
            assert actions[0]["action"] == "create_notebook"

    @pytest.mark.asyncio
    async def test_plan_actions_invalid_json(self):
        llm = LLMProvider()
        planner = ActionPlanner(llm)

        with patch.object(llm, "generate", new=AsyncMock(return_value="not json")):
            actions = await planner.plan_actions("test")
            assert len(actions) == 1
            assert actions[0]["action"] == "unknown"

    @pytest.mark.asyncio
    async def test_plan_with_reasoning(self):
        llm = LLMProvider()
        planner = ActionPlanner(llm)

        mock_response = json.dumps({
            "reasoning": "User wants a notebook",
            "actions": [{"action": "create_notebook", "params": {"title": "Test"}}],
        })

        with patch.object(llm, "generate", new=AsyncMock(return_value=mock_response)):
            plan = await planner.plan_with_reasoning("create a notebook")
            assert plan.reasoning == "User wants a notebook"
            assert len(plan.steps) == 1
            assert plan.steps[0].action == "create_notebook"


class TestExecutionEvent:
    def test_create_event(self):
        event = ExecutionEvent(type="thinking", description="test", data={"key": "value"})
        assert event.type == "thinking"
        assert event.description == "test"
        assert event.data == {"key": "value"}
        assert event.timestamp is not None

    def test_event_default_timestamp(self):
        event = ExecutionEvent(type="completed", description="done")
        assert event.timestamp is not None


class TestActionStep:
    def test_create_action_step(self):
        step = ActionStep(action="create_notebook", params={"title": "Test"})
        assert step.action == "create_notebook"
        assert step.params["title"] == "Test"

    def test_action_step_with_description(self):
        step = ActionStep(action="test", description="a step")
        assert step.description == "a step"


class TestExecutionPlan:
    def test_create_empty_plan(self):
        plan = ExecutionPlan()
        assert plan.steps == []
        assert plan.reasoning is None

    def test_create_plan_with_steps(self):
        step = ActionStep(action="test")
        plan = ExecutionPlan(steps=[step], reasoning="because")
        assert len(plan.steps) == 1
        assert plan.reasoning == "because"


class TestAPIEndpoints:
    @pytest.mark.asyncio
    async def test_refine_input_unauthorized(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/agent/refine",
                json={"input_text": "Hello world", "language": "en"},
            )
            assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_execute_workflow_unauthorized(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/agent/execute",
                json={"input_text": "Test input"},
            )
            assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_status_unauthorized(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/agent/status/test-execution-id")
            assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_history_unauthorized(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/agent/history")
            assert response.status_code in [401, 403, 422]


class TestLLMProvider:
    @pytest.mark.asyncio
    async def test_provider_fallback_order(self):
        provider = LLMProvider("openrouter")
        assert "openrouter" in provider.fallback_order
        assert "openai" in provider.fallback_order
        assert "ollama" in provider.fallback_order

    @pytest.mark.asyncio
    async def test_provider_config(self):
        provider = LLMProvider("openai")
        cfg = provider._get_provider_config("openai")
        assert cfg["default_model"] == "gpt-4"
        assert cfg["api_key_env"] == "OPENAI_API_KEY"

    @pytest.mark.asyncio
    async def test_provider_config_with_custom_model(self):
        provider = LLMProvider("openai")
        cfg = provider._get_provider_config("openai", "gpt-4-turbo")
        assert cfg["default_model"] == "gpt-4-turbo"
