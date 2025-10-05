"""
AtHome API module.

This module provides methods for getting chapter image URLs from MangaDx@Home.
"""

from typing import Any, Dict, List

from ..http_client import HTTPClient


class AtHomeAPI:
    """API client for MangaDx@Home operations."""

    def __init__(self, http_client: HTTPClient):
        """
        Initialize AtHome API.

        Args:
            http_client: HTTP client instance
        """
        self.client = http_client

    def get_server(self, chapter_id: str, force_port_443: bool = False) -> Dict[str, Any]:
        """
        Get MangaDx@Home server URL for chapter.
        
        Args:
            chapter_id: Chapter UUID
            force_port_443: Force HTTPS port 443

        Returns:
            Dictionary with baseUrl and chapter data
        """
        params = {}
        if force_port_443:
            params["forcePort443"] = "true"

        response = self.client.get(f"/at-home/server/{chapter_id}", params=params)
        return response

    def get_image_urls(self, chapter_id: str, data_saver: bool = False) -> List[str]:
        """
        Get list of image URLs for chapter.

        Args:
            chapter_id: Chapter UUID
            data_saver: Use data saver images (lower quality)

        Returns:
            List of full image URLs
        """
        server_data = self.get_server(chapter_id)
        base_url = server_data.get("baseUrl", "")
        chapter_data = server_data.get("chapter", {})
        chapter_hash = chapter_data.get("hash", "")

        if data_saver:
            images = chapter_data.get("dataSaver", [])
            quality = "data-saver"
        else:
            images = chapter_data.get("data", [])
            quality = "data"

        return [f"{base_url}/{quality}/{chapter_hash}/{image}" for image in images]
