"""NotebookLM chat pipeline — connects user input to Playwright automation.

All operations go through the server's single Google account.
"""
import json
import logging
import time
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
5. GENERATE_AUDIO — Generate audio overview/podcast from notebook
6. GENERATE_VIDEO — Generate video overview from notebook
7. GENERATE_QUIZ — Generate quiz from notebook content
8. GENERATE_FLASHCARDS — Generate flashcards from notebook content
9. GENERATE_SLIDES — Generate slide deck from notebook content

RULES:
- ALWAYS search for existing notebooks FIRST using SEARCH_NOTEBOOK
- If user asks to "generate quiz" or "create quiz" or "make quiz", use GENERATE_QUIZ
- If user asks to "generate audio" or "create audio" or "podcast", use GENERATE_AUDIO
- If user asks to "generate video" or "create video", use GENERATE_VIDEO
- If user asks to "generate flashcards" or "create flashcards", use GENERATE_FLASHCARDS
- If user asks to "generate slides" or "create slides" or "presentation", use GENERATE_SLIDES
- If user asks a question about a topic, use QUERY_NOTEBOOK
- If user asks to "list notebooks" or "show notebooks", use LIST_NOTEBOOKS
- If no notebook exists, CREATE one first, then perform the action
- DO NOT add sources automatically - user adds sources manually

Output a JSON array of actions to execute in order. Each action is:
{{"action": "ACTION_NAME", "params": {{...}}}}

For GENERATE_QUIZ, use:
{{"action": "GENERATE_QUIZ", "params": {{"notebook_id": "found_notebook_id", "num_questions": 10}}}}

For GENERATE_AUDIO, use:
{{"action": "GENERATE_AUDIO", "params": {{"notebook_id": "found_notebook_id"}}}}

For GENERATE_VIDEO, use:
{{"action": "GENERATE_VIDEO", "params": {{"notebook_id": "found_notebook_id"}}}}

For GENERATE_FLASHCARDS, use:
{{"action": "GENERATE_FLASHCARDS", "params": {{"notebook_id": "found_notebook_id", "num_cards": 10}}}}

For GENERATE_SLIDES, use:
{{"action": "GENERATE_SLIDES", "params": {{"notebook_id": "found_notebook_id"}}}}

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

    try:
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
        return [{"action": "QUERY_NOTEBOOK", "params": {"query": refined_prompt}}]


async def execute_in_notebooklm(
    user_id: str,
    actions: list,
    refined_prompt: str,
) -> str:
    """Execute actions in NotebookLM via Playwright and return the response.

    Uses the server's single Google account — no per-user tokens needed.
    """
    page = await session_service.get_authenticated_page(user_id)
    if not page:
        return (
            "Could not connect to NotebookLM. "
            "The server session may have expired. Please contact admin."
        )

    try:
        notebook_id = None
        for act in actions:
            if act["action"] == "CREATE_NOTEBOOK":
                notebook_id = await _create_notebook(
                    page, act["params"].get("title", "NovaAI Notes")
                )
            elif act["action"] == "SEARCH_NOTEBOOK":
                notebook_id = await _search_notebook(
                    page, act["params"].get("keyword", "")
                )
            elif act["action"] == "LIST_NOTEBOOKS":
                return await _list_notebooks(page)

        if not notebook_id:
            notebooks = await _list_notebooks_raw(page)
            if notebooks:
                notebook_id = notebooks[0]["id"]
            else:
                notebook_id = await _create_notebook(page, "NovaAI Notes")

        # Handle different action types
        for act in actions:
            action_type = act["action"]
            
            if action_type == "QUERY_NOTEBOOK":
                query = act["params"].get("query", refined_prompt)
                return await _query_notebook(page, notebook_id, query)
            
            elif action_type == "GENERATE_QUIZ":
                num_questions = act["params"].get("num_questions", 10)
                return await _generate_quiz(page, notebook_id, num_questions)
            
            elif action_type == "GENERATE_AUDIO":
                return await _generate_audio(page, notebook_id)
            
            elif action_type == "GENERATE_VIDEO":
                return await _generate_video(page, notebook_id)
            
            elif action_type == "GENERATE_FLASHCARDS":
                num_cards = act["params"].get("num_cards", 10)
                return await _generate_flashcards(page, notebook_id, num_cards)
            
            elif action_type == "GENERATE_SLIDES":
                return await _generate_slides(page, notebook_id)

        # Default: query the notebook
        return await _query_notebook(page, notebook_id, refined_prompt)

    except Exception as e:
        logger.error(f"NotebookLM execution error: {e}")
        return f"Error interacting with NotebookLM: {str(e)}"
    finally:
        await page.close()


