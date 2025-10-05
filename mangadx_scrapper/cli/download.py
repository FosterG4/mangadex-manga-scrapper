"""
Download command for MangaDx Scrapper CLI.

This module provides the download functionality for the CLI.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from colorama import Fore, Style, init

from ..client import MangaDxClient
from ..downloader import DownloadManager
from ..exceptions import MangaDxException
from ..utils import get_logger
from config import Settings

# Initialize colorama
init(autoreset=True)

logger = get_logger(__name__)


def print_success(message: str) -> None:
    """
    Print success message in green.
    
    Args:
        message: The success message to display
    """
    print(f"{Fore.GREEN}✓ {message}")


def print_error(message: str) -> None:
    """
    Print error message in red.
    
    Args:
        message: The error message to display
    """
    print(f"{Fore.RED}✗ {message}")


def print_info(message: str) -> None:
    """
    Print info message in cyan.
    
    Args:
        message: The info message to display
    """
    print(f"{Fore.CYAN}ℹ {message}")


def print_warning(message: str) -> None:
    """
    Print warning message in yellow.
    
    Args:
        message: The warning message to display
    """
    print(f"{Fore.YELLOW}⚠ {message}")


def download_manga(
    manga_id: str,
    languages: Optional[List[str]] = None,
    volumes: Optional[List[str]] = None,
    chapters: Optional[List[str]] = None,
    chapter_range: Optional[str] = None,
    data_saver: bool = False,
    output_dir: Optional[str] = None,
    quiet: bool = False
) -> None:
    """
    Download manga chapters.

    Args:
        manga_id: Manga UUID to download
        languages: Language codes to download (e.g., ['en', 'ja'])
        volumes: Volume numbers to download (e.g., ['1', '2', '3'])
        chapters: Chapter numbers to download (e.g., ['1', '2.5', '3'])
        chapter_range: Chapter range in format 'start-end' (e.g., '1-10')
        data_saver: Use data saver mode for lower quality images
        output_dir: Custom output directory path
        quiet: Suppress progress output and show minimal information
        
    Raises:
        MangaDxException: If download fails due to API issues
        Exception: For unexpected errors during download
    """
    try:
        client = MangaDxClient()
        downloader = DownloadManager(client)
        
        # Set custom download directory if provided
        if output_dir:
            downloader.download_dir = Path(output_dir)
            downloader.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Set default language if not provided
        if languages is None:
            languages = [Settings.DEFAULT_LANGUAGE]
        
        if not quiet:
            print_info(f"Starting download for manga ID: {manga_id}")
            print_info(f"Languages: {', '.join(languages)}")
            if volumes:
                print_info(f"Volumes: {', '.join(volumes)}")
            if chapters:
                print_info(f"Chapters: {', '.join(chapters)}")
            if chapter_range:
                print_info(f"Chapter range: {chapter_range}")
            print_info(f"Data saver mode: {'enabled' if data_saver else 'disabled'}")
            print_info(f"Output directory: {downloader.download_dir}")
            print()
        
        # Handle chapter range
        if chapter_range:
            if "-" not in chapter_range:
                print_error("Invalid chapter range format. Use 'start-end' (e.g., '1-10')")
                sys.exit(1)
            
            try:
                start, end = chapter_range.split("-")
                start_ch = float(start.strip())
                end_ch = float(end.strip())
                
                if not quiet:
                    print_info(f"Downloading chapters {start_ch} to {end_ch}")
                
                stats = downloader.download_chapter_range(
                    manga_id=manga_id,
                    start_chapter=start_ch,
                    end_chapter=end_ch,
                    language=languages[0],
                    data_saver=data_saver,
                )
            except ValueError:
                print_error("Invalid chapter range format. Use numeric values (e.g., '1-10')")
                sys.exit(1)
        else:
            # Regular download
            stats = downloader.download_manga(
                manga_id=manga_id,
                languages=languages,
                volume_filter=volumes,
                chapter_filter=chapters,
                data_saver=data_saver,
            )
        
        # Print statistics
        if not quiet:
            print(f"\n{Fore.YELLOW}{'─' * 60}")
            print(f"{Fore.YELLOW}DOWNLOAD COMPLETE")
            print(f"{Fore.YELLOW}{'─' * 60}\n")
            
            print(f"{Fore.WHITE}Manga: {stats['manga_title']}")
            print(f"{Fore.GREEN}Downloaded: {stats['downloaded']}/{stats['total_chapters']} chapters")
            
            if stats.get("failed", 0) > 0:
                print(f"{Fore.RED}Failed: {stats['failed']} chapters")
            
            print(f"\n{Fore.CYAN}Files saved to: {downloader.download_dir}")
        else:
            # Quiet mode - just print essential info
            print(f"Downloaded {stats['downloaded']}/{stats['total_chapters']} chapters")
            if stats.get("failed", 0) > 0:
                print(f"Failed: {stats['failed']} chapters")
        
        client.close()
        
    except MangaDxException as e:
        print_error(f"Download failed: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logger.exception("Download error")
        sys.exit(1)


def download_command() -> None:
    """
    Entry point for mangadx-download command.
    
    Parses command line arguments and executes the download functionality.
    """
    parser = argparse.ArgumentParser(
        description="Download manga from MangaDx",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mangadx-download abc123-def456-ghi789          # Download all chapters
  mangadx-download abc123 --language en ja       # Multiple languages
  mangadx-download abc123 --volumes 1 2 3        # Specific volumes
  mangadx-download abc123 --chapters 1 2.5 3     # Specific chapters
  mangadx-download abc123 --range 1-10           # Chapter range
  mangadx-download abc123 --data-saver           # Lower quality
  mangadx-download abc123 --output ./downloads   # Custom directory
  mangadx-download abc123 --quiet                # Minimal output
        """
    )
    
    parser.add_argument(
        "manga_id",
        help="Manga UUID to download"
    )
    
    parser.add_argument(
        "--language", "--lang",
        nargs="+",
        default=None,
        help=f"Language codes to download (default: {Settings.DEFAULT_LANGUAGE})"
    )
    
    parser.add_argument(
        "--volumes", "--vol",
        nargs="+",
        help="Volume numbers to download (e.g., --volumes 1 2 3)"
    )
    
    parser.add_argument(
        "--chapters", "--ch",
        nargs="+",
        help="Chapter numbers to download (e.g., --chapters 1 2.5 3)"
    )
    
    parser.add_argument(
        "--range",
        help="Chapter range to download (e.g., --range 1-10)"
    )
    
    parser.add_argument(
        "--data-saver",
        action="store_true",
        help="Use data saver mode (lower quality, smaller file size)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output directory for downloads"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="MangaDx Scrapper 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.range and (args.chapters or args.volumes):
        print_error("Cannot use --range with --chapters or --volumes")
        sys.exit(1)
    
    download_manga(
        manga_id=args.manga_id,
        languages=args.language,
        volumes=args.volumes,
        chapters=args.chapters,
        chapter_range=args.range,
        data_saver=args.data_saver,
        output_dir=args.output,
        quiet=args.quiet
    )


if __name__ == "__main__":
    download_command()