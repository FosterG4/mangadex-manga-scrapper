"""
MangaDex API Client Library.

A comprehensive Python client for the MangaDex API v5.
"""

__version__ = "1.0.0"
__author__ = "MangaDex Scrapper Team"

from .client import MangaDexClient
from .exceptions import (
    APIException,
    AuthenticationException,
    MangaDexException,
    NotFoundException,
    RateLimitException,
)

__all__ = [
    "MangaDexClient",
    "MangaDexException",
    "APIException",
    "AuthenticationException",
    "RateLimitException",
    "NotFoundException",
]
