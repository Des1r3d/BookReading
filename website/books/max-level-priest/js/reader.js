/**
 * Max Level Priest - Reader JavaScript
 * Handles chapter reading experience, settings, and navigation
 */

// Book configuration
const BOOK_ID = 'max-level-priest';

// Reader Settings Management
const ReaderSettings = {
    storageKey: 'library_readerSettings',

    defaults: {
        fontSize: 18,
        lineHeight: 1.8,
        maxWidth: 720,
        theme: 'dark'
    },

    getSettings() {
        try {
            const saved = JSON.parse(localStorage.getItem(this.storageKey));
            return { ...this.defaults, ...saved };
        } catch {
            return { ...this.defaults };
        }
    },

    saveSetting(key, value) {
        const settings = this.getSettings();
        settings[key] = value;
        localStorage.setItem(this.storageKey, JSON.stringify(settings));
    },

    applySettings() {
        const settings = this.getSettings();

        document.documentElement.style.setProperty('--reading-font-size', `${settings.fontSize}px`);
        document.documentElement.style.setProperty('--reading-line-height', settings.lineHeight);
        document.documentElement.style.setProperty('--reading-max-width', `${settings.maxWidth}px`);
        document.documentElement.setAttribute('data-theme', settings.theme);

        // Update UI controls
        const fontSizeSlider = document.getElementById('fontSizeSlider');
        const fontSizeValue = document.getElementById('fontSizeValue');
        const lineHeightSlider = document.getElementById('lineHeightSlider');
        const lineHeightValue = document.getElementById('lineHeightValue');
        const widthSlider = document.getElementById('widthSlider');
        const widthValue = document.getElementById('widthValue');

        if (fontSizeSlider) fontSizeSlider.value = settings.fontSize;
        if (fontSizeValue) fontSizeValue.textContent = `${settings.fontSize}px`;
        if (lineHeightSlider) lineHeightSlider.value = settings.lineHeight;
        if (lineHeightValue) lineHeightValue.textContent = settings.lineHeight;
        if (widthSlider) widthSlider.value = settings.maxWidth;
        if (widthValue) widthValue.textContent = `${settings.maxWidth}px`;

        // Update theme buttons
        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === settings.theme);
        });
    }
};

// Settings Panel
const SettingsPanel = {
    init() {
        this.panel = document.getElementById('settingsPanel');
        this.bindEvents();
        ReaderSettings.applySettings();
    },

    open() {
        this.panel?.classList.add('active');
        document.body.style.overflow = 'hidden';
    },

    close() {
        this.panel?.classList.remove('active');
        document.body.style.overflow = '';
    },

    bindEvents() {
        // Open/close settings
        document.getElementById('settingsBtn')?.addEventListener('click', () => this.open());
        document.getElementById('settingsClose')?.addEventListener('click', () => this.close());
        document.getElementById('settingsOverlay')?.addEventListener('click', () => this.close());

        // Font size slider
        document.getElementById('fontSizeSlider')?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            document.getElementById('fontSizeValue').textContent = `${value}px`;
            document.documentElement.style.setProperty('--reading-font-size', `${value}px`);
            ReaderSettings.saveSetting('fontSize', value);
        });

        // Line height slider
        document.getElementById('lineHeightSlider')?.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            document.getElementById('lineHeightValue').textContent = value.toFixed(1);
            document.documentElement.style.setProperty('--reading-line-height', value);
            ReaderSettings.saveSetting('lineHeight', value);
        });

        // Width slider
        document.getElementById('widthSlider')?.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            document.getElementById('widthValue').textContent = `${value}px`;
            document.documentElement.style.setProperty('--reading-max-width', `${value}px`);
            ReaderSettings.saveSetting('maxWidth', value);
        });

        // Theme options
        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const theme = btn.dataset.theme;
                document.documentElement.setAttribute('data-theme', theme);
                ReaderSettings.saveSetting('theme', theme);

                document.querySelectorAll('.theme-option').forEach(b => {
                    b.classList.toggle('active', b.dataset.theme === theme);
                });
            });
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
                TOCPanel.close();
            }
        });
    }
};

// Table of Contents Panel
const TOCPanel = {
    init() {
        this.sidebar = document.getElementById('tocSidebar');
        this.renderTOC();
        this.bindEvents();
    },

    open() {
        this.sidebar?.classList.add('active');
        document.body.style.overflow = 'hidden';
    },

    close() {
        this.sidebar?.classList.remove('active');
        document.body.style.overflow = '';
    },

    renderTOC() {
        const container = document.getElementById('tocList');
        if (!container || typeof chaptersData === 'undefined') return;

        const currentChapterId = ChapterReader.getCurrentChapterId();
        let html = '';

        chaptersData.chapters.forEach(chapter => {
            const isActive = chapter.id === currentChapterId;
            html += `
                <a href="reader.html?chapter=${chapter.id}" 
                   class="toc-item ${isActive ? 'active' : ''}">
                    <div class="toc-item-number">Chương ${chapter.id}</div>
                    <div class="toc-item-title">${chapter.title}</div>
                </a>
            `;
        });

        container.innerHTML = html;

        // Scroll to active chapter
        setTimeout(() => {
            container.querySelector('.toc-item.active')?.scrollIntoView({ block: 'center' });
        }, 100);
    },

    filterTOC(query) {
        const items = document.querySelectorAll('.toc-item');
        const normalizedQuery = query.toLowerCase().trim();

        items.forEach(item => {
            const title = item.querySelector('.toc-item-title').textContent.toLowerCase();
            const number = item.querySelector('.toc-item-number').textContent.toLowerCase();
            const matches = title.includes(normalizedQuery) || number.includes(normalizedQuery);
            item.style.display = matches ? '' : 'none';
        });
    },

    bindEvents() {
        document.getElementById('tocBtn')?.addEventListener('click', () => this.open());
        document.getElementById('tocClose')?.addEventListener('click', () => this.close());
        document.getElementById('tocOverlay')?.addEventListener('click', () => this.close());

        document.getElementById('tocSearch')?.addEventListener('input', (e) => {
            this.filterTOC(e.target.value);
        });
    }
};

