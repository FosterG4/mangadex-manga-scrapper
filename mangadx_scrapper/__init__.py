"""MangaDx Scrapper - A Python library for downloading manga from MangaDx.

This package provides both a programmatic API and command-line interface
for searching and downloading manga from the MangaDx platform.

Basic Usage:
    >>> from mangadx_scrapper import MangaDxClient, DownloadManager
    >>> 
    >>> # Create client
    >>> client = MangaDxClient()
    >>> 
    >>> # Search for manga
    >>> manga_list = client.manga.search("One Piece", limit=5)
    >>> 
    >>> # Download manga
    >>> downloader = DownloadManager(client)
    >>> downloader.download_manga(manga_list[0].id, languages=["en"])
    >>> 
    >>> # Close client
    >>> client.close()

CLI Usage:
    $ mangadx-search "One Piece"
    $ mangadx-download abc123-def456-ghi789 --language en
    $ mangadx-scrapper  # Interactive mode
"""

from .client import MangaDxClient
from .downloader import DownloadManager
from .models import Manga, Chapter, Relationship, LocalizedString
from .exceptions import (
    MangaDxException,
    APIException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    RateLimitException,
    ValidationException,
    ServerException,
    NetworkException,
    TimeoutException,
    DownloadException,
)

# Import API modules for convenience
from .api import (
    MangaAPI,
    ChapterAPI,
    AtHomeAPI,
    AuthorAPI,
    CoverAPI,
    ScanlationGroupAPI,
)

__version__ = "1.0.0"
__author__ = "MangaDx Scrapper Team"
__email__ = ""
__license__ = "MIT"

__all__ = [
    # Core classes
    "MangaDxClient",
    "DownloadManager",
    
    # Models
    "Manga",
    "Chapter", 
    "Relationship",
    "LocalizedString",
    
    # API classes
    "MangaAPI",
    "ChapterAPI",
    "AtHomeAPI",
    "AuthorAPI",
    "CoverAPI",
    "ScanlationGroupAPI",
    
    # Exceptions
    "MangaDxException",
    "APIException",
    "AuthenticationException",
    "AuthorizationException",
    "NotFoundException",
    "RateLimitException",
    "ValidationException",
    "ServerException",
    "NetworkException",
    "TimeoutException",
    "DownloadException",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]