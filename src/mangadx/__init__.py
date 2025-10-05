"""MangaDx API Client Library.

A comprehensive Python client for the MangaDx API v5.
Provides easy access to manga, chapters, authors, and more.
"""

__version__ = "1.0.0"
__author__ = "MangaDx Scrapper Team"

from .client import MangaDxClient
from .exceptions import (
    APIException,
    AuthenticationException,
    AuthorizationException,
    MangaDxException,
    NotFoundException,
    RateLimitException,
)

__all__ = [
    "APIException",
    "AuthenticationException",
    "AuthorizationException",
    "MangaDxClient",
    "MangaDxException",
    "NotFoundException",
    "RateLimitException",
]