// Progress Bar
const ProgressBar = {
    init() {
        this.fill = document.getElementById('progressFill');
        this.bindEvents();
    },

    update() {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = Math.min((scrollTop / docHeight) * 100, 100);

        if (this.fill) {
            this.fill.style.width = `${progress}%`;
        }

        return progress;
    },

    bindEvents() {
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.update();
                    ticking = false;
                });
                ticking = true;
            }
        });
    }
};

// Chapter Reader
const ChapterReader = {
    currentChapter: null,

    init() {
        const chapterId = this.getCurrentChapterId();
        if (chapterId) {
            this.loadChapter(chapterId);
        }
        this.bindEvents();
    },

    getCurrentChapterId() {
        const params = new URLSearchParams(window.location.search);
        return parseInt(params.get('chapter')) || null;
    },

    getChapterById(id) {
        if (typeof chaptersData === 'undefined') return null;
        return chaptersData.chapters.find(ch => ch.id === id);
    },

    getChapterIndex(id) {
        if (typeof chaptersData === 'undefined') return -1;
        return chaptersData.chapters.findIndex(ch => ch.id === id);
    },

    loadChapter(chapterId) {
        const chapter = this.getChapterById(chapterId);
        if (!chapter) {
            document.getElementById('chapterText').innerHTML = `
                <div class="loading-spinner">
                    <p>Không tìm thấy chương ${chapterId}</p>
                </div>
            `;
            return;
        }

        this.currentChapter = chapter;

        // Update page title
        document.title = `Chương ${chapter.id}: ${chapter.title} - Max Level Priest`;

        // Update header
        document.getElementById('chapterTitle').textContent = chapter.title;
        document.getElementById('chapterNumber').textContent = `Chương ${chapter.id}`;
        document.getElementById('volumeTag').textContent = `Volume ${chapter.volume}`;
        document.getElementById('chapterHeading').textContent = `Chương ${chapter.id}: ${chapter.title}`;

        // Render content
        const contentHtml = chapter.content
            .split('\n')
            .filter(p => p.trim())
            .map(p => `<p>${p}</p>`)
            .join('');

        document.getElementById('chapterText').innerHTML = contentHtml;

        // Update navigation
        this.updateNavigation(chapterId);

        // Save progress
        this.saveProgress(chapterId);

        // Scroll to top
        window.scrollTo(0, 0);

        // Update TOC active state
        TOCPanel.renderTOC();
    },

    updateNavigation(chapterId) {
        const index = this.getChapterIndex(chapterId);
        const prevBtn = document.getElementById('prevChapter');
        const nextBtn = document.getElementById('nextChapter');

        if (index > 0) {
            prevBtn.disabled = false;
            prevBtn.onclick = () => this.navigateToChapter(chaptersData.chapters[index - 1].id);
        } else {
            prevBtn.disabled = true;
            prevBtn.onclick = null;
        }

        if (index < chaptersData.chapters.length - 1) {
            nextBtn.disabled = false;
            nextBtn.onclick = () => this.navigateToChapter(chaptersData.chapters[index + 1].id);
        } else {
            nextBtn.disabled = true;
            nextBtn.onclick = null;
        }
    },

    navigateToChapter(chapterId) {
        window.history.pushState({}, '', `reader.html?chapter=${chapterId}`);
        this.loadChapter(chapterId);
    },

    saveProgress(chapterId) {
        try {
            const progress = {
                lastChapter: chapterId,
                lastRead: Date.now(),
                scrollPercent: 0
            };
            localStorage.setItem(`${BOOK_ID}_progress`, JSON.stringify(progress));
        } catch (e) {
            console.warn('Could not save progress:', e);
        }
    },

    bindEvents() {
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Don't navigate if typing in an input
            if (e.target.tagName === 'INPUT') return;

            const index = this.getChapterIndex(this.currentChapter?.id);
            if (index === -1) return;

            if (e.key === 'ArrowLeft' && index > 0) {
                this.navigateToChapter(chaptersData.chapters[index - 1].id);
            } else if (e.key === 'ArrowRight' && index < chaptersData.chapters.length - 1) {
                this.navigateToChapter(chaptersData.chapters[index + 1].id);
            }
        });

        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            const chapterId = this.getCurrentChapterId();
            if (chapterId) {
                this.loadChapter(chapterId);
            }
        });

        // Save scroll position periodically
        let saveTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                const progress = ProgressBar.update();
                if (this.currentChapter) {
                    try {
                        const saved = JSON.parse(localStorage.getItem(`${BOOK_ID}_progress`)) || {};
                        saved.scrollPercent = progress;
                        localStorage.setItem(`${BOOK_ID}_progress`, JSON.stringify(saved));
                    } catch (e) { }
                }
            }, 500);
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    SettingsPanel.init();
    TOCPanel.init();
    ProgressBar.init();
    ChapterReader.init();
});
