# 📚 Thư Viện Truyện - Book Reading Website

A beautiful Vietnamese book reading website with a modern, premium design. Features dark/light/sepia themes, customizable reading experience, and mobile-responsive layout.

![Vietnamese](https://img.shields.io/badge/language-Vietnamese-blue)
![Static Site](https://img.shields.io/badge/type-Static%20Site-green)

## ✨ Features

- **Premium Reading Experience** - Clean typography with Lora serif font
- **Multiple Themes** - Dark, Light, and Sepia modes
- **Customizable Reader** - Adjust font size, line height, and page width
- **Reading Progress** - Visual progress bar and saved position
- **Mobile Responsive** - Works beautifully on all devices
- **Chapter Navigation** - Easy prev/next and table of contents
- **Fast & Lightweight** - Static HTML/CSS/JS, no framework overhead

## 🚀 Quick Start

### View Locally
Simply open `website/index.html` in your browser.

### Deploy to VPS
See [deploy/README.md](deploy/README.md) for detailed nginx + Cloudflare deployment guide.

## 📁 Project Structure

```
├── website/              # Main web application
│   ├── index.html        # Library/home page
│   ├── reader.html       # Chapter reader page
│   ├── css/main.css      # Styles with theme system
│   ├── js/               # JavaScript modules
│   └── books/            # Individual book pages
│
├── scripts/              # Utility scripts
│   ├── auto_scrape.py          # Web scraper
│   ├── translate_chapters.py   # AI translation
│   ├── format_for_website.py   # Output formatting
│   └── update_chapters_json.py # Data updates
│
├── Chapters/             # Translated chapter files (.vn.txt)
│
└── deploy/               # VPS deployment documentation
```

## 🛠️ Scripts Usage

### Scraping New Chapters
```bash
cd scripts
python auto_scrape.py
```

### Translating Chapters
```bash
python translate_chapters.py
```

### Updating Website Data
```bash
python update_chapters_json.py
```

## 🎨 Themes

| Theme | Description |
|-------|-------------|
| 🌙 Dark | Deep blue-black background, easy on the eyes |
| ☀️ Light | Clean white background for daytime reading |
| 📜 Sepia | Warm paper-like tones for classic feel |

## 📄 License

This project is for personal use.

---
