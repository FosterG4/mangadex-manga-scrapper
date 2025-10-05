# Quick Start Guide

Get started with the Mangadx Manga Scrapper in 5 minutes!

This guide will help you quickly set up and start downloading manga from MangaDx using the Mangadx scrapper tool.

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment file
cp .env.example .env

# 3. (Optional) Edit .env if needed
# Default settings work out of the box
```

## Basic Usage

### Download Manga (Interactive)

```bash
python main.py
```

Then:
1. Choose option **1** (Search and download manga)
2. Enter manga title (e.g., "One Piece")
3. Select manga from results
4. Choose language and filters
5. Confirm download

### Download by Manga ID

If you know the manga ID from MangaDex URL:

```bash
python main.py
# Choose option 2
# Enter: 2b5a3b43-effb-4f54-aa9b-d6093d523452
```

## Common Tasks

### Download Specific Chapters

When prompted:
- **Volumes**: Enter `1,2,3` or press Enter for all
- **Chapters**: Enter `1,2,3,4,5` or press Enter for all
- **Range**: Enter `1-10` for chapters 1 through 10

### Download Multiple Languages

When asked for language:
- Enter: `en,es,fr` (comma-separated)

### Use Data Saver Mode

When prompted "Use data saver mode?":
- Enter `y` for lower quality, smaller files
- Enter `n` for high quality (default)

## Folder Structure

Downloads are saved to `./downloads/` by default:

```
downloads/
└── Manga Title/
    ├── Ch.1/
    ├── Ch.2/
    └── Vol.1/
        └── Ch.3/
```

## Updating Volume Assignments

If MangaDex updates volume assignments:

```bash
# Update specific manga
python update_volumes.py --manga-id MANGA_ID

# Preview changes first
python update_volumes.py --manga-id MANGA_ID --dry-run
```

## Reorganizing Old Downloads

Fix old downloads with issues:

```bash
python reorganize_downloads.py
```

Fixes:
- `Vol.none` folders → Moves to root
- Language code folders → Renames to proper titles

## Configuration

Edit `.env` to customize:

```bash
# Download location
DOWNLOAD_DIR=./downloads

# Number of parallel downloads
MAX_CONCURRENT_DOWNLOADS=10

# Rate limiting (don't go below 0.2!)
RATE_LIMIT_DELAY=0.25

# Default language
DEFAULT_LANGUAGE=en
```

## Tips

### ✅ Best Practices

- Use default rate limit settings (avoid IP ban)
- Search with shorter titles for better results
- Check available languages before downloading
- Use data saver on slow connections

### ⚠️ Avoid

- Setting `RATE_LIMIT_DELAY` below 0.2 (risk of ban)
- Running multiple instances simultaneously
- Downloading same manga twice without checking

## Troubleshooting

### "No manga found"

- Try shorter search term: "Silent Witch" instead of full title
- Check spelling
- Try alternative title (Japanese, English, etc.)

### "Rate limited" errors

- Increase `RATE_LIMIT_DELAY` in `.env`:
  ```bash
  RATE_LIMIT_DELAY=0.5
  ```
- Wait a few minutes before retrying

### Folder named "ja" or "Vol.none"

- Run: `python reorganize_downloads.py`

### Volume assignments changed

- Run: `python update_volumes.py --manga-id MANGA_ID`

## Next Steps

- **Full documentation**: See [README.md](../README.md)
- **API reference**: See [API_REFERENCE.md](API_REFERENCE.md)
- **Usage examples**: See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **Rate limits**: See [RATE_LIMITS.md](RATE_LIMITS.md)
- **Folder structure**: See [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)

## Support

- Check documentation first
- Review error messages carefully
- Ensure API is accessible: https://api.mangadex.org/ping
- Check MangaDex status if issues persist

Happy downloading! 🎉
