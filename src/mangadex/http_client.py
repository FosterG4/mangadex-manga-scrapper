"""
HTTP client for MangaDex API.

This module provides a robust HTTP client with retry logic, rate limiting,
and error handling.
"""

import time
import logging
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Settings
from .exceptions import (
    APIException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    RateLimitException,
    ValidationException,
    ServerException,
    NetworkException,
    TimeoutException,
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
        Handle API response and raise appropriate exceptions.

        Args:
            response: Response object from requests

        Returns:
            Parsed JSON response

        Raises:
            Various MangaDex exceptions based on status code
        """
        try:
            data = response.json() if response.content else {}
        except ValueError:
            data = {"content": response.text}

        if response.status_code == 200:
            return data

        # Extract error message
        error_message = "Unknown error"
        if isinstance(data, dict):
            if "errors" in data and data["errors"]:
                error_message = data["errors"][0].get("detail", error_message)
            elif "message" in data:
                error_message = data["message"]

        # Raise appropriate exception based on status code
        if response.status_code == 400:
            raise ValidationException(error_message, response.status_code, data)
        elif response.status_code == 401:
            raise AuthenticationException(error_message, response.status_code, data)
        elif response.status_code == 403:
            raise AuthorizationException(error_message, response.status_code, data)
        elif response.status_code == 404:
            raise NotFoundException(error_message, response.status_code, data)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitException(
                error_message,
                retry_after=int(retry_after) if retry_after else None,
                status_code=response.status_code,
                response_data=data,
            )
        elif 500 <= response.status_code < 600:
            raise ServerException(error_message, response.status_code, data)
        else:
            raise APIException(error_message, response.status_code, data)

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        skip_rate_limit: bool = False,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Additional headers
            timeout: Request timeout in seconds
            skip_rate_limit: Skip rate limiting for this request

        Returns:
            Parsed JSON response

        Raises:
            Various MangaDex exceptions on error
        """
        if not skip_rate_limit:
            self._apply_rate_limit()

        url = urljoin(self.base_url, endpoint)
        request_headers = self._get_headers(headers)
        timeout = timeout or Settings.REQUEST_TIMEOUT

        try:
            logger.debug(f"{method} {url} - Params: {params}")

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data if isinstance(data, dict) else None,
                data=data if isinstance(data, str) else None,
                headers=request_headers,
                timeout=timeout,
            )

            return self._handle_response(response)

        except requests.Timeout as e:
            raise TimeoutException(f"Request timed out after {timeout}s: {str(e)}")
        except requests.ConnectionError as e:
            raise NetworkException(f"Network error: {str(e)}")
        except requests.RequestException as e:
            raise APIException(f"Request failed: {str(e)}")

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