async def _create_notebook(page, title: str) -> Optional[str]:
    """Create a new notebook in NotebookLM."""
    try:
        # Click "Create new" button on the homepage
        new_btn = page.locator('button:has-text("Create new")')
        if await new_btn.count() > 0:
            await new_btn.first.click()
            await page.wait_for_timeout(3000)
            
            # Extract notebook ID from URL
            url = page.url
            if "/notebook/" in url:
                notebook_id = url.split("/notebook/")[1].split("?")[0].split("/")[0]
                logger.info(f"Created notebook with ID: {notebook_id}")
                return notebook_id
        
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
        # Try multiple selectors for notebooks
        selectors = [
            'a[href*="/notebook/"]',
            '[data-notebook-id]',
        ]
        
        for sel in selectors:
            elements = await page.query_selector_all(sel)
            if elements:
                for el in elements:
                    href = await el.get_attribute("href") or ""
                    if "/notebook/" in href:
                        nb_id = href.split("/notebook/")[1].split("?")[0]
                        # Get text from element or its children
                        title = await el.inner_text()
                        if not title.strip():
                            # Try to get title from aria-labelledby or other attributes
                            aria_labelledby = await el.get_attribute("aria-labelledby") or ""
                            if aria_labelledby:
                                title_el = page.locator(f'#{aria_labelledby.split()[0]}')
                                if await title_el.count() > 0:
                                    title = await title_el.first.inner_text()
                        if title.strip():
                            notebooks.append({"id": nb_id, "title": title.strip()})
                break
        
        return notebooks
    except Exception:
        return []


async def _list_notebooks(page) -> str:
    """List all notebooks as formatted string."""
    notebooks = await _list_notebooks_raw(page)
    if not notebooks:
        return "No notebooks found in NotebookLM."
    lines = [f"- {nb['title']} (ID: {nb['id']})" for nb in notebooks]
    return "NotebookLM notebooks:\n" + "\n".join(lines)


async def _query_notebook(page, notebook_id: str, query: str) -> str:
    """Open a notebook and ask a question, then capture the response."""
    try:
        # Navigate to notebook if not already there
        if notebook_id and notebook_id not in page.url:
            await page.goto(f"https://notebooklm.google.com/notebook/{notebook_id}", 
                          wait_until="load", timeout=60000)
            await page.wait_for_timeout(5000)
        
        # Try to dismiss any overlays/dialogs
        try:
            close_btns = page.locator('button:has-text("Close"), button[aria-label="Close"]')
            if await close_btns.count() > 0:
                await close_btns.first.click()
                await page.wait_for_timeout(1000)
        except:
            pass
        
        # Find the chat input using JavaScript click
        chat_input = page.locator('textarea[placeholder="Start typing..."]')
        
        if await chat_input.count() == 0:
            return "Could not find the chat input in NotebookLM."

        # Use JavaScript to click and fill
        await chat_input.first.evaluate("""
            (el) => {
                el.scrollIntoView();
                el.click();
                el.focus();
            }
        """)
        await page.wait_for_timeout(500)
        
        # Type the query
        await page.keyboard.type(query, delay=50)
        await page.wait_for_timeout(500)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)

        response = await _wait_for_response(page, timeout=120)
        return response

    except Exception as e:
        logger.error(f"Query notebook error: {e}")
        return f"Error querying notebook: {str(e)}"


