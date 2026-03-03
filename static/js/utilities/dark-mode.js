// Dark Mode Implementation
// Apply theme immediately to prevent flash of light mode
(function() {
    const storageKey = 'theme-preference';
    const savedTheme = localStorage.getItem(storageKey);
    let initialTheme = 'light';
    
    if (savedTheme) {
        initialTheme = savedTheme;
    } else {
        // Default to light theme (project is "light" by default)
        initialTheme = 'light';
    }
    
    // Apply theme immediately
    document.documentElement.setAttribute('data-theme', initialTheme);
})();

class DarkMode {
    constructor() {
        this.theme = 'light';
        this.storageKey = 'theme-preference';
        this.init();
    }

    init() {
        this.loadTheme();
        this.createToggleButton();
        this.bindEvents();
        this.applyTheme();
        this.setupSystemThemeDetection();
    }

    loadTheme() {
        // Check localStorage first
        const savedTheme = localStorage.getItem(this.storageKey);
        if (savedTheme) {
            this.theme = savedTheme;
        } else {
            // Default to light theme
            this.theme = 'light';
        }
    }

    createToggleButton() {
        // Check if button already exists in header (desktop)
        let toggleButton = document.getElementById('theme-toggle-header');
        const themeIcon = document.getElementById('theme-icon');
        const themeIconMobile = document.getElementById('theme-icon-mobile');
        const mobileToggle = document.getElementById('theme-toggle-mobile');
        
        if (!toggleButton) {
            // Fallback: Create button if it doesn't exist in header
            toggleButton = document.createElement('button');
            toggleButton.id = 'theme-toggle-header';
            toggleButton.className = 'theme-toggle theme-toggle-fallback';
            toggleButton.setAttribute('aria-label', 'Toggle dark mode');
            toggleButton.innerHTML = this.getToggleIcon();
            document.body.appendChild(toggleButton);
        }
        
        // Update icons if they exist
        this.updateIcons();
        
        this.toggleButton = toggleButton;
    }

    getToggleIcon() {
        return this.theme === 'dark' ? 
            '<i class="fas fa-sun text-xl"></i>' : 
            '<i class="fas fa-moon text-xl"></i>';
    }

    updateIcons() {
        const themeIcon = document.getElementById('theme-icon');
        const themeIconMobile = document.getElementById('theme-icon-mobile');
        const themeIconMobileMenu = document.getElementById('theme-icon-mobile-menu');
        
        const iconClass = this.theme === 'dark' ? 
            'fas fa-sun text-xl' : 
            'fas fa-moon text-xl';
        
        if (themeIcon) {
            themeIcon.className = iconClass;
        }
        if (themeIconMobile) {
            themeIconMobile.className = iconClass;
        }
        if (themeIconMobileMenu) {
            themeIconMobileMenu.className = iconClass;
        }
    }

    bindEvents() {
        // Desktop toggle button click
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Mobile toggle button click (header)
        const mobileToggle = document.getElementById('theme-toggle-mobile');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Mobile menu toggle button click
        const mobileMenuToggle = document.getElementById('theme-toggle-mobile-menu');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Keyboard shortcut (Ctrl/Cmd + Shift + D)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }

    setupSystemThemeDetection() {
        // Listen for system theme changes
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            // Only update if user hasn't manually set a preference
            if (!localStorage.getItem(this.storageKey)) {
                this.theme = e.matches ? 'dark' : 'light';
                this.applyTheme();
            }
        });
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        this.applyTheme();
        this.saveTheme();
        this.animateToggle();
    }

    applyTheme() {
        // Update data attribute on html element
        document.documentElement.setAttribute('data-theme', this.theme);
        
        // Update toggle button icons
        this.updateIcons();
        
        // Update fallback button if it exists
        if (this.toggleButton && this.toggleButton.classList.contains('theme-toggle-fallback')) {
            this.toggleButton.innerHTML = this.getToggleIcon();
        }
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor();
        
        // Trigger custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: this.theme }
        }));
    }

    updateMetaThemeColor() {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        metaThemeColor.content = this.theme === 'dark' ? '#0f172a' : '#ffffff';
    }

    saveTheme() {
        localStorage.setItem(this.storageKey, this.theme);
    }

    animateToggle() {
        // Add animation class
        this.toggleButton.classList.add('theme-transition');
        
        // Remove after animation completes
        setTimeout(() => {
            this.toggleButton.classList.remove('theme-transition');
        }, 300);
    }

    // Public methods
    setTheme(theme) {
        if (theme === 'dark' || theme === 'light') {
            this.theme = theme;
            this.applyTheme();
            this.saveTheme();
        }
    }

    getTheme() {
        return this.theme;
    }

    isDark() {
        return this.theme === 'dark';
    }

    isLight() {
        return this.theme === 'light';
    }
}

// Theme-aware image optimization
class ThemeAwareImages {
    constructor() {
        this.init();
    }

    init() {
        // Listen for theme changes
        window.addEventListener('themeChanged', (e) => {
            this.updateImages(e.detail.theme);
        });
    }

    updateImages(theme) {
        const images = document.querySelectorAll('img[data-dark-src]');
        
        images.forEach(img => {
            if (theme === 'dark' && img.dataset.darkSrc) {
                img.src = img.dataset.darkSrc;
            } else if (theme === 'light' && img.dataset.lightSrc) {
                img.src = img.dataset.lightSrc;
            }
        });
    }
}

// Theme-aware charts and visualizations
class ThemeAwareCharts {
    constructor() {
        this.chartThemes = {
            light: {
                backgroundColor: '#ffffff',
                textColor: '#1e293b',
                gridColor: '#e2e8f0',
                primaryColor: '#059669',
                secondaryColor: '#10b981'
            },
            dark: {
                backgroundColor: '#0f172a',
                textColor: '#f1f5f9',
                gridColor: '#475569',
                primaryColor: '#10b981',
                secondaryColor: '#34d399'
            }
        };
        
        this.init();
    }

    init() {
        window.addEventListener('themeChanged', (e) => {
            this.updateCharts(e.detail.theme);
        });
    }

    updateCharts(theme) {
        const chartConfig = this.chartThemes[theme];
        
        // Update Chart.js charts if they exist
        if (window.Chart) {
            Chart.defaults.color = chartConfig.textColor;
            Chart.defaults.backgroundColor = chartConfig.backgroundColor;
            Chart.defaults.borderColor = chartConfig.gridColor;
        }
        
        // Trigger custom event for chart updates
        window.dispatchEvent(new CustomEvent('chartThemeChanged', {
            detail: { theme, config: chartConfig }
        }));
    }
}

// Theme persistence across tabs
class ThemeSync {
    constructor() {
        this.init();
    }

    init() {
        // Listen for storage changes from other tabs
        window.addEventListener('storage', (e) => {
            if (e.key === 'theme-preference' && e.newValue) {
                const theme = e.newValue;
                document.documentElement.setAttribute('data-theme', theme);
                
                // Update toggle button icons if they exist
                if (window.darkMode) {
                    window.darkMode.updateIcons();
                }
            }
        });
    }
}

// Initialize dark mode when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize dark mode
    window.darkMode = new DarkMode();
    
    // Initialize theme-aware components
    window.themeAwareImages = new ThemeAwareImages();
    window.themeAwareCharts = new ThemeAwareCharts();
    window.themeSync = new ThemeSync();
    
    // Add theme transition class to body for smooth transitions
    document.body.classList.add('theme-transition');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DarkMode, ThemeAwareImages, ThemeAwareCharts, ThemeSync };
}
