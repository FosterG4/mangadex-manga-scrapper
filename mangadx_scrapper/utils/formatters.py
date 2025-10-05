"""
Formatting utilities for displaying data.

This module provides functions to format manga and chapter information.
"""

from typing import List

from ..models import Chapter, Manga


def format_manga_info(manga: Manga, verbose: bool = False) -> str:
    """
    Format manga information for display.

    Args:
        manga: Manga object to format
        verbose: Include detailed information if True

    Returns:
        Formatted string representation of the manga
    """
    # Get primary title (English or first available)
    title_en = manga.title.get("en")

    lines = [
        f"Title (EN): {title_en or 'N/A'}",
    ]

    # Show alternative titles
    if manga.alt_titles:
        alt_titles_str = []
        for alt_title in manga.alt_titles[:3]:  # Show first 3 alt titles
            for lang, title in alt_title.values.items():
                alt_titles_str.append(f"{title} ({lang})")
        if alt_titles_str:
            lines.append(f"Alt Titles: {', '.join(alt_titles_str)}")

    # Show all title languages
    if manga.title.values:
        all_titles = []
        for lang, title in manga.title.values.items():
            all_titles.append(f"{lang}: {title}")
        lines.append(f"All Titles: {' | '.join(all_titles)}")

    lines.extend([
        f"ID: {manga.id}",
        f"Status: {manga.status or 'Unknown'}",
        f"Content Rating: {manga.content_rating or 'Unknown'}",
    ])

    if manga.year:
        lines.append(f"Year: {manga.year}")

    if manga.publication_demographic:
        lines.append(f"Demographic: {manga.publication_demographic}")

    if manga.original_language:
        lines.append(f"Original Language: {manga.original_language}")

    if manga.last_volume:
        lines.append(f"Last Volume: {manga.last_volume}")

    if manga.last_chapter:
        lines.append(f"Last Chapter: {manga.last_chapter}")

    if manga.available_translated_languages:
        langs = ', '.join(manga.available_translated_languages)
        lines.append(f"Available Languages ({len(manga.available_translated_languages)}): {langs}")

    # Get authors and artists from relationships
    authors = []
    artists = []
    cover_art = None

    for rel in manga.relationships:
        if rel.type == "author":
            author_name = rel.attributes.get("name") if rel.attributes else None
            if author_name:
                authors.append(author_name)
        elif rel.type == "artist":
            artist_name = rel.attributes.get("name") if rel.attributes else None
            if artist_name:
                artists.append(artist_name)
        elif rel.type == "cover_art":
            cover_art = rel

    if authors:
        lines.append(f"Author(s): {', '.join(authors)}")

    if artists:
        lines.append(f"Artist(s): {', '.join(artists)}")

    if verbose:
        # Full description
        if manga.description.values:
            desc_en = manga.description.get("en")
            if desc_en:
                lines.append(f"\nDescription (EN):\n{desc_en}")
            else:
                # Show first available description
                for lang, desc in manga.description.values.items():
                    lines.append(f"\nDescription ({lang}):\n{desc}")
                    break

        # Tags with categories
        if manga.tags:
            tag_names = [tag.get("attributes", {}).get("name", {}).get("en", "") for tag in manga.tags]
            tag_names = [t for t in tag_names if t]
            if tag_names:
                lines.append(f"\nTags ({len(tag_names)}): {', '.join(tag_names)}")

        # Cover art info
        if cover_art and cover_art.attributes:
            cover_file = cover_art.attributes.get("fileName")
            if cover_file:
                lines.append(f"\nCover Art: {cover_file}")
                lines.append(f"Cover URL: https://uploads.mangadex.org/covers/{manga.id}/{cover_file}")

        # Additional metadata
        if manga.created_at:
            lines.append(f"\nCreated At: {manga.created_at}")
        if manga.updated_at:
            lines.append(f"Updated At: {manga.updated_at}")

    return "\n".join(lines)


def format_chapter_info(chapter: Chapter) -> str:
    """
    Format chapter information for display.

    Args:
        chapter: Chapter object to format

    Returns:
        Formatted string representation of the chapter
    """
    parts = []

    if chapter.volume:
        parts.append(f"Vol.{chapter.volume}")

    if chapter.chapter:
        parts.append(f"Ch.{chapter.chapter}")

    if chapter.title:
        parts.append(f"- {chapter.title}")

    chapter_str = " ".join(parts) if parts else f"Chapter {chapter.id}"

    if chapter.translated_language:
        chapter_str += f" [{chapter.translated_language}]"

    if chapter.pages:
        chapter_str += f" ({chapter.pages} pages)"

    return chapter_str


def format_manga_list(manga_list: List[Manga]) -> str:
    """
    Format a list of manga for display.

    Args:
        manga_list: List of Manga objects to format

    Returns:
        Formatted string representation of the manga list
    """
    if not manga_list:
        return "No manga found."

    lines = []
    for idx, manga in enumerate(manga_list, 1):
        # Get English title first, then try Japanese, then any available title
        title = manga.title.get("en")
        if not title:
            title = manga.title.get("ja")
        if not title:
            title = manga.title.get("ja-ro")  # Romanized Japanese
        if not title and manga.title.values:
            # Get first available title from any language
            title = list(manga.title.values.values())[0]
        if not title:
            title = "Unknown"

        status = manga.status or "Unknown"
        year = manga.year or "N/A"

        # Check for English alternative title if main title is not English
        alt_en_title = None
        if not manga.title.get("en") and manga.alt_titles:
            for alt_title in manga.alt_titles:
                if "en" in alt_title.values:
                    alt_en_title = alt_title.values["en"]
                    break

        # Show title with language indicator if not English
        title_lang = None
        if not manga.title.get("en"):
            # Determine the language of the displayed title
            for lang, lang_title in manga.title.values.items():
                if lang_title == title:
                    title_lang = lang
                    break

        # Format the line
        line = f"{idx:2d}. {title}"

        if title_lang and title_lang != "en":
            line += f" [{title_lang}]"

        if alt_en_title:
            line += f" (EN: {alt_en_title})"

        line += f" | {status} | {year}"

        # Add content rating if available
        if manga.content_rating:
            line += f" | {manga.content_rating}"

        lines.append(line)

    return "\n".join(lines)