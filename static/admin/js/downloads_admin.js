/**
 * Downloads Admin JavaScript
 * Enhanced functionality for the downloads admin interface
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // Initialize downloads admin functionality
    initDownloadsAdmin();
    
    // Initialize analytics dashboard
    initAnalyticsDashboard();
    
    // Initialize bulk actions
    initBulkActions();
    
    // Initialize file preview
    initFilePreview();
});

/**
 * Initialize downloads admin functionality
 */
function initDownloadsAdmin() {
    // Add file type icons to list view
    addFileTypeIcons();
    
    // Add priority indicators
    addPriorityIndicators();
    
    // Add status badges
    addStatusBadges();
    
    // Add download statistics
    addDownloadStatistics();
    
    // Add search functionality
    initSearchFunctionality();
    
    // Add filter functionality
    initFilterFunctionality();
}

/**
 * Add file type icons to the admin list
 */
function addFileTypeIcons() {
    const fileTypeCells = document.querySelectorAll('.field-file_type');
    
    fileTypeCells.forEach(cell => {
        const fileType = cell.textContent.trim().toLowerCase();
        const icon = getFileTypeIcon(fileType);
        
        if (icon) {
            cell.innerHTML = `<span class="file-type-icon file-type-${fileType}">${icon}</span>${fileType.toUpperCase()}`;
                        }
                    });
                }

/**
 * Get file type icon
 */
function getFileTypeIcon(fileType) {
    const icons = {
        'pdf': '📄',
        'doc': '📝',
        'docx': '📝',
        'xls': '📊',
        'xlsx': '📊',
        'ppt': '📽️',
        'pptx': '📽️',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'png': '🖼️',
        'txt': '📄'
    };
    
    return icons[fileType] || '📄';
}

/**
 * Add priority indicators
 */
function addPriorityIndicators() {
    const priorityCells = document.querySelectorAll('.field-priority');
    
    priorityCells.forEach(cell => {
        const priority = cell.textContent.trim().toLowerCase();
        const badge = createPriorityBadge(priority);
        
        if (badge) {
            cell.innerHTML = badge;
        }
    });
}

/**
 * Create priority badge
 */
function createPriorityBadge(priority) {
    const badges = {
        'urgent': '<span class="priority-badge priority-urgent">🚨 URGENT</span>',
        'high': '<span class="priority-badge priority-high">⬆️ HIGH</span>',
        'medium': '<span class="priority-badge priority-medium">➡️ MEDIUM</span>',
        'low': '<span class="priority-badge priority-low">⬇️ LOW</span>'
    };
    
    return badges[priority] || '';
}

/**
 * Add status badges
 */
function addStatusBadges() {
    const statusCells = document.querySelectorAll('.field-is_active, .field-is_featured, .field-requires_login');
    
    statusCells.forEach(cell => {
        const fieldName = cell.className.split(' ')[0].replace('field-', '');
        const value = cell.textContent.trim();
        
        if (value === 'True' || value === 'Yes') {
            const badge = createStatusBadge(fieldName);
            if (badge) {
                cell.innerHTML = badge;
            }
        }
    });
}

/**
 * Create status badge
 */
function createStatusBadge(fieldName) {
    const badges = {
        'is_active': '<span class="status-indicator status-active">✅ ACTIVE</span>',
        'is_featured': '<span class="status-indicator status-featured">⭐ FEATURED</span>',
        'requires_login': '<span class="status-indicator status-login-required">🔒 LOGIN REQUIRED</span>'
    };
    
    return badges[fieldName] || '';
}

/**
 * Add download statistics
 */
function addDownloadStatistics() {
    const downloadCountCells = document.querySelectorAll('.field-download_count');
    const viewCountCells = document.querySelectorAll('.field-view_count');
    
    downloadCountCells.forEach(cell => {
        const count = parseInt(cell.textContent.trim()) || 0;
        cell.innerHTML = `<div class="stat-item"><i class="fas fa-download"></i> ${count} downloads</div>`;
    });
    
    viewCountCells.forEach(cell => {
        const count = parseInt(cell.textContent.trim()) || 0;
        cell.innerHTML = `<div class="stat-item"><i class="fas fa-eye"></i> ${count} views</div>`;
    });
}

/**
 * Initialize search functionality
 */
function initSearchFunctionality() {
    const searchInput = document.querySelector('#searchbar');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            filterTableRows(query);
        });
    }
}

/**
 * Filter table rows based on search query
 */
function filterTableRows(query) {
    const rows = document.querySelectorAll('#result_list tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const matches = text.includes(query);
        
        row.style.display = matches ? '' : 'none';
    });
}

/**
 * Initialize filter functionality
 */
function initFilterFunctionality() {
    const filterSelects = document.querySelectorAll('select[name="category"], select[name="priority"]');
    
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            applyFilters();
        });
    });
}

