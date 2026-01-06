// Bulk Download Functionality
function updateSelection() {
    const checkboxes = document.querySelectorAll('.file-checkbox:checked');
    const count = checkboxes.length;
    const countElement = document.getElementById('selected-count');
    const downloadBtn = document.getElementById('bulk-download-btn');

    countElement.textContent = `${count} file${count !== 1 ? 's' : ''} selected`;
    downloadBtn.disabled = count === 0;

    if (count > 0) {
        downloadBtn.classList.remove('disabled:bg-gray-300', 'disabled:cursor-not-allowed');
        downloadBtn.classList.add('bg-deuraligreen', 'hover:bg-bhanjyangred');
    } else {
        downloadBtn.classList.add('disabled:bg-gray-300', 'disabled:cursor-not-allowed');
        downloadBtn.classList.remove('bg-deuraligreen', 'hover:bg-bhanjyangred');
    }
}

function selectAllFiles() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
    updateSelection();
}

function clearSelection() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    updateSelection();
}

function downloadSelected() {
    const checkboxes = document.querySelectorAll('.file-checkbox:checked');
    const fileIds = Array.from(checkboxes).map(checkbox => checkbox.getAttribute('data-file-id'));

    if (fileIds.length === 0) {
        alert('Please select at least one file to download.');
        return;
    }

    if (fileIds.length > 10) {
        if (!confirm(`You are about to download ${fileIds.length} files. This may take a while. Continue?`)) {
            return;
        }
    }

    // Track bulk download
    trackBulkDownload(fileIds.length);

    // Create form and submit
    const form = document.createElement('form');
    form.method = 'POST';

    const container = document.getElementById('downloadable-files');
    const bulkUrl = container ? container.dataset.bulkUrl : '/downloads/bulk/';
    form.action = bulkUrl;

    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken.value;
        form.appendChild(csrfInput);
    }

    // Add file IDs
    fileIds.forEach(fileId => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'file_ids';
        input.value = fileId;
        form.appendChild(input);
    });

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

// Initialize selection count on page load
document.addEventListener('DOMContentLoaded', function () {
    updateSelection();
});

function showMoreFiles(categoryCode) {
    // Get current URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('show_all', 'true');

    // Redirect to show all files
    window.location.href = '?' + urlParams.toString();
}

// Add smooth scroll animation for better UX
document.addEventListener('DOMContentLoaded', function () {
    // Add fade-in animation to category sections
    const categorySections = document.querySelectorAll('[id^="category-"]');
    categorySections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';

        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// ============================================================================
// PROGRESSIVE ENHANCEMENT: Service Worker
// ============================================================================

// Service Worker for offline support and caching
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function (registration) {
                console.log('✅ ServiceWorker registered with scope:', registration.scope);
            })
            .catch(function (error) {
                console.log('❌ ServiceWorker registration failed:', error);
            });
    });
}

// ============================================================================
// ANALYTICS: Track Downloads and User Behavior
// ============================================================================

// Track individual file downloads
function trackFileDownload(fileId, fileTitle) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'file_download', {
            'event_category': 'Downloads',
            'event_label': fileTitle,
            'file_id': fileId
        });
    }
}

// Track bulk downloads
function trackBulkDownload(fileCount) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'bulk_download', {
            'event_category': 'Downloads',
            'event_label': `${fileCount} files`,
            'value': fileCount
        });
    }
}

// Track search queries
function trackSearch(query) {
    if (typeof gtag !== 'undefined' && query) {
        gtag('event', 'search', {
            'event_category': 'Downloads',
            'search_term': query
        });
    }
}

// Track category filters
function trackCategoryFilter(category) {
    if (typeof gtag !== 'undefined' && category) {
        gtag('event', 'filter_category', {
            'event_category': 'Downloads',
            'event_label': category
        });
    }
}

// Auto-track search on form submission
document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.querySelector('form[role="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function () {
            const searchInput = searchForm.querySelector('input[name="q"]');
            if (searchInput && searchInput.value) {
                trackSearch(searchInput.value);
            }

            const categorySelect = searchForm.querySelector('select[name="category"]');
            if (categorySelect && categorySelect.value) {
                trackCategoryFilter(categorySelect.value);
            }
        });
    }
});

// ============================================================================
// UX ENHANCEMENTS: Loading States
// ============================================================================

// Show loading indicator during AJAX operations
function showLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'loading-indicator';
    indicator.className = 'fixed top-4 right-4 z-50 bg-white px-6 py-3 rounded-lg shadow-xl border-l-4 border-deuraligreen';
    indicator.innerHTML = `
        <div class="flex items-center space-x-3">
            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-deuraligreen"></div>
            <span class="text-gray-700 font-semibold">Loading...</span>
        </div>
    `;
    document.body.appendChild(indicator);
}

function hideLoadingIndicator() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// ============================================================================
// ACCESSIBILITY: Keyboard Navigation
// ============================================================================

// Add keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + K for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput && document.activeElement === searchInput) {
            searchInput.value = '';
            searchInput.blur();
        }
    }
});

console.log('✅ Downloads app enhanced with PWA, Analytics, and Accessibility features');
