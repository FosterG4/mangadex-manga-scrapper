# Download Folder Structure

This document explains how manga downloads are organized and how to fix existing folders.

## Default Folder Structure

### With Volumes

```
downloads/
└── Silent Witch - Chinmoku no Majo no Kakushigoto/
    ├── Vol.1/
    │   ├── Ch.1/
    │   │   ├── 001.jpg
    │   │   ├── 002.jpg
    │   │   └── ...
    │   └── Ch.2/
    │       └── ...
    └── Vol.2/
        └── ...
```

### Without Volumes

```
downloads/
└── Silent Witch - Chinmoku no Majo no Kakushigoto/
    ├── Ch.1/
    │   ├── 001.jpg
    │   ├── 002.jpg
    │   └── ...
    ├── Ch.2/
    │   └── ...
    └── Ch.3/
        └── ...
```

## Title Selection Priority

The application uses this priority for folder names:

1. **English title** (`en`)
2. **Japanese title** (`ja`) - e.g., "Silent Witch - Chinmoku no Majo no Kakushigoto"
3. **Romanized Japanese** (`ja-ro`)
4. **Any available title**
5. **Fallback**: `Manga_{first-8-chars-of-id}`

## Volume Handling

### Chapters With Volumes

If a chapter has a volume number (e.g., "1", "2", "3"):
- Creates: `Manga Title/Vol.X/Ch.Y/`

### Chapters Without Volumes

If a chapter has no volume or volume is "none":
- Creates: `Manga Title/Ch.Y/`
- **No "Vol.none" folder is created**

### Mixed Volumes

Some manga have both:
- Chapters 1-10 with volumes → `Vol.1/Ch.1/`, `Vol.1/Ch.2/`, etc.
- Chapters 11+ without volumes → `Ch.11/`, `Ch.12/`, etc.

This is normal and handled automatically.

## Updating Volume Assignments

### Automatic Volume Updates

When MangaDex updates volume assignments (e.g., chapters move from "no volume" to "Volume 7"), use the update script:

```bash
# Update specific manga
python update_volumes.py --manga-id 2b5a3b43-effb-4f54-aa9b-d6093d523452

# Scan all manga folders
python update_volumes.py --scan-all

# Dry run (preview changes without applying)
python update_volumes.py --manga-id MANGA_ID --dry-run

# Interactive mode
python update_volumes.py
```

### Example Scenario

**Day 1 - Initial Download:**
```
Silent Witch/
├── Ch.1/
├── Ch.2/
├── Ch.3/
└── Vol.1/
    └── Ch.4/
```

**Day 4 - MangaDex Updates:**
- Chapters 1-3 are now assigned to Volume 7
- You run: `python update_volumes.py --manga-id MANGA_ID`

**After Update:**
```
Silent Witch/
├── Vol.1/
│   └── Ch.4/
└── Vol.7/
    ├── Ch.1/  ← Moved
    ├── Ch.2/  ← Moved
    └── Ch.3/  ← Moved
```

### Features

- ✅ Detects volume assignment changes from MangaDex API
- ✅ Moves chapters to correct volume folders
- ✅ Removes empty volume folders
- ✅ Dry-run mode to preview changes
- ✅ Interactive confirmation before applying
- ✅ Handles both volume additions and removals

## Reorganizing Existing Downloads

If you have old downloads with issues, use the reorganizer script:

### Issues Fixed

1. **Vol.none folders** → Moves chapters to manga root
2. **Language code folders** (ja, en, etc.) → Renames to proper title
3. **Short folder names** → Renames with full title

### Running the Reorganizer

```bash
python reorganize_downloads.py
```

The script will:
1. Scan your downloads folder
2. Find and fix Vol.none folders automatically
3. Detect language code folders
4. Ask for manga IDs to rename them properly
5. Merge or rename as needed

### Example

**Before:**
```
downloads/
├── ja/                    # Language code instead of title
│   ├── Vol.none/         # Should be at root
│   │   ├── Ch.1/
│   │   └── Ch.2/
│   └── Vol.1/
│       └── Ch.3/
```

**After:**
```
downloads/
└── Silent Witch - Chinmoku no Majo no Kakushigoto/
    ├── Ch.1/             # Moved from Vol.none
    ├── Ch.2/             # Moved from Vol.none
    └── Vol.1/
        └── Ch.3/
```

## Manual Reorganization

If you prefer to reorganize manually:

### Step 1: Move Chapters from Vol.none

```bash
# Windows PowerShell
Move-Item "downloads\MangaTitle\Vol.none\*" "downloads\MangaTitle\"
Remove-Item "downloads\MangaTitle\Vol.none"

# Linux/Mac
mv downloads/MangaTitle/Vol.none/* downloads/MangaTitle/
rmdir downloads/MangaTitle/Vol.none
```

### Step 2: Rename Language Code Folders

1. Find the manga on MangaDex website
2. Get the proper title
3. Rename the folder

```bash
# Windows PowerShell
Rename-Item "downloads\ja" "downloads\Silent Witch - Chinmoku no Majo no Kakushigoto"

# Linux/Mac
mv "downloads/ja" "downloads/Silent Witch - Chinmoku no Majo no Kakushigoto"
```

## Filename Sanitization

Invalid characters are replaced with underscores:

- `< > : " / \ | ? *` → `_`

Examples:
- `Manga: Title` → `Manga_ Title`
- `Title/Subtitle` → `Title_Subtitle`

## Best Practices

### ✅ DO

- Let the application create folder structure automatically
- Use the reorganizer script for bulk fixes
- Keep manga titles descriptive

### ❌ DON'T

- Manually create Vol.none folders
- Use special characters in folder names
- Mix different manga in same folder

## Configuration

You can change the download location in `.env`:

```bash
DOWNLOAD_DIR=./downloads        # Default
# or
DOWNLOAD_DIR=D:/Manga          # Custom path
# or
DOWNLOAD_DIR=/mnt/storage/manga # Linux path
```

## Troubleshooting

### Folder Named "ja" or Other Language Code

**Cause**: Old version used first available language code

**Fix**: Run `python reorganize_downloads.py`

### Vol.none Folders

**Cause**: Old version created volume folders even when none specified

**Fix**: Run `python reorganize_downloads.py` or manually move chapters

### Duplicate Chapters

**Cause**: Downloaded same chapter multiple times

**Fix**: Check chapter numbers and delete duplicates manually

### Special Characters in Names

**Cause**: Manga title contains invalid filesystem characters

**Fix**: Automatically sanitized to underscores

## Future Downloads

All new downloads will automatically:
- Use proper manga titles (not language codes)
- Skip Vol.none folders
- Organize chapters correctly

No manual intervention needed! 🎉
