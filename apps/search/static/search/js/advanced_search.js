// Advanced Search Functionality
class AdvancedSearch {
    constructor() {
        this.searchInput = document.getElementById('search-input');
        this.suggestionsContainer = document.getElementById('search-suggestions');
        this.searchForm = document.querySelector('.search-form');
        this.debounceTimer = null;

        this.init();
    }

    init() {
        if (!this.searchInput || !this.searchForm) return;
        this.bindEvents();
    }

    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        this.searchInput.addEventListener('focus', () => {
            this.showSuggestions();
        });

        this.searchInput.addEventListener('blur', () => {
            // Delay hiding to allow clicking on suggestions
            setTimeout(() => this.hideSuggestions(), 200);
        });

        // Form submission
        this.searchForm.addEventListener('submit', (e) => {
            this.trackSearch();
        });

        // Search tips modal
        const tipsBtn = document.getElementById('search-tips-btn');
        const tipsModal = document.getElementById('search-tips-modal');
        const closeTipsBtn = document.getElementById('close-tips-modal');

        if (tipsBtn && tipsModal) {
            tipsBtn.addEventListener('click', () => {
                tipsModal.classList.remove('hidden');
            });

            closeTipsBtn.addEventListener('click', () => {
                tipsModal.classList.add('hidden');
            });

            tipsModal.addEventListener('click', (e) => {
                if (e.target === tipsModal) {
                    tipsModal.classList.add('hidden');
                }
            });
        }
    }

    handleSearchInput(query) {
        clearTimeout(this.debounceTimer);

        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }

        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300);
    }

    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/search/api/?q=${encodeURIComponent(query)}&limit=5`);
            const data = await response.json();

            if (data.suggestions) {
                this.displaySuggestions(data.suggestions);
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }

    displaySuggestions(suggestions) {
        if (!this.suggestionsContainer) return;

        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        const html = suggestions.map(suggestion => `
            <div class="suggestion-item p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0" 
                 data-suggestion="${suggestion.text}">
                <div class="flex items-center">
                    <i class="fas fa-search text-gray-400 mr-3"></i>
                    <div>
                        <div class="font-medium">${suggestion.text}</div>
                        <div class="text-sm text-gray-500">${suggestion.type}</div>
                    </div>
                </div>
            </div>
        `).join('');

        this.suggestionsContainer.innerHTML = html;
        this.showSuggestions();

        // Bind suggestion clicks
        this.suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const suggestion = item.dataset.suggestion;
                this.searchInput.value = suggestion;
                this.hideSuggestions();
                this.searchForm.submit();
            });
        });
    }

    showSuggestions() {
        if (this.suggestionsContainer) {
            this.suggestionsContainer.classList.remove('hidden');
        }
    }

    hideSuggestions() {
        if (this.suggestionsContainer) {
            this.suggestionsContainer.classList.add('hidden');
        }
    }

    trackSearch() {
        const query = this.searchInput.value.trim();
        if (query) {
            // Track search analytics
            console.log('Search tracked:', query);
        }
    }
}

// Initialize search when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.advancedSearch = new AdvancedSearch();
});