/**
 * Apply filters to the table
 */
function applyFilters() {
    const categoryFilter = document.querySelector('select[name="category"]')?.value;
    const priorityFilter = document.querySelector('select[name="priority"]')?.value;
    
    const rows = document.querySelectorAll('#result_list tbody tr');
    
    rows.forEach(row => {
        let showRow = true;
        
        if (categoryFilter) {
            const categoryCell = row.querySelector('.field-category');
            if (categoryCell && !categoryCell.textContent.includes(categoryFilter)) {
                showRow = false;
            }
        }
        
        if (priorityFilter) {
            const priorityCell = row.querySelector('.field-priority');
            if (priorityCell && !priorityCell.textContent.includes(priorityFilter)) {
                showRow = false;
            }
        }
        
        row.style.display = showRow ? '' : 'none';
    });
}

/**
 * Initialize analytics dashboard
 */
function initAnalyticsDashboard() {
    // Add refresh functionality
    addRefreshButton();
    
    // Add export functionality
    addExportFunctionality();
    
    // Add real-time updates
    initRealTimeUpdates();
}

/**
 * Add refresh button to analytics
 */
function addRefreshButton() {
    const analyticsHeader = document.querySelector('.analytics-header');
    
    if (analyticsHeader) {
        const refreshButton = document.createElement('button');
        refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
        refreshButton.className = 'btn btn-primary';
        refreshButton.onclick = function() {
            location.reload();
        };
        
        analyticsHeader.appendChild(refreshButton);
    }
}

/**
 * Add export functionality
 */
function addExportFunctionality() {
    const exportButton = document.querySelector('.export-button');
    
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            exportAnalyticsData();
        });
    }
}

/**
 * Export analytics data
 */
function exportAnalyticsData() {
    const data = {
        totalFiles: document.querySelector('.stat-number').textContent,
        timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'downloads-analytics.json';
    a.click();
    
    URL.revokeObjectURL(url);
}

/**
 * Initialize real-time updates
 */
function initRealTimeUpdates() {
    // Update statistics every 30 seconds
    setInterval(updateStatistics, 30000);
}

/**
 * Update statistics
 */
function updateStatistics() {
    // This would typically make an AJAX request to get updated statistics
    console.log('Updating statistics...');
}

/**
 * Initialize bulk actions
 */
function initBulkActions() {
    const actionSelect = document.querySelector('select[name="action"]');
    
    if (actionSelect) {
        actionSelect.addEventListener('change', function() {
            if (this.value) {
                showBulkActionConfirmation(this.value);
            }
        });
    }
}

/**
 * Show bulk action confirmation
 */
function showBulkActionConfirmation(action) {
    const selectedCount = document.querySelectorAll('input[name="_selected_action"]:checked').length;
    
    if (selectedCount === 0) {
        alert('Please select at least one file to perform this action.');
        return;
    }
    
    const actionNames = {
        'mark_as_featured': 'mark as featured',
        'mark_as_not_featured': 'remove featured status',
        'activate_files': 'activate',
        'deactivate_files': 'deactivate',
        'set_high_priority': 'set to high priority',
        'set_urgent_priority': 'set to urgent priority'
    };
    
    const actionName = actionNames[action] || action;
    const confirmed = confirm(`Are you sure you want to ${actionName} ${selectedCount} file(s)?`);
    
    if (confirmed) {
        document.querySelector('form').submit();
    }
}

/**
 * Initialize file preview
 */
function initFilePreview() {
    const fileLinks = document.querySelectorAll('a[href*="/downloads/"]');
    
    fileLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const fileType = getFileTypeFromUrl(this.href);
            
            if (fileType === 'pdf' || fileType === 'jpg' || fileType === 'png') {
                e.preventDefault();
                showFilePreview(this.href, fileType);
            }
        });
    });
}

/**
 * Get file type from URL
 */
function getFileTypeFromUrl(url) {
    const extension = url.split('.').pop().toLowerCase();
    return extension;
}

/**
 * Show file preview
 */
function showFilePreview(url, fileType) {
    const modal = document.createElement('div');
    modal.className = 'file-preview-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <iframe src="${url}" width="100%" height="600px"></iframe>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close modal when clicking X
    modal.querySelector('.close').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

/**
 * Utility function to format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Utility function to format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

/**
 * Add loading states
 */
function addLoadingState(element) {
    element.classList.add('loading-skeleton');
}

/**
 * Remove loading states
 */
function removeLoadingState(element) {
    element.classList.remove('loading-skeleton');
}

// Export functions for global access
window.DownloadsAdmin = {
    initDownloadsAdmin,
    initAnalyticsDashboard,
    initBulkActions,
    initFilePreview,
    formatFileSize,
    formatDate,
    addLoadingState,
    removeLoadingState
};