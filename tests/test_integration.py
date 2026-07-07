"""
Integration tests for NotebookLM Playwright Agent.

These tests require a valid Google session and should be run
with caution as they interact with real NotebookLM.
"""

import pytest
import asyncio
from src.main import NotebookLMAgent


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization."""
    agent = NotebookLMAgent("test")
    assert agent.profile_name == "test"
    assert agent.browser_config is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_start_stop():
    """Test agent start and stop."""
    agent = NotebookLMAgent("test")
    
    # Start in headless mode
    started = await agent.start(headless=True)
    assert started
    
    # Stop
    await agent.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_list_notebooks():
    """Test listing notebooks (requires valid session)."""
    agent = NotebookLMAgent("default")
    
    try:
        started = await agent.start(headless=True)
        if not started:
            pytest.skip("Failed to start agent")
        
        # Navigate to NotebookLM
        navigated = await agent.navigate_to_notebooklm()
        if not navigated:
            pytest.skip("Not authenticated")
        
        # List notebooks
        notebooks = await agent.list_notebooks()
        assert isinstance(notebooks, list)
        
    finally:
        await agent.stop()
