/**
 * Dark Mode Utilities
 * Handles dark mode toggle and system preference detection
 */

class DarkMode {
    constructor() {
        this.htmlElement = document.documentElement;
        this.darkModeToggle = document.getElementById('darkModeToggle');
        this.prefersDarkQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        this.initialized = false;
    }

    /**
     * Initialize dark mode functionality
     */
    init() {
        if (this.initialized) return;
        
        // Set initial mode based on localStorage or system preference
        this._setInitialMode();
        
        // Add event listeners
        this._addEventListeners();
        
        this.initialized = true;
    }

    /**
     * Toggle dark mode
     */
    toggle() {
        if (this.htmlElement.classList.contains('dark')) {
            this.htmlElement.classList.remove('dark');
            localStorage.setItem('darkMode', 'false');
        } else {
            this.htmlElement.classList.add('dark');
            localStorage.setItem('darkMode', 'true');
        }
        
        // Dispatch event for other components to react
        window.dispatchEvent(new CustomEvent('darkmodechange', {
            detail: { isDarkMode: this.htmlElement.classList.contains('dark') }
        }));
    }

    /**
     * Check if dark mode is active
     * @returns {boolean} - True if dark mode is active
     */
    isDarkMode() {
        return this.htmlElement.classList.contains('dark');
    }

    /**
     * Set dark mode based on saved preference or system preference
     * @private
     */
    _setInitialMode() {
        const savedMode = localStorage.getItem('darkMode');
        
        if (savedMode === 'true') {
            this.htmlElement.classList.add('dark');
        } else if (savedMode === 'false') {
            this.htmlElement.classList.remove('dark');
        } else if (this.prefersDarkQuery.matches) {
            // No saved preference, use system preference
            this.htmlElement.classList.add('dark');
        }
    }

    /**
     * Add event listeners for dark mode toggle and system preference change
     * @private
     */
    _addEventListeners() {
        // Toggle button click
        if (this.darkModeToggle) {
            this.darkModeToggle.addEventListener('click', () => this.toggle());
        }
        
        // System preference change
        this.prefersDarkQuery.addEventListener('change', (e) => {
            // Only update if no user preference is saved
            if (!localStorage.getItem('darkMode')) {
                if (e.matches) {
                    this.htmlElement.classList.add('dark');
                } else {
                    this.htmlElement.classList.remove('dark');
                }
                
                // Dispatch event for other components to react
                window.dispatchEvent(new CustomEvent('darkmodechange', {
                    detail: { isDarkMode: this.htmlElement.classList.contains('dark') }
                }));
            }
        });
    }
}

// Initialize dark mode when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const darkMode = new DarkMode();
    darkMode.init();
    
    // Make available globally
    window.darkMode = darkMode;
});
