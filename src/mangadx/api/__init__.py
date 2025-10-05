"""API modules for different MangaDx resources."""

from .at_home import AtHomeAPI
from .author import AuthorAPI
from .chapter import ChapterAPI
from .cover import CoverAPI
from .manga import MangaAPI
from .scanlation_group import ScanlationGroupAPI

__all__ = [
    "MangaAPI",
    "ChapterAPI",
    "AuthorAPI",
    "CoverAPI",
    "ScanlationGroupAPI",
    "AtHomeAPI",
]
