"""
Manga API module.

This module provides methods for interacting with manga endpoints.
"""

from typing import List, Optional, Dict, Any
from ..http_client import HTTPClient
from ..models import Manga


class MangaAPI:
    """API client for manga operations."""

    def __init__(self, http_client: HTTPClient):
        """
        Initialize Manga API.

        Args:
            http_client: HTTP client instance
        """
        self.client = http_client

    def search(
        self,
        title: Optional[str] = None,
        authors: Optional[List[str]] = None,
        artists: Optional[List[str]] = None,
        year: Optional[int] = None,
        included_tags: Optional[List[str]] = None,
        included_tags_mode: str = "AND",
        excluded_tags: Optional[List[str]] = None,
        excluded_tags_mode: str = "OR",
        status: Optional[List[str]] = None,
        original_language: Optional[List[str]] = None,
        excluded_original_language: Optional[List[str]] = None,
        available_translated_language: Optional[List[str]] = None,
        publication_demographic: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        content_rating: Optional[List[str]] = None,
        created_at_since: Optional[str] = None,
        updated_at_since: Optional[str] = None,
        order: Optional[Dict[str, str]] = None,
        includes: Optional[List[str]] = None,
        has_available_chapters: Optional[bool] = None,
        group: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Manga]:
        """
        Search for manga.

        Args:
            title: Manga title to search for
            authors: List of author UUIDs
            artists: List of artist UUIDs
            year: Year of release
            included_tags: Tags to include (UUIDs)
            included_tags_mode: "AND" or "OR" for included tags
            excluded_tags: Tags to exclude (UUIDs)
            excluded_tags_mode: "AND" or "OR" for excluded tags
            status: Publication status (ongoing, completed, hiatus, cancelled)
            original_language: Original language codes
            excluded_original_language: Excluded original language codes
            available_translated_language: Available translated language codes
            publication_demographic: Demographics (shounen, shoujo, josei, seinen)
            ids: List of manga UUIDs (max 100)
            content_rating: Content ratings (safe, suggestive, erotica, pornographic)
            created_at_since: Filter by creation date (YYYY-MM-DDTHH:MM:SS)
            updated_at_since: Filter by update date (YYYY-MM-DDTHH:MM:SS)
            order: Sort order dictionary
            includes: Related entities to include
            has_available_chapters: Filter by chapter availability
            group: Scanlation group UUID
            limit: Number of results (max 100)
            offset: Pagination offset

        Returns:
            List of Manga objects
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        if title:
            params["title"] = title
        if authors:
            params["authors[]"] = authors
        if artists:
            params["artists[]"] = artists
        if year:
            params["year"] = year
        if included_tags:
            params["includedTags[]"] = included_tags
            params["includedTagsMode"] = included_tags_mode
        if excluded_tags:
            params["excludedTags[]"] = excluded_tags
            params["excludedTagsMode"] = excluded_tags_mode
        if status:
            params["status[]"] = status
        if original_language:
            params["originalLanguage[]"] = original_language
        if excluded_original_language:
            params["excludedOriginalLanguage[]"] = excluded_original_language
        if available_translated_language:
            params["availableTranslatedLanguage[]"] = available_translated_language
        if publication_demographic:
            params["publicationDemographic[]"] = publication_demographic
        if ids:
            params["ids[]"] = ids
        if content_rating:
            params["contentRating[]"] = content_rating
        if created_at_since:
            params["createdAtSince"] = created_at_since
        if updated_at_since:
            params["updatedAtSince"] = updated_at_since
        if order:
            params["order"] = order
        if includes:
            params["includes[]"] = includes
        if has_available_chapters is not None:
            params["hasAvailableChapters"] = "1" if has_available_chapters else "0"
        if group:
            params["group"] = group

        response = self.client.get("/manga", params=params)
        return [Manga.from_dict(item) for item in response.get("data", [])]

    def get(self, manga_id: str, includes: Optional[List[str]] = None) -> Manga:
        """
        Get manga by ID.

        Args:
            manga_id: Manga UUID
            includes: Related entities to include

        Returns:
            Manga object
        """
        params = {}
        if includes:
            params["includes[]"] = includes

        response = self.client.get(f"/manga/{manga_id}", params=params)
        return Manga.from_dict(response["data"])

    def get_aggregate(
        self,
        manga_id: str,
        translated_language: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get manga volumes and chapters aggregate.

        Args:
            manga_id: Manga UUID
            translated_language: Filter by translated languages
            groups: Filter by scanlation group UUIDs

        Returns:
            Dictionary with volumes and chapters structure
        """
        params = {}
        if translated_language:
            params["translatedLanguage[]"] = translated_language
        if groups:
            params["groups[]"] = groups

        response = self.client.get(f"/manga/{manga_id}/aggregate", params=params)
        return response.get("volumes", {})

    def get_chapters_list(
        self,
        manga_id: str,
        translated_language: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get a flat list of chapters from aggregate data.

        Args:
            manga_id: Manga UUID
            translated_language: Filter by translated languages
            groups: Filter by scanlation group UUIDs

        Returns:
            List of chapter dictionaries with chapter number and ID
        """
        volumes = self.get_aggregate(manga_id, translated_language, groups)
        chapters = []

        for volume_data in volumes.values():
            for chapter_data in volume_data.get("chapters", {}).values():
                chapters.append({
                    "volume": volume_data.get("volume"),
                    "chapter": chapter_data.get("chapter"),
                    "id": chapter_data.get("id"),
                    "others": chapter_data.get("others", []),
                    "count": chapter_data.get("count", 0),
                })

        return chapters

    def get_feed(
        self,
        manga_id: str,
        limit: int = 100,
        offset: int = 0,
        translated_language: Optional[List[str]] = None,
        original_language: Optional[List[str]] = None,
        excluded_original_language: Optional[List[str]] = None,
        content_rating: Optional[List[str]] = None,
        excluded_groups: Optional[List[str]] = None,
        excluded_uploaders: Optional[List[str]] = None,
        include_future_updates: Optional[bool] = None,
        created_at_since: Optional[str] = None,
        updated_at_since: Optional[str] = None,
        publish_at_since: Optional[str] = None,
        order: Optional[Dict[str, str]] = None,
        includes: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get manga chapter feed.

        Args:
            manga_id: Manga UUID
            limit: Number of results (max 500)
            offset: Pagination offset
            translated_language: Filter by translated languages
            original_language: Filter by original languages
            excluded_original_language: Exclude original languages
            content_rating: Content ratings filter
            excluded_groups: Exclude scanlation groups
            excluded_uploaders: Exclude uploaders
            include_future_updates: Include future chapter updates
            created_at_since: Filter by creation date
            updated_at_since: Filter by update date
            publish_at_since: Filter by publish date
            order: Sort order
            includes: Related entities to include

        Returns:
            List of chapter data
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

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

        response = self.client.get(f"/manga/{manga_id}/feed", params=params)
        return response.get("data", [])

    def get_random(self, includes: Optional[List[str]] = None, content_rating: Optional[List[str]] = None) -> Manga:
        """
        Get random manga.

        Args:
            includes: Related entities to include
            content_rating: Content ratings filter

        Returns:
            Random Manga object
        """
        params = {}
        if includes:
            params["includes[]"] = includes
        if content_rating:
            params["contentRating[]"] = content_rating

        response = self.client.get("/manga/random", params=params)
        return Manga.from_dict(response["data"])

    def get_tag_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available manga tags.

        Returns:
            List of tag dictionaries
        """
        response = self.client.get("/manga/tag")
        return response.get("data", [])
