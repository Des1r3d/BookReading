/**
 * Library Page JavaScript
 * Handles theme for the main library page
 */

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
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === theme);
        });
    },

    bindEvents() {
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.setTheme(btn.dataset.theme);
            });
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});
