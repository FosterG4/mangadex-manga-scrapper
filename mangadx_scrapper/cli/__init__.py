"""
Command-line interface for MangaDx Scrapper.

This package provides CLI commands for the MangaDx Scrapper.
"""

from .main import main
from .search import search_command
from .download import download_command

__all__ = ["main", "search_command", "download_command"]