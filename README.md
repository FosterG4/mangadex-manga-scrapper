# Mangadx Manga Scrapper

A powerful, user-friendly Python package for downloading manga from MangaDx (https://mangadx.org) with automatic updates, smart organization, and multi-language support. Available as both a pip-installable package and a standalone application.

> **Note**: This project name is "Mangadx" (the scrapper tool), while "MangaDx" refers to the website and API service.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/thorryuk/mangadex-manga-scrapper/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/thorryuk/mangadex-manga-scrapper/actions/workflows/test.yml)
[![Quick Tests](https://github.com/thorryuk/mangadex-manga-scrapper/actions/workflows/quick-test.yml/badge.svg?branch=master)](https://github.com/thorryuk/mangadex-manga-scrapper/actions/workflows/quick-test.yml)

## ✨ Key Features

### 🚀 Automatic & Smart
- **Auto-Update Folders** - Renames "somename" → proper manga titles automatically
- **Auto-Update Volumes** - Reorganizes chapters when MangaDx changes volumes
- **Auto-Resume** - Skips already downloaded images
- **Auto-Cleanup** - Removes empty folders automatically
- **Just run the downloader again!** No separate commands needed

### 📥 Download Features
- **Interactive CLI** - User-friendly menu with colors and progress bars
- **Multi-Language** - Download in English, Japanese, Spanish, French, etc.
- **Flexible Filtering** - Choose specific volumes, chapters, or ranges
- **Concurrent Downloads** - Fast parallel downloading (configurable)
- **Data Saver Mode** - Lower quality for slower connections
- **Resume Support** - Continue interrupted downloads

### 📁 Smart Organization
- **Proper Titles** - Uses full manga titles (not language codes)
- **Clean Structure** - `Manga Title/Vol.X/Ch.Y/` or `Manga Title/Ch.Y/`
- **No Vol.none** - Chapters without volumes go directly in manga folder
- **Automatic Updates** - Structure updates when you re-download

### 🔍 Advanced Search
- **Search by Title** - Find manga by name
- **Filter by Tags** - Action, Romance, Comedy, etc.
- **Filter by Status** - Ongoing, Completed, Hiatus
- **Filter by Year** - Find manga from specific year
- **Filter by Demographic** - Shounen, Seinen, Shoujo, Josei
- **Filter by Rating** - Safe, Suggestive, Erotica

### 🛡️ Reliable & Safe
- **Rate Limiting** - Respects MangaDx's ~5 req/s limit (default: 4 req/s)
- **Auto-Retry** - Automatic retry with exponential backoff
- **Error Handling** - Comprehensive exception handling
- **Detailed Logging** - Track progress and debug issues
- **Safe Defaults** - Works out of the box, no configuration needed

### 📚 Complete API Coverage
- **Manga API** - Search, details, aggregate, feed, random, tags
- **Chapter API** - List, filter, get chapter details
- **Author API** - Search authors and artists
- **Cover API** - Get cover art in multiple sizes
- **Scanlation Group API** - Group information
- **AtHome API** - Chapter images from MangaDx@Home network

## Architecture

The project follows a modular architecture for maintainability and scalability:

```
mangadex-manga-scrapper/
├── mangadx_scrapper/       # Main package
│   ├── __init__.py        # Package initialization
│   ├── client.py          # Main API client
│   ├── downloader.py      # Download manager
│   ├── exceptions.py      # Custom exceptions
│   ├── http_client.py     # HTTP layer with retry logic
│   ├── models.py          # Data models
│   ├── api/               # API endpoint modules
│   │   ├── __init__.py
│   │   ├── manga.py       # Manga API
│   │   ├── chapter.py     # Chapter API
│   │   ├── author.py      # Author API
│   │   ├── cover.py       # Cover API
│   │   ├── scanlation_group.py  # Scanlation Group API
│   │   └── at_home.py     # AtHome API
│   ├── cli/               # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py        # Interactive CLI
│   │   ├── search.py      # Search command
│   │   └── download.py    # Download command
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── logger.py      # Logging setup
│       └── formatters.py  # Display formatters
├── config/                # Configuration management
│   ├── __init__.py
│   └── settings.py        # Environment-based settings
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
│   └── API_REFERENCE.md   # API reference guide
├── downloads/             # Default download directory
├── main.py                # Legacy entry point
├── setup.py               # Package setup
├── pyproject.toml         # Modern package configuration
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 📦 Installation

### Option 1: Pip Installation (Recommended)

Install the package directly from source:

```bash
# Install the package
pip install git+https://github.com/thorryuk/mangadex-manga-scrapper.git

# Or install in development mode (if you cloned the repo)
git clone https://github.com/thorryuk/mangadex-manga-scrapper.git
cd mangadex-manga-scrapper
pip install -e .
```

**That's it!** The package is now installed with CLI commands available globally.

### Option 2: Manual Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/thorryuk/mangadex-manga-scrapper.git
   cd mangadex-manga-scrapper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure (optional)**
   ```bash
   # Copy example configuration
   cp .env.example .env
   
   # Edit .env if you want to customize
   # Default values work great out of the box!
   ```

4. **Run it!**
   ```bash
   python main.py
   ```

### Prerequisites
- **Python 3.9+** - [Download here](https://www.python.org/downloads/)
- **pip** - Comes with Python

## 🚀 Quick Start

### Using CLI Commands (After pip install)

```bash
# Interactive mode - easiest way to get started
mangadx-scrapper

# Search for manga
mangadx-search "One Piece" --limit 10 --verbose

# Download manga by ID
mangadx-download abc123-def456-ghi789 --language en ja --volumes 1 2 3
```

### Using Python Script (Manual installation)

```bash
# Interactive mode
python main.py

# Or use the library programmatically
python -c "from mangadx_scrapper import MangaDxClient; print('Ready!')"
```

## 💡 Usage

### CLI Commands (Pip Installation)

#### Interactive Mode
```bash
mangadx-scrapper
```

**What you'll see:**
```
============================================================
  MangaDx Manga Scrapper v1.0
============================================================

MAIN MENU
1. Search and download manga
2. Download by manga ID  
3. Exit

Enter your choice: _
```

#### Search Command
```bash
# Basic search
mangadx-search "One Piece"

# Advanced search with filters
mangadx-search "Attack on Titan" --limit 10 --verbose --status completed --demographic shounen

# Search with content rating filters
mangadx-search "Romance Manga" --content-rating safe suggestive --year 2020

# JSON output for scripting
mangadx-search "Naruto" --json > results.json
```

#### Download Command
```bash
# Download all chapters in English
mangadx-download abc123-def456-ghi789

# Download specific languages
mangadx-download abc123-def456-ghi789 --language en ja es

# Download specific volumes
mangadx-download abc123-def456-ghi789 --volumes 1 2 3

# Download specific chapters
mangadx-download abc123-def456-ghi789 --chapters 1 2.5 3

# Download chapter range
mangadx-download abc123-def456-ghi789 --range 1-10

# Data saver mode (lower quality, faster)
mangadx-download abc123-def456-ghi789 --data-saver

# Custom output directory
mangadx-download abc123-def456-ghi789 --output ./my-manga

# Quiet mode (minimal output)
mangadx-download abc123-def456-ghi789 --quiet
```

#### Get Help
```bash
mangadx-scrapper --version
mangadx-search --help
mangadx-download --help
```

### Interactive Mode (Manual Installation)

```bash
python main.py
```

**Choose option 1** and follow the prompts:
1. Enter manga title (e.g., "One Piece")
2. Select manga from results
3. Choose language (default: English)
4. Select volumes/chapters (or press Enter for all)
5. Confirm and watch it download!

### Common Use Cases

#### Download Complete Manga

```bash
python main.py
# 1. Search and download manga
# Enter: One Piece
# Select manga
# Press Enter for all chapters
# Confirm: Y
```

#### Download Specific Volumes

```bash
python main.py
# 1. Search and download manga
# Enter: Silent Witch
# Select manga
# Volumes: 1,2,3
# Confirm: Y
```

#### Download by Manga ID

If you have the manga ID from MangaDx URL:

```bash
python main.py
# 2. Download by manga ID
# Enter: 2b5a3b43-effb-4f54-aa9b-d6093d523452
# Follow prompts
```

### Programmatic Usage

Use the library in your own Python scripts:

```python
from mangadx_scrapper import MangaDxClient
from mangadx_scrapper.downloader import DownloadManager

# Initialize client
client = MangaDxClient()

# Search for manga
manga_list = client.manga.search(
    title="One Piece",
    limit=10,
    content_rating=["safe", "suggestive"],
    available_translated_language=["en"]
)

# Get manga details
manga = client.manga.get(manga_list[0].id)
print(f"Title: {manga.title.get('en')}")
print(f"Status: {manga.status}")

# Download manga
downloader = DownloadManager(client)
stats = downloader.download_manga(
    manga_id=manga.id,
    languages=["en"],
    volume_filter=["1", "2"],  # Optional: specific volumes
    chapter_filter=None,        # Optional: specific chapters
    data_saver=False            # False = high quality
)

print(f"Downloaded: {stats['downloaded']}/{stats['total_chapters']} chapters")

# Close client
client.close()
```

### Quick API Examples

```python
# Simple search and download
from mangadx_scrapper import MangaDxClient

client = MangaDxClient()

# Search for manga
results = client.manga.search("One Piece", limit=5)
for manga in results:
    print(f"{manga.title.get('en')} - {manga.status}")

# Get specific manga
manga = client.manga.get("manga-uuid-here")
print(f"Description: {manga.description.get('en')}")

# Get chapters for a manga
chapters = client.chapter.list(manga=manga.id, translated_language=["en"])
print(f"Found {len(chapters)} chapters")

client.close()
```

### Advanced Examples

#### Download Specific Chapter Range
```python
stats = downloader.download_chapter_range(
    manga_id="manga-uuid",
    start_chapter=1.0,
    end_chapter=10.0,
    language="en"
)
```

#### Search with Advanced Filters
```python
manga_list = client.manga.search(
    title="Attack on Titan",
    status=["completed"],
    publication_demographic=["shounen"],
    year=2009,
    included_tags=["action-tag-uuid", "drama-tag-uuid"],
    included_tags_mode="AND",
    order={"rating": "desc"},
    limit=20
)
```

#### Get Chapter Images
```python
# Get image URLs for a chapter
image_urls = client.at_home.get_image_urls(
    chapter_id="chapter-uuid",
    data_saver=False  # True for compressed images
)

# Download single chapter
chapter_dir = downloader.download_chapter(
    chapter_id="chapter-uuid",
    manga_title="Manga Title",
    volume="1",
    chapter_number="1"
)
```

## ⚙️ Configuration

### Quick Config (Optional)

The app works great with defaults! But you can customize:

```bash
# Edit .env file
DOWNLOAD_DIR=./downloads              # Where to save manga
DEFAULT_LANGUAGE=en                   # Your preferred language
MAX_CONCURRENT_DOWNLOADS=10           # Download speed (1-20)
```

### All Configuration Options

#### 📁 Download Settings
```bash
DOWNLOAD_DIR=./downloads              # Download location
MAX_CONCURRENT_DOWNLOADS=10           # Parallel downloads (1-20)
CHUNK_SIZE=8192                       # Download chunk size
```

#### ⏱️ Rate Limiting (Important!)
```bash
RATE_LIMIT_DELAY=0.25                 # Delay between requests (0.25s = 4 req/s)
MAX_RETRIES=3                         # Retry attempts on failure
RETRY_DELAY=2.0                       # Delay between retries
```

**⚠️ Warning**: MangaDx allows ~5 requests/second. Don't set `RATE_LIMIT_DELAY` below 0.2!

**Consequences of exceeding limit:**
- 🚫 HTTP 429 responses
- 🚫 Temporary IP ban (HTTP 403)
- 🚫 Complete IP block

See [docs/RATE_LIMITS.md](docs/RATE_LIMITS.md) for details.

#### 🌍 Default Filters
```bash
DEFAULT_LANGUAGE=en                   # Default language (en, ja, es, fr, etc.)
DEFAULT_CONTENT_RATING=safe,suggestive,erotica  # Content ratings
```

#### 📝 Logging
```bash
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR
LOG_FILE=                             # Optional: path/to/logfile.log
```

#### ✨ Features
```bash
AUTO_UPDATE_STRUCTURE=true            # Auto-update folders (recommended)
ENABLE_CACHE=true                     # Cache API responses
```

### Configuration Tips

✅ **Recommended Settings:**
- Keep `RATE_LIMIT_DELAY=0.25` (safe and fast)
- Use `MAX_CONCURRENT_DOWNLOADS=10` (good balance)
- Enable `AUTO_UPDATE_STRUCTURE=true` (automatic updates)

⚠️ **Don't Change:**
- `RATE_LIMIT_DELAY` below 0.2 (risk of ban)
- `MAX_CONCURRENT_DOWNLOADS` above 20 (diminishing returns)

📖 **Full list**: See `.env.example` for all options with descriptions.

## 🧪 Testing

### Automated Testing (CI/CD)

This project uses GitHub Actions for automated testing:

- **Quick Tests** - Fast validation on every push (~2 minutes)
  - Unit tests
  - API connectivity check
  - Import validation
  - Configuration validation

- **Full Tests** - Comprehensive testing on PRs (~5 minutes)
  - Tests on Python 3.9, 3.10, 3.11, 3.12
  - Tests on Ubuntu and Windows
  - Limited integration tests
  - Code quality checks

**Status:** Check the badges above for current test status

### Run Tests Locally

#### Unit Tests (Fast)
```bash
python -m unittest discover tests/unit
```

#### Integration Tests (Slower)
```bash
# Set environment variable to enable
export RUN_INTEGRATION_TESTS=true  # Linux/Mac
set RUN_INTEGRATION_TESTS=true     # Windows

python -m unittest discover tests/integration
```

#### Specific Test
```bash
python -m unittest tests.unit.test_http_client
```

#### Quick Validation
```bash
# Same as CI quick test
python -m unittest discover tests/unit -v
python -c "from src.mangadx import MangaDxClient; client = MangaDxClient(); assert client.ping(); client.close()"
```

## Folder Organization

Downloads are organized as:
- **With volumes**: `Manga Title/Vol.X/Ch.Y/`
- **Without volumes**: `Manga Title/Ch.Y/` (no "Vol.none" folders)

### Automatic Updates ✨

**Just run the downloader again!** The application automatically:

1. **Renames old folders** - "ja" → "Silent Witch - Chinmoku no Majo no Kakushigoto"
2. **Updates volume assignments** - Moves chapters if MangaDx changed volumes
3. **Cleans up empty folders** - Removes old Vol.none or empty volume folders

**No separate commands needed!** Simply download the manga again:

```bash
python main.py
# Search for the same manga and download
# Structure updates automatically
```

**Manual update** (if needed):

```bash
python update_volumes.py --manga-id MANGA_ID
```

See [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) for details.

## API Reference

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for detailed API documentation.

## Error Handling

The library provides comprehensive exception handling:

```python
from mangadx_scrapper.exceptions import (
    MangaDxException,
    NotFoundException,
    RateLimitException,
    AuthenticationException
)

try:
    manga = client.manga.get("manga-id")
except NotFoundException:
    print("Manga not found")
except RateLimitException as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except MangaDxException as e:
    print(f"API error: {e.message}")
```

## Project Structure Details

### Core Modules

- **config/settings.py**: Centralized configuration management
- **mangadx_scrapper/client.py**: Main API client with all endpoints
- **mangadx_scrapper/http_client.py**: HTTP layer with retry and rate limiting
- **mangadx_scrapper/models.py**: Data models for API responses
- **mangadx_scrapper/downloader.py**: Download manager with progress tracking
- **mangadx_scrapper/exceptions.py**: Custom exception hierarchy
- **mangadx_scrapper/cli/**: Command-line interface modules

### API Modules

Each API module provides methods for specific resources:
- **manga.py**: Manga search, details, aggregate, feed
- **chapter.py**: Chapter listing and details
- **author.py**: Author information
- **cover.py**: Cover art management
- **scanlation_group.py**: Scanlation group data
- **at_home.py**: Image URL retrieval

### CLI Commands

The package provides three main CLI commands:

- **mangadx-scrapper**: Interactive mode with menu-driven interface
- **mangadx-search**: Search for manga with advanced filtering options
- **mangadx-download**: Download manga chapters with flexible options

All commands support `--help` for detailed usage information and examples.

## Best Practices

1. **Rate Limiting**: Respect the API by not setting `RATE_LIMIT_DELAY` too low
2. **Error Handling**: Always wrap API calls in try-except blocks
3. **Resource Cleanup**: Use context managers or call `client.close()`
4. **Concurrent Downloads**: Adjust `MAX_CONCURRENT_DOWNLOADS` based on your connection
5. **Content Rating**: Filter content appropriately for your use case

## 🔧 Troubleshooting

### Common Issues & Solutions

#### ❌ "No manga found"

**Problem**: Search returns no results

**Solutions:**
- ✅ Try shorter search term: "Silent Witch" instead of full title
- ✅ Check spelling
- ✅ Try alternative title (Japanese, English, etc.)
- ✅ Search by manga ID if you have it

#### ❌ "Rate limited" errors

**Problem**: Getting HTTP 429 responses

**Solutions:**
- ✅ Increase `RATE_LIMIT_DELAY` in `.env`:
  ```bash
  RATE_LIMIT_DELAY=0.5
  ```
- ✅ Wait 5-10 minutes before retrying
- ✅ Check if you're running multiple instances

#### ❌ Folder named "ja" or "Vol.none"

**Problem**: Old downloads with wrong folder names

**Solutions:**
- ✅ Just run the downloader again! Auto-updates enabled by default
- ✅ Or run: `python reorganize_downloads.py`

#### ❌ Volume assignments changed

**Problem**: MangaDx moved chapters to different volumes

**Solutions:**
- ✅ Run the downloader again (auto-updates)
- ✅ Or run: `python update_volumes.py --manga-id MANGA_ID`

#### ❌ "Connection failed" or "Timeout"

**Problem**: Can't connect to MangaDx

**Solutions:**
- ✅ Check internet connection
- ✅ Verify MangaDx is online: https://mangadx.org
- ✅ Try again in a few minutes
- ✅ Check firewall/antivirus settings

#### ❌ "Import Error" or "Module not found"

**Problem**: Python can't find modules

**Solutions:**
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Check Python version: `python --version` (need 3.9+)
- ✅ Activate virtual environment if using one

#### ❌ Download is slow

**Problem**: Downloads taking too long

**Solutions:**
- ✅ Increase concurrent downloads in `.env`:
  ```bash
  MAX_CONCURRENT_DOWNLOADS=15
  ```
- ✅ Check your internet speed
- ✅ Use data saver mode (lower quality, faster)

#### ❌ Disk space errors

**Problem**: Running out of space

**Solutions:**
- ✅ Check available disk space
- ✅ Change download location in `.env`:
  ```bash
  DOWNLOAD_DIR=D:/Manga
  ```
- ✅ Delete old/unwanted downloads

### Getting More Help

**Still having issues?**

1. **Check logs**: Look for error messages in console
2. **Enable debug logging**:
   ```bash
   LOG_LEVEL=DEBUG
   ```
3. **Check documentation**: See `docs/` folder
4. **Open an issue**: Include error messages and steps to reproduce

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

**MIT License** - Copyright (c) 2025 thorryuk

See [LICENSE](LICENSE) file for full details.

### MangaDx API Usage Terms

This software uses the MangaDx API and must comply with their terms:

**Required:**
- ✅ Credit MangaDx (https://mangadx.org)
- ✅ Credit scanlation groups
- ✅ Respect rate limits (~5 req/s)

**Prohibited:**
- ❌ Running advertisements
- ❌ Operating paid services
- ❌ Commercial use without permission
- ❌ Removing credits

**For personal and educational use only.** Users are responsible for compliance with all applicable laws and terms of service.

## Acknowledgments

- **MangaDx** for providing the API
- **Scanlation groups** for their hard work
- All contributors to this project

## Support

For issues and questions:
- Open an issue on GitHub
- Check [API_REFERENCE.md](docs/API_REFERENCE.md)
- Review MangaDx API documentation

## Changelog

### Version 1.0.0
- **Package Structure**: Professional pip-installable Python package
- **CLI Commands**: Three dedicated CLI commands (`mangadx-scrapper`, `mangadx-search`, `mangadx-download`)
- **API Coverage**: Full MangaDx API v5 implementation with all endpoints
- **Interactive Interface**: User-friendly menu-driven CLI
- **Modular Architecture**: Clean separation of concerns with proper package structure
- **Error Handling**: Comprehensive exception handling with custom exception hierarchy
- **Multi-language Support**: Download manga in multiple languages
- **Advanced Filtering**: Search and filter by tags, status, year, demographic, content rating
- **Concurrent Downloads**: Fast parallel downloading with configurable limits
- **Smart Organization**: Automatic folder structure with proper manga titles
- **Rate Limiting**: Built-in respect for MangaDx API limits
- **Testing**: Unit and integration test suites
- **Documentation**: Comprehensive API reference and usage examples
- **Type Hints**: Full type annotation support throughout the codebase

