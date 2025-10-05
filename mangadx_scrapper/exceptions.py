"""
Custom exceptions for MangaDx API client.

This module defines all custom exceptions used throughout the library with
comprehensive error information and validation capabilities.
"""

import json
from typing import Any, Dict, List, Optional, Union


class MangaDxException(Exception):
    """
    Base exception for all MangaDx API errors.
    
    Provides comprehensive error information including status codes,
    request IDs, error details, and user-friendly messages.
    """

    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
        retry_info: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize MangaDx exception with comprehensive error information.

        Args:
            message: Human-readable error message
            status_code: HTTP status code if applicable
            response_data: Raw response data from API
            request_id: Request ID from API response headers
            error_details: Detailed error information extracted from response
            retry_info: Information about retry attempts and recommendations
        """
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_id = request_id
        self.error_details = error_details or {}
        self.retry_info = retry_info or {}
        
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return comprehensive string representation of the exception."""
        parts = []
        
        if self.status_code:
            parts.append(f"HTTP {self.status_code}")
        
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        
        parts.append(self.message)
        
        return " | ".join(parts)

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"status_code={self.status_code}, "
            f"request_id='{self.request_id}'"
            f")"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for serialization.
        
        Returns:
            Dictionary representation of the exception
        """
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "request_id": self.request_id,
            "error_details": self.error_details,
            "retry_info": self.retry_info,
            "response_data": self.response_data
        }

    def get_user_message(self) -> str:
        """
        Get a user-friendly error message.
        
        Returns:
            Simplified error message suitable for end users
        """
        if self.status_code == 429:
            retry_after = self.retry_info.get("retry_after")
            if retry_after:
                return f"Rate limit exceeded. Please wait {retry_after} seconds before retrying."
            return "Rate limit exceeded. Please wait before retrying."
        
        if self.status_code == 404:
            return "The requested resource was not found."
        
        if self.status_code == 401:
            return "Authentication failed. Please check your credentials."
        
        if self.status_code == 403:
            return "Access denied. You don't have permission to access this resource."
        
        if self.status_code and 500 <= self.status_code < 600:
            return "Server error occurred. Please try again later."
        
        return self.message

    def is_retryable(self) -> bool:
        """
        Determine if the error is retryable.
        
        Returns:
            True if the request can be retried, False otherwise
        """
        # Network errors are generally retryable
        if isinstance(self, (NetworkException, TimeoutException)):
            return True
        
        # Rate limit errors are retryable after waiting
        if isinstance(self, RateLimitException):
            return True
        
        # Server errors (5xx) are retryable
        if self.status_code and 500 <= self.status_code < 600:
            return True
        
        # Client errors (4xx) are generally not retryable
        if self.status_code and 400 <= self.status_code < 500:
            return False
        
        return False


class APIException(MangaDxException):
    """
    Exception raised for general API errors.
    
    This is the base class for all API-related exceptions that don't
    fit into more specific categories.
    """
    
    def get_user_message(self) -> str:
        """Get user-friendly message for API errors."""
        if self.status_code:
            return f"API error occurred (HTTP {self.status_code}). Please try again later."
        return "An API error occurred. Please try again later."


class AuthenticationException(MangaDxException):
    """
    Exception raised for authentication failures (401 Unauthorized).
    
    This typically indicates missing or invalid authentication credentials.
    """
    
    def get_user_message(self) -> str:
        """Get user-friendly message for authentication errors."""
        return "Authentication failed. Please check your API credentials."
    
    def is_retryable(self) -> bool:
        """Authentication errors are not retryable without fixing credentials."""
        return False


class AuthorizationException(MangaDxException):
    """
    Exception raised for authorization failures (403 Forbidden).
    
    This indicates the user is authenticated but lacks permission
    for the requested resource or action.
    """
    
    def get_user_message(self) -> str:
        """Get user-friendly message for authorization errors."""
        return "Access denied. You don't have permission to access this resource."
    
    def is_retryable(self) -> bool:
        """Authorization errors are not retryable without changing permissions."""
        return False


class NotFoundException(MangaDxException):
    """
    Exception raised when a resource is not found (404).
    
    This typically indicates the requested manga, chapter, or other
    resource does not exist or has been removed.
    """
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None, **kwargs):
        """
        Initialize not found exception with resource information.
        
        Args:
            message: Error message
            resource_type: Type of resource that was not found (e.g., 'manga', 'chapter')
            resource_id: ID of the resource that was not found
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id
    
    def get_user_message(self) -> str:
        """Get user-friendly message for not found errors."""
        if self.resource_type and self.resource_id:
            return f"The {self.resource_type} with ID '{self.resource_id}' was not found."
        elif self.resource_type:
            return f"The requested {self.resource_type} was not found."
        return "The requested resource was not found."
    
    def is_retryable(self) -> bool:
        """Not found errors are generally not retryable."""
        return False


