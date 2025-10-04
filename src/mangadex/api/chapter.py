"""
Chapter API module.

This module provides methods for interacting with chapter endpoints.
"""

from typing import List, Optional, Dict, Any
from ..http_client import HTTPClient
from ..models import Chapter


class ChapterAPI:
    """API client for chapter operations."""

    def __init__(self, http_client: HTTPClient):
        """
        Initialize Chapter API.

        Args:
            http_client: HTTP client instance
        """
        self.client = http_client

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        ids: Optional[List[str]] = None,
        title: Optional[str] = None,
        groups: Optional[List[str]] = None,
        uploader: Optional[str] = None,
        manga: Optional[str] = None,
        volume: Optional[str] = None,
        chapter: Optional[str] = None,
        translated_language: Optional[List[str]] = None,
        original_language: Optional[List[str]] = None,
        excluded_original_language: Optional[List[str]] = None,
        content_rating: Optional[List[str]] = None,
        excluded_groups: Optional[List[str]] = None,
        excluded_uploaders: Optional[List[str]] = None,
        include_future_updates: Optional[bool] = None,
        include_empty_pages: Optional[bool] = None,
        include_future_publish_at: Optional[bool] = None,
        include_external_url: Optional[bool] = None,
        created_at_since: Optional[str] = None,
        updated_at_since: Optional[str] = None,
        publish_at_since: Optional[str] = None,
        order: Optional[Dict[str, str]] = None,
        includes: Optional[List[str]] = None,
    ) -> List[Chapter]:
        """
        Get chapter list.

        Args:
            limit: Number of results (max 100)
            offset: Pagination offset
            ids: Chapter UUIDs (max 100)
            title: Chapter title
            groups: Scanlation group UUIDs
            uploader: Uploader UUID
            manga: Manga UUID
            volume: Volume number
            chapter: Chapter number
            translated_language: Translated language codes
            original_language: Original language codes
            excluded_original_language: Excluded original language codes
            content_rating: Content ratings
            excluded_groups: Excluded scanlation groups
            excluded_uploaders: Excluded uploaders
            include_future_updates: Include future updates
            include_empty_pages: Include chapters with 0 pages
            include_future_publish_at: Include future publish dates
            include_external_url: Include external URL chapters
            created_at_since: Filter by creation date
            updated_at_since: Filter by update date
            publish_at_since: Filter by publish date
            order: Sort order
            includes: Related entities to include

        Returns:
            List of Chapter objects
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        if ids:
            params["ids[]"] = ids
        if title:
            params["title"] = title
        if groups:
            params["groups[]"] = groups
        if uploader:
            params["uploader"] = uploader
        if manga:
            params["manga"] = manga
        if volume:
            params["volume"] = volume
        if chapter:
            params["chapter"] = chapter
        if translated_language:
            params["translatedLanguage[]"] = translated_language
        if original_language:
            params["originalLanguage[]"] = original_language
        if excluded_original_language:
            params["excludedOriginalLanguage[]"] = excluded_original_language
        if content_rating:
            params["contentRating[]"] = content_rating
        if excluded_groups:
            params["excludedGroups[]"] = excluded_groups
        if excluded_uploaders:
            params["excludedUploaders[]"] = excluded_uploaders
        if include_future_updates is not None:
            params["includeFutureUpdates"] = "1" if include_future_updates else "0"
        if include_empty_pages is not None:
            params["includeEmptyPages"] = "1" if include_empty_pages else "0"
        if include_future_publish_at is not None:
            params["includeFuturePublishAt"] = "1" if include_future_publish_at else "0"
        if include_external_url is not None:
            params["includeExternalUrl"] = "1" if include_external_url else "0"
        if created_at_since:
            params["createdAtSince"] = created_at_since
        if updated_at_since:
            params["updatedAtSince"] = updated_at_since
        if publish_at_since:
            params["publishAtSince"] = publish_at_since
        if order:
            params["order"] = order
        if includes:
            params["includes[]"] = includes

        response = self.client.get("/chapter", params=params)
        return [Chapter.from_dict(item) for item in response.get("data", [])]

    def get(self, chapter_id: str, includes: Optional[List[str]] = None) -> Chapter:
        """
        Get chapter by ID.

        Args:
            chapter_id: Chapter UUID
            includes: Related entities to include

        Returns:
            Chapter object
        """
        params = {}
        if includes:
            params["includes[]"] = includes

        response = self.client.get(f"/chapter/{chapter_id}", params=params)
        return Chapter.from_dict(response["data"])
