"""
Main MangaDex API client.

This module provides the main client interface for all API operations.
"""

import logging
from typing import Optional

from config import Settings
from .http_client import HTTPClient
from .api import (
    MangaAPI,
    ChapterAPI,
    AuthorAPI,
    CoverAPI,
    ScanlationGroupAPI,
    AtHomeAPI,
)

logger = logging.getLogger(__name__)


class MangaDexClient:
    """Main client for MangaDex API operations."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """
        Initialize MangaDex client.

        Args:
            base_url: Base URL for API (defaults to Settings.BASE_URL)
            access_token: Optional access token for authenticated requests
        """
        self.base_url = base_url or Settings.BASE_URL
        self.http_client = HTTPClient(self.base_url, access_token)

        # Initialize API modules
        self.manga = MangaAPI(self.http_client)
        self.chapter = ChapterAPI(self.http_client)
        self.author = AuthorAPI(self.http_client)
        self.cover = CoverAPI(self.http_client)
        self.scanlation_group = ScanlationGroupAPI(self.http_client)
        self.at_home = AtHomeAPI(self.http_client)

        logger.info(f"MangaDex client initialized with base URL: {self.base_url}")

    def ping(self) -> bool:
        """
        Ping the API to check if it's available.

        Returns:
            True if API is available, False otherwise
        """
        try:
            response = self.http_client.get("/ping", skip_rate_limit=True)
            return response.get("result") == "ok" or "pong" in str(response).lower()
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    def close(self) -> None:
        """Close the HTTP client session."""
        self.http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
