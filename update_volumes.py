"""
Automatic volume structure updater.

This script checks if MangaDx has updated volume assignments for downloaded manga
and reorganizes folders accordingly.
"""

import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from src.mangadx import MangaDxClient
from config import Settings
from colorama import init, Fore

init(autoreset=True)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename.strip()


def get_manga_title(client: MangaDxClient, manga_id: str) -> str:
    """Get proper manga title from API."""
    try:
        manga = client.manga.get(manga_id)
        
        title = manga.title.get("en")
        if not title:
            title = manga.title.get("ja")
        if not title:
            title = manga.title.get("ja-ro")
        if not title and manga.title.values:
            title = list(manga.title.values.values())[0]
        
        return title
    except Exception as e:
        print(f"{Fore.RED}Error getting title for {manga_id}: {e}")
        return None


def get_current_structure(manga_dir: Path) -> Dict[str, Dict[str, Path]]:
    """
    Get current folder structure.
    
    Returns:
        Dict mapping chapter numbers to their current location
        Format: {chapter_num: {"volume": vol_num, "path": Path}}
    """
    structure = {}
    
    # Check chapters in root
    for item in manga_dir.iterdir():
        if item.is_dir() and item.name.startswith("Ch."):
            chapter_num = item.name.replace("Ch.", "")
            structure[chapter_num] = {
                "volume": None,
                "path": item
            }
    
    # Check chapters in volume folders
    for vol_dir in manga_dir.iterdir():
        if vol_dir.is_dir() and vol_dir.name.startswith("Vol."):
            vol_num = vol_dir.name.replace("Vol.", "")
            
            for chapter_dir in vol_dir.iterdir():
                if chapter_dir.is_dir() and chapter_dir.name.startswith("Ch."):
                    chapter_num = chapter_dir.name.replace("Ch.", "")
                    structure[chapter_num] = {
                        "volume": vol_num,
                        "path": chapter_dir
                    }
    
    return structure


def get_api_structure(client: MangaDxClient, manga_id: str, language: str = "en") -> Dict[str, Optional[str]]:
    """
    Get current volume structure from MangaDx API.
    
    Returns:
        Dict mapping chapter numbers to volume numbers
        Format: {chapter_num: vol_num or None}
    """
    try:
        chapters_data = client.manga.get_chapters_list(
            manga_id,
            translated_language=[language]
        )
        
        api_structure = {}
        for chapter in chapters_data:
            chapter_num = chapter.get("chapter")
            volume = chapter.get("volume")
            
            # Normalize volume (treat "none", "null", empty as None)
            if volume and volume.lower() not in ["none", "null", ""]:
                api_structure[chapter_num] = volume
            else:
                api_structure[chapter_num] = None
        
        return api_structure
    
    except Exception as e:
        print(f"{Fore.RED}Error getting API structure: {e}")
        return {}


def compare_structures(current: Dict, api: Dict) -> List[Dict]:
    """
    Compare current and API structures to find changes.
    
    Returns:
        List of changes needed
        Format: [{"chapter": ch_num, "from_vol": old_vol, "to_vol": new_vol, "path": current_path}]
    """
    changes = []
    
    for chapter_num, api_vol in api.items():
        if chapter_num in current:
            current_vol = current[chapter_num]["volume"]
            
            # Check if volume assignment changed
            if current_vol != api_vol:
                changes.append({
                    "chapter": chapter_num,
                    "from_vol": current_vol,
                    "to_vol": api_vol,
                    "path": current[chapter_num]["path"]
                })
    
    return changes


def apply_changes(manga_dir: Path, changes: List[Dict], dry_run: bool = False) -> int:
    """
    Apply volume structure changes.
    
    Args:
        manga_dir: Manga directory path
        changes: List of changes to apply
        dry_run: If True, only show what would be done
    
    Returns:
        Number of chapters moved
    """
    moved_count = 0
    
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
        
        # Show change
        from_str = f"Vol.{from_vol}" if from_vol else "root"
        to_str = f"Vol.{to_vol}" if to_vol else "root"
        
        if dry_run:
            print(f"{Fore.YELLOW}  [DRY RUN] Would move Ch.{chapter_num}: {from_str} → {to_str}")
        else:
            try:
                # Create parent directory if needed
                new_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move chapter folder
                if new_path.exists():
                    print(f"{Fore.YELLOW}  ⚠ Ch.{chapter_num} already exists at destination, skipping")
                else:
                    shutil.move(str(old_path), str(new_path))
                    print(f"{Fore.GREEN}  ✓ Moved Ch.{chapter_num}: {from_str} → {to_str}")
                    moved_count += 1
                
                # Clean up empty volume folder
                if from_vol:
                    old_vol_dir = manga_dir / f"Vol.{from_vol}"
                    if old_vol_dir.exists() and not any(old_vol_dir.iterdir()):
                        old_vol_dir.rmdir()
                        print(f"{Fore.CYAN}    Removed empty Vol.{from_vol}")
            
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed to move Ch.{chapter_num}: {e}")
    
    return moved_count


