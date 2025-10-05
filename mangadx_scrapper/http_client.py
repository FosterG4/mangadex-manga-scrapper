"""
HTTP client for MangaDx API.

This module provides a robust HTTP client with retry logic, rate limiting,
comprehensive error handling, and response validation following MangaDx API guidelines.

Features:
- Automatic retry with exponential backoff
- Rate limiting compliance (5 req/s max)
- Comprehensive error handling with meaningful messages
- Request/response logging for debugging
- Response validation and structure checking
- Proper authentication header handling
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Settings
from .exceptions import (
    APIException,
    AuthenticationException,
    AuthorizationException,
    NetworkException,
    NotFoundException,
    RateLimitException,
    ServerException,
    TimeoutException,
    ValidationException,
)

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client with retry logic and error handling."""

    def __init__(self, base_url: str = None, access_token: Optional[str] = None):
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL for API requests
            access_token: Optional access token for authenticated requests
        """
        self.base_url = base_url or Settings.BASE_URL
        self.access_token = access_token
        self.session = self._create_session()
        self.last_request_time = 0

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=Settings.MAX_RETRIES,
            backoff_factor=Settings.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update({
            "User-Agent": Settings.USER_AGENT,
            "Content-Type": "application/json",
        })

        return session

    def _apply_rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < Settings.RATE_LIMIT_DELAY:
            time.sleep(Settings.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get headers for request.

        Args:
            additional_headers: Additional headers to include

        Returns:
            Complete headers dictionary
        """
        headers = {}

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        if additional_headers:
            headers.update(additional_headers)

        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response with comprehensive validation and error handling.

        Args:
            response: Response object from requests

        Returns:
            Parsed and validated JSON response

        Raises:
            Various MangaDx exceptions based on status code and response validation
        """
        # Get request ID for debugging (MangaDx API provides this)
        request_id = response.headers.get("X-Request-ID", "unknown")
        
        # Log response details for debugging
        logger.debug(
            f"Response: {response.status_code} {response.reason} "
            f"(Request ID: {request_id}) - Content-Length: {len(response.content)}"
        )
        
        # Parse response content
        try:
            data = response.json() if response.content else {}
        except ValueError as e:
            logger.error(f"Failed to parse JSON response (Request ID: {request_id}): {e}")
            data = {"content": response.text, "parse_error": str(e)}

        # Handle successful responses
        if 200 <= response.status_code < 300:
            # Validate response structure for successful responses
            validated_data = self._validate_response_structure(data, response.status_code)
            logger.debug(f"Successful response validated (Request ID: {request_id})")
            return validated_data

        # Extract detailed error information
        error_details = self._extract_error_details(data, response, request_id)
        error_message = error_details["message"]
        
        # Log error details for debugging
        logger.error(
            f"API Error (Request ID: {request_id}): {response.status_code} {response.reason}\n"
            f"Message: {error_message}\n"
            f"Details: {error_details.get('details', 'None')}"
        )

        # Raise appropriate exception based on status code
        if response.status_code == 400:
            raise ValidationException(
                error_message, 
                response.status_code, 
                data,
                request_id=request_id,
                error_details=error_details
            )
        elif response.status_code == 401:
            raise AuthenticationException(
                error_message, 
                response.status_code, 
                data,
                request_id=request_id,
                error_details=error_details
            )
        elif response.status_code == 403:
            raise AuthorizationException(
                error_message, 
                response.status_code, 
                data,
                request_id=request_id,
                error_details=error_details
            )
        elif response.status_code == 404:
            raise NotFoundException(
                error_message, 
                response.status_code, 
                data,
                request_id=request_id,
                error_details=error_details
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitException(
                error_message,
                retry_after=int(retry_after) if retry_after else None,
                status_code=response.status_code,
                response_data=data,
                request_id=request_id,
                error_details=error_details
            )
        elif 500 <= response.status_code < 600:
            raise ServerException(
                error_message, 
                response.status_code, 
                data,
                request_id=request_id,
                error_details=error_details
            )
        else:
            raise APIException(
                error_message, 
                response.status_code, 
                data,
                request_id=request_id,
                error_details=error_details
            )
    
    def _validate_response_structure(self, data: Dict[str, Any], status_code: int) -> Dict[str, Any]:
        """
        Validate the structure of a successful API response.
        
        Args:
            data: Parsed response data
            status_code: HTTP status code
            
        Returns:
            Validated response data
            
        Raises:
            ValidationException: If response structure is invalid
        """
        if not isinstance(data, dict):
            raise ValidationException(
                f"Expected JSON object in response, got {type(data).__name__}",
                status_code,
                data
            )
        
        # Check for required fields in MangaDx API responses
        if status_code == 200 and data:
            # Most MangaDx API responses have a 'result' field
            if 'result' not in data and 'data' not in data and 'response' not in data:
                logger.warning(f"Response missing expected structure fields: {list(data.keys())}")
        
        return data
    
    def _extract_error_details(self, data: Dict[str, Any], response: requests.Response, request_id: str) -> Dict[str, Any]:
        """
        Extract detailed error information from API response.
        
        Args:
            data: Parsed response data
            response: HTTP response object
            request_id: Request ID from headers
            
        Returns:
            Dictionary with error details
        """
        error_details = {
            "message": "Unknown error",
            "details": None,
            "request_id": request_id,
            "status_code": response.status_code,
            "status_text": response.reason,
        }
        
        if isinstance(data, dict):
            # MangaDx API error format
            if "errors" in data and data["errors"]:
                error = data["errors"][0]
                error_details["message"] = error.get("detail", error_details["message"])
                error_details["details"] = {
                    "id": error.get("id"),
                    "status": error.get("status"),
                    "code": error.get("code"),
                    "title": error.get("title"),
                    "source": error.get("source"),
                }
            elif "message" in data:
                error_details["message"] = data["message"]
                error_details["details"] = data.get("details")
            elif "error" in data:
                error_details["message"] = data["error"]
                if "error_description" in data:
                    error_details["details"] = data["error_description"]
        
        # Fallback to status code description
        if error_details["message"] == "Unknown error":
            error_details["message"] = f"HTTP {response.status_code}: {response.reason}"
        
        return error_details

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        skip_rate_limit: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to MangaDx API with comprehensive validation and logging.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative to base URL)
            params: Query parameters for the request
            data: Request body data (will be JSON-encoded)
            headers: Additional headers to include
            timeout: Request timeout in seconds (uses default if not provided)
            skip_rate_limit: Skip rate limiting for this request
            **kwargs: Additional arguments passed to requests

        Returns:
            Parsed and validated JSON response

        Raises:
            ValidationException: Invalid request parameters
            TimeoutException: Request timed out
            NetworkException: Network-related error
            APIException: API-related error
        """
        # Validate request parameters
        self._validate_request_params(method, endpoint, params, data)
        
        if not skip_rate_limit:
            self._apply_rate_limit()

        url = urljoin(self.base_url, endpoint)
        request_headers = self._get_headers(headers)
        timeout = timeout or Settings.REQUEST_TIMEOUT

        # Log request details
        logger.debug(
            f"Making {method.upper()} request to {url}\n"
            f"Params: {params}\n"
            f"Data: {data}\n"
            f"Headers: {self._sanitize_headers_for_logging(request_headers)}"
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data if isinstance(data, dict) else None,
                data=data if isinstance(data, str) else None,
                headers=request_headers,
                timeout=timeout,
                **kwargs,
            )
            
            # Log response summary
            logger.debug(
                f"Response received: {response.status_code} {response.reason} "
                f"({len(response.content)} bytes)"
            )

            return self._handle_response(response)

        except requests.Timeout as e:
            error_msg = f"Request timed out after {timeout}s for {method.upper()} {url}: {str(e)}"
            logger.error(error_msg)
            raise TimeoutException(error_msg) from e
        except requests.ConnectionError as e:
            error_msg = f"Network error for {method.upper()} {url}: {str(e)}"
            logger.error(error_msg)
            raise NetworkException(error_msg) from e
        except requests.RequestException as e:
            error_msg = f"Request failed for {method.upper()} {url}: {str(e)}"
            logger.error(error_msg)
            raise APIException(error_msg) from e
    
    def _validate_request_params(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]], 
        data: Optional[Union[Dict[str, Any], str]]
    ) -> None:
        """
        Validate request parameters before making the request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            
        Raises:
            ValidationException: If parameters are invalid
        """
        # Validate HTTP method
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if method.upper() not in valid_methods:
            raise ValidationException(f"Invalid HTTP method: {method}")
        
        # Validate endpoint
        if not endpoint or not isinstance(endpoint, str):
            raise ValidationException("Endpoint must be a non-empty string")
        
        # Validate params
        if params is not None and not isinstance(params, dict):
            raise ValidationException("Params must be a dictionary")
        
        # Validate data
        if data is not None and not isinstance(data, (dict, str)):
            raise ValidationException("Data must be a dictionary or string")
        
        # Check for data in GET requests (should use params instead)
        if method.upper() == "GET" and data is not None:
            logger.warning("Data provided for GET request, consider using params instead")
    
    def _sanitize_headers_for_logging(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize headers for logging by masking sensitive information.
        
        Args:
            headers: Headers dictionary
            
        Returns:
            Sanitized headers for logging
        """
        sanitized = headers.copy()
        sensitive_keys = {"authorization", "x-api-key", "cookie", "set-cookie"}
        
        for key in sanitized:
            if key.lower() in sensitive_keys:
                sanitized[key] = "***MASKED***"
        
        return sanitized

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return self.request("POST", endpoint, data=data, **kwargs)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return self.request("PUT", endpoint, data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()