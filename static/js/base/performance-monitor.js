/**
 * Performance Monitoring JavaScript
 * Tracks page load times, errors, and user interactions
 */

class PerformanceMonitor {
    constructor() {
        this.startTime = performance.now();
        this.metrics = {};
        this.init();
    }

    init() {
        // Initialize session management
        this.initSession();
        
        // Track page load time
        window.addEventListener('load', () => {
            this.trackPageLoad();
            this.trackSessionHealth();
        });

        // Track errors
        window.addEventListener('error', (event) => {
            this.trackError(event);
            this.incrementSessionErrors();
        });

        // Track unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.trackError({
                message: event.reason?.message || 'Unhandled Promise Rejection',
                filename: 'Promise',
                lineno: 0,
                colno: 0,
                error: event.reason
            });
            this.incrementSessionErrors();
        });

        // Track form submissions
        document.addEventListener('submit', (event) => {
            this.trackFormSubmission(event);
        });

        // Track search queries
        document.addEventListener('input', (event) => {
            if (event.target.matches('input[type="search"], input[name="query"]')) {
                this.trackSearchQuery(event);
            }
        });

        // Track page visibility changes
        document.addEventListener('visibilitychange', () => {
            this.trackVisibilityChange();
        });

        // Track beforeunload for session cleanup
        window.addEventListener('beforeunload', () => {
            this.trackSessionEnd();
        });
    }

    trackPageLoad() {
        const loadTime = performance.now() - this.startTime;
        const navigation = performance.getEntriesByType('navigation')[0];
        
        const data = {
            page_url: window.location.href,
            page_title: document.title,
            load_time: Math.round(loadTime),
            referrer: document.referrer,
            is_mobile: this.isMobile(),
            browser: this.getBrowser(),
            os: this.getOS(),
            connection_type: this.getConnectionType(),
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            timing: {
                dom_content_loaded: navigation ? Math.round(navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart) : 0,
                first_paint: this.getFirstPaint(),
                first_contentful_paint: this.getFirstContentfulPaint()
            }
        };

        this.sendMetric('/dashboard/track/page-view/', data);
    }

    trackError(event) {
        const data = {
            error_type: 'javascript',
            error_message: event.message || 'Unknown error',
            page_url: window.location.href,
            stack_trace: event.error ? event.error.stack : '',
            additional_data: {
                filename: event.filename || '',
                lineno: event.lineno || 0,
                colno: event.colno || 0,
                user_agent: navigator.userAgent,
                timestamp: new Date().toISOString()
            }
        };

        this.sendMetric('/performance/track/error/', data);
    }

    trackFormSubmission(event) {
        const form = event.target;
        const startTime = performance.now();
        
        form.addEventListener('submit', () => {
            const submitTime = performance.now() - startTime;
            
            const data = {
                form_id: form.id || form.name || 'unknown',
                form_action: form.action,
                submit_time: Math.round(submitTime),
                field_count: form.elements.length,
                page_url: window.location.href
            };

            this.sendMetric('/dashboard/track/form-submit/', data);
        });
    }

    trackSearchQuery(event) {
        const query = event.target.value;
        if (query.length < 3) return; // Only track meaningful queries

        const startTime = performance.now();
        
        // Debounce search tracking
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            const searchTime = performance.now() - startTime;
            
            const data = {
                query: query,
                search_time: Math.round(searchTime),
                query_length: query.length,
                page_url: window.location.href
            };

            this.sendMetric('/dashboard/track/search/', data);
        }, 500);
    }

    trackImageLoad(imageElement) {
        const startTime = performance.now();
        
        imageElement.addEventListener('load', () => {
            const loadTime = performance.now() - startTime;
            
            const data = {
                image_src: imageElement.src,
                image_size: imageElement.naturalWidth * imageElement.naturalHeight,
                load_time: Math.round(loadTime),
                page_url: window.location.href
            };

            this.sendMetric('/dashboard/track/image-load/', data);
        });

        imageElement.addEventListener('error', () => {
            const data = {
                error_type: 'image_load',
                error_message: 'Failed to load image',
                image_src: imageElement.src,
                page_url: window.location.href
            };

            this.sendMetric('/performance/track/error/', data);
        });
    }

    trackCustomMetric(name, value, unit = 'ms') {
        const data = {
            metric_name: name,
            value: value,
            unit: unit,
            page_url: window.location.href,
            timestamp: new Date().toISOString()
        };

        this.sendMetric('/dashboard/track/custom-metric/', data);
    }

    sendMetric(url, data) {
        const csrfToken = this.getCSRFToken();
        
        // Only send if we have CSRF token or if it's a GET request
        if (!csrfToken && url.includes('/track/')) {
            console.warn('CSRF token not found, skipping performance tracking');
            return;
        }
        
        // Use sendBeacon for better reliability
        if (navigator.sendBeacon && csrfToken) {
            // For sendBeacon, we need to use FormData to include CSRF token
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', csrfToken);
            formData.append('data', JSON.stringify(data));
            navigator.sendBeacon(url, formData);
        } else if (csrfToken) {
            // Fallback to fetch
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            }).catch(error => {
                console.warn('Failed to send performance metric:', error);
            });
        }
    }

    initSession() {
        try {
            // Initialize session if not exists
            if (!sessionStorage.getItem('performance_session_id')) {
                this.getSessionId();
                sessionStorage.setItem('session_start', new Date().toISOString());
                sessionStorage.setItem('page_loads', '0');
                sessionStorage.setItem('session_errors', '0');
            }
        } catch (error) {
            console.warn('Session initialization failed:', error);
        }
    }

    getSessionId() {
        let sessionId = sessionStorage.getItem('performance_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('performance_session_id', sessionId);
        }
        return sessionId;
    }

    incrementSessionErrors() {
        try {
            const errors = parseInt(sessionStorage.getItem('session_errors') || '0') + 1;
            sessionStorage.setItem('session_errors', errors.toString());
        } catch (error) {
            console.warn('Failed to increment session errors:', error);
        }
    }

    trackSessionHealth() {
        try {
            const healthData = {
                session_id: this.getSessionId(),
                page_loads: parseInt(sessionStorage.getItem('page_loads') || '0') + 1,
                errors: parseInt(sessionStorage.getItem('session_errors') || '0'),
                start_time: sessionStorage.getItem('session_start') || new Date().toISOString(),
                current_url: window.location.href,
                user_agent: navigator.userAgent
            };
            
            sessionStorage.setItem('page_loads', healthData.page_loads.toString());
            
            // Send session health data every 5 page loads
            if (healthData.page_loads % 5 === 0) {
                this.sendMetric('/dashboard/track/session-health/', healthData);
            }
        } catch (error) {
            console.warn('Session health tracking failed:', error);
        }
    }

    trackVisibilityChange() {
        const visibilityData = {
            session_id: this.getSessionId(),
            visibility_state: document.visibilityState,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        this.sendMetric('/dashboard/track/visibility/', visibilityData);
    }

    trackSessionEnd() {
        try {
            const sessionData = {
                session_id: this.getSessionId(),
                duration: Date.now() - new Date(sessionStorage.getItem('session_start')).getTime(),
                page_loads: parseInt(sessionStorage.getItem('page_loads') || '0'),
                errors: parseInt(sessionStorage.getItem('session_errors') || '0'),
                end_time: new Date().toISOString()
            };
            
            // Use sendBeacon for reliable data transmission on page unload
            if (navigator.sendBeacon) {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
                if (csrfToken) {
                    const formData = new FormData();
                    formData.append('csrfmiddlewaretoken', csrfToken);
                    formData.append('data', JSON.stringify(sessionData));
                    navigator.sendBeacon('/dashboard/track/session-end/', formData);
                }
            }
        } catch (error) {
            console.warn('Session end tracking failed:', error);
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    getBrowser() {
        const userAgent = navigator.userAgent;
        if (userAgent.includes('Chrome')) return 'Chrome';
        if (userAgent.includes('Firefox')) return 'Firefox';
        if (userAgent.includes('Safari')) return 'Safari';
        if (userAgent.includes('Edge')) return 'Edge';
        if (userAgent.includes('Opera')) return 'Opera';
        return 'Unknown';
    }

    getOS() {
        const userAgent = navigator.userAgent;
        if (userAgent.includes('Windows')) return 'Windows';
        if (userAgent.includes('Mac')) return 'macOS';
        if (userAgent.includes('Linux')) return 'Linux';
        if (userAgent.includes('Android')) return 'Android';
        if (userAgent.includes('iOS')) return 'iOS';
        return 'Unknown';
    }

    getConnectionType() {
        if (navigator.connection) {
            return navigator.connection.effectiveType || 'unknown';
        }
        return 'unknown';
    }

    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
        return firstPaint ? Math.round(firstPaint.startTime) : 0;
    }

    getFirstContentfulPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstContentfulPaint = paintEntries.find(entry => entry.name === 'first-contentful-paint');
        return firstContentfulPaint ? Math.round(firstContentfulPaint.startTime) : 0;
    }

    // Public API for manual tracking
    static trackPageLoad() {
        if (window.performanceMonitor) {
            window.performanceMonitor.trackPageLoad();
        }
    }

    static trackError(error) {
        if (window.performanceMonitor) {
            window.performanceMonitor.trackError(error);
        }
    }

    static trackCustomMetric(name, value, unit) {
        if (window.performanceMonitor) {
            window.performanceMonitor.trackCustomMetric(name, value, unit);
        }
    }

    static trackImageLoad(imageElement) {
        if (window.performanceMonitor) {
            window.performanceMonitor.trackImageLoad(imageElement);
        }
    }
}

// Initialize performance monitoring
document.addEventListener('DOMContentLoaded', function() {
    window.performanceMonitor = new PerformanceMonitor();
    
    // Track all images
    document.querySelectorAll('img').forEach(img => {
        if (img.complete) {
            // Image already loaded
            PerformanceMonitor.trackImageLoad(img);
        } else {
            // Image still loading
            PerformanceMonitor.trackImageLoad(img);
        }
    });
});

// Export for use in other scripts
window.PerformanceMonitor = PerformanceMonitor;
