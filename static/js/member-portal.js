/**
 * Member Portal JavaScript
 * 
 * Main JavaScript functionality for the Bhanjyang Cooperative Member Portal
 * Includes Alpine.js data, animations, and interactive features
 */

// Alpine.js data for member portal
function memberPortal() {
    return {
        // State
        loading: false,
        darkMode: localStorage.getItem('theme') === 'dark',
        mobileMenuOpen: false,
        notifications: [],
        unreadNotifications: 0,
        user: {
            first_name: '{{ user.first_name|default:"" }}',
            last_name: '{{ user.last_name|default:"" }}',
            email: '{{ user.email|default:"" }}',
            profile_photo: '{{ user.member_profile.profile_photo.url|default:"" }}'
        },

        // Initialize
        init() {
            this.loadNotifications();
            this.setupTheme();
            this.setupAnimations();
            this.setupKeyboardShortcuts();
        },

        // Theme management
        setupTheme() {
            if (this.darkMode) {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
            }
        },

        toggleTheme() {
            this.darkMode = !this.darkMode;
            localStorage.setItem('theme', this.darkMode ? 'dark' : 'light');
            this.setupTheme();
            
            // Animate theme transition
            gsap.to(document.documentElement, {
                duration: 0.3,
                ease: "power2.inOut"
            });
        },

        // Notifications
        async loadNotifications() {
            try {
                const response = await fetch('/members/api/notifications/');
                const data = await response.json();
                this.notifications = data.notifications || [];
                this.unreadNotifications = data.unread_count || 0;
            } catch (error) {
                console.error('Failed to load notifications:', error);
            }
        },

        async markAsRead(notificationId) {
            try {
                await fetch(`/members/api/notifications/${notificationId}/mark-read/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                        'Content-Type': 'application/json'
                    }
                });
                
                const notification = this.notifications.find(n => n.id === notificationId);
                if (notification) {
                    notification.is_read = true;
                    this.unreadNotifications = Math.max(0, this.unreadNotifications - 1);
                }
            } catch (error) {
                console.error('Failed to mark notification as read:', error);
            }
        },

        async markAllAsRead() {
            try {
                await fetch('/members/api/notifications/mark-all-read/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                        'Content-Type': 'application/json'
                    }
                });
                
                this.notifications.forEach(notification => {
                    notification.is_read = true;
                });
                this.unreadNotifications = 0;
            } catch (error) {
                console.error('Failed to mark all notifications as read:', error);
            }
        },

        // Animations
        setupAnimations() {
            // Animate stat cards on scroll
            gsap.registerPlugin(ScrollTrigger);
            
            gsap.utils.toArray('.stat-card').forEach(card => {
                gsap.fromTo(card, 
                    { 
                        opacity: 0, 
                        y: 50,
                        scale: 0.9
                    },
                    {
                        opacity: 1,
                        y: 0,
                        scale: 1,
                        duration: 0.6,
                        ease: "back.out(1.7)",
                        scrollTrigger: {
                            trigger: card,
                            start: "top 80%",
                            toggleActions: "play none none reverse"
                        }
                    }
                );
            });

            // Animate cards on scroll
            gsap.utils.toArray('.card').forEach(card => {
                gsap.fromTo(card,
                    { 
                        opacity: 0, 
                        y: 30
                    },
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.5,
                        ease: "power2.out",
                        scrollTrigger: {
                            trigger: card,
                            start: "top 85%",
                            toggleActions: "play none none reverse"
                        }
                    }
                );
            });

            // Animate page transitions
            gsap.fromTo('.page-content',
                { 
                    opacity: 0, 
                    y: 20
                },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.4,
                    ease: "power2.out"
                }
            );
        },

        // Keyboard shortcuts
        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + K for search
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    this.openSearch();
                }
                
                // Escape to close modals/dropdowns
                if (e.key === 'Escape') {
                    this.closeAllDropdowns();
                }
                
                // Ctrl/Cmd + D for dark mode toggle
                if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                    e.preventDefault();
                    this.toggleTheme();
                }
            });
        },

        // Utility functions
        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        },

        openSearch() {
            // Implement search functionality
            Toast.info('Search functionality coming soon!');
        },

        closeAllDropdowns() {
            // Close all open dropdowns
            this.mobileMenuOpen = false;
        },

        // Loading states
        showLoading() {
            this.loading = true;
        },

        hideLoading() {
            this.loading = false;
        },

        // Form submission with loading
        async submitForm(formElement, url, options = {}) {
            this.showLoading();
            
            try {
                const formData = new FormData(formElement);
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    ...options
                });
                
                if (response.ok) {
                    const data = await response.json();
                    Toast.success(data.message || 'Operation completed successfully!');
                    return data;
                } else {
                    const error = await response.json();
                    Toast.error(error.message || 'An error occurred');
                    throw new Error(error.message);
                }
            } catch (error) {
                Toast.error('Network error occurred');
                throw error;
            } finally {
                this.hideLoading();
            }
        },

        // AJAX requests
        async makeRequest(url, options = {}) {
            try {
                const response = await fetch(url, {
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error('Request failed:', error);
                Toast.error('Request failed. Please try again.');
                throw error;
            }
        },

        // Format currency
        formatCurrency(amount) {
            return new Intl.NumberFormat('en-NP', {
                style: 'currency',
                currency: 'NPR',
                minimumFractionDigits: 2
            }).format(amount);
        },

        // Format date
        formatDate(dateString) {
            return new Date(dateString).toLocaleDateString('en-NP', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        },

        // Format date and time
        formatDateTime(dateString) {
            return new Date(dateString).toLocaleString('en-NP', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        // Copy to clipboard
        async copyToClipboard(text) {
            try {
                await navigator.clipboard.writeText(text);
                Toast.success('Copied to clipboard!');
            } catch (error) {
                console.error('Failed to copy:', error);
                Toast.error('Failed to copy to clipboard');
            }
        },

        // Download file
        downloadFile(url, filename) {
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },

        // Print page
        printPage() {
            window.print();
        },

        // Refresh data
        async refreshData() {
            this.showLoading();
            try {
                await this.loadNotifications();
                // Add other data refresh calls here
                Toast.success('Data refreshed successfully!');
            } catch (error) {
                Toast.error('Failed to refresh data');
            } finally {
                this.hideLoading();
            }
        }
    };
}

// Global utility functions
window.MemberPortal = {
    // Format helpers
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-NP', {
            style: 'currency',
            currency: 'NPR',
            minimumFractionDigits: 2
        }).format(amount);
    },

    formatDate: (dateString) => {
        return new Date(dateString).toLocaleDateString('en-NP', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    formatDateTime: (dateString) => {
        return new Date(dateString).toLocaleString('en-NP', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Animation helpers
    animateIn: (element, delay = 0) => {
        gsap.fromTo(element, 
            { 
                opacity: 0, 
                y: 30,
                scale: 0.95
            },
            {
                opacity: 1,
                y: 0,
                scale: 1,
                duration: 0.5,
                delay: delay,
                ease: "power2.out"
            }
        );
    },

    animateOut: (element, callback) => {
        gsap.to(element, {
            opacity: 0,
            y: -30,
            scale: 0.95,
            duration: 0.3,
            ease: "power2.in",
            onComplete: callback
        });
    },

    // Scroll to element
    scrollToElement: (element, offset = 0) => {
        const targetPosition = element.offsetTop - offset;
        gsap.to(window, {
            duration: 0.8,
            scrollTo: { y: targetPosition, autoKill: false },
            ease: "power2.inOut"
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling
    gsap.registerPlugin(ScrollToPlugin);
    
    // Initialize tooltips (if using a tooltip library)
    // Initialize other global features
    
    console.log('Member Portal initialized');
});
