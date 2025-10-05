"""
Utility script to reorganize downloaded manga folders.

This script helps fix:
1. Folders named "ja" or other language codes -> proper manga titles
2. "Vol.none" folders -> move chapters to manga root
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import Settings
from src.mangadx import MangaDxClient


def get_manga_title(client: MangaDxClient, manga_id: str) -> str:
    """Get proper manga title from API."""
    try:
        manga = client.manga.get(manga_id)

        # Get best available title
        title = manga.title.get("en")
        if not title:
            title = manga.title.get("ja")
        if not title:
            title = manga.title.get("ja-ro")
        if not title and manga.title.values:
            title = list(manga.title.values.values())[0]

        return title
    except Exception as e:
        print(f"Error getting title for {manga_id}: {e}")
        return None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename.strip()


def reorganize_vol_none(download_dir: Path):
    """Move chapters from Vol.none folders to manga root."""
    print("\n=== Reorganizing Vol.none folders ===\n")

    for manga_dir in download_dir.iterdir():
        if not manga_dir.is_dir():
            continue

        vol_none_dir = manga_dir / "Vol.none"
        if vol_none_dir.exists():
            print(f"Found Vol.none in: {manga_dir.name}")

            # Move all chapters from Vol.none to manga root
            for chapter_dir in vol_none_dir.iterdir():
                if chapter_dir.is_dir():
                    target = manga_dir / chapter_dir.name

                    if target.exists():
                        print(f"  ⚠ {chapter_dir.name} already exists, skipping")
                    else:
                        shutil.move(str(chapter_dir), str(target))
                        print(f"  ✓ Moved {chapter_dir.name}")

            # Remove empty Vol.none folder
            try:
                vol_none_dir.rmdir()
                print(f"  ✓ Removed Vol.none folder\n")
            except OSError:
                print(f"  ⚠ Vol.none folder not empty, skipping removal\n")


def rename_language_code_folders(download_dir: Path, client: MangaDxClient):
    """Rename folders that are just language codes to proper titles."""
    print("\n=== Checking for language code folders ===\n")

    # Common language codes that might be folder names
    lang_codes = ["ja", "en", "es", "fr", "de", "it", "pt", "pt-br", "zh", "ko", "ru"]

    for folder in download_dir.iterdir():
        if not folder.is_dir():
            continue

        folder_name = folder.name.lower()

        # Check if folder name is a language code or very short
        if folder_name in lang_codes or len(folder_name) <= 3:
            print(f"Found suspicious folder: {folder.name}")

            # Try to find manga ID in a chapter folder
            manga_id = None
            for chapter_dir in folder.iterdir():
                if chapter_dir.is_dir():
                    # Check if there's a way to identify the manga
                    # For now, ask user for manga ID
                    print(
                        f"  Chapters found: {[d.name for d in folder.iterdir() if d.is_dir()][:5]}"
                    )
                    manga_id = input(
                        f"  Enter manga ID for '{folder.name}' (or press Enter to skip): "
                    ).strip()
                    break

            if manga_id:
                proper_title = get_manga_title(client, manga_id)
                if proper_title:
                    safe_title = sanitize_filename(proper_title)
                    new_path = download_dir / safe_title

                    if new_path.exists():
                        print(f"  ⚠ Folder '{safe_title}' already exists")
                        merge = input(f"  Merge contents? (y/N): ").strip().lower()
                        if merge == "y":
                            # Merge folders
                            for item in folder.iterdir():
                                target = new_path / item.name
                                if not target.exists():
                                    shutil.move(str(item), str(target))
                            folder.rmdir()
                            print(f"  ✓ Merged into '{safe_title}'\n")
                    else:
                        folder.rename(new_path)
                        print(f"  ✓ Renamed to: {safe_title}\n")


def main():
    """Main reorganization function."""
    print("=" * 60)
    print("  MangaDx Download Reorganizer")
    print("=" * 60)

    download_dir = Settings.DOWNLOAD_DIR

    if not download_dir.exists():
        print(f"\nDownload directory not found: {download_dir}")
        return

    print(f"\nDownload directory: {download_dir}")
    print(f"Found {len(list(download_dir.iterdir()))} items\n")

    # Initialize client
    client = MangaDxClient()

    try:
        # Step 1: Fix Vol.none folders
        reorganize_vol_none(download_dir)

        # Step 2: Rename language code folders
        rename_language_code_folders(download_dir, client)

        print("\n" + "=" * 60)
        print("  Reorganization complete!")
        print("=" * 60)

    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
