"""
Cover API module for MangaDx integration.

This module provides comprehensive methods for interacting with cover art endpoints
of the MangaDx API, including cover listing, retrieval, and URL generation.

API Reference: https://api.mangadex.org/docs/swagger.html#/Cover
Rate Limiting: All requests are subject to rate limiting (5 requests/second)

Supported Operations:
    - List cover art with filtering
    - Get individual cover details
    - Generate cover image URLs
    - Filter by manga, uploaders, locales

Authentication: Most operations are public, but some may require authentication
for uploading or modifying cover art.

Example Usage:
    >>> from mangadx_scrapper.http_client import HTTPClient
    >>> from mangadx_scrapper.api.cover import CoverAPI
    >>> 
    >>> client = HTTPClient()
    >>> cover_api = CoverAPI(client)
    >>> 
    >>> # List covers for a manga
    >>> covers = cover_api.list(manga=["manga-uuid-here"])
    >>> 
    >>> # Get cover image URL
    >>> url = cover_api.get_cover_url("manga-uuid", "cover-filename")
"""

from typing import Any, Dict, List, Optional

from ..exceptions import ValidationException
from ..http_client import HTTPClient
from ..models import Cover


class CoverAPI:
    """
    API client for cover art operations on MangaDx.
    
    This class provides methods to interact with cover art endpoints,
    including listing, filtering, and retrieving cover information.
    
    Attributes:
        client: HTTP client instance for making API requests
    """

    def __init__(self, http_client: HTTPClient):
        """
        Initialize Cover API client.

        Args:
            http_client: HTTP client instance for API communication
            
        Raises:
            ValueError: If http_client is None or invalid
        """
        if not http_client:
            raise ValueError("http_client cannot be None")
        self.client = http_client

    def list(
        self,
        limit: int = 10,
        offset: int = 0,
        manga: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        uploaders: Optional[List[str]] = None,
        locales: Optional[List[str]] = None,
        order: Optional[Dict[str, str]] = None,
        includes: Optional[List[str]] = None,
    ) -> List[Cover]:
        """
        Get cover art list.

        Args:
            limit: Number of results (max 100)
            offset: Pagination offset
            manga: Manga UUIDs
            ids: Cover art UUIDs
            uploaders: Uploader UUIDs
            locales: Locale codes
            order: Sort order
            includes: Related entities to include

        Returns:
            List of Cover objects
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        if manga:
            params["manga[]"] = manga
        if ids:
            params["ids[]"] = ids
        if uploaders:
            params["uploaders[]"] = uploaders
        if locales:
            params["locales[]"] = locales
        if order:
            params["order"] = order
        if includes:
            params["includes[]"] = includes

        response = self.client.get("/cover", params=params)
        return [Cover.from_dict(item) for item in response.get("data", [])]

    def get(self, cover_id: str, includes: Optional[List[str]] = None) -> Cover:
        """
        Get cover art by ID.

        Args:
            cover_id: Cover art UUID
            includes: Related entities to include

        Returns:
            Cover object
        """
        params = {}
        if includes:
            params["includes[]"] = includes

        response = self.client.get(f"/cover/{cover_id}", params=params)
        return Cover.from_dict(response["data"])

    def get_cover_url(self, manga_id: str, file_name: str, size: str = "original") -> str:
        """
        Get cover image URL.

        Args:
            manga_id: Manga UUID
            file_name: Cover file name
            size: Image size (original, 512, 256)

        Returns:
            Cover image URL
        """
        from ..config import Settings

        if size == "original":
            return f"{Settings.UPLOADS_URL}/covers/{manga_id}/{file_name}"
        else:
            return f"{Settings.UPLOADS_URL}/covers/{manga_id}/{file_name}.{size}.jpg"