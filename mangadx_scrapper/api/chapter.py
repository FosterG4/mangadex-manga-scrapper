"""
Chapter API module for MangaDx integration.

This module provides comprehensive methods for interacting with chapter endpoints
of the MangaDx API, including chapter listing, retrieval, and filtering operations.

API Reference: https://api.mangadex.org/docs/swagger.html#/Chapter
Rate Limiting: All requests are subject to rate limiting (5 requests/second)

Supported Operations:
    - List chapters with advanced filtering
    - Get individual chapter details
    - Filter by manga, groups, uploaders, languages
    - Sort and paginate results

Authentication: Most operations are public, but some may require authentication
for access to certain content ratings or private chapters.

Example Usage:
    >>> from mangadx_scrapper.http_client import HTTPClient
    >>> from mangadx_scrapper.api.chapter import ChapterAPI
    >>> 
    >>> client = HTTPClient()
    >>> chapter_api = ChapterAPI(client)
    >>> 
    >>> # List recent chapters
    >>> chapters = chapter_api.list(limit=10, order={"publishAt": "desc"})
    >>> 
    >>> # Get specific chapter
    >>> chapter = chapter_api.get("chapter-uuid-here")
    >>> print(f"Chapter {chapter.chapter}: {chapter.title}")
"""

from typing import Any, Dict, List, Optional

from ..exceptions import ValidationException
from ..http_client import HTTPClient
from ..models import Chapter


