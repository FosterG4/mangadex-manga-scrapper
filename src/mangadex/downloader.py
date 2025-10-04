"""
Download manager for manga chapters.

This module handles downloading manga chapters with progress tracking,
filtering, and multi-language support.
"""

import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tqdm import tqdm

from config import Settings
from .client import MangaDexClient
from .exceptions import DownloadException

logger = logging.getLogger(__name__)


class DownloadManager:
    """Manager for downloading manga chapters."""

    def __init__(
        self,
        client: MangaDexClient,
        download_dir: Optional[Path] = None,
        max_workers: Optional[int] = None,
        auto_update_structure: bool = True,
    ):
        """
        Initialize download manager.

        Args:
            client: MangaDex client instance
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
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
        return filename.strip()

    def _auto_update_structure(self, manga_id: str, manga_title: str, languages: List[str]):
        """
        Automatically update folder structure if it exists.

        This checks for:
        1. Old folder names (language codes) and renames them
        2. Volume assignment changes and reorganizes chapters

        Args:
            manga_id: Manga UUID
            manga_title: Current manga title from API
            languages: Languages being downloaded
        """
        safe_title = self._sanitize_filename(manga_title)
        manga_dir = self.download_dir / safe_title

        # Check if manga folder exists
        if not manga_dir.exists():
            # Check for old folder names (language codes or short names)
            for existing_dir in self.download_dir.iterdir():
                if not existing_dir.is_dir():
                    continue

                # Check if this might be the same manga with old name
                old_name = existing_dir.name.lower()

                # Common language codes or very short names
                if len(old_name) <= 3 or old_name in ["ja", "en", "es", "fr", "de", "ko", "zh", "pt", "pt-br"]:
                    # Check if it has chapters (likely a manga folder)
                    has_chapters = any(
                        d.name.startswith("Ch.") or d.name.startswith("Vol.")
                        for d in existing_dir.iterdir()
                        if d.is_dir()
                    )

                    if has_chapters:
                        logger.info(f"Found old folder '{existing_dir.name}', renaming to '{safe_title}'")
                        try:
                            existing_dir.rename(manga_dir)
                            logger.info("✓ Renamed folder to proper title")
                            break
                        except Exception as e:
                            logger.warning(f"Could not rename folder: {e}")

        # If manga folder exists, check for volume updates
        if manga_dir.exists():
            self._update_volume_structure(manga_dir, manga_id, languages[0] if languages else "en")

    def _update_volume_structure(self, manga_dir: Path, manga_id: str, language: str):
        """
        Update volume structure based on current API data.

        Args:
            manga_dir: Manga directory path
            manga_id: Manga UUID
            language: Language code
        """
        try:
            # Get current local structure
            local_structure = {}

            # Scan chapters in root
            for item in manga_dir.iterdir():
                if item.is_dir() and item.name.startswith("Ch."):
                    chapter_num = item.name.replace("Ch.", "")
                    local_structure[chapter_num] = {"volume": None, "path": item}

            # Scan chapters in volume folders
            for vol_dir in manga_dir.iterdir():
                if vol_dir.is_dir() and vol_dir.name.startswith("Vol."):
                    vol_num = vol_dir.name.replace("Vol.", "")
                    for chapter_dir in vol_dir.iterdir():
                        if chapter_dir.is_dir() and chapter_dir.name.startswith("Ch."):
                            chapter_num = chapter_dir.name.replace("Ch.", "")
                            local_structure[chapter_num] = {"volume": vol_num, "path": chapter_dir}

            if not local_structure:
                return  # No chapters to update

            # Get current API structure
            chapters_data = self.client.manga.get_chapters_list(
                manga_id,
                translated_language=[language]
            )

            api_structure = {}
            for chapter in chapters_data:
                chapter_num = chapter.get("chapter")
                volume = chapter.get("volume")

                # Normalize volume
                if volume and volume.lower() not in ["none", "null", ""]:
                    api_structure[chapter_num] = volume
                else:
                    api_structure[chapter_num] = None

            # Find changes
            changes = []
            for chapter_num, api_vol in api_structure.items():
                if chapter_num in local_structure:
                    local_vol = local_structure[chapter_num]["volume"]
                    if local_vol != api_vol:
                        changes.append({
                            "chapter": chapter_num,
                            "from_vol": local_vol,
                            "to_vol": api_vol,
                            "path": local_structure[chapter_num]["path"]
                        })

            if not changes:
                return  # No updates needed

            # Apply changes
            logger.info(f"Detected {len(changes)} volume assignment changes, updating structure...")

            for change in changes:
                chapter_num = change["chapter"]
                from_vol = change["from_vol"]
                to_vol = change["to_vol"]
                old_path = change["path"]

                # Determine new path
                if to_vol:
                    new_path = manga_dir / f"Vol.{to_vol}" / f"Ch.{chapter_num}"
                else:
                    new_path = manga_dir / f"Ch.{chapter_num}"

                try:
                    # Create parent directory if needed
                    new_path.parent.mkdir(parents=True, exist_ok=True)

                    # Move chapter folder
                    if not new_path.exists():
                        import shutil
                        shutil.move(str(old_path), str(new_path))

                        from_str = f"Vol.{from_vol}" if from_vol else "root"
                        to_str = f"Vol.{to_vol}" if to_vol else "root"
                        logger.info(f"  ✓ Moved Ch.{chapter_num}: {from_str} → {to_str}")

                        # Clean up empty volume folder
                        if from_vol:
                            old_vol_dir = manga_dir / f"Vol.{from_vol}"
                            if old_vol_dir.exists() and not any(old_vol_dir.iterdir()):
                                old_vol_dir.rmdir()

                except Exception as e:
                    logger.warning(f"Could not move Ch.{chapter_num}: {e}")

            logger.info("✓ Structure updated successfully")

        except Exception as e:
            logger.warning(f"Could not update volume structure: {e}")

    def _get_chapter_dir(self, manga_title: str, volume: Optional[str], chapter: str) -> Path:
        """
        Get directory path for chapter.

        Args:
            manga_title: Manga title
            volume: Volume number (optional)
            chapter: Chapter number

        Returns:
            Path to chapter directory
        """
        safe_title = self._sanitize_filename(manga_title)

        # Only create volume folder if volume is specified and not "none"
        if volume and volume.lower() not in ["none", "null", ""]:
            chapter_dir = self.download_dir / safe_title / f"Vol.{volume}" / f"Ch.{chapter}"
        else:
            # No volume or volume is "none" - put chapters directly under manga folder
            chapter_dir = self.download_dir / safe_title / f"Ch.{chapter}"

        return chapter_dir

    def _download_image(
        self,
        url: str,
        file_path: Path,
        retry_count: int = 0,
    ) -> bool:
        """
        Download single image.

        Args:
            url: Image URL
            file_path: Destination file path
            retry_count: Current retry attempt

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(
                url,
                timeout=Settings.REQUEST_TIMEOUT,
                headers={"User-Agent": Settings.USER_AGENT},
            )
            response.raise_for_status()

            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(response.content)

            return True

        except Exception as e:
            if retry_count < Settings.MAX_RETRIES:
                logger.warning(f"Retry {retry_count + 1}/{Settings.MAX_RETRIES} for {file_path.name}: {e}")
                time.sleep(Settings.RETRY_DELAY)
                return self._download_image(url, file_path, retry_count + 1)
            else:
                logger.error(f"Failed to download {file_path.name}: {e}")
                return False

    def download_chapter(
        self,
        chapter_id: str,
        manga_title: str,
        volume: Optional[str] = None,
        chapter_number: Optional[str] = None,
        data_saver: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Path:
        """
        Download a single chapter.

        Args:
            chapter_id: Chapter UUID
            manga_title: Manga title for directory structure
            volume: Volume number (optional)
            chapter_number: Chapter number (optional)
            data_saver: Use data saver images (lower quality)
            progress_callback: Callback function for progress updates

        Returns:
            Path to downloaded chapter directory

        Raises:
            DownloadException: If download fails
        """
        try:
            # Get chapter info if not provided
            if not chapter_number:
                chapter = self.client.chapter.get(chapter_id)
                chapter_number = chapter.chapter or "Unknown"
                volume = volume or chapter.volume

            # Get image URLs
            image_urls = self.client.at_home.get_image_urls(chapter_id, data_saver)

            if not image_urls:
                raise DownloadException(f"No images found for chapter {chapter_id}")

            # Create chapter directory
            chapter_dir = self._get_chapter_dir(manga_title, volume, chapter_number)
            chapter_dir.mkdir(parents=True, exist_ok=True)

            # Check for existing images
            existing_images = set(chapter_dir.glob("*.*"))
            if len(existing_images) == len(image_urls):
                logger.info(f"Chapter {chapter_number} already downloaded")
                return chapter_dir

            # Download images
            logger.info(f"Downloading chapter {chapter_number} ({len(image_urls)} images)")

            download_tasks = []
            for idx, url in enumerate(image_urls, 1):
                ext = url.split(".")[-1]
                file_path = chapter_dir / f"{idx:03d}.{ext}"

                if not file_path.exists():
                    download_tasks.append((url, file_path))

            if not download_tasks:
                logger.info(f"All images already exist for chapter {chapter_number}")
                return chapter_dir

            # Download with progress bar
            success_count = 0
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self._download_image, url, path): (url, path)
                    for url, path in download_tasks
                }

                with tqdm(total=len(download_tasks), desc=f"Ch.{chapter_number}", unit="img") as pbar:
                    for future in as_completed(futures):
                        success = future.result()
                        if success:
                            success_count += 1
                        pbar.update(1)

                        if progress_callback:
                            progress_callback(success_count, len(download_tasks))

            if success_count < len(download_tasks):
                logger.warning(
                    f"Downloaded {success_count}/{len(download_tasks)} images for chapter {chapter_number}"
                )
            else:
                logger.info(f"Successfully downloaded chapter {chapter_number}")

            return chapter_dir

        except Exception as e:
            raise DownloadException(f"Failed to download chapter {chapter_id}: {e}")

    def download_manga(
        self,
        manga_id: str,
        languages: Optional[List[str]] = None,
        volume_filter: Optional[List[str]] = None,
        chapter_filter: Optional[List[str]] = None,
        data_saver: bool = False,
    ) -> Dict[str, Any]:
        """
        Download entire manga or filtered chapters.

        Args:
            manga_id: Manga UUID
            languages: List of language codes to download (defaults to Settings.DEFAULT_LANGUAGE)
            volume_filter: List of volume numbers to download (None = all)
            chapter_filter: List of chapter numbers to download (None = all)
            data_saver: Use data saver images (lower quality)

        Returns:
            Dictionary with download statistics

        Raises:
            DownloadException: If download fails
        """
        try:
            # Get manga info
            manga = self.client.manga.get(manga_id, includes=["cover_art"])

            # Get best available title (prefer English, then Japanese, then romanized, then any)
            manga_title = manga.title.get("en")
            if not manga_title:
                manga_title = manga.title.get("ja")
            if not manga_title:
                manga_title = manga.title.get("ja-ro")
            if not manga_title and manga.title.values:
                manga_title = list(manga.title.values.values())[0]
            if not manga_title:
                manga_title = f"Manga_{manga_id[:8]}"

            logger.info(f"Downloading manga: {manga_title}")

            # Auto-update existing folder structure if enabled
            if self.auto_update_structure:
                self._auto_update_structure(manga_id, manga_title, languages or [Settings.DEFAULT_LANGUAGE])

            # Get chapters
            languages = languages or [Settings.DEFAULT_LANGUAGE]
            chapters_data = self.client.manga.get_chapters_list(
                manga_id,
                translated_language=languages,
            )

            if not chapters_data:
                raise DownloadException(f"No chapters found for manga {manga_id}")

            # Apply filters
            if volume_filter:
                chapters_data = [
                    ch for ch in chapters_data
                    if ch.get("volume") in volume_filter
                ]

            if chapter_filter:
                chapters_data = [
                    ch for ch in chapters_data
                    if ch.get("chapter") in chapter_filter
                ]

            if not chapters_data:
                raise DownloadException("No chapters match the specified filters")

            logger.info(f"Found {len(chapters_data)} chapters to download")

            # Download chapters
            stats = {
                "manga_title": manga_title,
                "total_chapters": len(chapters_data),
                "downloaded": 0,
                "failed": 0,
                "skipped": 0,
            }

            for chapter_data in tqdm(chapters_data, desc="Chapters", unit="ch"):
                try:
                    self.download_chapter(
                        chapter_id=chapter_data["id"],
                        manga_title=manga_title,
                        volume=chapter_data.get("volume"),
                        chapter_number=chapter_data.get("chapter"),
                        data_saver=data_saver,
                    )
                    stats["downloaded"] += 1

                    # Rate limiting between chapters (extra delay to avoid hitting limits)
                    # MangaDex allows ~5 req/s, but we add extra delay between chapters
                    time.sleep(Settings.RATE_LIMIT_DELAY * 2)

                except Exception as e:
                    logger.error(f"Failed to download chapter {chapter_data.get('chapter')}: {e}")
                    stats["failed"] += 1

            logger.info(
                f"Download complete: {stats['downloaded']}/{stats['total_chapters']} chapters"
            )

            return stats

        except Exception as e:
            raise DownloadException(f"Failed to download manga {manga_id}: {e}")

    def download_chapter_range(
        self,
        manga_id: str,
        start_chapter: float,
        end_chapter: float,
        language: Optional[str] = None,
        data_saver: bool = False,
    ) -> Dict[str, Any]:
        """
        Download a range of chapters.

        Args:
            manga_id: Manga UUID
            start_chapter: Starting chapter number
            end_chapter: Ending chapter number
            language: Language code (defaults to Settings.DEFAULT_LANGUAGE)
            data_saver: Use data saver images

        Returns:
            Dictionary with download statistics
        """
        language = language or Settings.DEFAULT_LANGUAGE

        # Get all chapters
        chapters_data = self.client.manga.get_chapters_list(
            manga_id,
            translated_language=[language],
        )

        # Filter by range
        filtered_chapters = []
        for ch in chapters_data:
            try:
                ch_num = float(ch.get("chapter", "0"))
                if start_chapter <= ch_num <= end_chapter:
                    filtered_chapters.append(ch)
            except ValueError:
                continue

        # Get manga info
        manga = self.client.manga.get(manga_id)

        # Get best available title (prefer English, then Japanese, then romanized, then any)
        manga_title = manga.title.get("en")
        if not manga_title:
            manga_title = manga.title.get("ja")
        if not manga_title:
            manga_title = manga.title.get("ja-ro")
        if not manga_title and manga.title.values:
            manga_title = list(manga.title.values.values())[0]
        if not manga_title:
            manga_title = f"Manga_{manga_id[:8]}"

        # Download filtered chapters
        stats = {
            "manga_title": manga_title,
            "total_chapters": len(filtered_chapters),
            "downloaded": 0,
            "failed": 0,
        }

        for chapter_data in tqdm(filtered_chapters, desc="Chapters", unit="ch"):
            try:
                self.download_chapter(
                    chapter_id=chapter_data["id"],
                    manga_title=manga_title,
                    volume=chapter_data.get("volume"),
                    chapter_number=chapter_data.get("chapter"),
                    data_saver=data_saver,
                )
                stats["downloaded"] += 1
                time.sleep(Settings.RATE_LIMIT_DELAY)

            except Exception as e:
                logger.error(f"Failed to download chapter {chapter_data.get('chapter')}: {e}")
                stats["failed"] += 1

        return stats
