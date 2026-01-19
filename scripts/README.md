# Scripts

Utility scripts for scraping, translating, and formatting book chapters.

## Scripts Overview

| Script | Description |
|--------|-------------|
| `auto_scrape.py` | Web scraper for Ko-fi posts |
| `kofi_scraper_fast.py` | Fast parallel scraping engine |
| `translate_chapters.py` | AI translation using OpenAI API |
| `format_for_website.py` | Format chapters for website |
| `parse_chapters.py` | Parse chapter files |
| `update_chapters_json.py` | Update website JSON data |

## Directories

- `Chapters_Untranslated/` - Raw scraped chapters
- `Chapters_Translated/` - Translated chapters ready for website

## Usage

```bash
# Activate virtual environment first
../.venv/Scripts/activate  # Windows
# source ../.venv/bin/activate  # Linux/Mac

# Scrape new chapters
python auto_scrape.py

# Translate chapters
python translate_chapters.py

# Update website data
python update_chapters_json.py
```
