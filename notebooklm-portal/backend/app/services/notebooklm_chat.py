"""NotebookLM chat pipeline — connects user input to Playwright automation."""
import logging
import asyncio
from typing import Optional

from app.agents.llm_provider import LLMProvider
from app.services.playwright_session import session_service

logger = logging.getLogger(__name__)

# Prompts for the pipeline
REFINE_PROMPT = """You are a prompt refiner. The user is writing in Roman Urdu/Hindi or English.
Your job: translate and refine their message into a clear, structured English prompt for Google NotebookLM.

Rules:
- If already in English, just clean it up and make it more specific
- If in Roman Urdu/Hindi, translate to English
- Make it actionable and clear
- Keep the original intent
- Output ONLY the refined English prompt, nothing else

User message: {message}"""

PLAN_PROMPT = """You are a NotebookLM action planner. Given a user request, decide what to do in NotebookLM.

Available actions:
1. SEARCH_NOTEBOOK — Search for an existing notebook by keyword
2. CREATE_NOTEBOOK — Create a new notebook with a title
3. QUERY_NOTEBOOK — Ask a question to a specific notebook (generates AI response)
4. LIST_NOTEBOOKS — List all available notebooks

Output a JSON array of actions to execute in order. Each action is:
{{"action": "ACTION_NAME", "params": {{...}}}}

For QUERY_NOTEBOOK, use:
{{"action": "QUERY_NOTEBOOK", "params": {{"notebook_id": "found_notebook_id", "query": "the refined query"}}}}

If no notebook exists for the topic, first CREATE one, then QUERY it.

User request: {refined_prompt}

Output ONLY the JSON array, no explanation."""


async def refine_user_input(message: str, llm: LLMProvider) -> str:
    """Refine user input — translate Roman Urdu to English, structure the prompt."""
    prompt = REFINE_PROMPT.format(message=message)
    response = await llm.generate(
        prompt=prompt,
        system_prompt="You are a prompt refiner. Output only the refined prompt.",
    )
    return response.strip()


async def plan_actions(refined_prompt: str, llm: LLMProvider) -> list:
    """Plan NotebookLM actions using LLM."""
    prompt = PLAN_PROMPT.format(refined_prompt=refined_prompt)
    response = await llm.generate(
        prompt=prompt,
        system_prompt="You are a JSON action planner. Output ONLY valid JSON arrays.",
    )

    # Parse JSON
    import json
    try:
        # Try to extract JSON from response
        text = response.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        actions = json.loads(text)
        if isinstance(actions, list):
            return actions
        return [actions]
    except json.JSONDecodeError:
        # Fallback: create a simple query action
        return [{"action": "QUERY_NOTEBOOK", "params": {"query": refined_prompt}}]


async def execute_in_notebooklm(
    user_id: str,
    actions: list,
    refined_prompt: str,
    google_access_token: Optional[str] = None,
    google_refresh_token: Optional[str] = None,
) -> str:
    """Execute actions in NotebookLM via Playwright and return the response."""
    page = await session_service.get_authenticated_page(
        user_id,
        google_access_token=google_access_token,
        google_refresh_token=google_refresh_token,
    )
    if not page:
        return (
            "Could not connect to NotebookLM. "
            "Please log in to your Google account first by clicking 'Connect NotebookLM' in Settings."
        )

    try:
        # Get or create notebook
        notebook_id = None
        for act in actions:
            if act["action"] == "CREATE_NOTEBOOK":
                notebook_id = await _create_notebook(page, act["params"].get("title", "NovaAI Notes"))
            elif act["action"] == "SEARCH_NOTEBOOK":
                notebook_id = await _search_notebook(page, act["params"].get("keyword", ""))
            elif act["action"] == "LIST_NOTEBOOKS":
                return await _list_notebooks(page)

        # If no notebook found/created, try to find any existing one, or create new
        if not notebook_id:
            notebooks = await _list_notebooks_raw(page)
            if notebooks:
                notebook_id = notebooks[0]["id"]
            else:
                # Create a default notebook
                notebook_id = await _create_notebook(page, "NovaAI Notes")

        # Query the notebook
        query = refined_prompt
        for act in actions:
            if act["action"] == "QUERY_NOTEBOOK":
                query = act["params"].get("query", refined_prompt)
                break

        response = await _query_notebook(page, notebook_id, query)
        return response

    except Exception as e:
        logger.error(f"NotebookLM execution error: {e}")
        return f"Error interacting with NotebookLM: {str(e)}"
    finally:
        await page.context.close()


async def _create_notebook(page, title: str) -> Optional[str]:
    """Create a new notebook in NotebookLM."""
    try:
        # Click "New Notebook" button
        new_btn = page.locator('button:has-text("New Notebook"), button:has-text("Create notebook")')
        if await new_btn.count() > 0:
            await new_btn.first.click()
            await page.wait_for_timeout(2000)

            # Fill title
            title_input = page.locator('input[placeholder*="title"], input[placeholder*="name"], input[type="text"]')
            if await title_input.count() > 0:
                await title_input.first.fill(title)
                await page.wait_for_timeout(500)

            # Click create
            create_btn = page.locator('button:has-text("Create"), button:has-text("Save")')
            if await create_btn.count() > 0:
                await create_btn.first.click()
                await page.wait_for_timeout(3000)

            # Try to get notebook ID
            notebook_el = page.locator('[data-notebook-id]')
            if await notebook_el.count() > 0:
                return await notebook_el.first.get_attribute("data-notebook-id")

        return None
    except Exception as e:
        logger.error(f"Create notebook error: {e}")
        return None


