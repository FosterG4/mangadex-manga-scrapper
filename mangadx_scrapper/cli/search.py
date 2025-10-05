"""
Search command for MangaDx Scrapper CLI.

This module provides the search functionality for the CLI.
"""

import argparse
import sys
from typing import List, Optional

from colorama import Fore, Style, init

from config import Settings

from ..client import MangaDxClient
from ..exceptions import MangaDxException
from ..models import Manga
from ..utils import format_manga_info, format_manga_list, get_logger

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


def search_manga(
    title: str,
    limit: int = 20,
    content_rating: Optional[List[str]] = None,
    status: Optional[List[str]] = None,
    demographic: Optional[List[str]] = None,
    year: Optional[int] = None,
    verbose: bool = False,
    json_output: bool = False
) -> None:
    """
    Search for manga and display results.

    Args:
        title: Manga title to search for
        limit: Maximum number of results to return (default: 20)
        content_rating: Content rating filter (safe, suggestive, erotica, pornographic)
        status: Publication status filter (ongoing, completed, hiatus, cancelled)
        demographic: Publication demographic filter (shounen, shoujo, josei, seinen)
        year: Publication year filter
        verbose: Show detailed information for each manga
        json_output: Output results in JSON format instead of formatted text
        
    Raises:
        MangaDxException: If API request fails
        Exception: For unexpected errors
    """
    try:
        client = MangaDxClient()
        
        print_info(f"Searching for '{title}'...")
        
        # Set default content rating if not provided
        if content_rating is None:
            content_rating = Settings.DEFAULT_CONTENT_RATING
        
        manga_list = client.manga.search(
            title=title,
            limit=limit,
            content_rating=content_rating,
            status=status,
            publication_demographic=demographic,
            year=year,
            includes=["cover_art", "author", "artist"],
        )
        
        if not manga_list:
            print_warning("No manga found matching your search criteria")
            return
        
        if json_output:
            import json

            # Convert to JSON-serializable format
            results = []
            for manga in manga_list:
                result = {
                    "id": manga.id,
                    "title": manga.title.values,
                    "status": manga.status,
                    "content_rating": manga.content_rating,
                    "year": manga.year,
                    "demographic": manga.publication_demographic,
                    "original_language": manga.original_language,
                    "available_languages": manga.available_translated_languages,
                }
                
                # Add relationships
                authors = []
                artists = []
                for rel in manga.relationships:
                    if rel.type == "author" and rel.attributes:
                        authors.append(rel.attributes.get("name"))
                    elif rel.type == "artist" and rel.attributes:
                        artists.append(rel.attributes.get("name"))
                
                result["authors"] = [a for a in authors if a]
                result["artists"] = [a for a in artists if a]
                
                results.append(result)
            
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"\n{Fore.GREEN}Found {len(manga_list)} manga:\n")
            
            if verbose:
                for i, manga in enumerate(manga_list, 1):
                    print(f"{Fore.YELLOW}{'─' * 60}")
                    print(f"{Fore.YELLOW}{i}. {manga.title.get('en', 'Unknown Title')}")
                    print(f"{Fore.YELLOW}{'─' * 60}")
                    print(format_manga_info(manga, verbose=True))
                    print()
            else:
                print(format_manga_list(manga_list))
        
        client.close()
        
    except MangaDxException as e:
        print_error(f"API error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logger.exception("Search error")
        sys.exit(1)


def search_command() -> None:
    """
    Entry point for mangadx-search command.
    
    Parses command line arguments and executes the search functionality.
    """
    parser = argparse.ArgumentParser(
        description="Search for manga on MangaDx",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mangadx-search "One Piece"                    # Basic search
  mangadx-search "Attack on Titan" --verbose   # Detailed results
  mangadx-search "Naruto" --limit 10           # Limit results
  mangadx-search "Manga" --status ongoing      # Filter by status
  mangadx-search "Title" --year 2020           # Filter by year
  mangadx-search "Title" --json                # JSON output
        """
    )
    
    parser.add_argument(
        "title",
        help="Manga title to search for"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of results (default: 20)"
    )
    
    parser.add_argument(
        "--content-rating",
        nargs="+",
        choices=["safe", "suggestive", "erotica", "pornographic"],
        help="Content rating filter (default: safe, suggestive, erotica)"
    )
    
    parser.add_argument(
        "--status",
        nargs="+",
        choices=["ongoing", "completed", "hiatus", "cancelled"],
        help="Publication status filter"
    )
    
    parser.add_argument(
        "--demographic",
        nargs="+",
        choices=["shounen", "shoujo", "josei", "seinen"],
        help="Publication demographic filter"
    )
    
    parser.add_argument(
        "--year",
        type=int,
        help="Publication year filter"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information for each manga"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="MangaDx Scrapper 1.0.0"
    )
    
    args = parser.parse_args()
    
    search_manga(
        title=args.title,
        limit=args.limit,
        content_rating=args.content_rating,
        status=args.status,
        demographic=args.demographic,
        year=args.year,
        verbose=args.verbose,
        json_output=args.json
    )


if __name__ == "__main__":
    search_command()