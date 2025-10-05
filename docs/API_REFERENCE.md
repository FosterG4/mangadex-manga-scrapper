# API Reference

This document provides detailed information about the Mangadx API client library for interacting with the MangaDx API.

## Overview

The Mangadx library provides a comprehensive Python interface for the MangaDx API (https://api.mangadex.org). This library follows the official MangaDx API specifications and includes proper rate limiting, error handling, and data validation.

## Table of Contents

- [Client Initialization](#client-initialization)
- [Manga API](#manga-api)
- [Chapter API](#chapter-api)
- [Author API](#author-api)
- [Cover API](#cover-api)
- [Scanlation Group API](#scanlation-group-api)
- [AtHome API](#athome-api)
- [Download Manager](#download-manager)
- [Models](#models)
- [Exceptions](#exceptions)
- [Rate Limiting](#rate-limiting)
- [Authentication](#authentication)

## Client Initialization

```python
from src.mangadx import MangaDxClient

# Basic initialization (uses default API URL: https://api.mangadex.org)
client = MangaDxClient()

# With custom configuration
client = MangaDxClient(
    base_url="https://api.mangadex.org",
    uploads_url="https://uploads.mangadex.org"
)

# With authentication (for protected endpoints)
client = MangaDxClient(access_token="your_token_here")

# Using context manager (recommended for resource management)
with MangaDxClient() as client:
    # Your code here
    manga = client.manga.get("manga-uuid-here")
    print(f"Title: {manga.title}")
```

### Configuration Options

- `base_url`: MangaDx API base URL (default: `https://api.mangadex.org`)
- `uploads_url`: MangaDx uploads CDN URL (default: `https://uploads.mangadex.org`)
- `access_token`: Authentication token for protected endpoints
- `rate_limit_delay`: Delay between requests in seconds (default: 0.2 for 5 req/sec)
- `max_retries`: Maximum number of retry attempts (default: 3)
- `timeout`: Request timeout in seconds (default: 30)

## Manga API

### Search Manga

```python
manga_list = client.manga.search(
    title="One Piece",
    limit=10,
    offset=0,
    content_rating=["safe", "suggestive"],
    status=["ongoing"],
    available_translated_language=["en"],
    includes=["cover_art", "author", "artist"]
)
```

**Parameters:**
- `title` (str): Manga title to search
- `authors` (List[str]): Author UUIDs
- `artists` (List[str]): Artist UUIDs
- `year` (int): Publication year
- `included_tags` (List[str]): Tag UUIDs to include
- `excluded_tags` (List[str]): Tag UUIDs to exclude
- `status` (List[str]): Publication status
- `content_rating` (List[str]): Content ratings
- `limit` (int): Results per page (max 100)
- `offset` (int): Pagination offset

### Get Manga by ID

```python
manga = client.manga.get(
    manga_id="manga-uuid",
    includes=["cover_art", "author", "artist"]
)
```

### Get Manga Aggregate

```python
volumes = client.manga.get_aggregate(
    manga_id="manga-uuid",
    translated_language=["en"],
    groups=["group-uuid"]
)
```

### Get Manga Feed

```python
chapters = client.manga.get_feed(
    manga_id="manga-uuid",
    limit=100,
    translated_language=["en"],
    order={"chapter": "asc"}
)
```

### Get Random Manga

```python
manga = client.manga.get_random(
    includes=["cover_art"],
    content_rating=["safe", "suggestive"]
)
```

### Get Tag List

```python
tags = client.manga.get_tag_list()
```

## Chapter API

### List Chapters

```python
chapters = client.chapter.list(
    manga="manga-uuid",
    translated_language=["en"],
    limit=100,
    offset=0,
    order={"chapter": "asc"}
)
```

**Parameters:**
- `manga` (str): Manga UUID
- `volume` (str): Volume number
- `chapter` (str): Chapter number
- `translated_language` (List[str]): Language codes
- `groups` (List[str]): Scanlation group UUIDs
- `limit` (int): Results per page
- `offset` (int): Pagination offset

### Get Chapter by ID

```python
chapter = client.chapter.get(
    chapter_id="chapter-uuid",
    includes=["scanlation_group", "manga"]
)
```

## Author API

### List Authors

```python
authors = client.author.list(
    name="Author Name",
    limit=10,
    offset=0
)
```

### Get Author by ID

```python
author = client.author.get(author_id="author-uuid")
```

## Cover API

### List Cover Art

```python
covers = client.cover.list(
    manga=["manga-uuid"],
    limit=10,
    offset=0
)
```

### Get Cover by ID

```python
cover = client.cover.get(cover_id="cover-uuid")
```

### Get Cover URL

```python
url = client.cover.get_cover_url(
    manga_id="manga-uuid",
    file_name="cover.jpg",
    size="original"  # or "512", "256"
)
```

## Scanlation Group API

### List Groups

```python
groups = client.scanlation_group.list(
    name="Group Name",
    limit=10,
    offset=0
)
```

### Get Group by ID

```python
group = client.scanlation_group.get(group_id="group-uuid")
```

## AtHome API

### Get Chapter Images

```python
# Get image URLs
image_urls = client.at_home.get_image_urls(
    chapter_id="chapter-uuid",
    data_saver=False  # True for lower quality
)

# Get server data
server_data = client.at_home.get_server(
    chapter_id="chapter-uuid",
    force_port_443=False
)
```

## Download Manager

### Initialize

```python
from src.mangadex.downloader import DownloadManager

downloader = DownloadManager(
    client=client,
    download_dir=Path("./downloads"),
    max_workers=10
)
```

### Download Single Chapter

```python
chapter_dir = downloader.download_chapter(
    chapter_id="chapter-uuid",
    manga_title="Manga Title",
    volume="1",
    chapter_number="1",
    data_saver=False
)
```

### Download Entire Manga

```python
stats = downloader.download_manga(
    manga_id="manga-uuid",
    languages=["en"],
    volume_filter=["1", "2"],  # Optional
    chapter_filter=["1", "2", "3"],  # Optional
    data_saver=False
)

print(f"Downloaded: {stats['downloaded']}/{stats['total_chapters']}")
```

### Download Chapter Range

```python
stats = downloader.download_chapter_range(
    manga_id="manga-uuid",
    start_chapter=1.0,
    end_chapter=10.0,
    language="en",
    data_saver=False
)
```

## Models

### Manga

```python
manga.id              # UUID
manga.title           # LocalizedString
manga.description     # LocalizedString
manga.status          # str
manga.year            # int
manga.content_rating  # str
manga.tags            # List[Dict]
manga.relationships   # List[Relationship]
```

### Chapter

```python
chapter.id                  # UUID
chapter.title               # str
chapter.volume              # str
chapter.chapter             # str
chapter.pages               # int
chapter.translated_language # str
chapter.relationships       # List[Relationship]
```

### Author

```python
author.id         # UUID
author.name       # str
author.biography  # LocalizedString
author.twitter    # str
author.pixiv      # str
```

### LocalizedString

```python
title = manga.title
title.get("en")           # Get English title
title.get("ja", "N/A")    # Get Japanese with default
title["en"]               # Bracket notation
```

## Exceptions

All exceptions inherit from `MangaDxException`:

- `APIException` - General API errors
- `AuthenticationException` - 401 Unauthorized
- `AuthorizationException` - 403 Forbidden
- `NotFoundException` - 404 Not Found
- `RateLimitException` - 429 Rate Limited
- `ValidationException` - 400 Bad Request
- `ServerException` - 5xx Server Errors
- `NetworkException` - Network errors
- `TimeoutException` - Request timeout
- `DownloadException` - Download failures

### Error Handling

```python
from src.mangadx.exceptions import (
    MangaDxException,
    NotFoundException,
    RateLimitException
)

try:
    manga = client.manga.get("invalid-id")
except NotFoundException as e:
    print(f"Manga not found: {e}")
except RateLimitException as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except MangaDxException as e:
    print(f"API error [{e.status_code}]: {e.message}")
```

## Configuration

All configuration is managed through environment variables in `.env`:

```bash
# API URLs
MANGADX_API_URL=https://api.mangadex.org
MANGADX_UPLOADS_URL=https://uploads.mangadex.org

# Download settings
DOWNLOAD_DIR=./downloads
MAX_CONCURRENT_DOWNLOADS=10

# Rate limiting
RATE_LIMIT_DELAY=0.5
MAX_RETRIES=3
RETRY_DELAY=2.0

# Defaults
DEFAULT_LANGUAGE=en
DEFAULT_CONTENT_RATING=safe,suggestive,erotica
```

See `.env.example` for all available options.
