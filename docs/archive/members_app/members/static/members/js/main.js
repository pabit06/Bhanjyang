// Main JavaScript for Member Management System

// Global variables
window.MemberPortal = {
    config: {
        apiBaseUrl: '/api/v1/',
        csrfToken: document.querySelector('[name=csrfmiddlewaretoken]')?.value,
        user: window.user || null,
        language: 'en'
    },
    utils: {},
    components: {},
    api: {}
};

// Utility functions
window.MemberPortal.utils = {
    // Format currency
    formatCurrency: function(amount, currency = 'NPR') {
        return new Intl.NumberFormat('en-NP', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(amount);
    },

    // Format date
    formatDate: function(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        return new Intl.DateTimeFormat('en-NP', { ...defaultOptions, ...options }).format(new Date(date));
    },

    // Format number
    formatNumber: function(number, decimals = 0) {
        return new Intl.NumberFormat('en-NP', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    },

    // Debounce function
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    },

    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Show loading state
    showLoading: function(element) {
        if (element) {
            element.classList.add('btn-loading');
            element.disabled = true;
        }
    },

    // Hide loading state
    hideLoading: function(element) {
        if (element) {
            element.classList.remove('btn-loading');
            element.disabled = false;
        }
    },

    // Show toast notification
    showToast: function(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toast-container') || this.createToastContainer();
        const toast = this.createToast(message, type);
        
        container.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            this.removeToast(toast);
        }, duration);
    },

    // Create toast container
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(container);
        return container;
    },

    // Create toast element
    createToast: function(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast-notification bg-white border-l-4 shadow-medium rounded-lg p-4 max-w-sm animate-slide-down ${
            type === 'error' ? 'border-danger-500' :
            type === 'warning' ? 'border-warning-500' :
            type === 'success' ? 'border-success-500' :
            'border-primary-500'
        }`;
        
        const icon = this.getToastIcon(type);
        
        toast.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    ${icon}
                </div>
                <div class="ml-3 flex-1">
                    <p class="text-sm font-medium text-gray-900">${message}</p>
                </div>
                <div class="ml-4 flex-shrink-0">
                    <button type="button" class="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600" onclick="MemberPortal.utils.removeToast(this.parentElement.parentElement.parentElement)">
                        <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        
        return toast;
    },

    // Get toast icon
    getToastIcon: function(type) {
        const icons = {
            error: '<svg class="h-5 w-5 text-danger-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
            warning: '<svg class="h-5 w-5 text-warning-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>',
            success: '<svg class="h-5 w-5 text-success-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
            info: '<svg class="h-5 w-5 text-primary-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>'
        };
        return icons[type] || icons.info;
    },

    // Remove toast
    removeToast: function(toast) {
        if (toast && toast.parentElement) {
            toast.classList.add('fade-out');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.parentElement.removeChild(toast);
                }
            }, 300);
        }
    },

    // Validate form
    validateForm: function(form) {
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });
        
        return isValid;
    },

    // Show field error
    showFieldError: function(field, message) {
        const fieldContainer = field.closest('.form-field');
        if (fieldContainer) {
            fieldContainer.classList.add('error');
            
            // Remove existing error message
            const existingError = fieldContainer.querySelector('.field-error');
            if (existingError) {
                existingError.remove();
            }
            
            // Add new error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error mt-1 text-sm text-danger-600';
            errorDiv.textContent = message;
            fieldContainer.appendChild(errorDiv);
        }
    },

    // Clear field error
    clearFieldError: function(field) {
        const fieldContainer = field.closest('.form-field');
        if (fieldContainer) {
            fieldContainer.classList.remove('error');
            const errorDiv = fieldContainer.querySelector('.field-error');
            if (errorDiv) {
                errorDiv.remove();
            }
        }
    },

    // Copy to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Copied to clipboard', 'success');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showToast('Copied to clipboard', 'success');
        }
    }
};

// API functions
window.MemberPortal.api = {
    // Make API request
    request: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.MemberPortal.config.csrfToken
            }
        };
        
        return fetch(url, { ...defaultOptions, ...options })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API request failed:', error);
                window.MemberPortal.utils.showToast('Request failed. Please try again.', 'error');
                throw error;
            });
    },

    // Get member data
    getMemberData: function() {
        return this.request('/api/v1/members/profile/');
    },

    // Get account data
    getAccountData: function() {
        return this.request('/api/v1/members/accounts/');
    },

    // Get transaction data
    getTransactionData: function(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/api/v1/members/transactions/?${queryString}`);
    },

    // Submit loan application
    submitLoanApplication: function(data) {
        return this.request('/api/v1/members/loans/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
};

// Form components
window.MemberPortal.components = {
    // Initialize form validation
    initFormValidation: function() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!window.MemberPortal.utils.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    },

    // Initialize file upload
    initFileUpload: function() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            const container = input.closest('.file-upload-container');
            if (container) {
                const dropZone = container.querySelector('.file-upload-area');
                if (dropZone) {
                    // Drag and drop functionality
                    dropZone.addEventListener('dragover', function(e) {
                        e.preventDefault();
                        dropZone.classList.add('dragover');
                    });
                    
                    dropZone.addEventListener('dragleave', function(e) {
                        e.preventDefault();
                        dropZone.classList.remove('dragover');
                    });
                    
                    dropZone.addEventListener('drop', function(e) {
                        e.preventDefault();
                        dropZone.classList.remove('dragover');
                        const files = e.dataTransfer.files;
                        if (files.length > 0) {
                            input.files = files;
                            this.updateFilePreview(input, files[0]);
                        }
                    });
                    
                    // Click to upload
                    dropZone.addEventListener('click', function() {
                        input.click();
                    });
                    
                    // File selection
                    input.addEventListener('change', function() {
                        if (this.files.length > 0) {
                            this.updateFilePreview(input, this.files[0]);
                        }
                    });
                }
            }
        });
    },

    // Update file preview
    updateFilePreview: function(input, file) {
        const container = input.closest('.file-upload-container');
        const preview = container.querySelector('.file-preview');
        
        if (preview) {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = `
                        <div class="file-preview-image">
                            <img src="${e.target.result}" alt="Preview" class="max-w-full max-h-32 rounded-lg">
                            <p class="mt-2 text-sm text-gray-600">${file.name}</p>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            } else {
                preview.innerHTML = `
                    <div class="file-preview-document">
                        <div class="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                        </div>
                        <p class="mt-2 text-sm text-gray-600">${file.name}</p>
                    </div>
                `;
            }
        }
    },

    // Initialize data tables
    initDataTables: function() {
        const tables = document.querySelectorAll('table[data-sortable]');
        tables.forEach(table => {
            this.makeTableSortable(table);
        });
    },

    // Make table sortable
    makeTableSortable: function(table) {
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const column = this.dataset.column;
                const currentSort = this.dataset.sort || 'asc';
                const newSort = currentSort === 'asc' ? 'desc' : 'asc';
                
                // Update all headers
                headers.forEach(h => {
                    h.dataset.sort = '';
                    h.classList.remove('sort-asc', 'sort-desc');
                });
                
                // Update current header
                this.dataset.sort = newSort;
                this.classList.add(`sort-${newSort}`);
                
                // Sort table
                window.MemberPortal.components.sortTable(table, column, newSort);
            });
        });
    },

    // Sort table
    sortTable: function(table, column, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aVal = a.querySelector(`td[data-column="${column}"]`)?.textContent || '';
            const bVal = b.querySelector(`td[data-column="${column}"]`)?.textContent || '';
            
            if (direction === 'asc') {
                return aVal.localeCompare(bVal);
            } else {
                return bVal.localeCompare(aVal);
            }
        });
        
        // Reorder rows
        rows.forEach(row => tbody.appendChild(row));
    },

    // Initialize charts
    initCharts: function() {
        // This will be implemented when Chart.js is loaded
        if (typeof Chart !== 'undefined') {
            this.initializeDashboardCharts();
        }
    },

    // Initialize dashboard charts
    initializeDashboardCharts: function() {
        // Balance trend chart
        const balanceCtx = document.getElementById('balanceChart');
        if (balanceCtx) {
            new Chart(balanceCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Account Balance',
                        data: [100000, 110000, 105000, 120000, 125000, 130000],
                        borderColor: '#0ea5e9',
                        backgroundColor: 'rgba(14, 165, 233, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return window.MemberPortal.utils.formatCurrency(value);
                                }
                            }
                        }
                    }
                }
            });
        }
    }
};

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    window.MemberPortal.components.initFormValidation();
    window.MemberPortal.components.initFileUpload();
    window.MemberPortal.components.initDataTables();
    window.MemberPortal.components.initCharts();
    
    // Initialize real-time updates
    window.MemberPortal.initRealTimeUpdates();
    
    // Initialize language switching
    window.MemberPortal.initLanguageSwitching();
    
    console.log('Member Portal initialized');
});

// Real-time updates
window.MemberPortal.initRealTimeUpdates = function() {
    // Simulate real-time balance updates
    setInterval(function() {
        // Update balance displays
        const balanceElements = document.querySelectorAll('.balance-display');
        balanceElements.forEach(element => {
            element.classList.add('animate-pulse');
            setTimeout(() => {
                element.classList.remove('animate-pulse');
            }, 1000);
        });
    }, 30000); // Update every 30 seconds
};

// Language switching
window.MemberPortal.initLanguageSwitching = function() {
    const languageToggle = document.querySelector('[data-language-toggle]');
    if (languageToggle) {
        languageToggle.addEventListener('click', function() {
            const currentLang = window.MemberPortal.config.language;
            const newLang = currentLang === 'en' ? 'ne' : 'en';
            window.MemberPortal.config.language = newLang;
            
            // Update UI elements
            document.documentElement.lang = newLang;
            
            // Show success message
            window.MemberPortal.utils.showToast(
                `Language switched to ${newLang === 'en' ? 'English' : 'Nepali'}`,
                'success'
            );
        });
    }
};

// Export for global access
window.MemberPortal = window.MemberPortal;
