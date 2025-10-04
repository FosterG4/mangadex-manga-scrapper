# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-10-04

### Added

#### Core Features
- **Complete MangaDex API v5 implementation** with all endpoints
- **Interactive CLI** for easy manga search and download
- **Multi-language support** with configurable default language
- **Advanced filtering** by volume, chapter, tags, status, demographic, etc.
- **Concurrent downloads** with configurable worker count
- **Resume support** - automatically skips already downloaded images
- **Progress tracking** with tqdm progress bars

#### Automatic Updates ✨
- **Auto-rename folders** - Language codes ("ja") automatically renamed to proper titles
- **Auto-update volumes** - Chapters automatically moved when MangaDex changes volume assignments
- **Auto-cleanup** - Empty folders automatically removed
- **No manual intervention** - Just run the downloader again!

#### Smart Folder Organization
- **Proper titles** - Uses English → Japanese → Romanized → Any available
- **No Vol.none** - Chapters without volumes go directly in manga root
- **Clean structure** - `Manga Title/Vol.X/Ch.Y/` or `Manga Title/Ch.Y/`
- **Automatic detection** - Detects and fixes old folder structures

#### API Client
- **Modular architecture** - Separate modules for Manga, Chapter, Author, Cover, etc.
- **HTTP client** with retry logic and rate limiting
- **Error handling** - Comprehensive exception hierarchy
- **Rate limit compliance** - Respects MangaDex's ~5 req/s limit (default: 4 req/s)
- **Automatic retries** - Exponential backoff on failures

#### Download Manager
- **Smart downloads** - Only downloads missing images
- **Volume filtering** - Download specific volumes or chapters
- **Chapter ranges** - Download chapters 1-50 with single command
- **Data saver mode** - Lower quality for slower connections
- **Multi-language** - Download same manga in multiple languages

#### Configuration
- **Environment-based** - All settings in `.env` file
- **Safe defaults** - Works out of the box
- **Flexible** - Customize download location, rate limits, workers, etc.
- **Feature flags** - Enable/disable cache, auto-updates, etc.

#### Documentation
- **Comprehensive README** - Installation, usage, examples
- **API Reference** - Complete API documentation
- **Usage Examples** - Common use cases and patterns
- **Rate Limits Guide** - Understanding and respecting API limits
- **Folder Structure Guide** - Organization and reorganization
- **Quick Start** - Get started in 5 minutes

#### Utilities
- **reorganize_downloads.py** - Fix old downloads (Vol.none, language codes)
- **update_volumes.py** - Manually update volume assignments
- **Automatic integration** - Updates run automatically during downloads

#### Testing
- **Unit tests** - HTTP client, models, formatters
- **Integration tests** - Real API calls (optional)
- **Test coverage** - Core functionality tested

### Technical Details

#### Architecture
- **Modular design** - Clean separation of concerns
- **Type hints** - Full type annotations
- **Logging** - Comprehensive logging with configurable levels
- **Error handling** - Graceful degradation and clear error messages

#### Performance
- **Concurrent downloads** - Up to 10 parallel image downloads
- **Rate limiting** - 0.25s between API calls (4 req/s)
- **Smart caching** - Optional caching for API responses
- **Efficient I/O** - Streaming downloads with progress tracking

#### Security
- **No hardcoded credentials** - All auth in environment variables
- **Safe file operations** - Filename sanitization
- **Proper permissions** - Creates directories with correct permissions

### Configuration Options

```bash
# API
MANGADEX_API_URL=https://api.mangadex.org
MANGADEX_UPLOADS_URL=https://uploads.mangadex.org

# Downloads
DOWNLOAD_DIR=./downloads
MAX_CONCURRENT_DOWNLOADS=10

# Rate Limiting
RATE_LIMIT_DELAY=0.25  # 4 req/s (safe for ~5 req/s limit)
MAX_RETRIES=3
RETRY_DELAY=2.0

# Defaults
DEFAULT_LANGUAGE=en
DEFAULT_CONTENT_RATING=safe,suggestive,erotica

# Features
AUTO_UPDATE_STRUCTURE=true  # Automatic folder updates
ENABLE_CACHE=true
```

### Dependencies

- `requests` - HTTP client
- `python-dotenv` - Environment configuration
- `tqdm` - Progress bars
- `colorama` - Colored terminal output
- `urllib3` - HTTP utilities

### Known Limitations

- Authentication endpoints not fully implemented (not needed for downloading)
- Some advanced API features not exposed in CLI (available programmatically)
- Windows-specific path handling (works on all platforms)

### Future Enhancements

Potential features for future versions:
- Web UI for easier management
- Download queue management
- Automatic new chapter detection
- CBZ/CBR archive creation
- Metadata embedding
- Cover art download
- Reading progress tracking

## How to Update

### From Old Version

If you have an old version:

1. **Backup your downloads** (optional, but recommended)
2. **Pull latest code** or download new version
3. **Update dependencies**: `pip install -r requirements.txt`
4. **Update .env**: Add new settings from `.env.example`
5. **Run downloader**: Old folders will auto-update!

### Auto-Update Features

The new version automatically:
- Renames "ja" folders to proper titles
- Moves chapters to correct volumes
- Cleans up Vol.none folders
- No manual scripts needed!

## Support

- **Documentation**: See [README.md](README.md)
- **Issues**: Open GitHub issue
- **API Docs**: https://api.mangadex.org/docs/

## License

MIT License - Copyright (c) 2025 thorryuk

For personal and educational use. Must comply with MangaDex's terms of service.

## Credits

- **MangaDex** for the API
- **Scanlation groups** for their work
- All contributors
