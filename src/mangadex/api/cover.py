"""
Cover API module.

This module provides methods for interacting with cover art endpoints.
"""

from typing import List, Optional, Dict, Any
from ..http_client import HTTPClient
from ..models import Cover


class CoverAPI:
    """API client for cover art operations."""

    def __init__(self, http_client: HTTPClient):
        """
        Initialize Cover API.

        Args:
            http_client: HTTP client instance
        """
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
        from config import Settings

        if size == "original":
            return f"{Settings.UPLOADS_URL}/covers/{manga_id}/{file_name}"
        else:
            return f"{Settings.UPLOADS_URL}/covers/{manga_id}/{file_name}.{size}.jpg"
