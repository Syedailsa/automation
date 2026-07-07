import asyncio
from playwright.async_api import Page
from ..resilience.human_delays import HumanDelays


class NotebookManager:
    """Manages NotebookLM notebook operations."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        
    async def create_notebook(self, title: str) -> str:
        """
        Create a new notebook and return its ID.
        
        Args:
            title: Notebook title
            
        Returns:
            Notebook ID
        """
        # Click new notebook button
        await self.delays.click_delay()
        await self.page.click('button:has-text("New Notebook")')
        
        # Wait for dialog
        await self.page.wait_for_selector('input[placeholder*="title"], input[type="text"]')
        
        # Enter title
        title_input = self.page.locator('input[placeholder*="title"], input[type="text"]').first
        await title_input.fill('')
        await title_input.type(title, delay=50)
        
        await self.delays.random_delay(0.5, 1.0)
        
        # Click create
        await self.page.click('button:has-text("Create")')
        
        # Wait for notebook to appear
        await asyncio.sleep(2)
        
        # Try to get notebook ID
        try:
            notebook_element = await self.page.wait_for_selector(
                f'[data-notebook-title="{title}"], [aria-label*="{title}"]',
                timeout=10000
            )
            notebook_id = await notebook_element.get_attribute('data-notebook-id')
            if notebook_id:
                return notebook_id
        except Exception:
            pass
        
        # Fallback: generate ID from title
        return title.lower().replace(' ', '_')
    
    async def list_notebooks(self) -> list[dict]:
        """
        List all notebooks.
        
        Returns:
            List of notebook dicts with id and title
        """
        await asyncio.sleep(1)
        
        notebooks = await self.page.query_selector_all('[data-notebook-id]')
        
        result = []
        for nb in notebooks:
            nb_id = await nb.get_attribute('data-notebook-id')
            title_elem = await nb.query_selector('h3, h4, [role="heading"]')
            title_text = await title_elem.inner_text() if title_elem else "Untitled"
            result.append({'id': nb_id, 'title': title_text})
        
        return result
    
    async def open_notebook(self, notebook_id: str) -> bool:
        """
        Open a specific notebook.
        
        Args:
            notebook_id: ID of notebook to open
            
        Returns:
            True if successful
        """
        try:
            await self.page.click(f'[data-notebook-id="{notebook_id}"]')
            await self.page.wait_for_load_state('networkidle')
            await self.delays.random_delay(1.0, 2.0)
            return True
        except Exception as e:
            print(f"Error opening notebook: {e}")
            return False
    
    async def delete_notebook(self, notebook_id: str) -> bool:
        """
        Delete a notebook.
        
        Args:
            notebook_id: ID of notebook to delete
            
        Returns:
            True if successful
        """
        try:
            # Right-click to open context menu
            await self.page.click(
                f'[data-notebook-id="{notebook_id}"]',
                button='right'
            )
            
            await self.delays.random_delay(0.3, 0.5)
            
            # Click delete
            await self.page.click('button:has-text("Delete")')
            
            await self.delays.random_delay(0.3, 0.5)
            
            # Confirm deletion
            await self.page.click('button:has-text("Confirm"), button:has-text("Yes")')
            
            await asyncio.sleep(1)
            
            return True
        except Exception as e:
            print(f"Error deleting notebook: {e}")
            return False
    
    async def rename_notebook(self, notebook_id: str, new_title: str) -> bool:
        """
        Rename a notebook.
        
        Args:
            notebook_id: ID of notebook to rename
            new_title: New title
            
        Returns:
            True if successful
        """
        try:
            # Right-click to open context menu
            await self.page.click(
                f'[data-notebook-id="{notebook_id}"]',
                button='right'
            )
            
            await self.delays.random_delay(0.3, 0.5)
            
            # Click rename
            await self.page.click('button:has-text("Rename")')
            
            await self.delays.random_delay(0.3, 0.5)
            
            # Enter new title
            title_input = self.page.locator('input[type="text"]').first
            await title_input.fill('')
            await title_input.type(new_title, delay=50)
            
            # Click save
            await self.page.click('button:has-text("Save"), button:has-text("OK")')
            
            await asyncio.sleep(1)
            
            return True
        except Exception as e:
            print(f"Error renaming notebook: {e}")
            return False
    
    async def get_notebook_count(self) -> int:
        """Get total number of notebooks."""
        notebooks = await self.page.query_selector_all('[data-notebook-id]')
        return len(notebooks)
