"""
Download manager for manga chapters.

This module handles downloading manga chapters with progress tracking,
filtering, and multi-language support.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

import requests
from tqdm import tqdm

from .config import Settings
from .exceptions import DownloadException

if TYPE_CHECKING:
    from .client import MangaDxClient

logger = logging.getLogger(__name__)


class DownloadManager:
    """Manager for downloading manga chapters."""

    def __init__(
        self,
        client: "MangaDxClient",
        download_dir: Optional[Path] = None,
        max_workers: Optional[int] = None,
        auto_update_structure: bool = True,
    ) -> None:
        """
        Initialize download manager.

        Args:
            client: MangaDx client instance for API operations
            download_dir: Directory for downloads (defaults to Settings.DOWNLOAD_DIR)
            max_workers: Max concurrent downloads (defaults to Settings.MAX_CONCURRENT_DOWNLOADS)
            auto_update_structure: Automatically update folder structure if changed (default: True)
        """
        self.client = client
        self.download_dir = download_dir or Settings.DOWNLOAD_DIR
        self.max_workers = max_workers or Settings.MAX_CONCURRENT_DOWNLOADS
        self.auto_update_structure = auto_update_structure
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem.

        Args:
            filename: Original filename to sanitize

        Returns:
            Sanitized filename safe for filesystem use
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
        return filename.strip()

    def download_manga(
        self,
        manga_id: str,
        languages: Optional[List[str]] = None,
        chapters: Optional[List[str]] = None,
        volumes: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> Dict[str, int]:
        """
        Download manga chapters.

        Args:
            manga_id: Manga UUID to download
            languages: List of language codes (defaults to ["en"])
            chapters: Specific chapters to download (optional)
            volumes: Specific volumes to download (optional)
            progress_callback: Callback for progress updates (message, current, total)

        Returns:
            Download statistics with counts of downloaded, failed, and skipped chapters
        """
        if languages is None:
            languages = [Settings.DEFAULT_LANGUAGE]

        logger.info(f"Starting download for manga {manga_id}")
        logger.info(f"Languages: {languages}")

        try:
            # Get manga info
            manga = self.client.manga.get(manga_id)
            manga_title = manga.title.get("en", manga.title.get("ja", "Unknown"))
            
            logger.info(f"Manga: {manga_title}")

            # Get chapters
            all_chapters = []
            for language in languages:
                chapters_data = self.client.manga.get_chapters_list(
                    manga_id,
                    translated_language=[language],
                    limit=500
                )
                all_chapters.extend(chapters_data)

            if not all_chapters:
                logger.warning("No chapters found")
                return {"downloaded": 0, "failed": 0, "skipped": 0}

            # Filter chapters if specified
            if chapters:
                all_chapters = [ch for ch in all_chapters if ch.get("chapter") in chapters]
            
            if volumes:
                all_chapters = [ch for ch in all_chapters if ch.get("volume") in volumes]

            logger.info(f"Found {len(all_chapters)} chapters to download")

            # Download chapters
            stats = {"downloaded": 0, "failed": 0, "skipped": 0}
            
            for i, chapter in enumerate(all_chapters):
                try:
                    if progress_callback:
                        progress_callback(f"Downloading chapter {chapter.get('chapter', 'Unknown')}", i, len(all_chapters))
                    
                    self._download_chapter(manga_title, chapter)
                    stats["downloaded"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to download chapter {chapter.get('chapter', 'Unknown')}: {e}")
                    stats["failed"] += 1

            logger.info(f"Download complete. Downloaded: {stats['downloaded']}, Failed: {stats['failed']}")
            return stats

        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise DownloadException(f"Download failed: {e}")

    def _download_chapter(self, manga_title: str, chapter_data: Dict[str, Any]) -> None:
        """
        Download a single chapter.

        Args:
            manga_title: Manga title for directory structure
            chapter_data: Chapter data from API containing ID and metadata
        """
        chapter_id = chapter_data["id"]
        chapter_num = chapter_data.get("chapter", "Unknown")
        volume = chapter_data.get("volume")
        
        # Create directory structure
        safe_title = self._sanitize_filename(manga_title)
        manga_dir = self.download_dir / safe_title
        
        if volume and volume.lower() not in ["none", "null", ""]:
            chapter_dir = manga_dir / f"Vol.{volume}" / f"Ch.{chapter_num}"
        else:
            chapter_dir = manga_dir / f"Ch.{chapter_num}"
        
        chapter_dir.mkdir(parents=True, exist_ok=True)

        # Check if already downloaded
        if any(chapter_dir.glob("*.jpg")) or any(chapter_dir.glob("*.png")):
            logger.debug(f"Chapter {chapter_num} already downloaded, skipping")
            return

        # Get chapter pages
        try:
            at_home_data = self.client.at_home.get_server(chapter_id)
            base_url = at_home_data["baseUrl"]
            chapter_hash = at_home_data["chapter"]["hash"]
            pages = at_home_data["chapter"]["data"]

            # Download pages
            for i, page in enumerate(pages):
                page_url = f"{base_url}/data/{chapter_hash}/{page}"
                page_path = chapter_dir / f"{i+1:03d}_{page}"
                
                if not page_path.exists():
                    self._download_file(page_url, page_path)

            logger.info(f"✓ Downloaded chapter {chapter_num} ({len(pages)} pages)")

        except Exception as e:
            logger.error(f"Failed to download chapter {chapter_num}: {e}")
            raise

    def _download_file(self, url: str, path: Path) -> None:
        """
        Download a file from URL to path.

        Args:
            url: File URL to download from
            path: Destination path for the downloaded file

        Raises:
            DownloadException: If download fails
        """
        try:
            response = requests.get(url, timeout=Settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            with open(path, "wb") as f:
                f.write(response.content)
                
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            raise DownloadException(f"Failed to download file: {e}")