/**
 * Max Level Priest - Main Application JavaScript
 * Handles chapter list, navigation, and theme management
 */

// Book configuration
const BOOK_ID = 'max-level-priest';

// Theme Management
const ThemeManager = {
    storageKey: 'library_theme',

    init() {
        const savedTheme = localStorage.getItem(this.storageKey) || 'dark';
        this.setTheme(savedTheme);
        this.bindEvents();
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(this.storageKey, theme);

        // Update active state on theme buttons
        document.querySelectorAll('.theme-btn, .theme-option').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === theme);
        });
    },

    bindEvents() {
        document.querySelectorAll('.theme-btn, .theme-option').forEach(btn => {
            btn.addEventListener('click', () => {
                this.setTheme(btn.dataset.theme);
            });
        });
    }
};

// Reading Progress Management
const ProgressManager = {
    getStorageKey() {
        return `${BOOK_ID}_progress`;
    },

    getProgress() {
        try {
            return JSON.parse(localStorage.getItem(this.getStorageKey())) || {};
        } catch {
            return {};
        }
    },

    saveProgress(chapterId, scrollPercent = 0) {
        const progress = this.getProgress();
        progress.lastChapter = chapterId;
        progress.lastRead = Date.now();
        progress.scrollPercent = scrollPercent;
        localStorage.setItem(this.getStorageKey(), JSON.stringify(progress));
    },

    getLastChapter() {
        const progress = this.getProgress();
        return progress.lastChapter || null;
    }
};

// Chapter List Management
const ChapterListManager = {
    init() {
        this.renderChapters();
        this.bindEvents();
        this.updateContinueButton();
        this.updateChapterCount();
    },

    renderChapters() {
        const container = document.getElementById('chaptersList');
        if (!container || typeof chaptersData === 'undefined') return;

        const lastChapter = ProgressManager.getLastChapter();
        let html = '';

        chaptersData.chapters.forEach(chapter => {
            const isReading = chapter.id === lastChapter;
            html += `
                <a href="reader.html?chapter=${chapter.id}" 
                   class="chapter-card ${isReading ? 'reading' : ''}"
                   data-chapter-id="${chapter.id}">
                    <div class="chapter-card-number">Chương ${chapter.id}</div>
                    <div class="chapter-card-title">${chapter.title}</div>
                </a>
            `;
        });

        container.innerHTML = html;
    },

    filterChapters(query) {
        const cards = document.querySelectorAll('.chapter-card');
        const normalizedQuery = query.toLowerCase().trim();

        cards.forEach(card => {
            const title = card.querySelector('.chapter-card-title').textContent.toLowerCase();
            const number = card.querySelector('.chapter-card-number').textContent.toLowerCase();
            const matches = title.includes(normalizedQuery) || number.includes(normalizedQuery);
            card.style.display = matches ? '' : 'none';
        });
    },

    bindEvents() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterChapters(e.target.value);
            });
        }
    },

    updateContinueButton() {
        const btn = document.getElementById('continueBtn');
        if (!btn) return;

        const lastChapter = ProgressManager.getLastChapter();
        if (lastChapter && typeof chaptersData !== 'undefined') {
            btn.href = `reader.html?chapter=${lastChapter}`;
            btn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                Tiếp tục chương ${lastChapter}
            `;
        } else if (typeof chaptersData !== 'undefined' && chaptersData.chapters.length > 0) {
            const firstChapter = chaptersData.chapters[0].id;
            btn.href = `reader.html?chapter=${firstChapter}`;
            btn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                Bắt đầu đọc
            `;
        }
    },

    updateChapterCount() {
        const countEl = document.getElementById('chapterCount');
        if (countEl && typeof chaptersData !== 'undefined') {
            countEl.textContent = chaptersData.chapters.length;
        }
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    ChapterListManager.init();
});

// Export for use in other modules
window.ThemeManager = ThemeManager;
window.ProgressManager = ProgressManager;
window.BOOK_ID = BOOK_ID;