class ChapterAPI:
    """
    API client for chapter operations on MangaDx.
    
    This class provides methods to interact with chapter-related endpoints,
    including listing, filtering, and retrieving individual chapters.
    
    Attributes:
        client: HTTP client instance for making API requests
    """

    def __init__(self, http_client: HTTPClient):
        """
        Initialize Chapter API client.

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
        List chapters with comprehensive filtering and sorting options.
        
        This method provides advanced chapter listing functionality with extensive
        filtering capabilities for finding specific chapters across the MangaDx database.
        
        API Endpoint: GET /chapter
        Documentation: https://api.mangadex.org/docs/swagger.html#/Chapter/get-chapter

        Args:
            limit: Number of results to return (1-500, default: 100)
            offset: Pagination offset for result sets (default: 0)
            ids: List of specific chapter UUIDs to retrieve (max 100)
            title: Chapter title to search for (partial matching supported)
            groups: List of scanlation group UUIDs to filter by
            uploader: UUID of the uploader to filter by
            manga: UUID of the manga to get chapters for
            volume: Volume number to filter by (string format)
            chapter: Chapter number to filter by (string format, supports decimals)
            translated_language: List of ISO 639-1 language codes for translations
            original_language: List of ISO 639-1 codes for original language
            excluded_original_language: List of ISO 639-1 codes to exclude
            content_rating: Content rating filter. Valid values:
                - "safe": Safe for all audiences
                - "suggestive": Mildly suggestive content
                - "erotica": Erotic content
                - "pornographic": Pornographic content
            excluded_groups: List of scanlation group UUIDs to exclude
            excluded_uploaders: List of uploader UUIDs to exclude
            include_future_updates: Include chapters with future update dates
            include_empty_pages: Include chapters that have no pages
            include_future_publish_at: Include chapters with future publish dates
            include_external_url: Include chapters that link to external sites
            created_at_since: Filter by creation date (ISO 8601 format)
            updated_at_since: Filter by last update date (ISO 8601 format)
            publish_at_since: Filter by publish date (ISO 8601 format)
            order: Sort order dictionary. Valid keys:
                - "createdAt": Sort by creation date
                - "updatedAt": Sort by update date
                - "publishAt": Sort by publish date
                - "readableAt": Sort by readable date
                - "volume": Sort by volume number
                - "chapter": Sort by chapter number
                Values: "asc" (ascending) or "desc" (descending)
            includes: Related entities to include in response. Valid values:
                - "manga": Include manga information
                - "scanlation_group": Include scanlation group information
                - "user": Include uploader information

        Returns:
            List of Chapter objects matching the specified criteria
            
        Raises:
            ValidationException: If parameters are invalid (e.g., limit > 500)
            APIException: If the API request fails
            NetworkException: If there's a network connectivity issue
            
        Example:
            >>> # Get recent chapters for a specific manga
            >>> chapters = chapter_api.list(
            ...     manga="manga-uuid-here",
            ...     translated_language=["en"],
            ...     order={"publishAt": "desc"},
            ...     limit=20
            ... )
            >>> 
            >>> # Get chapters from specific scanlation groups
            >>> chapters = chapter_api.list(
            ...     groups=["group-uuid-1", "group-uuid-2"],
            ...     content_rating=["safe", "suggestive"],
            ...     limit=50
            ... )
            >>> 
            >>> # Search for specific chapter numbers
            >>> chapters = chapter_api.list(
            ...     manga="manga-uuid-here",
            ...     chapter="1",
            ...     translated_language=["en"]
            ... )
            >>> 
            >>> # Get chapters published since a specific date
            >>> chapters = chapter_api.list(
            ...     publish_at_since="2024-01-01T00:00:00",
            ...     order={"publishAt": "asc"},
            ...     limit=100
            ... )
            
        Note:
            - Large result sets should use pagination with limit/offset
            - Chapter and volume numbers are stored as strings and support decimals
            - Date filters use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
            - Rate limiting applies: max 5 requests per second
            - Some content may require authentication based on content rating
        """
        # Validate parameters
        if limit < 1 or limit > 500:
            raise ValidationException("Limit must be between 1 and 500")
        
        if offset < 0:
            raise ValidationException("Offset must be non-negative")
            
        if ids and len(ids) > 100:
            raise ValidationException("Maximum 100 chapter IDs allowed")
            
        valid_content_ratings = ["safe", "suggestive", "erotica", "pornographic"]
        if content_rating and any(r not in valid_content_ratings for r in content_rating):
            raise ValidationException(f"Invalid content rating. Valid values: {valid_content_ratings}")
            
        valid_order_keys = ["createdAt", "updatedAt", "publishAt", "readableAt", "volume", "chapter"]
        valid_order_values = ["asc", "desc"]
        if order:
            for key, value in order.items():
                if key not in valid_order_keys:
                    raise ValidationException(f"Invalid order key '{key}'. Valid keys: {valid_order_keys}")
                if value not in valid_order_values:
                    raise ValidationException(f"Invalid order value '{value}'. Valid values: {valid_order_values}")
                    
        valid_includes = ["manga", "scanlation_group", "user"]
        if includes and any(i not in valid_includes for i in includes):
            raise ValidationException(f"Invalid include value. Valid values: {valid_includes}")
            
        # Validate language codes
        if translated_language:
            for lang in translated_language:
                if not isinstance(lang, str) or len(lang) != 2:
                    raise ValidationException(f"Invalid language code '{lang}'. Must be 2-character ISO 639-1 code")
                    
        if original_language:
            for lang in original_language:
                if not isinstance(lang, str) or len(lang) != 2:
                    raise ValidationException(f"Invalid original language code '{lang}'. Must be 2-character ISO 639-1 code")
                    
        if excluded_original_language:
            for lang in excluded_original_language:
                if not isinstance(lang, str) or len(lang) != 2:
                    raise ValidationException(f"Invalid excluded language code '{lang}'. Must be 2-character ISO 639-1 code")
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
        Retrieve a specific chapter by its UUID.
        
        This method fetches detailed information about a single chapter,
        including its metadata, relationships, and optionally related entities.
        
        API Endpoint: GET /chapter/{id}
        Documentation: https://api.mangadex.org/docs/swagger.html#/Chapter/get-chapter-id

        Args:
            chapter_id: The UUID of the chapter to retrieve
            includes: Related entities to include in response. Valid values:
                - "manga": Include manga information
                - "scanlation_group": Include scanlation group information
                - "user": Include uploader information

        Returns:
            Chapter object containing the chapter's complete information
            
        Raises:
            ValidationException: If chapter_id is not a valid UUID format
            NotFoundException: If the chapter with the given ID doesn't exist
            APIException: If the API request fails
            NetworkException: If there's a network connectivity issue
            
        Example:
            >>> # Get basic chapter information
            >>> chapter = chapter_api.get("chapter-uuid-here")
            >>> print(f"Chapter {chapter.chapter}: {chapter.title}")
            >>> print(f"Pages: {chapter.pages}")
            >>> 
            >>> # Get chapter with related information
            >>> chapter = chapter_api.get(
            ...     "chapter-uuid-here",
            ...     includes=["manga", "scanlation_group"]
            ... )
            >>> print(f"Manga: {chapter.manga.title}")
            >>> print(f"Group: {chapter.scanlation_group.name}")
            
        Note:
            - The chapter_id must be a valid UUID format
            - Including related entities may increase response time
            - Rate limiting applies: max 5 requests per second
            - Some chapters may require authentication based on content rating
        """
        # Validate chapter_id format
        if not chapter_id or not isinstance(chapter_id, str):
            raise ValidationException("chapter_id must be a non-empty string")
            
        if len(chapter_id) != 36 or chapter_id.count('-') != 4:
            raise ValidationException("chapter_id must be a valid UUID format")
            
        valid_includes = ["manga", "scanlation_group", "user"]
        if includes and any(i not in valid_includes for i in includes):
            raise ValidationException(f"Invalid include value. Valid values: {valid_includes}")
        params = {}
        if includes:
            params["includes[]"] = includes

        response = self.client.get(f"/chapter/{chapter_id}", params=params)
        return Chapter.from_dict(response["data"])