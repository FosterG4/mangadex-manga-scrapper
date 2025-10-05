"""
Data models for MangaDx API responses.

This module defines data classes for API responses.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Relationship:
    """Represents a relationship to another entity."""
    id: str
    type: str
    attributes: Optional[Dict[str, Any]] = None


@dataclass
class LocalizedString:
    """Represents a localized string dictionary."""
    values: Dict[str, str] = field(default_factory=dict)

    def get(self, language: str, default: str = "") -> str:
        """Get localized string for language."""
        return self.values.get(language, default)

    def __getitem__(self, language: str) -> str:
        """Get localized string using bracket notation."""
        return self.values.get(language, "")


@dataclass
class Tag:
    """Represents a manga tag."""
    id: str
    name: LocalizedString
    description: LocalizedString = field(default_factory=lambda: LocalizedString())
    group: Optional[str] = None
    version: int = 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tag":
        """Create Tag from API response dictionary."""
        attributes = data.get("attributes", {})
        
        name_dict = attributes.get("name", {})
        name = LocalizedString(values=name_dict)
        
        description_dict = attributes.get("description", {})
        description = LocalizedString(values=description_dict)
        
        return cls(
            id=data["id"],
            name=name,
            description=description,
            group=attributes.get("group"),
            version=attributes.get("version", 1),
        )


@dataclass
class Manga:
    """Represents a manga."""
    id: str
    title: LocalizedString
    alt_titles: List[LocalizedString] = field(default_factory=list)
    description: LocalizedString = field(default_factory=lambda: LocalizedString())
    is_locked: bool = False
    original_language: Optional[str] = None
    last_volume: Optional[str] = None
    last_chapter: Optional[str] = None
    publication_demographic: Optional[str] = None
    status: Optional[str] = None
    year: Optional[int] = None
    content_rating: Optional[str] = None
    tags: List[Dict[str, Any]] = field(default_factory=list)
    state: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: int = 1
    available_translated_languages: List[str] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Manga":
        """Create Manga from API response dictionary."""
        attributes = data.get("attributes", {})

        # Parse title
        title_dict = attributes.get("title", {})
        title = LocalizedString(values=title_dict)

        # Parse alt titles
        alt_titles = []
        for alt_title in attributes.get("altTitles", []):
            alt_titles.append(LocalizedString(values=alt_title))

        # Parse description
        description_dict = attributes.get("description", {})
        description = LocalizedString(values=description_dict)

        # Parse relationships
        relationships = []
        for rel in data.get("relationships", []):
            relationships.append(Relationship(
                id=rel["id"],
                type=rel["type"],
                attributes=rel.get("attributes"),
            ))

        return cls(
            id=data["id"],
            title=title,
            alt_titles=alt_titles,
            description=description,
            is_locked=attributes.get("isLocked", False),
            original_language=attributes.get("originalLanguage"),
            last_volume=attributes.get("lastVolume"),
            last_chapter=attributes.get("lastChapter"),
            publication_demographic=attributes.get("publicationDemographic"),
            status=attributes.get("status"),
            year=attributes.get("year"),
            content_rating=attributes.get("contentRating"),
            tags=attributes.get("tags", []),
            state=attributes.get("state"),
            created_at=attributes.get("createdAt"),
            updated_at=attributes.get("updatedAt"),
            version=attributes.get("version", 1),
            available_translated_languages=attributes.get("availableTranslatedLanguages", []),
            relationships=relationships,
        )


@dataclass
class Chapter:
    """Represents a manga chapter."""
    id: str
    title: Optional[str] = None
    volume: Optional[str] = None
    chapter: Optional[str] = None
    pages: int = 0
    translated_language: Optional[str] = None
    uploader: Optional[str] = None
    external_url: Optional[str] = None
    version: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    publish_at: Optional[datetime] = None
    readable_at: Optional[datetime] = None
    relationships: List[Relationship] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chapter":
        """Create Chapter from API response dictionary."""
        attributes = data.get("attributes", {})

        # Parse relationships
        relationships = []
        for rel in data.get("relationships", []):
            relationships.append(Relationship(
                id=rel["id"],
                type=rel["type"],
                attributes=rel.get("attributes"),
            ))

        return cls(
            id=data["id"],
            title=attributes.get("title"),
            volume=attributes.get("volume"),
            chapter=attributes.get("chapter"),
            pages=attributes.get("pages", 0),
            translated_language=attributes.get("translatedLanguage"),
            uploader=attributes.get("uploader"),
            external_url=attributes.get("externalUrl"),
            version=attributes.get("version", 1),
            created_at=attributes.get("createdAt"),
            updated_at=attributes.get("updatedAt"),
            publish_at=attributes.get("publishAt"),
            readable_at=attributes.get("readableAt"),
            relationships=relationships,
        )


@dataclass
class Author:
    """Represents an author or artist."""
    id: str
    name: str
    image_url: Optional[str] = None
    biography: LocalizedString = field(default_factory=lambda: LocalizedString())
    twitter: Optional[str] = None
    pixiv: Optional[str] = None
    melon_book: Optional[str] = None
    fan_box: Optional[str] = None
    booth: Optional[str] = None
    nico_video: Optional[str] = None
    skeb: Optional[str] = None
    fantia: Optional[str] = None
    tumblr: Optional[str] = None
    youtube: Optional[str] = None
    weibo: Optional[str] = None
    naver: Optional[str] = None
    website: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: int = 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Author":
        """Create Author from API response dictionary."""
        attributes = data.get("attributes", {})

        biography_dict = attributes.get("biography", {})
        biography = LocalizedString(values=biography_dict)

        return cls(
            id=data["id"],
            name=attributes.get("name", ""),
            image_url=attributes.get("imageUrl"),
            biography=biography,
            twitter=attributes.get("twitter"),
            pixiv=attributes.get("pixiv"),
            melon_book=attributes.get("melonBook"),
            fan_box=attributes.get("fanBox"),
            booth=attributes.get("booth"),
            nico_video=attributes.get("nicoVideo"),
            skeb=attributes.get("skeb"),
            fantia=attributes.get("fantia"),
            tumblr=attributes.get("tumblr"),
            youtube=attributes.get("youtube"),
            weibo=attributes.get("weibo"),
            naver=attributes.get("naver"),
            website=attributes.get("website"),
            created_at=attributes.get("createdAt"),
            updated_at=attributes.get("updatedAt"),
            version=attributes.get("version", 1),
        )


@dataclass
class Cover:
    """Represents a manga cover art."""
    id: str
    volume: Optional[str] = None
    file_name: Optional[str] = None
    description: Optional[str] = None
    locale: Optional[str] = None
    version: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    relationships: List[Relationship] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cover":
        """Create Cover from API response dictionary."""
        attributes = data.get("attributes", {})

        # Parse relationships
        relationships = []
        for rel in data.get("relationships", []):
            relationships.append(Relationship(
                id=rel["id"],
                type=rel["type"],
                attributes=rel.get("attributes"),
            ))

        return cls(
            id=data["id"],
            volume=attributes.get("volume"),
            file_name=attributes.get("fileName"),
            description=attributes.get("description"),
            locale=attributes.get("locale"),
            version=attributes.get("version", 1),
            created_at=attributes.get("createdAt"),
            updated_at=attributes.get("updatedAt"),
            relationships=relationships,
        )


@dataclass
class ScanlationGroup:
    """Represents a scanlation group."""
    id: str
    name: str
    alt_names: List[LocalizedString] = field(default_factory=list)
    website: Optional[str] = None
    irc_server: Optional[str] = None
    irc_channel: Optional[str] = None
    discord: Optional[str] = None
    contact_email: Optional[str] = None
    description: Optional[str] = None
    twitter: Optional[str] = None
    manga_updates: Optional[str] = None
    focused_languages: List[str] = field(default_factory=list)
    locked: bool = False
    official: bool = False
    verified: bool = False
    inactive: bool = False
    publish_delay: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: int = 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScanlationGroup":
        """Create ScanlationGroup from API response dictionary."""
        attributes = data.get("attributes", {})

        # Parse alt names
        alt_names = []
        for alt_name in attributes.get("altNames", []):
            alt_names.append(LocalizedString(values=alt_name))

        return cls(
            id=data["id"],
            name=attributes.get("name", ""),
            alt_names=alt_names,
            website=attributes.get("website"),
            irc_server=attributes.get("ircServer"),
            irc_channel=attributes.get("ircChannel"),
            discord=attributes.get("discord"),
            contact_email=attributes.get("contactEmail"),
            description=attributes.get("description"),
            twitter=attributes.get("twitter"),
            manga_updates=attributes.get("mangaUpdates"),
            focused_languages=attributes.get("focusedLanguages", []),
            locked=attributes.get("locked", False),
            official=attributes.get("official", False),
            verified=attributes.get("verified", False),
            inactive=attributes.get("inactive", False),
            publish_delay=attributes.get("publishDelay"),
            created_at=attributes.get("createdAt"),
            updated_at=attributes.get("updatedAt"),
            version=attributes.get("version", 1),
        )