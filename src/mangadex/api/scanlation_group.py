"""
Scanlation Group API module.

This module provides methods for interacting with scanlation group endpoints.
"""

from typing import List, Optional, Dict, Any
from ..http_client import HTTPClient
from ..models import ScanlationGroup


class ScanlationGroupAPI:
    """API client for scanlation group operations."""

    def __init__(self, http_client: HTTPClient):
        """
        Initialize Scanlation Group API.

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
        focused_language: Optional[str] = None,
        order: Optional[Dict[str, str]] = None,
        includes: Optional[List[str]] = None,
    ) -> List[ScanlationGroup]:
        """
        Get scanlation group list.

        Args:
            limit: Number of results (max 100)
            offset: Pagination offset
            ids: Group UUIDs (max 100)
            name: Group name to search
            focused_language: Focused language code
            order: Sort order
            includes: Related entities to include

        Returns:
            List of ScanlationGroup objects
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        if ids:
            params["ids[]"] = ids
        if name:
            params["name"] = name
        if focused_language:
            params["focusedLanguage"] = focused_language
        if order:
            params["order"] = order
        if includes:
            params["includes[]"] = includes

        response = self.client.get("/group", params=params)
        return [ScanlationGroup.from_dict(item) for item in response.get("data", [])]

    def get(self, group_id: str, includes: Optional[List[str]] = None) -> ScanlationGroup:
        """
        Get scanlation group by ID.

        Args:
            group_id: Group UUID
            includes: Related entities to include

        Returns:
            ScanlationGroup object
        """
        params = {}
        if includes:
            params["includes[]"] = includes

        response = self.client.get(f"/group/{group_id}", params=params)
        return ScanlationGroup.from_dict(response["data"])
