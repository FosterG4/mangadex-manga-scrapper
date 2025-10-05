"""
Author API module.

This module provides methods for interacting with author endpoints.
"""

from typing import Any, Dict, List, Optional

from ..http_client import HTTPClient
from ..models import Author


class AuthorAPI:
    """API client for author operations."""

    def __init__(self, http_client: HTTPClient):
        """
        Initialize Author API.

        Args:
            http_client: HTTP client instance
        """
        self.client = http_client

    def list(
        self,
        limit: int = 10,
        offset: int = 0,
        ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        order: Optional[Dict[str, str]] = None,
        includes: Optional[List[str]] = None,
    ) -> List[Author]:
        """
        Get author list.

        Args:
            limit: Number of results (max 100)
            offset: Pagination offset
            ids: Author UUIDs (max 100)
            name: Author name to search
            order: Sort order
            includes: Related entities to include

        Returns:
            List of Author objects
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        if ids:
            params["ids[]"] = ids
        if name:
            params["name"] = name
        if order:
            params["order"] = order
        if includes:
            params["includes[]"] = includes

        response = self.client.get("/author", params=params)
        return [Author.from_dict(item) for item in response.get("data", [])]

    def get(self, author_id: str, includes: Optional[List[str]] = None) -> Author:
        """
        Get author by ID.

        Args:
            author_id: Author UUID
            includes: Related entities to include

        Returns:
            Author object
        """
        params = {}
        if includes:
            params["includes[]"] = includes

        response = self.client.get(f"/author/{author_id}", params=params)
        return Author.from_dict(response["data"])