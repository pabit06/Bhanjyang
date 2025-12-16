/**
 * Analytics Dashboard Initialization and Helper Functions
 */

// Google Analytics event tracking functions
function trackAnalyticsEvent(action, category, label, value) {
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            'event_category': category,
            'event_label': label,
            'value': value
        });
    }
}

// Export analytics data
function exportAnalytics(format) {
    trackAnalyticsEvent('export', 'analytics', format, 1);

    const url = `/analytics/export/?format=${format}`;
    window.open(url, '_blank');
}

// Initialize analytics dashboard
document.addEventListener('DOMContentLoaded', function () {
    if (typeof initializeAnalyticsDashboard === 'function') {
        initializeAnalyticsDashboard();

        // Track page view once dashboard is initialized
        trackAnalyticsEvent('page_view', 'analytics_dashboard', 'dashboard_view', 1);
    } else {
        console.warn('initializeAnalyticsDashboard function not found. Make sure analytics_dashboard.js is loaded.');
    }

    if (typeof startRealTimeUpdates === 'function') {
        startRealTimeUpdates();
    }
});