class RateLimitException(MangaDxException):
    """
    Exception raised when rate limit is exceeded (429 Too Many Requests).
    
    This indicates the client has made too many requests in a given time period.
    The exception includes information about when to retry.
    """

    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None, 
        rate_limit_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize rate limit exception with retry information.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            rate_limit_info: Additional rate limit information from headers
            **kwargs: Additional arguments for base exception
        """
        retry_info = kwargs.get("retry_info", {})
        retry_info.update({
            "retry_after": retry_after,
            "rate_limit_info": rate_limit_info or {}
        })
        kwargs["retry_info"] = retry_info
        
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.rate_limit_info = rate_limit_info or {}

    def get_user_message(self) -> str:
        """Get user-friendly message for rate limit errors."""
        if self.retry_after:
            return f"Rate limit exceeded. Please wait {self.retry_after} seconds before retrying."
        return "Rate limit exceeded. Please wait before making more requests."
    
    def is_retryable(self) -> bool:
        """Rate limit errors are retryable after waiting."""
        return True


class ValidationException(MangaDxException):
    """
    Exception raised for validation errors (400 Bad Request).
    
    This indicates the request parameters or data are invalid.
    """
    
    def __init__(
        self, 
        message: str, 
        validation_errors: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """
        Initialize validation exception with detailed validation errors.
        
        Args:
            message: Error message
            validation_errors: List of specific validation errors
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or []
    
    def get_user_message(self) -> str:
        """Get user-friendly message for validation errors."""
        if self.validation_errors:
            error_details = []
            for error in self.validation_errors[:3]:  # Show first 3 errors
                field = error.get("field", "unknown")
                detail = error.get("detail", "invalid value")
                error_details.append(f"{field}: {detail}")
            
            if len(self.validation_errors) > 3:
                error_details.append(f"... and {len(self.validation_errors) - 3} more errors")
            
            return f"Validation failed: {'; '.join(error_details)}"
        
        return "Request validation failed. Please check your parameters."
    
    def is_retryable(self) -> bool:
        """Validation errors are not retryable without fixing the request."""
        return False


class ServerException(MangaDxException):
    """
    Exception raised for server errors (5xx).
    
    This indicates an error on the server side that is typically
    temporary and may be resolved by retrying.
    """
    
    def get_user_message(self) -> str:
        """Get user-friendly message for server errors."""
        return "Server error occurred. Please try again in a few moments."
    
    def is_retryable(self) -> bool:
        """Server errors are generally retryable."""
        return True


class NetworkException(MangaDxException):
    """
    Exception raised for network-related errors.
    
    This includes connection errors, DNS resolution failures,
    and other network-level issues.
    """
    
    def __init__(self, message: str, original_error: Optional[Exception] = None, **kwargs):
        """
        Initialize network exception with original error information.
        
        Args:
            message: Error message
            original_error: The original exception that caused this error
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.original_error = original_error
    
    def get_user_message(self) -> str:
        """Get user-friendly message for network errors."""
        return "Network error occurred. Please check your internet connection and try again."
    
    def is_retryable(self) -> bool:
        """Network errors are generally retryable."""
        return True


class TimeoutException(MangaDxException):
    """
    Exception raised when a request times out.
    
    This indicates the request took longer than the configured timeout period.
    """
    
    def __init__(self, message: str, timeout_duration: Optional[float] = None, **kwargs):
        """
        Initialize timeout exception with duration information.
        
        Args:
            message: Error message
            timeout_duration: The timeout duration that was exceeded
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration
    
    def get_user_message(self) -> str:
        """Get user-friendly message for timeout errors."""
        if self.timeout_duration:
            return f"Request timed out after {self.timeout_duration} seconds. Please try again."
        return "Request timed out. Please try again."
    
    def is_retryable(self) -> bool:
        """Timeout errors are generally retryable."""
        return True


class DownloadException(MangaDxException):
    """
    Exception raised during download operations.
    
    This includes errors during file downloads, image processing,
    and file system operations.
    """
    
    def __init__(
        self, 
        message: str, 
        file_path: Optional[str] = None,
        bytes_downloaded: Optional[int] = None,
        total_size: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize download exception with progress information.
        
        Args:
            message: Error message
            file_path: Path of the file being downloaded
            bytes_downloaded: Number of bytes successfully downloaded
            total_size: Total expected file size
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.bytes_downloaded = bytes_downloaded
        self.total_size = total_size
    
    def get_user_message(self) -> str:
        """Get user-friendly message for download errors."""
        if self.file_path:
            return f"Failed to download file: {self.file_path}"
        return "Download failed. Please try again."
    
    def is_retryable(self) -> bool:
        """Download errors are generally retryable."""
        return True
    
    def get_progress_info(self) -> Optional[Dict[str, Any]]:
        """
        Get download progress information.
        
        Returns:
            Dictionary with progress information or None if not available
        """
        if self.bytes_downloaded is not None and self.total_size is not None:
            progress_percent = (self.bytes_downloaded / self.total_size) * 100
            return {
                "bytes_downloaded": self.bytes_downloaded,
                "total_size": self.total_size,
                "progress_percent": progress_percent,
                "remaining_bytes": self.total_size - self.bytes_downloaded
            }
        return None