async def _search_notebook(page, keyword: str) -> Optional[str]:
    """Search for a notebook by keyword."""
    notebooks = await _list_notebooks_raw(page)
    keyword_lower = keyword.lower()
    for nb in notebooks:
        if keyword_lower in nb.get("title", "").lower():
            return nb["id"]
    return notebooks[0]["id"] if notebooks else None


async def _list_notebooks_raw(page) -> list:
    """Get all notebooks as raw list."""
    try:
        notebooks = []
        elements = page.locator('[data-notebook-id]')
        count = await elements.count()
        for i in range(count):
            el = elements.nth(i)
            nb_id = await el.get_attribute("data-notebook-id")
            title = await el.inner_text()
            notebooks.append({"id": nb_id, "title": title.strip()})
        return notebooks
    except Exception:
        return []


async def _list_notebooks(page) -> str:
    """List all notebooks as formatted string."""
    notebooks = await _list_notebooks_raw(page)
    if not notebooks:
        return "No notebooks found in your NotebookLM."
    lines = [f"- {nb['title']} (ID: {nb['id']})" for nb in notebooks]
    return "Your NotebookLM notebooks:\n" + "\n".join(lines)


async def _query_notebook(page, notebook_id: str, query: str) -> str:
    """Open a notebook and ask a question, then capture the response."""
    try:
        # Click on the notebook
        notebook_el = page.locator(f'[data-notebook-id="{notebook_id}"]')
        if await notebook_el.count() > 0:
            await notebook_el.first.click()
            await page.wait_for_timeout(3000)

        # Find the chat input
        chat_input = page.locator(
            'textarea[placeholder*="question"], '
            'textarea[placeholder*="ask"], '
            'div[contenteditable="true"], '
            'input[placeholder*="prompt"], '
            '[aria-label*="chat"], '
            '[role="textbox"]'
        )

        if await chat_input.count() == 0:
            return "Could not find the chat input in NotebookLM."

        # Type the query
        await chat_input.first.click()
        await page.wait_for_timeout(500)
        await chat_input.first.fill(query)
        await page.wait_for_timeout(500)

        # Press Enter or click Send
        await chat_input.first.press("Enter")
        await page.wait_for_timeout(2000)

        # Wait for response (poll for new content)
        response = await _wait_for_response(page, timeout=120)
        return response

    except Exception as e:
        logger.error(f"Query notebook error: {e}")
        return f"Error querying notebook: {str(e)}"


async def _wait_for_response(page, timeout: int = 120) -> str:
    """Wait for NotebookLM to generate a response and capture it."""
    import time
    start = time.time()
    last_text = ""

    while time.time() - start < timeout:
        await page.wait_for_timeout(2000)

        # Look for the latest response bubble
        response_selectors = [
            '.response-container',
            '[data-message-id]',
            '.model-response',
            '.chat-response',
            'message-content',
            '.markdown',
            '[class*="response"]',
            '[class*="answer"]',
        ]

        for sel in response_selectors:
            elements = page.locator(sel)
            count = await elements.count()
            if count > 0:
                text = await elements.last.inner_text()
                if text and len(text) > len(last_text):
                    last_text = text
                    # Check if response is complete (no more loading)
                    loading = page.locator('.loading, .typing, [class*="loading"], [class*="typing"]')
                    if await loading.count() == 0:
                        return text.strip()

        # Also check for any substantial text content
        body_text = await page.inner_text('body')
        if 'NotebookLM' in body_text and len(body_text) > 500:
            # Extract the last substantial block of text
            lines = body_text.split('\n')
            response_lines = []
            capturing = False
            for line in reversed(lines):
                line = line.strip()
                if not line:
                    if capturing:
                        break
                    continue
                if len(line) > 20:
                    capturing = True
                    response_lines.insert(0, line)
                if len(response_lines) > 20:
                    break
            if response_lines:
                return '\n'.join(response_lines)

    return last_text or "Response could not be captured from NotebookLM. Please try again."


async def chat_with_notebooklm(
    user_id: str,
    message: str,
    google_access_token: Optional[str] = None,
    google_refresh_token: Optional[str] = None,
) -> str:
    """Main entry point — full pipeline from user message to NotebookLM response."""
    llm = LLMProvider()

    # Step 1: Refine the user's prompt
    logger.info(f"Refining prompt for user {user_id}: {message[:50]}...")
    refined = await refine_user_input(message, llm)
    logger.info(f"Refined: {refined[:100]}...")

    # Step 2: Plan actions
    logger.info("Planning NotebookLM actions...")
    actions = await plan_actions(refined, llm)
    logger.info(f"Actions: {actions}")

    # Step 3: Execute in NotebookLM
    logger.info("Executing in NotebookLM...")
    result = await execute_in_notebooklm(
        user_id,
        actions,
        refined,
        google_access_token=google_access_token,
        google_refresh_token=google_refresh_token,
    )

    return result

