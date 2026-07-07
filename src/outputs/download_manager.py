import asyncio
from pathlib import Path
from playwright.async_api import Page
from ..resilience.human_delays import HumanDelays
from ..config.settings import settings


class DownloadManager:
    """Manages file downloads from NotebookLM."""
    
    def __init__(self, page: Page):
        self.page = page
        self.delays = HumanDelays()
        self.download_dir = settings.home_dir / "downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    async def download_artifact(self, artifact_type: str, output_path: str = None) -> str:
        """
        Download any artifact type.
        
        Args:
            artifact_type: Type of artifact (audio, video, quiz, flashcards, slides)
            output_path: Optional output path
            
        Returns:
            Path to downloaded file
        """
        if output_path is None:
            output_path = str(self.download_dir / f"{artifact_type}_download")
        
        try:
            # Find and click download button for the artifact
            download_button = self.page.locator(
                f'button:has-text("Download"), a:has-text("Download")'
            ).first
            
            async with self.page.expect_download() as download_info:
                await download_button.click()
            
            download = await download_info.value
            
            # Determine file extension
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
    
    async def download_all_artifacts(self, output_dir: str = None) -> list[dict]:
        """
        Download all available artifacts.
        
        Args:
            output_dir: Directory to save all downloads
            
        Returns:
            List of download results
        """
        if output_dir is None:
            output_dir = str(self.download_dir / "all_artifacts")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        results = []
        artifact_types = ["audio", "video", "quiz", "flashcards", "slides"]
        
        for artifact_type in artifact_types:
            try:
                output_path = str(Path(output_dir) / f"{artifact_type}")
                result = await self.download_artifact(artifact_type, output_path)
                results.append({
                    'type': artifact_type,
                    'status': 'success' if result else 'failed',
                    'path': result
                })
            except Exception as e:
                results.append({
                    'type': artifact_type,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
