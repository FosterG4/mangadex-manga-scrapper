"""
Main entry point for MangaDx Manga Scrapper.

This script provides the main interface for the application.
For pip installations, use the CLI commands directly:
- mangadx-scrapper (interactive mode)
- mangadx-search (search functionality)
- mangadx-download (download functionality)
"""

from mangadx_scrapper.cli.main import main

if __name__ == "__main__":
    main()
