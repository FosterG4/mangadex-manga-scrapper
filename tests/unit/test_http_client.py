"""
Unit tests for HTTP client.
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

import requests

from src.mangadx.exceptions import (
    AuthenticationException,
    NotFoundException,
    RateLimitException,
    ValidationException,
)
from src.mangadx.http_client import HTTPClient


class TestHTTPClient(unittest.TestCase):
    """Test cases for HTTPClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = HTTPClient(base_url="https://api.test.com")

    def tearDown(self):
        """Clean up after tests."""
        self.client.close()

    @patch("src.mangadx.http_client.requests.Session.request")
    def test_successful_get_request(self, mock_request):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "ok", "data": []}
        mock_request.return_value = mock_response

        result = self.client.get("/test")
        
        self.assertEqual(result["result"], "ok")
        mock_request.assert_called_once()

    @patch("src.mangadx.http_client.requests.Session.request")
    def test_404_error(self, mock_request):
        """Test 404 Not Found error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errors": [{"detail": "Not found"}]}
        mock_response.content = b'{"errors": [{"detail": "Not found"}]}'
        mock_request.return_value = mock_response

        with self.assertRaises(NotFoundException):
            self.client.get("/test")

    @patch("src.mangadx.http_client.requests.Session.request")
    def test_400_validation_error(self, mock_request):
        """Test 400 Bad Request error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"errors": [{"detail": "Invalid input"}]}
        mock_response.content = b'{"errors": [{"detail": "Invalid input"}]}'
        mock_request.return_value = mock_response

        with self.assertRaises(ValidationException):
            self.client.get("/test")

    @patch("src.mangadx.http_client.requests.Session.request")
    def test_401_authentication_error(self, mock_request):
        """Test 401 Unauthorized error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"errors": [{"detail": "Unauthorized"}]}
        mock_response.content = b'{"errors": [{"detail": "Unauthorized"}]}'
        mock_request.return_value = mock_response

        with self.assertRaises(AuthenticationException):
            self.client.get("/test")

    @patch("src.mangadx.http_client.requests.Session.request")
    def test_429_rate_limit_error(self, mock_request):
        """Test 429 Rate Limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"errors": [{"detail": "Rate limited"}]}
        mock_response.content = b'{"errors": [{"detail": "Rate limited"}]}'
        mock_request.return_value = mock_response

        with self.assertRaises(RateLimitException) as context:
            self.client.get("/test")
        
        self.assertEqual(context.exception.retry_after, 60)

    def test_authorization_header(self):
        """Test that authorization header is set correctly."""
        client = HTTPClient(access_token="test_token")
        headers = client._get_headers()
        
        self.assertEqual(headers["Authorization"], "Bearer test_token")
        client.close()


if __name__ == "__main__":
    unittest.main()
