"""
Configuration settings for MangaDx API client.

This module loads and manages all configuration from environment variables.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

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
    # MangaDx API allows ~5 requests/second. Default 0.25s = 4 req/s to stay safe
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
        """Validate configuration settings."""
        if cls.MAX_CONCURRENT_DOWNLOADS < 1:
            raise ValueError("MAX_CONCURRENT_DOWNLOADS must be at least 1")
        
        if cls.RATE_LIMIT_DELAY < 0:
            raise ValueError("RATE_LIMIT_DELAY must be non-negative")
        
        if cls.REQUEST_TIMEOUT < 1:
            raise ValueError("REQUEST_TIMEOUT must be at least 1")
        
        # Create necessary directories
        cls.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        if cls.ENABLE_CACHE:
            cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)


# Validate settings on import
Settings.validate()