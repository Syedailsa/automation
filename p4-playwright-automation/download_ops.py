import asyncio
from pathlib import Path
from playwright.async_api import Page
from .browser_manager import HumanDelays
from .selectors import settings


class DownloadManager:
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.download_dir = settings.HOME_DIR / "downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)

    async def download_artifact(self, artifact_type: str, output_path: str = None) -> str:
        if output_path is None:
            output_path = str(self.download_dir / f"{artifact_type}_download")
        try:
            download_button = self.page.locator('button:has-text("Download"), a:has-text("Download")').first
            async with self.page.expect_download() as download_info:
                await download_button.click()
            download = await download_info.value
            suggested_filename = download.suggested_filename
            if suggested_filename:
                final_path = str(Path(output_path).parent / suggested_filename)
            else:
                final_path = output_path
            await download.save_as(final_path)
            return final_path
        except Exception as e:
            print(f"Error downloading artifact: {e}")
            return None
