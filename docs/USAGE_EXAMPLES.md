# Usage Examples

This document provides practical examples for common use cases.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Searching Manga](#searching-manga)
- [Downloading Manga](#downloading-manga)
- [Advanced Filtering](#advanced-filtering)
- [Working with Chapters](#working-with-chapters)
- [Multi-Language Downloads](#multi-language-downloads)
- [Error Handling](#error-handling)
- [Custom Scripts](#custom-scripts)

## Basic Usage

### Simple Download Script

```python
from src.mangadx import MangaDxClient
from src.mangadx.downloader import DownloadManager

# Initialize
client = MangaDxClient()
downloader = DownloadManager(client)

# Search and download
manga_list = client.manga.search(title="One Piece", limit=1)
if manga_list:
    manga = manga_list[0]
    stats = downloader.download_manga(
        manga_id=manga.id,
        languages=["en"]
    )
    print(f"Downloaded {stats['downloaded']} chapters")

client.close()
```

## Searching Manga

### Search by Title

```python
# Basic search
results = client.manga.search(title="Naruto")

# With filters
results = client.manga.search(
    title="Naruto",
    status=["completed"],
    content_rating=["safe", "suggestive"],
    limit=10
)

# Display results
for manga in results:
    title = manga.title.get("en", "No English title")
    print(f"{title} - {manga.status}")
```

### Search by Tags

```python
# Get all tags first
tags = client.manga.get_tag_list()

# Find action tag
action_tag = next((t for t in tags if t["attributes"]["name"]["en"] == "Action"), None)

if action_tag:
    # Search manga with action tag
    results = client.manga.search(
        included_tags=[action_tag["id"]],
        included_tags_mode="AND",
        limit=20
    )
```

### Search by Author

```python
# Search for author
authors = client.author.list(name="Oda Eiichiro")

if authors:
    author_id = authors[0].id
    
    # Find manga by this author
    manga_list = client.manga.search(
        authors=[author_id],
        limit=10
    )
```

### Advanced Search

```python
# Complex search with multiple filters
results = client.manga.search(
    title="Attack",
    year=2009,
    status=["completed"],
    publication_demographic=["shounen"],
    included_tags=["action-uuid", "drama-uuid"],
    included_tags_mode="AND",
    excluded_tags=["romance-uuid"],
    available_translated_language=["en"],
    content_rating=["safe", "suggestive"],
    order={"rating": "desc"},
    limit=20
)
```

## Downloading Manga

### Download Complete Manga

```python
# Download all chapters in English
stats = downloader.download_manga(
    manga_id="manga-uuid",
    languages=["en"]
)

print(f"Total: {stats['total_chapters']}")
print(f"Downloaded: {stats['downloaded']}")
print(f"Failed: {stats['failed']}")
```

### Download Specific Volumes

```python
# Download only volumes 1-3
stats = downloader.download_manga(
    manga_id="manga-uuid",
    languages=["en"],
    volume_filter=["1", "2", "3"]
)
```

### Download Specific Chapters

```python
# Download specific chapters
stats = downloader.download_manga(
    manga_id="manga-uuid",
    languages=["en"],
    chapter_filter=["1", "2", "3", "4", "5"]
)
```

### Download Chapter Range

```python
# Download chapters 1-50
stats = downloader.download_chapter_range(
    manga_id="manga-uuid",
    start_chapter=1.0,
    end_chapter=50.0,
    language="en"
)
```

### Download with Data Saver

```python
# Use data saver mode (lower quality, smaller files)
stats = downloader.download_manga(
    manga_id="manga-uuid",
    languages=["en"],
    data_saver=True
)
```

## Advanced Filtering

### Filter by Publication Status

```python
# Find completed manga
completed = client.manga.search(
    status=["completed"],
    limit=20
)

# Find ongoing manga
ongoing = client.manga.search(
    status=["ongoing"],
    limit=20
)
```

### Filter by Content Rating

```python
# Safe content only
safe_manga = client.manga.search(
    content_rating=["safe"],
    limit=20
)

# Include suggestive content
manga_list = client.manga.search(
    content_rating=["safe", "suggestive"],
    limit=20
)
```

### Filter by Language

```python
# Find manga with English translations
english_manga = client.manga.search(
    available_translated_language=["en"],
    limit=20
)

# Find manga with multiple languages
multilang_manga = client.manga.search(
    available_translated_language=["en", "es", "fr"],
    limit=20
)
```

### Filter by Demographic

```python
# Shounen manga
shounen = client.manga.search(
    publication_demographic=["shounen"],
    limit=20
)

# Seinen manga
seinen = client.manga.search(
    publication_demographic=["seinen"],
    limit=20
)
```

## Working with Chapters

### Get Chapter List

```python
# Get all chapters for a manga
chapters = client.chapter.list(
    manga="manga-uuid",
    translated_language=["en"],
    limit=100,
    order={"chapter": "asc"}
)

for chapter in chapters:
    print(f"Chapter {chapter.chapter}: {chapter.title}")
```

### Get Chapter Details

```python
# Get specific chapter
chapter = client.chapter.get(
    chapter_id="chapter-uuid",
    includes=["scanlation_group", "manga"]
)

print(f"Chapter: {chapter.chapter}")
print(f"Pages: {chapter.pages}")
print(f"Language: {chapter.translated_language}")
```

### Get Chapter Images

```python
# Get image URLs
image_urls = client.at_home.get_image_urls(
    chapter_id="chapter-uuid",
    data_saver=False
)

print(f"Found {len(image_urls)} images")
for idx, url in enumerate(image_urls, 1):
    print(f"{idx}. {url}")
```

### Download Single Chapter

```python
# Download one chapter
chapter_dir = downloader.download_chapter(
    chapter_id="chapter-uuid",
    manga_title="Manga Title",
    volume="1",
    chapter_number="1"
)

print(f"Downloaded to: {chapter_dir}")
```

## Multi-Language Downloads

### Download Multiple Languages

```python
# Download in English and Spanish
stats = downloader.download_manga(
    manga_id="manga-uuid",
    languages=["en", "es"]
)
```

### Check Available Languages

```python
# Get manga details
manga = client.manga.get("manga-uuid")

# Check available languages
print("Available languages:")
for lang in manga.available_translated_languages:
    print(f"- {lang}")
```

### Language-Specific Downloads

```python
# Download each language separately
for language in ["en", "es", "fr"]:
    print(f"Downloading {language} chapters...")
    stats = downloader.download_manga(
        manga_id="manga-uuid",
        languages=[language]
    )
    print(f"  Downloaded: {stats['downloaded']} chapters")
```

## Error Handling

### Basic Error Handling

```python
from src.mangadx.exceptions import (
    MangaDxException,
    NotFoundException,
    RateLimitException
)

try:
    manga = client.manga.get("invalid-id")
except NotFoundException:
    print("Manga not found")
except MangaDxException as e:
    print(f"API error: {e.message}")
```

### Handling Rate Limits

```python
import time

try:
    results = client.manga.search(title="Test")
except RateLimitException as e:
    if e.retry_after:
        print(f"Rate limited. Waiting {e.retry_after} seconds...")
        time.sleep(e.retry_after)
        # Retry
        results = client.manga.search(title="Test")
```

### Download Error Handling

```python
from src.mangadex.exceptions import DownloadException

try:
    stats = downloader.download_manga(
        manga_id="manga-uuid",
        languages=["en"]
    )
except DownloadException as e:
    print(f"Download failed: {e.message}")
    # Log error or retry
```

## Custom Scripts

### Batch Download Script

```python
"""Download multiple manga from a list."""

from src.mangadx import MangaDxClient
from src.mangadx.downloader import DownloadManager

manga_ids = [
    "manga-uuid-1",
    "manga-uuid-2",
    "manga-uuid-3",
]

client = MangaDxClient()
downloader = DownloadManager(client)

for manga_id in manga_ids:
    try:
        print(f"\nDownloading {manga_id}...")
        stats = downloader.download_manga(
            manga_id=manga_id,
            languages=["en"]
        )
        print(f"  Success: {stats['downloaded']}/{stats['total_chapters']}")
    except Exception as e:
        print(f"  Failed: {e}")

client.close()
```

### Search and Filter Script

```python
"""Find manga matching specific criteria."""

from src.mangadx import MangaDxClient

client = MangaDxClient()

# Get action manga from 2020+
results = client.manga.search(
    status=["ongoing"],
    publication_demographic=["shounen"],
    available_translated_language=["en"],
    order={"followedCount": "desc"},
    limit=50
)

# Filter by year
recent_manga = [m for m in results if m.year and m.year >= 2020]

print(f"Found {len(recent_manga)} recent manga:")
for manga in recent_manga:
    title = manga.title.get("en", "No title")
    print(f"- {title} ({manga.year})")

client.close()
```

### Update Checker Script

```python
"""Check for new chapters of followed manga."""

from datetime import datetime, timedelta
from src.mangadx import MangaDxClient

client = MangaDxClient()

# Check for chapters updated in last 24 hours
yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")

manga_ids = ["manga-uuid-1", "manga-uuid-2"]

for manga_id in manga_ids:
    chapters = client.manga.get_feed(
        manga_id=manga_id,
        translated_language=["en"],
        updated_at_since=yesterday,
        order={"updatedAt": "desc"}
    )
    
    if chapters:
        manga = client.manga.get(manga_id)
        title = manga.title.get("en", "Unknown")
        print(f"\n{title}: {len(chapters)} new chapters")
        
        for ch in chapters:
            ch_num = ch.get("attributes", {}).get("chapter", "?")
            print(f"  - Chapter {ch_num}")

client.close()
```

### Bulk Metadata Export

```python
"""Export manga metadata to JSON."""

import json
from src.mangadx import MangaDxClient

client = MangaDxClient()

# Search for manga
results = client.manga.search(
    title="One Piece",
    limit=10,
    includes=["author", "artist", "cover_art"]
)

# Export metadata
metadata = []
for manga in results:
    metadata.append({
        "id": manga.id,
        "title": manga.title.get("en"),
        "status": manga.status,
        "year": manga.year,
        "content_rating": manga.content_rating,
        "languages": manga.available_translated_languages,
    })

# Save to file
with open("manga_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"Exported {len(metadata)} manga to manga_metadata.json")

client.close()
```

## Tips and Best Practices

1. **Always close the client** when done or use context managers
2. **Handle rate limits** gracefully with proper delays
3. **Check available languages** before downloading
4. **Use filters** to reduce API calls and download time
5. **Enable data saver** for slower connections
6. **Monitor disk space** for large downloads
7. **Use try-except blocks** for robust error handling
8. **Respect API limits** by not making too many concurrent requests
