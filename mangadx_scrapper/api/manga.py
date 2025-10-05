"""
Manga API module for MangaDx API integration.

This module provides comprehensive methods for interacting with MangaDx manga endpoints,
including search, retrieval, aggregation, and feed operations. All methods follow
RESTful principles and include proper error handling and validation.

API Reference: https://api.mangadex.org/docs/swagger.html#/Manga

Supported Operations:
    - Search manga with advanced filtering
    - Get manga by ID with related entities
    - Get manga volumes and chapters aggregate
    - Get manga chapter feed with pagination
    - Get random manga
    - Get available manga tags

Rate Limiting:
    All requests are subject to MangaDx API rate limits (5 requests per second by default).
    The HTTP client automatically handles rate limiting and retries.

Authentication:
    Most manga endpoints are public and don't require authentication.
    Some advanced features may require API authentication in the future.
"""

from typing import Any, Dict, List, Optional, Union

from ..exceptions import ValidationException, NotFoundException
from ..http_client import HTTPClient
from ..models import Manga


class MangaAPI:
    """
    API client for manga operations on MangaDx.
    
    This class provides methods to interact with all manga-related endpoints
    of the MangaDx API, including search, retrieval, and metadata operations.
    
    Attributes:
        client: HTTP client instance for making API requests
        
    Example:
        >>> from mangadx_scrapper import MangaDxClient
        >>> client = MangaDxClient()
        >>> manga_api = client.manga
        >>> 
        >>> # Search for manga
        >>> results = manga_api.search(title="One Piece", limit=5)
        >>> 
        >>> # Get specific manga
        >>> manga = manga_api.get("manga-id-here")
        >>> 
        >>> # Get chapters
        >>> chapters = manga_api.get_feed("manga-id-here", limit=10)
    """

    def __init__(self, http_client: HTTPClient):
        """
        Initialize Manga API client.

        Args:
            http_client: Configured HTTP client instance for API requests
            
        Raises:
            ValueError: If http_client is None
        """
        if http_client is None:
            raise ValueError("HTTP client cannot be None")
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
        Search for manga with advanced filtering options.
        
        This method provides comprehensive search functionality for manga on MangaDx,
        supporting multiple filters, sorting options, and pagination.
        
        API Endpoint: GET /manga
        Documentation: https://api.mangadex.org/docs/swagger.html#/Manga/get-search-manga

        Args:
            title: Manga title to search for (partial matching supported)
            authors: List of author UUIDs to filter by
            artists: List of artist UUIDs to filter by  
            year: Year of release (YYYY format)
            included_tags: List of tag UUIDs that must be included
            included_tags_mode: Logic for included tags ("AND" or "OR")
            excluded_tags: List of tag UUIDs to exclude
            excluded_tags_mode: Logic for excluded tags ("AND" or "OR")
            status: Publication status filter. Valid values:
                - "ongoing": Currently being published
                - "completed": Finished publication
                - "hiatus": On temporary break
                - "cancelled": Publication cancelled
            original_language: List of ISO 639-1 language codes for original language
            excluded_original_language: List of ISO 639-1 language codes to exclude
            available_translated_language: List of ISO 639-1 codes for available translations
            publication_demographic: Target demographic. Valid values:
                - "shounen": Young male audience
                - "shoujo": Young female audience  
                - "josei": Adult female audience
                - "seinen": Adult male audience
            ids: List of specific manga UUIDs to retrieve (max 100)
            content_rating: Content rating filter. Valid values:
                - "safe": Safe for all audiences
                - "suggestive": Mildly suggestive content
                - "erotica": Erotic content
                - "pornographic": Pornographic content
            created_at_since: Filter by creation date (ISO 8601 format: YYYY-MM-DDTHH:MM:SS)
            updated_at_since: Filter by last update date (ISO 8601 format)
            order: Sort order dictionary. Valid keys:
                - "title": Sort by title
                - "year": Sort by publication year
                - "createdAt": Sort by creation date
                - "updatedAt": Sort by update date
                - "latestUploadedChapter": Sort by latest chapter upload
                - "followedCount": Sort by follow count
                - "relevance": Sort by search relevance (only with title search)
                Values: "asc" (ascending) or "desc" (descending)
            includes: Related entities to include in response. Valid values:
                - "manga": Include manga data
                - "cover_art": Include cover art information
                - "author": Include author information
                - "artist": Include artist information
                - "tag": Include tag information
            has_available_chapters: Filter by chapter availability (True/False)
            group: Scanlation group UUID to filter by
            limit: Number of results to return (1-100, default: 10)
            offset: Pagination offset (default: 0)

        Returns:
            List of Manga objects matching the search criteria
            
        Raises:
            ValidationException: If parameters are invalid (e.g., limit > 100)
            APIException: If the API request fails
            NetworkException: If there's a network connectivity issue
            
        Example:
            >>> # Basic title search
            >>> results = manga_api.search(title="One Piece", limit=5)
            >>> 
            >>> # Advanced search with filters
            >>> results = manga_api.search(
            ...     title="romance",
            ...     status=["ongoing"],
            ...     content_rating=["safe", "suggestive"],
            ...     publication_demographic=["shoujo"],
            ...     available_translated_language=["en"],
            ...     order={"followedCount": "desc"},
            ...     limit=20
            ... )
            >>> 
            >>> # Search by specific tags
            >>> results = manga_api.search(
            ...     included_tags=["tag-uuid-1", "tag-uuid-2"],
            ...     included_tags_mode="AND",
            ...     excluded_tags=["tag-uuid-3"],
            ...     limit=10
            ... )
            
        Note:
            - Use get_tag_list() to retrieve available tag UUIDs
            - Large result sets should use pagination with limit/offset
            - Search relevance sorting only works when title parameter is provided
            - Rate limiting applies: max 5 requests per second
        """
        # Validate parameters
        if limit < 1 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")
        
        if offset < 0:
            raise ValidationException("Offset must be non-negative")
            
        if ids and len(ids) > 100:
            raise ValidationException("Maximum 100 manga IDs allowed")
            
        if included_tags_mode not in ["AND", "OR"]:
            raise ValidationException("included_tags_mode must be 'AND' or 'OR'")
            
        if excluded_tags_mode not in ["AND", "OR"]:
            raise ValidationException("excluded_tags_mode must be 'AND' or 'OR'")
            
        valid_status = ["ongoing", "completed", "hiatus", "cancelled"]
        if status and any(s not in valid_status for s in status):
            raise ValidationException(f"Invalid status. Valid values: {valid_status}")
            
        valid_demographics = ["shounen", "shoujo", "josei", "seinen"]
        if publication_demographic and any(d not in valid_demographics for d in publication_demographic):
            raise ValidationException(f"Invalid demographic. Valid values: {valid_demographics}")
            
        valid_content_ratings = ["safe", "suggestive", "erotica", "pornographic"]
        if content_rating and any(r not in valid_content_ratings for r in content_rating):
            raise ValidationException(f"Invalid content rating. Valid values: {valid_content_ratings}")
            
        valid_order_keys = ["title", "year", "createdAt", "updatedAt", "latestUploadedChapter", "followedCount", "relevance"]
        valid_order_values = ["asc", "desc"]
        if order:
            for key, value in order.items():
                if key not in valid_order_keys:
                    raise ValidationException(f"Invalid order key '{key}'. Valid keys: {valid_order_keys}")
                if value not in valid_order_values:
                    raise ValidationException(f"Invalid order value '{value}'. Valid values: {valid_order_values}")
                    
        valid_includes = ["manga", "cover_art", "author", "artist", "tag"]
        if includes and any(i not in valid_includes for i in includes):
            raise ValidationException(f"Invalid include value. Valid values: {valid_includes}")
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
        Retrieve a specific manga by its UUID.
        
        This method fetches detailed information about a single manga,
        including its metadata, relationships, and optionally related entities.
        
        API Endpoint: GET /manga/{id}
        Documentation: https://api.mangadex.org/docs/swagger.html#/Manga/get-manga-id

        Args:
            manga_id: The UUID of the manga to retrieve
            includes: Related entities to include in response. Valid values:
                - "manga": Include manga data (always included)
                - "cover_art": Include cover art information
                - "author": Include author information
                - "artist": Include artist information
                - "tag": Include tag information

        Returns:
            Manga object containing the manga's complete information
            
        Raises:
            ValidationException: If manga_id is not a valid UUID format
            NotFoundException: If the manga with the given ID doesn't exist
            APIException: If the API request fails
            NetworkException: If there's a network connectivity issue
            
        Example:
            >>> # Get basic manga information
            >>> manga = manga_api.get("manga-uuid-here")
            >>> print(f"Title: {manga.title}")
            >>> 
            >>> # Get manga with related information
            >>> manga = manga_api.get(
            ...     "manga-uuid-here",
            ...     includes=["cover_art", "author", "artist"]
            ... )
            >>> print(f"Cover URL: {manga.cover_art_url}")
            >>> print(f"Authors: {[author.name for author in manga.authors]}")
            
        Note:
            - The manga_id must be a valid UUID format
            - Including related entities may increase response time
            - Rate limiting applies: max 5 requests per second
        """
        # Validate manga_id format (basic UUID validation)
        if not manga_id or not isinstance(manga_id, str):
            raise ValidationException("manga_id must be a non-empty string")
            
        if len(manga_id) != 36 or manga_id.count('-') != 4:
            raise ValidationException("manga_id must be a valid UUID format")
            
        valid_includes = ["manga", "cover_art", "author", "artist", "tag"]
        if includes and any(i not in valid_includes for i in includes):
            raise ValidationException(f"Invalid include value. Valid values: {valid_includes}")
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
        Get manga aggregate data containing volumes and chapters structure.
        
        This method retrieves the complete volume and chapter structure for a manga,
        organized hierarchically. This is useful for understanding the manga's
        publication structure and available content.
        
        API Endpoint: GET /manga/{id}/aggregate
        Documentation: https://api.mangadex.org/docs/swagger.html#/Manga/get-manga-id-aggregate

        Args:
            manga_id: The UUID of the manga to get aggregate data for
            translated_language: List of ISO 639-1 language codes to filter chapters by.
                Examples: ["en", "ja", "es", "fr", "de"]
            groups: List of scanlation group UUIDs to filter chapters by.
                Only chapters from these groups will be included.

        Returns:
            Dictionary containing the aggregate structure with the following format:
            {
                "volumes": {
                    "volume_number": {
                        "volume": "volume_number",
                        "count": chapter_count,
                        "chapters": {
                            "chapter_number": {
                                "chapter": "chapter_number",
                                "id": "chapter_uuid",
                                "others": ["other_chapter_uuids"],
                                "count": 1
                            }
                        }
                    }
                }
            }
            
        Raises:
            ValidationException: If manga_id is not a valid UUID format
            NotFoundException: If the manga with the given ID doesn't exist
            APIException: If the API request fails
            NetworkException: If there's a network connectivity issue
            
        Example:
            >>> # Get all volumes and chapters
            >>> aggregate = manga_api.get_aggregate("manga-uuid-here")
            >>> for vol_num, vol_data in aggregate["volumes"].items():
            ...     print(f"Volume {vol_num}: {vol_data['count']} chapters")
            ...     for ch_num, ch_data in vol_data["chapters"].items():
            ...         print(f"  Chapter {ch_num}: {ch_data['id']}")
            >>> 
            >>> # Get only English chapters
            >>> aggregate = manga_api.get_aggregate(
            ...     "manga-uuid-here",
            ...     translated_language=["en"]
            ... )
            >>> 
            >>> # Filter by specific scanlation groups
            >>> aggregate = manga_api.get_aggregate(
            ...     "manga-uuid-here",
            ...     groups=["group-uuid-1", "group-uuid-2"]
            ... )
            
        Note:
            - The aggregate structure shows the organizational hierarchy of the manga
            - Filtering by language or groups will only affect which chapters are included
            - Volume "none" contains chapters not assigned to a specific volume
            - Chapter "others" array contains alternative versions of the same chapter
            - Rate limiting applies: max 5 requests per second
        """
        # Validate manga_id format
        if not manga_id or not isinstance(manga_id, str):
            raise ValidationException("manga_id must be a non-empty string")
            
        if len(manga_id) != 36 or manga_id.count('-') != 4:
            raise ValidationException("manga_id must be a valid UUID format")
            
        # Validate language codes (basic validation)
        if translated_language:
            for lang in translated_language:
                if not isinstance(lang, str) or len(lang) != 2:
                    raise ValidationException(f"Invalid language code '{lang}'. Must be 2-character ISO 639-1 code")
                    
        # Validate group UUIDs (basic validation)
        if groups:
            for group_id in groups:
                if not isinstance(group_id, str) or len(group_id) != 36:
                    raise ValidationException(f"Invalid group UUID '{group_id}'. Must be valid UUID format")
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