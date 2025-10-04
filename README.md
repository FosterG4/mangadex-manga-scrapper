# MangaDex Manga Downloader

A powerful, user-friendly Python application for downloading manga from MangaDex with automatic updates, smart organization, and multi-language support.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/thorryuk/mangadex-manga-scrapper/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/thorryuk/mangadex-manga-scrapper/actions/workflows/test.yml)
[![Quick Tests](https://github.com/thorryuk/mangadex-manga-scrapper/actions/workflows/quick-test.yml/badge.svg?branch=master)](https://github.com/thorryuk/mangadex-manga-scrapper/actions/workflows/quick-test.yml)

## ✨ Key Features

### 🚀 Automatic & Smart
- **Auto-Update Folders** - Renames "somename" → proper manga titles automatically
- **Auto-Update Volumes** - Reorganizes chapters when MangaDex changes volumes
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
- **Rate Limiting** - Respects MangaDex's ~5 req/s limit (default: 4 req/s)
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
- **AtHome API** - Chapter images from MangaDex@Home network

## Architecture

The project follows a modular architecture for maintainability and scalability:

```
mangadex-manga-scrapper/
├── config/                 # Configuration management
│   ├── settings.py        # Environment-based settings
│   └── __init__.py
├── src/
│   ├── mangadex/          # Core API client library
│   │   ├── api/           # API endpoint modules
│   │   │   ├── manga.py
│   │   │   ├── chapter.py
│   │   │   ├── author.py
│   │   │   ├── cover.py
│   │   │   ├── scanlation_group.py
│   │   │   └── at_home.py
│   │   ├── client.py      # Main client
│   │   ├── http_client.py # HTTP layer with retry logic
│   │   ├── models.py      # Data models
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── downloader.py  # Download manager
│   ├── utils/             # Utility modules
│   │   ├── logger.py      # Logging setup
│   │   └── formatters.py  # Display formatters
│   └── cli.py             # Interactive CLI
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
│   └── API_REFERENCE.md   # API reference guide
├── downloads/             # Default download directory
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🚀 Quick Start (3 Steps!)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment file (optional - has safe defaults)
cp .env.example .env

# 3. Run the downloader!
python main.py
```

That's it! The application will guide you through the rest.

## 📦 Installation

### Prerequisites
- **Python 3.9+** - [Download here](https://www.python.org/downloads/)
- **pip** - Comes with Python

### Detailed Setup

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

## 💡 Usage

### Interactive Mode (Easiest!)

```bash
python main.py
```

**What you'll see:**

```
============================================================
  MangaDex Manga Downloader v1.0
============================================================

MAIN MENU
1. Search and download manga
2. Download by manga ID  
3. Exit

Enter your choice: _
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

If you have the manga ID from MangaDex URL:

```bash
python main.py
# 2. Download by manga ID
# Enter: 2b5a3b43-effb-4f54-aa9b-d6093d523452
# Follow prompts
```

### Programmatic Usage

Use the library in your own Python scripts:

```python
from src.mangadex import MangaDexClient
from src.mangadex.downloader import DownloadManager

# Initialize client
client = MangaDexClient()

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

**⚠️ Warning**: MangaDex allows ~5 requests/second. Don't set `RATE_LIMIT_DELAY` below 0.2!

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
python -c "from src.mangadex import MangaDexClient; client = MangaDexClient(); assert client.ping(); client.close()"
```

## Folder Organization

Downloads are organized as:
- **With volumes**: `Manga Title/Vol.X/Ch.Y/`
- **Without volumes**: `Manga Title/Ch.Y/` (no "Vol.none" folders)

### Automatic Updates ✨

**Just run the downloader again!** The application automatically:

1. **Renames old folders** - "ja" → "Silent Witch - Chinmoku no Majo no Kakushigoto"
2. **Updates volume assignments** - Moves chapters if MangaDex changed volumes
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
from src.mangadex.exceptions import (
    MangaDexException,
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
except MangaDexException as e:
    print(f"API error: {e.message}")
```

## Project Structure Details

### Core Modules

- **config/settings.py**: Centralized configuration management
- **src/mangadex/client.py**: Main API client with all endpoints
- **src/mangadex/http_client.py**: HTTP layer with retry and rate limiting
- **src/mangadex/models.py**: Data models for API responses
- **src/mangadex/downloader.py**: Download manager with progress tracking
- **src/mangadex/exceptions.py**: Custom exception hierarchy

### API Modules

Each API module provides methods for specific resources:
- **manga.py**: Manga search, details, aggregate, feed
- **chapter.py**: Chapter listing and details
- **author.py**: Author information
- **cover.py**: Cover art management
- **scanlation_group.py**: Scanlation group data
- **at_home.py**: Image URL retrieval

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

**Problem**: MangaDex moved chapters to different volumes

**Solutions:**
- ✅ Run the downloader again (auto-updates)
- ✅ Or run: `python update_volumes.py --manga-id MANGA_ID`

#### ❌ "Connection failed" or "Timeout"

**Problem**: Can't connect to MangaDex

**Solutions:**
- ✅ Check internet connection
- ✅ Verify MangaDex is online: https://mangadex.org
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

### MangaDex API Usage Terms

This software uses the MangaDex API and must comply with their terms:

**Required:**
- ✅ Credit MangaDex (https://mangadex.org)
- ✅ Credit scanlation groups
- ✅ Respect rate limits (~5 req/s)

**Prohibited:**
- ❌ Running advertisements
- ❌ Operating paid services
- ❌ Commercial use without permission
- ❌ Removing credits

**For personal and educational use only.** Users are responsible for compliance with all applicable laws and terms of service.

## Acknowledgments

- **MangaDex** for providing the API
- **Scanlation groups** for their hard work
- All contributors to this project

## Support

For issues and questions:
- Open an issue on GitHub
- Check [API_REFERENCE.md](docs/API_REFERENCE.md)
- Review MangaDex API documentation

## Changelog

### Version 1.0.0
- Initial release
- Full MangaDex API v5 implementation
- Interactive CLI interface
- Modular architecture
- Comprehensive error handling
- Multi-language support
- Advanced filtering options
- Concurrent downloads
- Unit and integration tests

