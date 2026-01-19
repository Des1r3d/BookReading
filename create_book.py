"""
Book Template Generator for Doc Truyen Website
This script creates the folder structure and files for a new book.
Run: python create_book.py <book-slug>
"""

import os
import json
import sys
from datetime import datetime

def create_book_structure(book_slug, book_title_en="New Book", book_title_vi="Truyện Mới", genre="Light Novel"):
    """Create the folder structure for a new book."""
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    website_path = os.path.join(base_path, "website")
    book_path = os.path.join(website_path, "books", book_slug)
    js_path = os.path.join(book_path, "js")
    
    # Create directories
    os.makedirs(js_path, exist_ok=True)
    print(f"✓ Created directory: {book_path}")
    
    # Create index.html
    index_html = f'''<!DOCTYPE html>
<html lang="vi" data-theme="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title_en} - Đọc Truyện Online</title>
    <meta name="description"
        content="Đọc truyện {book_title_en} bản dịch tiếng Việt. Trải nghiệm đọc truyện mượt mà với chế độ tối, điều chỉnh font chữ.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400&display=swap"
        rel="stylesheet">
    <link rel="stylesheet" href="../../css/main.css">
</head>

<body>
    <!-- Hero Section -->
    <header class="hero">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <nav class="breadcrumb">
                <a href="../../index.html">Thư Viện</a>
                <span>/</span>
                <span>{book_title_en}</span>
            </nav>
            <div class="hero-badge">{genre}</div>
            <h1 class="hero-title">{book_title_en}</h1>
            <p class="hero-subtitle">{book_title_vi}</p>
            <p class="hero-description">Một câu chuyện hấp dẫn đang chờ bạn khám phá</p>
            <div class="hero-stats">
                <div class="stat">
                    <span class="stat-value" id="chapterCount">0</span>
                    <span class="stat-label">Chương</span>
                </div>
                <div class="stat">
                    <span class="stat-value">1</span>
                    <span class="stat-label">Volume</span>
                </div>
                <div class="stat">
                    <span class="stat-value">Đang tiến hành</span>
                    <span class="stat-label">Trạng thái</span>
                </div>
            </div>
            <div class="hero-actions">
                <a href="#" class="btn btn-primary" id="continueBtn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    Bắt đầu đọc
                </a>
                <a href="#chapters" class="btn btn-secondary">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="8" y1="6" x2="21" y2="6"></line>
                        <line x1="8" y1="12" x2="21" y2="12"></line>
                        <line x1="8" y1="18" x2="21" y2="18"></line>
                        <line x1="3" y1="6" x2="3.01" y2="6"></line>
                        <line x1="3" y1="12" x2="3.01" y2="12"></line>
                        <line x1="3" y1="18" x2="3.01" y2="18"></line>
                    </svg>
                    Danh sách chương
                </a>
            </div>
        </div>
    </header>

    <!-- Chapter List Section -->
    <main class="main-content">
        <section class="chapters-section" id="chapters">
            <div class="section-header">
                <h2 class="section-title">Danh Sách Chương</h2>
                <div class="search-box">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                    </svg>
                    <input type="text" id="searchInput" placeholder="Tìm chương...">
                </div>
            </div>

            <div class="chapters-grid" id="chaptersList">
                <!-- Chapters will be loaded dynamically -->
                <div class="no-chapters-message" style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted);">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 1rem; opacity: 0.5;">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                    </svg>
                    <p>Chưa có chương nào. Hãy thêm chương đầu tiên!</p>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <p>{book_title_en} © {datetime.now().year} - <a href="../../index.html">Về Thư Viện</a></p>
            <div class="theme-switcher">
                <button class="theme-btn active" data-theme="dark" title="Chế độ tối">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>
                </button>
                <button class="theme-btn" data-theme="light" title="Chế độ sáng">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="5"></circle>
                        <line x1="12" y1="1" x2="12" y2="3"></line>
                        <line x1="12" y1="21" x2="12" y2="23"></line>
                        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                        <line x1="1" y1="12" x2="3" y2="12"></line>
                        <line x1="21" y1="12" x2="23" y2="12"></line>
                        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                    </svg>
                </button>
                <button class="theme-btn" data-theme="sepia" title="Chế độ sepia">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                    </svg>
                </button>
            </div>
        </div>
    </footer>

    <script src="js/chapters.js"></script>
    <script src="js/app.js"></script>
</body>

</html>'''

    with open(os.path.join(book_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"✓ Created: index.html")
    
    # Create reader.html
    reader_html = f'''<!DOCTYPE html>
<html lang="vi" data-theme="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đang đọc... - {book_title_en}</title>
    <meta name="description" content="Đọc truyện {book_title_en} bản dịch tiếng Việt">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400&display=swap"
        rel="stylesheet">
    <link rel="stylesheet" href="../../css/main.css">
</head>

<body class="reader-page">
    <!-- Reading Progress Bar -->
    <div class="progress-bar">
        <div class="progress-fill" id="progressFill"></div>
    </div>

    <!-- Top Navigation -->
    <nav class="reader-nav">
        <a href="index.html" class="nav-back" title="Về danh sách chương">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m15 18-6-6 6-6"></path>
            </svg>
        </a>
        <div class="nav-info">
            <span class="nav-title" id="chapterTitle">Đang tải...</span>
            <span class="nav-chapter" id="chapterNumber"></span>
        </div>
        <button class="nav-settings" id="settingsBtn" title="Cài đặt">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path
                    d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z">
                </path>
            </svg>
        </button>
    </nav>

    <!-- Settings Panel -->
    <div class="settings-panel" id="settingsPanel">
        <div class="settings-overlay" id="settingsOverlay"></div>
        <div class="settings-content">
            <div class="settings-header">
                <h3>Cài đặt đọc truyện</h3>
                <button class="settings-close" id="settingsClose">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>

            <div class="settings-group">
                <label class="settings-label">Giao diện</label>
                <div class="theme-options">
                    <button class="theme-option active" data-theme="dark">
                        <span class="theme-preview dark-preview"></span>
                        <span>Tối</span>
                    </button>
                    <button class="theme-option" data-theme="light">
                        <span class="theme-preview light-preview"></span>
                        <span>Sáng</span>
                    </button>
                    <button class="theme-option" data-theme="sepia">
                        <span class="theme-preview sepia-preview"></span>
                        <span>Sepia</span>
                    </button>
                </div>
            </div>

            <div class="settings-group">
                <label class="settings-label">
                    Cỡ chữ
                    <span class="settings-value" id="fontSizeValue">18px</span>
                </label>
                <input type="range" class="settings-slider" id="fontSizeSlider" min="14" max="28" value="18" step="1">
                <div class="slider-labels">
                    <span>Nhỏ</span>
                    <span>Lớn</span>
                </div>
            </div>

            <div class="settings-group">
                <label class="settings-label">
                    Khoảng cách dòng
                    <span class="settings-value" id="lineHeightValue">1.8</span>
                </label>
                <input type="range" class="settings-slider" id="lineHeightSlider" min="1.4" max="2.4" value="1.8"
                    step="0.1">
                <div class="slider-labels">
                    <span>Chật</span>
                    <span>Thoáng</span>
                </div>
            </div>

            <div class="settings-group">
                <label class="settings-label">
                    Độ rộng trang
                    <span class="settings-value" id="widthValue">720px</span>
                </label>
                <input type="range" class="settings-slider" id="widthSlider" min="600" max="1000" value="720" step="20">
                <div class="slider-labels">
                    <span>Hẹp</span>
                    <span>Rộng</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Reading Content -->
    <main class="reader-content">
        <article class="chapter-content" id="chapterContent">
            <div class="chapter-header">
                <span class="volume-tag" id="volumeTag">Volume 1</span>
                <h1 class="chapter-heading" id="chapterHeading">Đang tải...</h1>
            </div>
            <div class="chapter-text" id="chapterText">
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p>Đang tải nội dung...</p>
                </div>
            </div>
        </article>
    </main>

    <!-- Chapter Navigation -->
    <nav class="chapter-nav">
        <button class="chapter-nav-btn prev" id="prevChapter" disabled>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m15 18-6-6 6-6"></path>
            </svg>
            <span>Chương trước</span>
        </button>
        <button class="chapter-nav-btn toc" id="tocBtn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
            </svg>
            <span>Mục lục</span>
        </button>
        <button class="chapter-nav-btn next" id="nextChapter">
            <span>Chương sau</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m9 18 6-6-6-6"></path>
            </svg>
        </button>
    </nav>

    <!-- Table of Contents Sidebar -->
    <div class="toc-sidebar" id="tocSidebar">
        <div class="toc-overlay" id="tocOverlay"></div>
        <div class="toc-content">
            <div class="toc-header">
                <h3>Mục lục</h3>
                <button class="toc-close" id="tocClose">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="toc-search">
                <input type="text" id="tocSearch" placeholder="Tìm chương...">
            </div>
            <div class="toc-list" id="tocList">
                <!-- Chapters will be loaded dynamically -->
            </div>
        </div>
    </div>

    <script src="js/chapters.js"></script>
    <script src="js/reader.js"></script>
</body>

</html>'''
    
    with open(os.path.join(book_path, "reader.html"), "w", encoding="utf-8") as f:
        f.write(reader_html)
    print(f"✓ Created: reader.html")
    
    # Create app.js
    app_js = f'''/**
 * {book_title_en} - Main Application JavaScript
 * Handles chapter list, navigation, and theme management
 */

// Book configuration
const BOOK_ID = '{book_slug}';

// Theme Management
const ThemeManager = {{
    storageKey: 'library_theme',

    init() {{
        const savedTheme = localStorage.getItem(this.storageKey) || 'dark';
        this.setTheme(savedTheme);
        this.bindEvents();
    }},

    setTheme(theme) {{
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(this.storageKey, theme);

        // Update active state on theme buttons
        document.querySelectorAll('.theme-btn, .theme-option').forEach(btn => {{
            btn.classList.toggle('active', btn.dataset.theme === theme);
        }});
    }},

    bindEvents() {{
        document.querySelectorAll('.theme-btn, .theme-option').forEach(btn => {{
            btn.addEventListener('click', () => {{
                this.setTheme(btn.dataset.theme);
            }});
        }});
    }}
}};

// Reading Progress Management
const ProgressManager = {{
    getStorageKey() {{
        return `${{BOOK_ID}}_progress`;
    }},

    getProgress() {{
        try {{
            return JSON.parse(localStorage.getItem(this.getStorageKey())) || {{}};
        }} catch {{
            return {{}};
        }}
    }},

    saveProgress(chapterId, scrollPercent = 0) {{
        const progress = this.getProgress();
        progress.lastChapter = chapterId;
        progress.lastRead = Date.now();
        progress.scrollPercent = scrollPercent;
        localStorage.setItem(this.getStorageKey(), JSON.stringify(progress));
    }},

    getLastChapter() {{
        const progress = this.getProgress();
        return progress.lastChapter || null;
    }}
}};

// Chapter List Management
const ChapterListManager = {{
    init() {{
        this.renderChapters();
        this.bindEvents();
        this.updateContinueButton();
        this.updateChapterCount();
    }},

    renderChapters() {{
        const container = document.getElementById('chaptersList');
        if (!container || typeof chaptersData === 'undefined') return;

        if (chaptersData.chapters.length === 0) {{
            return; // Keep the no-chapters message
        }}

        const lastChapter = ProgressManager.getLastChapter();
        let html = '';

        chaptersData.chapters.forEach(chapter => {{
            const isReading = chapter.id === lastChapter;
            html += `
                <a href="reader.html?chapter=${{chapter.id}}" 
                   class="chapter-card ${{isReading ? 'reading' : ''}}"
                   data-chapter-id="${{chapter.id}}">
                    <div class="chapter-card-number">Chương ${{chapter.id}}</div>
                    <div class="chapter-card-title">${{chapter.title}}</div>
                </a>
            `;
        }});

        container.innerHTML = html;
    }},

    filterChapters(query) {{
        const cards = document.querySelectorAll('.chapter-card');
        const normalizedQuery = query.toLowerCase().trim();

        cards.forEach(card => {{
            const title = card.querySelector('.chapter-card-title').textContent.toLowerCase();
            const number = card.querySelector('.chapter-card-number').textContent.toLowerCase();
            const matches = title.includes(normalizedQuery) || number.includes(normalizedQuery);
            card.style.display = matches ? '' : 'none';
        }});
    }},

    bindEvents() {{
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {{
            searchInput.addEventListener('input', (e) => {{
                this.filterChapters(e.target.value);
            }});
        }}
    }},

    updateContinueButton() {{
        const btn = document.getElementById('continueBtn');
        if (!btn) return;

        const lastChapter = ProgressManager.getLastChapter();
        if (lastChapter && typeof chaptersData !== 'undefined') {{
            btn.href = `reader.html?chapter=${{lastChapter}}`;
            btn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                Tiếp tục chương ${{lastChapter}}
            `;
        }} else if (typeof chaptersData !== 'undefined' && chaptersData.chapters.length > 0) {{
            const firstChapter = chaptersData.chapters[0].id;
            btn.href = `reader.html?chapter=${{firstChapter}}`;
            btn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                Bắt đầu đọc
            `;
        }}
    }},

    updateChapterCount() {{
        const countEl = document.getElementById('chapterCount');
        if (countEl && typeof chaptersData !== 'undefined') {{
            countEl.textContent = chaptersData.chapters.length;
        }}
    }}
}};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {{
    ThemeManager.init();
    ChapterListManager.init();
}});

// Export for use in other modules
window.ThemeManager = ThemeManager;
window.ProgressManager = ProgressManager;
window.BOOK_ID = BOOK_ID;
'''

    with open(os.path.join(js_path, "app.js"), "w", encoding="utf-8") as f:
        f.write(app_js)
    print(f"✓ Created: js/app.js")
    
    # Create reader.js
    reader_js = f'''/**
 * {book_title_en} - Reader JavaScript
 * Handles chapter reading experience, settings, and navigation
 */

// Book configuration
const BOOK_ID = '{book_slug}';

// Reader Settings Management
const ReaderSettings = {{
    storageKey: 'library_readerSettings',

    defaults: {{
        fontSize: 18,
        lineHeight: 1.8,
        maxWidth: 720,
        theme: 'dark'
    }},

    getSettings() {{
        try {{
            const saved = JSON.parse(localStorage.getItem(this.storageKey));
            return {{ ...this.defaults, ...saved }};
        }} catch {{
            return {{ ...this.defaults }};
        }}
    }},

    saveSetting(key, value) {{
        const settings = this.getSettings();
        settings[key] = value;
        localStorage.setItem(this.storageKey, JSON.stringify(settings));
    }},

    applySettings() {{
        const settings = this.getSettings();

        document.documentElement.style.setProperty('--reading-font-size', `${{settings.fontSize}}px`);
        document.documentElement.style.setProperty('--reading-line-height', settings.lineHeight);
        document.documentElement.style.setProperty('--reading-max-width', `${{settings.maxWidth}}px`);
        document.documentElement.setAttribute('data-theme', settings.theme);

        // Update UI controls
        const fontSizeSlider = document.getElementById('fontSizeSlider');
        const fontSizeValue = document.getElementById('fontSizeValue');
        const lineHeightSlider = document.getElementById('lineHeightSlider');
        const lineHeightValue = document.getElementById('lineHeightValue');
        const widthSlider = document.getElementById('widthSlider');
        const widthValue = document.getElementById('widthValue');

        if (fontSizeSlider) fontSizeSlider.value = settings.fontSize;
        if (fontSizeValue) fontSizeValue.textContent = `${{settings.fontSize}}px`;
        if (lineHeightSlider) lineHeightSlider.value = settings.lineHeight;
        if (lineHeightValue) lineHeightValue.textContent = settings.lineHeight;
        if (widthSlider) widthSlider.value = settings.maxWidth;
        if (widthValue) widthValue.textContent = `${{settings.maxWidth}}px`;

        // Update theme buttons
        document.querySelectorAll('.theme-option').forEach(btn => {{
            btn.classList.toggle('active', btn.dataset.theme === settings.theme);
        }});
    }}
}};

// Settings Panel
const SettingsPanel = {{
    init() {{
        this.panel = document.getElementById('settingsPanel');
        this.bindEvents();
        ReaderSettings.applySettings();
    }},

    open() {{
        this.panel?.classList.add('active');
        document.body.style.overflow = 'hidden';
    }},

    close() {{
        this.panel?.classList.remove('active');
        document.body.style.overflow = '';
    }},

    bindEvents() {{
        document.getElementById('settingsBtn')?.addEventListener('click', () => this.open());
        document.getElementById('settingsClose')?.addEventListener('click', () => this.close());
        document.getElementById('settingsOverlay')?.addEventListener('click', () => this.close());

        document.getElementById('fontSizeSlider')?.addEventListener('input', (e) => {{
            const value = parseInt(e.target.value);
            document.getElementById('fontSizeValue').textContent = `${{value}}px`;
            document.documentElement.style.setProperty('--reading-font-size', `${{value}}px`);
            ReaderSettings.saveSetting('fontSize', value);
        }});

        document.getElementById('lineHeightSlider')?.addEventListener('input', (e) => {{
            const value = parseFloat(e.target.value);
            document.getElementById('lineHeightValue').textContent = value.toFixed(1);
            document.documentElement.style.setProperty('--reading-line-height', value);
            ReaderSettings.saveSetting('lineHeight', value);
        }});

        document.getElementById('widthSlider')?.addEventListener('input', (e) => {{
            const value = parseInt(e.target.value);
            document.getElementById('widthValue').textContent = `${{value}}px`;
            document.documentElement.style.setProperty('--reading-max-width', `${{value}}px`);
            ReaderSettings.saveSetting('maxWidth', value);
        }});

        document.querySelectorAll('.theme-option').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const theme = btn.dataset.theme;
                document.documentElement.setAttribute('data-theme', theme);
                ReaderSettings.saveSetting('theme', theme);

                document.querySelectorAll('.theme-option').forEach(b => {{
                    b.classList.toggle('active', b.dataset.theme === theme);
                }});
            }});
        }});

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{
                this.close();
                TOCPanel.close();
            }}
        }});
    }}
}};

// Table of Contents Panel
const TOCPanel = {{
    init() {{
        this.sidebar = document.getElementById('tocSidebar');
        this.renderTOC();
        this.bindEvents();
    }},

    open() {{
        this.sidebar?.classList.add('active');
        document.body.style.overflow = 'hidden';
    }},

    close() {{
        this.sidebar?.classList.remove('active');
        document.body.style.overflow = '';
    }},

    renderTOC() {{
        const container = document.getElementById('tocList');
        if (!container || typeof chaptersData === 'undefined') return;

        const currentChapterId = ChapterReader.getCurrentChapterId();
        let html = '';

        chaptersData.chapters.forEach(chapter => {{
            const isActive = chapter.id === currentChapterId;
            html += `
                <a href="reader.html?chapter=${{chapter.id}}" 
                   class="toc-item ${{isActive ? 'active' : ''}}">
                    <div class="toc-item-number">Chương ${{chapter.id}}</div>
                    <div class="toc-item-title">${{chapter.title}}</div>
                </a>
            `;
        }});

        container.innerHTML = html;

        setTimeout(() => {{
            container.querySelector('.toc-item.active')?.scrollIntoView({{ block: 'center' }});
        }}, 100);
    }},

    filterTOC(query) {{
        const items = document.querySelectorAll('.toc-item');
        const normalizedQuery = query.toLowerCase().trim();

        items.forEach(item => {{
            const title = item.querySelector('.toc-item-title').textContent.toLowerCase();
            const number = item.querySelector('.toc-item-number').textContent.toLowerCase();
            const matches = title.includes(normalizedQuery) || number.includes(normalizedQuery);
            item.style.display = matches ? '' : 'none';
        }});
    }},

    bindEvents() {{
        document.getElementById('tocBtn')?.addEventListener('click', () => this.open());
        document.getElementById('tocClose')?.addEventListener('click', () => this.close());
        document.getElementById('tocOverlay')?.addEventListener('click', () => this.close());

        document.getElementById('tocSearch')?.addEventListener('input', (e) => {{
            this.filterTOC(e.target.value);
        }});
    }}
}};

// Progress Bar
const ProgressBar = {{
    init() {{
        this.fill = document.getElementById('progressFill');
        this.bindEvents();
    }},

    update() {{
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = Math.min((scrollTop / docHeight) * 100, 100);

        if (this.fill) {{
            this.fill.style.width = `${{progress}}%`;
        }}

        return progress;
    }},

    bindEvents() {{
        let ticking = false;
        window.addEventListener('scroll', () => {{
            if (!ticking) {{
                requestAnimationFrame(() => {{
                    this.update();
                    ticking = false;
                }});
                ticking = true;
            }}
        }});
    }}
}};

// Chapter Reader
const ChapterReader = {{
    currentChapter: null,

    init() {{
        const chapterId = this.getCurrentChapterId();
        if (chapterId) {{
            this.loadChapter(chapterId);
        }}
        this.bindEvents();
    }},

    getCurrentChapterId() {{
        const params = new URLSearchParams(window.location.search);
        return parseInt(params.get('chapter')) || null;
    }},

    getChapterById(id) {{
        if (typeof chaptersData === 'undefined') return null;
        return chaptersData.chapters.find(ch => ch.id === id);
    }},

    getChapterIndex(id) {{
        if (typeof chaptersData === 'undefined') return -1;
        return chaptersData.chapters.findIndex(ch => ch.id === id);
    }},

    loadChapter(chapterId) {{
        const chapter = this.getChapterById(chapterId);
        if (!chapter) {{
            document.getElementById('chapterText').innerHTML = `
                <div class="loading-spinner">
                    <p>Không tìm thấy chương ${{chapterId}}</p>
                </div>
            `;
            return;
        }}

        this.currentChapter = chapter;

        document.title = `Chương ${{chapter.id}}: ${{chapter.title}} - {book_title_en}`;

        document.getElementById('chapterTitle').textContent = chapter.title;
        document.getElementById('chapterNumber').textContent = `Chương ${{chapter.id}}`;
        document.getElementById('volumeTag').textContent = `Volume ${{chapter.volume}}`;
        document.getElementById('chapterHeading').textContent = `Chương ${{chapter.id}}: ${{chapter.title}}`;

        const contentHtml = chapter.content
            .split('\\n')
            .filter(p => p.trim())
            .map(p => `<p>${{p}}</p>`)
            .join('');

        document.getElementById('chapterText').innerHTML = contentHtml;

        this.updateNavigation(chapterId);
        this.saveProgress(chapterId);
        window.scrollTo(0, 0);
        TOCPanel.renderTOC();
    }},

    updateNavigation(chapterId) {{
        const index = this.getChapterIndex(chapterId);
        const prevBtn = document.getElementById('prevChapter');
        const nextBtn = document.getElementById('nextChapter');

        if (index > 0) {{
            prevBtn.disabled = false;
            prevBtn.onclick = () => this.navigateToChapter(chaptersData.chapters[index - 1].id);
        }} else {{
            prevBtn.disabled = true;
            prevBtn.onclick = null;
        }}

        if (index < chaptersData.chapters.length - 1) {{
            nextBtn.disabled = false;
            nextBtn.onclick = () => this.navigateToChapter(chaptersData.chapters[index + 1].id);
        }} else {{
            nextBtn.disabled = true;
            nextBtn.onclick = null;
        }}
    }},

    navigateToChapter(chapterId) {{
        window.history.pushState({{}}, '', `reader.html?chapter=${{chapterId}}`);
        this.loadChapter(chapterId);
    }},

    saveProgress(chapterId) {{
        try {{
            const progress = {{
                lastChapter: chapterId,
                lastRead: Date.now(),
                scrollPercent: 0
            }};
            localStorage.setItem(`${{BOOK_ID}}_progress`, JSON.stringify(progress));
        }} catch (e) {{
            console.warn('Could not save progress:', e);
        }}
    }},

    bindEvents() {{
        document.addEventListener('keydown', (e) => {{
            if (e.target.tagName === 'INPUT') return;

            const index = this.getChapterIndex(this.currentChapter?.id);
            if (index === -1) return;

            if (e.key === 'ArrowLeft' && index > 0) {{
                this.navigateToChapter(chaptersData.chapters[index - 1].id);
            }} else if (e.key === 'ArrowRight' && index < chaptersData.chapters.length - 1) {{
                this.navigateToChapter(chaptersData.chapters[index + 1].id);
            }}
        }});

        window.addEventListener('popstate', () => {{
            const chapterId = this.getCurrentChapterId();
            if (chapterId) {{
                this.loadChapter(chapterId);
            }}
        }});

        let saveTimeout;
        window.addEventListener('scroll', () => {{
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {{
                const progress = ProgressBar.update();
                if (this.currentChapter) {{
                    try {{
                        const saved = JSON.parse(localStorage.getItem(`${{BOOK_ID}}_progress`)) || {{}};
                        saved.scrollPercent = progress;
                        localStorage.setItem(`${{BOOK_ID}}_progress`, JSON.stringify(saved));
                    }} catch (e) {{ }}
                }}
            }}, 500);
        }});
    }}
}};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {{
    SettingsPanel.init();
    TOCPanel.init();
    ProgressBar.init();
    ChapterReader.init();
}});
'''

    with open(os.path.join(js_path, "reader.js"), "w", encoding="utf-8") as f:
        f.write(reader_js)
    print(f"✓ Created: js/reader.js")
    
    # Create empty chapters.js
    chapters_js = f'''/**
 * {book_title_en} - Chapter Data
 * Add your chapter data here
 */

const chaptersData = {{
    bookTitle: "{book_title_en}",
    bookTitleVi: "{book_title_vi}",
    totalChapters: 0,
    chapters: [
        // Example chapter format:
        // {{
        //     id: 1,
        //     volume: 1,
        //     title: "Tên chương",
        //     content: "Nội dung chương..."
        // }}
    ]
}};
'''

    with open(os.path.join(js_path, "chapters.js"), "w", encoding="utf-8") as f:
        f.write(chapters_js)
    print(f"✓ Created: js/chapters.js")
    
    print(f"\n✅ Book '{book_title_en}' created successfully!")
    print(f"📁 Location: {book_path}")
    print(f"\n📝 Next steps:")
    print(f"   1. Add chapter data to: {os.path.join(js_path, 'chapters.js')}")
    print(f"   2. Visit: books/{book_slug}/index.html")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_book.py <book-slug> [title-en] [title-vi] [genre]")
        print("Example: python create_book.py my-new-book 'My New Book' 'Truyện Mới' 'Light Novel'")
        sys.exit(1)
    
    slug = sys.argv[1]
    title_en = sys.argv[2] if len(sys.argv) > 2 else "New Book"
    title_vi = sys.argv[3] if len(sys.argv) > 3 else "Truyện Mới"
    genre = sys.argv[4] if len(sys.argv) > 4 else "Light Novel"
    
    create_book_structure(slug, title_en, title_vi, genre)
