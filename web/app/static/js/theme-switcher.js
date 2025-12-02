/**
 * Konwerter SF - Theme Switcher
 * =============================
 * Obsługa przełączania motywów kolorystycznych
 */

const ThemeSwitcher = {
    themes: [
        { id: 'teal', name: 'Turkusowy', color: '#0d9488' },
        { id: 'ocean', name: 'Ocean', color: '#2563eb' },
        { id: 'purple', name: 'Fioletowy', color: '#7c3aed' },
        { id: 'sunset', name: 'Zachód słońca', color: '#ea580c' },
        { id: 'forest', name: 'Leśny', color: '#16a34a' },
        { id: 'rose', name: 'Różowy', color: '#e11d48' },
        { id: 'midnight', name: 'Północ', color: '#6366f1' },
        { id: 'dark', name: 'Ciemny', color: '#14b8a6' }
    ],

    currentTheme: 'teal',
    dropdownOpen: false,

    init() {
        // Wczytaj zapisany motyw z localStorage
        const savedTheme = localStorage.getItem('sf-theme');
        if (savedTheme && this.themes.find(t => t.id === savedTheme)) {
            this.currentTheme = savedTheme;
        }

        this.applyTheme(this.currentTheme);
        this.renderSwitcher();
        this.bindEvents();
    },

    applyTheme(themeId) {
        document.documentElement.setAttribute('data-theme', themeId);
        this.currentTheme = themeId;
        localStorage.setItem('sf-theme', themeId);

        // Update meta theme-color for mobile browsers
        const metaTheme = document.querySelector('meta[name="theme-color"]');
        const theme = this.themes.find(t => t.id === themeId);
        if (metaTheme && theme) {
            metaTheme.setAttribute('content', theme.color);
        }

        // Update active state in dropdown
        this.updateActiveState();
    },

    updateActiveState() {
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.toggle('active', option.dataset.theme === this.currentTheme);
        });
    },

    renderSwitcher() {
        const container = document.getElementById('theme-switcher');
        if (!container) return;

        const currentThemeData = this.themes.find(t => t.id === this.currentTheme);

        container.innerHTML = `
            <button class="theme-toggle" aria-label="Zmień motyw" title="Zmień motyw">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
            </button>
            <div class="theme-dropdown" id="theme-dropdown">
                ${this.themes.map(theme => `
                    <div class="theme-option ${theme.id === this.currentTheme ? 'active' : ''}" data-theme="${theme.id}">
                        <span class="theme-color" style="background-color: ${theme.color}"></span>
                        <span>${theme.name}</span>
                    </div>
                `).join('')}
            </div>
        `;
    },

    toggleDropdown() {
        this.dropdownOpen = !this.dropdownOpen;
        const dropdown = document.getElementById('theme-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('open', this.dropdownOpen);
        }
    },

    closeDropdown() {
        this.dropdownOpen = false;
        const dropdown = document.getElementById('theme-dropdown');
        if (dropdown) {
            dropdown.classList.remove('open');
        }
    },

    bindEvents() {
        // Toggle button
        document.addEventListener('click', (e) => {
            const toggle = e.target.closest('.theme-toggle');
            const dropdown = e.target.closest('.theme-dropdown');
            const option = e.target.closest('.theme-option');

            if (toggle) {
                e.preventDefault();
                this.toggleDropdown();
            } else if (option) {
                const themeId = option.dataset.theme;
                this.applyTheme(themeId);
                this.closeDropdown();
            } else if (!dropdown) {
                this.closeDropdown();
            }
        });

        // Keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDropdown();
            }
        });

        // Detect system preference changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                // Only auto-switch if user hasn't manually selected a theme
                if (!localStorage.getItem('sf-theme')) {
                    this.applyTheme(e.matches ? 'dark' : 'teal');
                }
            });
        }
    }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ThemeSwitcher.init());
} else {
    ThemeSwitcher.init();
}

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeSwitcher;
}