async def _wait_for_response(page, timeout: int = 120) -> str:
    """Wait for NotebookLM to generate a response and capture it."""
    start = time.time()
    last_text = ""

    while time.time() - start < timeout:
        await page.wait_for_timeout(2000)

        response_selectors = [
            ".response-container",
            "[data-message-id]",
            ".model-response",
            ".chat-response",
            "message-content",
            ".markdown",
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
                    loading = page.locator(
                        ".loading, .typing, [class*='loading'], [class*='typing']"
                    )
                    if await loading.count() == 0:
                        return text.strip()

        body_text = await page.inner_text("body")
        if "NotebookLM" in body_text and len(body_text) > 500:
            lines = body_text.split("\n")
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
                return "\n".join(response_lines)

    return last_text or "Response could not be captured from NotebookLM. Please try again."


async def _add_url_source(page, url: str) -> bool:
    """Add a URL source to the notebook."""
    try:
        # Dismiss any overlays first
        await _dismiss_overlays(page)
        
        add_source_btn = page.locator('button:has-text("Add sources"), button:has-text("Add source")')
        if await add_source_btn.count() > 0:
            await add_source_btn.first.click(force=True)
            await page.wait_for_timeout(2000)
            
            url_input = page.locator('input[placeholder*="URL"], input[placeholder*="url"], input[type="url"]')
            if await url_input.count() > 0:
                await url_input.first.fill(url)
                await page.wait_for_timeout(500)
                
                insert_btn = page.locator('button:has-text("Insert"), button:has-text("Add"), button:has-text("Submit")')
                if await insert_btn.count() > 0:
                    await insert_btn.first.click()
                    await page.wait_for_timeout(3000)
                    return True
        return False
    except Exception as e:
        logger.error(f"Add URL source error: {e}")
        return False


async def _add_youtube_source(page, url: str) -> bool:
    """Add a YouTube source to the notebook."""
    try:
        # Dismiss any overlays first
        await _dismiss_overlays(page)
        
        add_source_btn = page.locator('button:has-text("Add sources"), button:has-text("Add source")')
        if await add_source_btn.count() > 0:
            await add_source_btn.first.click(force=True)
            await page.wait_for_timeout(2000)
            
            youtube_tab = page.locator('button:has-text("YouTube"), [role="tab"]:has-text("YouTube")')
            if await youtube_tab.count() > 0:
                await youtube_tab.first.click()
                await page.wait_for_timeout(1000)
            
            url_input = page.locator('input[placeholder*="YouTube"], input[placeholder*="youtube"], input[placeholder*="URL"]')
            if await url_input.count() > 0:
                await url_input.first.fill(url)
                await page.wait_for_timeout(500)
                
                insert_btn = page.locator('button:has-text("Insert"), button:has-text("Add"), button:has-text("Submit")')
                if await insert_btn.count() > 0:
                    await insert_btn.first.click()
                    await page.wait_for_timeout(3000)
                    return True
        return False
    except Exception as e:
        logger.error(f"Add YouTube source error: {e}")
        return False


async def _add_text_source(page, title: str, content: str) -> bool:
    """Add a text source to the notebook."""
    try:
        # Dismiss any overlays first
        await _dismiss_overlays(page)
        
        # Use JavaScript to click the Add sources button
        await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    if (btn.textContent.includes('Add sources') || btn.textContent.includes('Add source')) {
                        btn.click();
                        break;
                    }
                }
            }
        """)
        await page.wait_for_timeout(2000)
        
        # Click on Text tab using JavaScript
        await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button, [role="tab"]');
                for (const btn of buttons) {
                    if (btn.textContent.includes('Text') || btn.getAttribute('aria-label')?.includes('Text')) {
                        btn.click();
                        break;
                    }
                }
            }
        """)
        await page.wait_for_timeout(1000)
        
        # Fill title
        title_input = page.locator('input[placeholder*="title"], input[placeholder*="Title"]')
        if await title_input.count() > 0:
            await title_input.first.fill(title)
        
        # Fill content
        text_area = page.locator('textarea, div[contenteditable="true"]')
        if await text_area.count() > 0:
            await text_area.first.fill(content)
            await page.wait_for_timeout(500)
            
            # Click Insert button using JavaScript
            await page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.textContent.includes('Insert') || btn.textContent.includes('Add') || btn.textContent.includes('Submit')) {
                            btn.click();
                            break;
                        }
                    }
                }
            """)
            await page.wait_for_timeout(3000)
            return True
        return False
    except Exception as e:
        logger.error(f"Add text source error: {e}")
        return False


async def _dismiss_overlays(page):
    """Dismiss any overlay dialogs that might block clicks."""
    try:
        # Try to close overlay by clicking backdrop
        backdrop = page.locator('.cdk-overlay-backdrop')
        if await backdrop.count() > 0:
            await page.evaluate("document.querySelector('.cdk-overlay-backdrop')?.click()")
            await page.wait_for_timeout(500)
        
        # Try to close any dialog
        close_btns = page.locator('button:has-text("Close"), button[aria-label="Close"], button:has-text("Cancel")')
        if await close_btns.count() > 0:
            await close_btns.first.click(force=True)
            await page.wait_for_timeout(500)
    except:
        pass


async def _generate_quiz(page, notebook_id: str, num_questions: int = 10) -> str:
    """Generate a quiz from notebook content."""
    try:
        if notebook_id and notebook_id not in page.url:
            await page.goto(f"https://notebooklm.google.com/notebook/{notebook_id}", 
                          wait_until="load", timeout=60000)
            await page.wait_for_timeout(5000)
        
        # Dismiss overlays first
        await _dismiss_overlays(page)
        
        # Look for quiz button using aria-label
        quiz_btn = page.locator('button[aria-label="Customize Quiz"]')
        if await quiz_btn.count() == 0:
            # Try alternative selectors
            quiz_btn = page.locator('button:has-text("Quiz"), button:has-text("quiz")')
        
        if await quiz_btn.count() > 0:
            await quiz_btn.first.click(force=True)
            await page.wait_for_timeout(2000)
            
            # Look for generate button
            generate_btn = page.locator('button:has-text("Generate"), button:has-text("Create")')
            if await generate_btn.count() > 0:
                await generate_btn.first.click()
                await page.wait_for_timeout(5000)
                
                # Wait for quiz to generate
                try:
                    await page.wait_for_selector('button:has-text("Download"), [data-quiz-generated="true"]', timeout=120000)
                except:
                    pass
                
                return f"Quiz generated with {num_questions} questions! You can download it from NotebookLM."
        
        return "Could not find the quiz generation button in NotebookLM."
    except Exception as e:
        logger.error(f"Generate quiz error: {e}")
        return f"Error generating quiz: {str(e)}"


async def _generate_audio(page, notebook_id: str) -> str:
    """Generate audio overview from notebook."""
    try:
        if notebook_id and notebook_id not in page.url:
            await page.goto(f"https://notebooklm.google.com/notebook/{notebook_id}", 
                          wait_until="load", timeout=60000)
            await page.wait_for_timeout(5000)
        
        # Dismiss overlays first
        await _dismiss_overlays(page)
        
        # Look for audio button using aria-label
        audio_btn = page.locator('button[aria-label="Customize Audio Overview"]')
        if await audio_btn.count() == 0:
            # Try alternative selectors
            audio_btn = page.locator('button:has-text("Audio"), button:has-text("audio")')
        
        if await audio_btn.count() > 0:
            await audio_btn.first.click(force=True)
            await page.wait_for_timeout(2000)
            
            # Look for generate button
            generate_btn = page.locator('button:has-text("Generate"), button:has-text("Create")')
            if await generate_btn.count() > 0:
                await generate_btn.first.click()
                await page.wait_for_timeout(5000)
                
                # Wait for audio to generate
                try:
                    await page.wait_for_selector('button:has-text("Download"), audio', timeout=180000)
                except:
                    pass
                
                return "Audio overview generated! You can play or download it from NotebookLM."
        
        return "Could not find the audio generation button in NotebookLM."
    except Exception as e:
        logger.error(f"Generate audio error: {e}")
        return f"Error generating audio: {str(e)}"


async def _generate_video(page, notebook_id: str) -> str:
    """Generate video overview from notebook."""
    try:
        if notebook_id and notebook_id not in page.url:
            await page.goto(f"https://notebooklm.google.com/notebook/{notebook_id}", 
                          wait_until="load", timeout=60000)
            await page.wait_for_timeout(5000)
        
        # Dismiss overlays first
        await _dismiss_overlays(page)
        
        # Look for video button using aria-label
        video_btn = page.locator('button[aria-label="Customize Slide Deck"]')
        if await video_btn.count() == 0:
            # Try alternative selectors
            video_btn = page.locator('button:has-text("Video"), button:has-text("video")')
        
        if await video_btn.count() > 0:
            await video_btn.first.click(force=True)
            await page.wait_for_timeout(2000)
            
            # Look for generate button
            generate_btn = page.locator('button:has-text("Generate"), button:has-text("Create")')
            if await generate_btn.count() > 0:
                await generate_btn.first.click()
                await page.wait_for_timeout(5000)
                
                # Wait for video to generate
                try:
                    await page.wait_for_selector('button:has-text("Download"), video', timeout=180000)
                except:
                    pass
                
                return "Video overview generated! You can play or download it from NotebookLM."
        
        return "Could not find the video generation button in NotebookLM."
    except Exception as e:
        logger.error(f"Generate video error: {e}")
        return f"Error generating video: {str(e)}"


async def _generate_flashcards(page, notebook_id: str, num_cards: int = 10) -> str:
    """Generate flashcards from notebook content."""
    try:
        if notebook_id and notebook_id not in page.url:
            await page.goto(f"https://notebooklm.google.com/notebook/{notebook_id}", 
                          wait_until="load", timeout=60000)
            await page.wait_for_timeout(5000)
        
        # Dismiss overlays first
        await _dismiss_overlays(page)
        
        # Look for flashcard button using aria-label
        flashcard_btn = page.locator('button[aria-label="Customize Flashcards"]')
        if await flashcard_btn.count() == 0:
            # Try alternative selectors
            flashcard_btn = page.locator('button:has-text("Flashcards"), button:has-text("flashcards")')
        
        if await flashcard_btn.count() > 0:
            await flashcard_btn.first.click(force=True)
            await page.wait_for_timeout(2000)
            
            # Look for generate button
            generate_btn = page.locator('button:has-text("Generate"), button:has-text("Create")')
            if await generate_btn.count() > 0:
                await generate_btn.first.click()
                await page.wait_for_timeout(5000)
                
                # Wait for flashcards to generate
                try:
                    await page.wait_for_selector('button:has-text("Download"), [data-flashcard-generated="true"]', timeout=120000)
                except:
                    pass
                
                return f"Flashcards generated with {num_cards} cards! You can download them from NotebookLM."
        
        return "Could not find the flashcard generation button in NotebookLM."
    except Exception as e:
        logger.error(f"Generate flashcards error: {e}")
        return f"Error generating flashcards: {str(e)}"


async def _generate_slides(page, notebook_id: str) -> str:
    """Generate slide deck from notebook content."""
    try:
        if notebook_id and notebook_id not in page.url:
            await page.goto(f"https://notebooklm.google.com/notebook/{notebook_id}", 
                          wait_until="load", timeout=60000)
            await page.wait_for_timeout(5000)
        
        # Dismiss overlays first
        await _dismiss_overlays(page)
        
        # Look for slides button using aria-label
        slides_btn = page.locator('button[aria-label="Customize Slide Deck"]')
        if await slides_btn.count() == 0:
            # Try alternative selectors
            slides_btn = page.locator('button:has-text("Slides"), button:has-text("slides")')
        
        if await slides_btn.count() > 0:
            await slides_btn.first.click(force=True)
            await page.wait_for_timeout(2000)
            
            # Look for generate button
            generate_btn = page.locator('button:has-text("Generate"), button:has-text("Create")')
            if await generate_btn.count() > 0:
                await generate_btn.first.click()
                await page.wait_for_timeout(5000)
                
                # Wait for slides to generate
                try:
                    await page.wait_for_selector('button:has-text("Download"), [data-slides-generated="true"]', timeout=120000)
                except:
                    pass
                
                return "Slide deck generated! You can download it from NotebookLM."
        
        return "Could not find the slides generation button in NotebookLM."
    except Exception as e:
        logger.error(f"Generate slides error: {e}")
        return f"Error generating slides: {str(e)}"


async def chat_with_notebooklm(user_id: str, message: str) -> str:
    """Main entry point — full pipeline from user message to NotebookLM response.

    Uses the server's single Google account.
    """
    llm = LLMProvider()

    logger.info(f"Refining prompt for user {user_id}: {message[:50]}...")
    refined = await refine_user_input(message, llm)
    logger.info(f"Refined: {refined[:100]}...")

    logger.info("Planning NotebookLM actions...")
    actions = await plan_actions(refined, llm)
    logger.info(f"Actions: {actions}")

    logger.info("Executing in NotebookLM...")
    result = await execute_in_notebooklm(user_id, actions, refined)

    return result
