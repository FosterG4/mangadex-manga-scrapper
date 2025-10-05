"""
Custom exceptions for MangaDx API client.

This module defines all custom exceptions used throughout the library.
"""

from typing import Any, Dict, Optional


class MangaDxException(Exception):
    """Base exception for all MangaDx API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        """
        Initialize MangaDx exception.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: Raw response data from API
        """
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class APIException(MangaDxException):
    """Exception raised for general API errors."""
    pass


class AuthenticationException(MangaDxException):
    """Exception raised for authentication failures."""
    pass


class AuthorizationException(MangaDxException):
    """Exception raised for authorization failures (403 Forbidden)."""
    pass


class NotFoundException(MangaDxException):
    """Exception raised when a resource is not found (404)."""
    pass


class RateLimitException(MangaDxException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        """
        Initialize rate limit exception.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ValidationException(MangaDxException):
    """Exception raised for validation errors (400 Bad Request)."""
    pass


class ServerException(MangaDxException):
    """Exception raised for server errors (5xx)."""
    pass


class NetworkException(MangaDxException):
    """Exception raised for network-related errors."""
    pass


class TimeoutException(MangaDxException):
    """Exception raised when a request times out."""
    pass


class DownloadException(MangaDxException):
    """Exception raised during download operations."""
    pass
