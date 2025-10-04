"""API modules for different MangaDex resources."""

from .manga import MangaAPI
from .chapter import ChapterAPI
from .author import AuthorAPI
from .cover import CoverAPI
from .scanlation_group import ScanlationGroupAPI
from .at_home import AtHomeAPI

__all__ = [
    "MangaAPI",
    "ChapterAPI",
    "AuthorAPI",
    "CoverAPI",
    "ScanlationGroupAPI",
    "AtHomeAPI",
]
