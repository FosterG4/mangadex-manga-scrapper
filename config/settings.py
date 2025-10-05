"""Configuration settings for Mangadx API client.

This module loads and manages all configuration from environment variables.
Provides comprehensive validation and documentation for all settings."""

import os
import re
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables.
    
    This class manages all configuration for the Mangadx scrapper, including
    API endpoints, authentication, download settings, rate limiting, and more.
    All settings can be overridden via environment variables.
    """

    # API Configuration
    # The official MangaDx API endpoint
    BASE_URL: str = os.getenv("MANGADX_API_URL", "https://api.mangadex.org")
    # MangaDx uploads CDN for manga cover images and chapter pages
    UPLOADS_URL: str = os.getenv("MANGADX_UPLOADS_URL", "https://uploads.mangadex.org")
    
    # Authentication (Optional)
    USERNAME: Optional[str] = os.getenv("USERNAME")
    PASSWORD: Optional[str] = os.getenv("PASSWORD")
    CLIENT_ID: Optional[str] = os.getenv("CLIENT_ID")
    CLIENT_SECRET: Optional[str] = os.getenv("CLIENT_SECRET")
    REFRESH_TOKEN: Optional[str] = os.getenv("REFRESH_TOKEN")
    
    # Download Configuration
    DOWNLOAD_DIR: Path = Path(os.getenv("DOWNLOAD_DIR", "./downloads"))
    MAX_CONCURRENT_DOWNLOADS: int = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "10"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "8192"))
    
    # Rate Limiting Configuration
    # Mangadx API allows ~5 requests/second. Default 0.25s = 4 req/s to stay safe
    # See: https://api.mangadex.org/docs/2-limitations/
    RATE_LIMIT_DELAY: float = float(os.getenv("RATE_LIMIT_DELAY", "0.25"))
    # Maximum number of retry attempts for failed requests
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    # Base delay between retries (uses exponential backoff)
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "2.0"))
    
    # Request Configuration
    # Timeout for HTTP requests in seconds
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    # User agent string for API requests
    USER_AGENT: str = os.getenv("USER_AGENT", "MangadxDownloader/1.0")
    
    # Default Filters
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    DEFAULT_CONTENT_RATING: list = os.getenv(
        "DEFAULT_CONTENT_RATING", "safe,suggestive,erotica"
    ).split(",")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Feature Flags
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", "./.cache"))
    CACHE_EXPIRY: int = int(os.getenv("CACHE_EXPIRY", "3600"))
    AUTO_UPDATE_STRUCTURE: bool = os.getenv("AUTO_UPDATE_STRUCTURE", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> None:
        """Validate all configuration settings.
        
        Performs comprehensive validation of all settings including:
        - URL format validation
        - Numeric range validation  
        - Directory creation
        - Rate limiting compliance
        
        Raises:
            ValueError: If any setting is invalid
            OSError: If directory creation fails
        """
        # Validate API URLs
        cls._validate_url(cls.BASE_URL, "BASE_URL")
        cls._validate_url(cls.UPLOADS_URL, "UPLOADS_URL")
        
        # Validate numeric settings
        if cls.MAX_CONCURRENT_DOWNLOADS < 1:
            raise ValueError("MAX_CONCURRENT_DOWNLOADS must be at least 1")
        
        if cls.MAX_CONCURRENT_DOWNLOADS > 50:
            raise ValueError("MAX_CONCURRENT_DOWNLOADS should not exceed 50 to avoid overwhelming the server")
            
        if cls.RATE_LIMIT_DELAY < 0:
            raise ValueError("RATE_LIMIT_DELAY must be non-negative")
            
        if cls.RATE_LIMIT_DELAY < 0.1:
            raise ValueError("RATE_LIMIT_DELAY should be at least 0.1 seconds to respect Mangadx API limits")
        
        if cls.MAX_RETRIES < 0:
            raise ValueError("MAX_RETRIES must be non-negative")
            
        if cls.MAX_RETRIES > 10:
            raise ValueError("MAX_RETRIES should not exceed 10 to avoid excessive retry attempts")
        
        if cls.RETRY_DELAY < 0:
            raise ValueError("RETRY_DELAY must be non-negative")
        
        if cls.REQUEST_TIMEOUT < 1:
            raise ValueError("REQUEST_TIMEOUT must be at least 1 second")
            
        if cls.REQUEST_TIMEOUT > 300:
            raise ValueError("REQUEST_TIMEOUT should not exceed 300 seconds")
        
        if cls.CHUNK_SIZE < 1024:
            raise ValueError("CHUNK_SIZE should be at least 1024 bytes")
        
        # Validate content rating
        valid_ratings = {"safe", "suggestive", "erotica", "pornographic"}
        for rating in cls.DEFAULT_CONTENT_RATING:
            if rating.strip() not in valid_ratings:
                raise ValueError(f"Invalid content rating: {rating}. Must be one of: {valid_ratings}")
        
        # Validate language code format (ISO 639-1)
        if not re.match(r'^[a-z]{2}$', cls.DEFAULT_LANGUAGE):
            raise ValueError(f"DEFAULT_LANGUAGE must be a valid ISO 639-1 language code (e.g., 'en', 'ja')")
        
        # Create necessary directories
        try:
            cls.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
            if cls.ENABLE_CACHE:
                cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create required directories: {e}")
    
    @classmethod
    def _validate_url(cls, url: str, setting_name: str) -> None:
        """Validate URL format.
        
        Args:
            url: URL to validate
            setting_name: Name of the setting for error messages
            
        Raises:
            ValueError: If URL is invalid
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"{setting_name} must be a valid URL with scheme and domain")
            if parsed.scheme not in ('http', 'https'):
                raise ValueError(f"{setting_name} must use HTTP or HTTPS protocol")
        except Exception as e:
            raise ValueError(f"Invalid URL for {setting_name}: {e}")
    
    @classmethod
    def get_environment_info(cls) -> dict:
        """Get current environment configuration info.
        
        Returns:
            Dictionary with current settings and their sources
        """
        return {
            "api": {
                "base_url": cls.BASE_URL,
                "uploads_url": cls.UPLOADS_URL,
                "user_agent": cls.USER_AGENT,
            },
            "rate_limiting": {
                "delay": cls.RATE_LIMIT_DELAY,
                "max_retries": cls.MAX_RETRIES,
                "retry_delay": cls.RETRY_DELAY,
                "request_timeout": cls.REQUEST_TIMEOUT,
            },
            "downloads": {
                "directory": str(cls.DOWNLOAD_DIR),
                "max_concurrent": cls.MAX_CONCURRENT_DOWNLOADS,
                "chunk_size": cls.CHUNK_SIZE,
            },
            "defaults": {
                "language": cls.DEFAULT_LANGUAGE,
                "content_rating": cls.DEFAULT_CONTENT_RATING,
            },
            "features": {
                "cache_enabled": cls.ENABLE_CACHE,
                "cache_directory": str(cls.CACHE_DIR) if cls.ENABLE_CACHE else None,
                "auto_update_structure": cls.AUTO_UPDATE_STRUCTURE,
            }
        }


# Validate settings on import
Settings.validate()