def update_manga_volumes(manga_dir: Path, manga_id: str, client: MangaDxClient, language: str = "en", dry_run: bool = False):
    """Update volume structure for a single manga."""
    manga_name = manga_dir.name
    
    print(f"\n{Fore.CYAN}{'─' * 60}")
    print(f"{Fore.CYAN}Checking: {manga_name}")
    print(f"{Fore.CYAN}{'─' * 60}")
    
    # Get current structure
    print(f"{Fore.WHITE}Scanning local folders...")
    current_structure = get_current_structure(manga_dir)
    print(f"{Fore.WHITE}Found {len(current_structure)} chapters locally")
    
    # Get API structure
    print(f"{Fore.WHITE}Fetching structure from MangaDx API...")
    api_structure = get_api_structure(client, manga_id, language)
    
    if not api_structure:
        print(f"{Fore.RED}✗ Could not fetch API structure")
        return
    
    print(f"{Fore.WHITE}Found {len(api_structure)} chapters on MangaDx")
    
    # Compare structures
    changes = compare_structures(current_structure, api_structure)
    
    if not changes:
        print(f"{Fore.GREEN}✓ Structure is up to date, no changes needed")
        return
    
    # Show changes
    print(f"\n{Fore.YELLOW}Found {len(changes)} volume assignment changes:")
    for change in changes:
        from_str = f"Vol.{change['from_vol']}" if change['from_vol'] else "root"
        to_str = f"Vol.{change['to_vol']}" if change['to_vol'] else "root"
        print(f"{Fore.YELLOW}  • Ch.{change['chapter']}: {from_str} → {to_str}")
    
    # Apply changes
    if not dry_run:
        confirm = input(f"\n{Fore.CYAN}Apply these changes? (Y/n): ").strip().lower()
        if confirm == 'n':
            print(f"{Fore.YELLOW}Skipped")
            return
    
    print(f"\n{Fore.WHITE}Applying changes...")
    moved = apply_changes(manga_dir, changes, dry_run)
    
    if not dry_run:
        print(f"\n{Fore.GREEN}✓ Updated {moved} chapters")


def scan_and_update(download_dir: Path, client: MangaDxClient, language: str = "en", dry_run: bool = False):
    """Scan all manga and update volumes."""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}  MangaDx Volume Structure Updater")
    print(f"{Fore.CYAN}{'=' * 60}")
    
    if dry_run:
        print(f"{Fore.YELLOW}\n⚠ DRY RUN MODE - No changes will be made\n")
    
    # Get all manga folders
    manga_folders = [d for d in download_dir.iterdir() if d.is_dir()]
    
    if not manga_folders:
        print(f"\n{Fore.YELLOW}No manga folders found in {download_dir}")
        return
    
    print(f"\n{Fore.WHITE}Found {len(manga_folders)} manga folders")
    print(f"{Fore.WHITE}Language: {language}\n")
    
    # Process each manga
    for manga_dir in manga_folders:
        # Ask for manga ID
        print(f"\n{Fore.CYAN}Manga: {manga_dir.name}")
        manga_id = input(f"{Fore.WHITE}Enter manga ID (or press Enter to skip): ").strip()
        
        if not manga_id:
            print(f"{Fore.YELLOW}Skipped")
            continue
        
        try:
            update_manga_volumes(manga_dir, manga_id, client, language, dry_run)
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {e}")


def update_specific_manga(manga_id: str, download_dir: Path, client: MangaDxClient, language: str = "en", dry_run: bool = False):
    """Update volumes for a specific manga by ID."""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}  Updating Manga: {manga_id}")
    print(f"{Fore.CYAN}{'=' * 60}")
    
    # Get manga title
    print(f"\n{Fore.WHITE}Fetching manga information...")
    manga_title = get_manga_title(client, manga_id)
    
    if not manga_title:
        print(f"{Fore.RED}✗ Could not fetch manga information")
        return
    
    safe_title = sanitize_filename(manga_title)
    manga_dir = download_dir / safe_title
    
    if not manga_dir.exists():
        print(f"{Fore.RED}✗ Manga folder not found: {manga_dir}")
        print(f"{Fore.YELLOW}  Expected: {safe_title}")
        return
    
    update_manga_volumes(manga_dir, manga_id, client, language, dry_run)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update manga volume structure from MangaDx")
    parser.add_argument("--manga-id", help="Specific manga ID to update")
    parser.add_argument("--language", default="en", help="Language code (default: en)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--scan-all", action="store_true", help="Scan all manga folders")
    
    args = parser.parse_args()
    
    download_dir = Settings.DOWNLOAD_DIR
    
    if not download_dir.exists():
        print(f"{Fore.RED}Download directory not found: {download_dir}")
        return
    
    client = MangaDxClient()
    
    try:
        if args.manga_id:
            # Update specific manga
            update_specific_manga(args.manga_id, download_dir, client, args.language, args.dry_run)
        elif args.scan_all:
            # Scan all manga
            scan_and_update(download_dir, client, args.language, args.dry_run)
        else:
            # Interactive mode
            print(f"\n{Fore.CYAN}{'=' * 60}")
            print(f"{Fore.CYAN}  MangaDx Volume Structure Updater")
            print(f"{Fore.CYAN}{'=' * 60}\n")
            print(f"{Fore.WHITE}1. Update specific manga by ID")
            print(f"{Fore.WHITE}2. Scan all manga folders")
            print(f"{Fore.WHITE}3. Exit\n")
            
            choice = input(f"{Fore.CYAN}Enter your choice: ").strip()
            
            if choice == "1":
                manga_id = input(f"\n{Fore.CYAN}Enter manga ID: ").strip()
                if manga_id:
                    update_specific_manga(manga_id, download_dir, client, args.language, args.dry_run)
            elif choice == "2":
                scan_and_update(download_dir, client, args.language, args.dry_run)
            else:
                print(f"{Fore.YELLOW}Goodbye!")
        
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}  Update complete!")
        print(f"{Fore.CYAN}{'=' * 60}\n")
    
    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Operation cancelled by user")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}")
