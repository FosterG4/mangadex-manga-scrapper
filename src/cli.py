"""
Command-line interface for MangaDex downloader.

This module provides an interactive CLI for searching and downloading manga.
"""

from typing import Optional
from colorama import init, Fore, Style

from config import Settings
from src.mangadex import MangaDexClient
from src.mangadex.downloader import DownloadManager
from src.mangadex.exceptions import MangaDexException
from src.utils import setup_logger, format_manga_info, format_manga_list

# Initialize colorama
init(autoreset=True)

logger = setup_logger()


class CLI:
    """Interactive command-line interface."""

    def __init__(self):
        """Initialize CLI."""
        self.client = MangaDexClient()
        self.downloader = DownloadManager(self.client)

    def print_header(self):
        """Print application header."""
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}  MangaDex Manga Downloader v1.0")
        print(f"{Fore.CYAN}{'=' * 60}\n")

    def print_success(self, message: str):
        """Print success message."""
        print(f"{Fore.GREEN}✓ {message}")

    def print_error(self, message: str):
        """Print error message."""
        print(f"{Fore.RED}✗ {message}")

    def print_info(self, message: str):
        """Print info message."""
        print(f"{Fore.CYAN}ℹ {message}")

    def print_warning(self, message: str):
        """Print warning message."""
        print(f"{Fore.YELLOW}⚠ {message}")

    def search_manga(self) -> Optional[str]:
        """
        Search for manga and return selected manga ID.

        Returns:
            Selected manga ID or None
        """
        try:
            print(f"\n{Fore.YELLOW}{'─' * 60}")
            print(f"{Fore.YELLOW}MANGA SEARCH")
            print(f"{Fore.YELLOW}{'─' * 60}\n")

            title = input(f"{Fore.CYAN}Enter manga title to search: {Style.RESET_ALL}").strip()

            if not title:
                self.print_error("Title cannot be empty")
                return None

            self.print_info(f"Searching for '{title}'...")

            manga_list = self.client.manga.search(
                title=title,
                limit=20,
                content_rating=Settings.DEFAULT_CONTENT_RATING,
                includes=["cover_art", "author", "artist"],
            )

            if not manga_list:
                self.print_warning("No manga found matching your search")
                return None

            print(f"\n{Fore.GREEN}Found {len(manga_list)} manga:\n")
            print(format_manga_list(manga_list))

            print(f"\n{Fore.YELLOW}{'─' * 60}\n")
            selection = input(f"{Fore.CYAN}Enter manga number (or 0 to cancel): {Style.RESET_ALL}").strip()

            try:
                idx = int(selection)
                if idx == 0:
                    self.print_info("Search cancelled")
                    return None

                if 1 <= idx <= len(manga_list):
                    selected_manga = manga_list[idx - 1]
                    print(f"\n{Fore.GREEN}Selected manga:")
                    print(f"{Fore.WHITE}{format_manga_info(selected_manga, verbose=True)}\n")
                    return selected_manga.id
                else:
                    self.print_error("Invalid selection")
                    return None

            except ValueError:
                self.print_error("Invalid input. Please enter a number")
                return None

        except MangaDexException as e:
            self.print_error(f"API error: {e}")
            return None
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            logger.exception("Search error")
            return None

    def get_download_options(self) -> dict:
        """
        Get download options from user.

        Returns:
            Dictionary with download options
        """
        options = {
            "languages": [],
            "volume_filter": None,
            "chapter_filter": None,
            "data_saver": False,
        }

        print(f"\n{Fore.YELLOW}{'─' * 60}")
        print(f"{Fore.YELLOW}DOWNLOAD OPTIONS")
        print(f"{Fore.YELLOW}{'─' * 60}\n")

        # Language selection
        lang_input = input(
            f"{Fore.CYAN}Enter language codes (comma-separated, default: {Settings.DEFAULT_LANGUAGE}): {Style.RESET_ALL}"
        ).strip()

        if lang_input:
            options["languages"] = [lang.strip() for lang in lang_input.split(",")]
        else:
            options["languages"] = [Settings.DEFAULT_LANGUAGE]

        # Volume filter
        volume_input = input(
            f"{Fore.CYAN}Enter volume numbers to download (comma-separated, or press Enter for all): {Style.RESET_ALL}"
        ).strip()

        if volume_input:
            options["volume_filter"] = [vol.strip() for vol in volume_input.split(",")]

        # Chapter filter
        chapter_input = input(
            f"{Fore.CYAN}Enter chapter numbers to download (comma-separated, or press Enter for all): {Style.RESET_ALL}"
        ).strip()

        if chapter_input:
            options["chapter_filter"] = [ch.strip() for ch in chapter_input.split(",")]

        # Chapter range option
        if not options["chapter_filter"]:
            range_input = input(
                f"{Fore.CYAN}Download chapter range? (e.g., '1-10', or press Enter to skip): {Style.RESET_ALL}"
            ).strip()

            if range_input and "-" in range_input:
                try:
                    start, end = range_input.split("-")
                    start_ch = float(start.strip())
                    end_ch = float(end.strip())

                    # Generate chapter list
                    options["chapter_range"] = (start_ch, end_ch)
                except ValueError:
                    self.print_warning("Invalid range format, downloading all chapters")

        # Data saver option
        data_saver_input = input(
            f"{Fore.CYAN}Use data saver mode (lower quality, smaller size)? (y/N): {Style.RESET_ALL}"
        ).strip().lower()

        options["data_saver"] = data_saver_input == "y"

        return options

    def download_manga(self, manga_id: str):
        """
        Download manga with user-specified options.

        Args:
            manga_id: Manga UUID
        """
        try:
            options = self.get_download_options()

            print(f"\n{Fore.YELLOW}{'─' * 60}")
            print(f"{Fore.YELLOW}STARTING DOWNLOAD")
            print(f"{Fore.YELLOW}{'─' * 60}\n")

            self.print_info("Fetching manga information...")

            # Check if using chapter range
            if "chapter_range" in options:
                start_ch, end_ch = options["chapter_range"]
                self.print_info(f"Downloading chapters {start_ch} to {end_ch}")

                stats = self.downloader.download_chapter_range(
                    manga_id=manga_id,
                    start_chapter=start_ch,
                    end_chapter=end_ch,
                    language=options["languages"][0],
                    data_saver=options["data_saver"],
                )
            else:
                stats = self.downloader.download_manga(
                    manga_id=manga_id,
                    languages=options["languages"],
                    volume_filter=options["volume_filter"],
                    chapter_filter=options["chapter_filter"],
                    data_saver=options["data_saver"],
                )

            # Print statistics
            print(f"\n{Fore.YELLOW}{'─' * 60}")
            print(f"{Fore.YELLOW}DOWNLOAD COMPLETE")
            print(f"{Fore.YELLOW}{'─' * 60}\n")

            print(f"{Fore.WHITE}Manga: {stats['manga_title']}")
            print(f"{Fore.GREEN}Downloaded: {stats['downloaded']}/{stats['total_chapters']} chapters")

            if stats.get("failed", 0) > 0:
                print(f"{Fore.RED}Failed: {stats['failed']} chapters")

            print(f"\n{Fore.CYAN}Files saved to: {self.downloader.download_dir}\n")

        except MangaDexException as e:
            self.print_error(f"Download failed: {e}")
            logger.exception("Download error")
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            logger.exception("Download error")

    def run(self):
        """Run the interactive CLI."""
        try:
            self.print_header()

            # Check API connectivity
            self.print_info("Checking API connectivity...")
            if not self.client.ping():
                self.print_error("Cannot connect to MangaDex API")
                return

            self.print_success("Connected to MangaDex API")

            while True:
                print(f"\n{Fore.YELLOW}{'─' * 60}")
                print(f"{Fore.YELLOW}MAIN MENU")
                print(f"{Fore.YELLOW}{'─' * 60}\n")
                print(f"{Fore.WHITE}1. Search and download manga")
                print(f"{Fore.WHITE}2. Download by manga ID")
                print(f"{Fore.WHITE}3. Exit\n")

                choice = input(f"{Fore.CYAN}Enter your choice: {Style.RESET_ALL}").strip()

                if choice == "1":
                    manga_id = self.search_manga()
                    if manga_id:
                        confirm = input(
                            f"\n{Fore.CYAN}Proceed with download? (Y/n): {Style.RESET_ALL}"
                        ).strip().lower()

                        if confirm != "n":
                            self.download_manga(manga_id)

                elif choice == "2":
                    manga_id = input(
                        f"\n{Fore.CYAN}Enter manga ID: {Style.RESET_ALL}"
                    ).strip()

                    if manga_id:
                        self.download_manga(manga_id)

                elif choice == "3":
                    self.print_info("Goodbye!")
                    break

                else:
                    self.print_error("Invalid choice. Please try again.")

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Operation cancelled by user")
        except Exception as e:
            self.print_error(f"Fatal error: {e}")
            logger.exception("Fatal error")
        finally:
            self.client.close()


def main():
    """Main entry point."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
