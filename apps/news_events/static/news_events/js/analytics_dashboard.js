// Analytics Dashboard JavaScript

class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        this.isInitialized = false;
        this.urls = this.getApiUrls();
    }

    getApiUrls() {
        const config = document.getElementById('analytics-config');
        if (!config) {
            console.error('Analytics config element not found');
            return {};
        }
        return {
            metrics: config.dataset.metricsUrl,
            traffic: config.dataset.trafficUrl,
            contentPerformance: config.dataset.contentPerformanceUrl,
            userDemographics: config.dataset.userDemographicsUrl,
            deviceUsage: config.dataset.deviceUsageUrl,
            topArticles: config.dataset.topArticlesUrl,
            topEvents: config.dataset.topEventsUrl
        };
    }

    async initialize() {
        try {
            await this.loadRealTimeMetrics();
            await this.initializeCharts();
            await this.loadTopContent();
            this.startRealTimeUpdates();
            this.isInitialized = true;
        } catch (error) {
            console.error('Failed to initialize analytics dashboard:', error);
        }
    }

    async loadRealTimeMetrics() {
        try {
            if (!this.urls.metrics) {
                throw new Error('Metrics URL not configured');
            }
            const response = await fetch(this.urls.metrics);
            const data = await response.json();
            
            this.updateMetricDisplay('active-users', data.active_users);
            this.updateMetricDisplay('page-views', data.page_views);
            this.updateMetricDisplay('bounce-rate', data.bounce_rate + '%');
            this.updateMetricDisplay('avg-session', data.avg_session_duration + 'm');
            
            this.updateMetricChange('active-users-change', data.active_users_change);
            this.updateMetricChange('page-views-change', data.page_views_change);
            this.updateMetricChange('bounce-rate-change', data.bounce_rate_change);
            this.updateMetricChange('avg-session-change', data.avg_session_change);
        } catch (error) {
            console.error('Failed to load real-time metrics:', error);
        }
    }

    updateMetricDisplay(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    updateMetricChange(elementId, change) {
        const element = document.getElementById(elementId);
        if (element) {
            const isPositive = change >= 0;
            element.textContent = (isPositive ? '+' : '') + change + '%';
            element.className = `text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`;
        }
    }

    async initializeCharts() {
        await this.createTrafficSourcesChart();
        await this.createContentPerformanceChart();
        await this.createUserDemographicsChart();
        await this.createDeviceUsageChart();
    }

    async createTrafficSourcesChart() {
        try {
            if (!this.urls.traffic) {
                throw new Error('Traffic sources URL not configured');
            }
            const response = await fetch(this.urls.traffic);
            const data = await response.json();
            
            const ctx = document.getElementById('trafficSourcesChart').getContext('2d');
            this.charts.trafficSources = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [
                            '#dc2626', // red
                            '#059669', // green
                            '#2563eb', // blue
                            '#7c3aed', // purple
                            '#ea580c'  // orange
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Failed to create traffic sources chart:', error);
        }
    }

    async createContentPerformanceChart() {
        try {
            if (!this.urls.contentPerformance) {
                throw new Error('Content performance URL not configured');
            }
            const response = await fetch(this.urls.contentPerformance);
            const data = await response.json();
            
            const ctx = document.getElementById('contentPerformanceChart').getContext('2d');
            this.charts.contentPerformance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Views',
                        data: data.views,
                        backgroundColor: '#059669',
                        borderColor: '#047857',
                        borderWidth: 1
                    }, {
                        label: 'Shares',
                        data: data.shares,
                        backgroundColor: '#dc2626',
                        borderColor: '#b91c1c',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Failed to create content performance chart:', error);
        }
    }

    async createUserDemographicsChart() {
        try {
            if (!this.urls.userDemographics) {
                throw new Error('User demographics URL not configured');
            }
            const response = await fetch(this.urls.userDemographics);
            const data = await response.json();
            
            const ctx = document.getElementById('userDemographicsChart').getContext('2d');
            this.charts.userDemographics = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [
                            '#dc2626',
                            '#059669',
                            '#2563eb',
                            '#7c3aed'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Failed to create user demographics chart:', error);
        }
    }

    async createDeviceUsageChart() {
        try {
            if (!this.urls.deviceUsage) {
                throw new Error('Device usage URL not configured');
            }
            const response = await fetch(this.urls.deviceUsage);
            const data = await response.json();
            
            const ctx = document.getElementById('deviceUsageChart').getContext('2d');
            this.charts.deviceUsage = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [
                            '#059669',
                            '#dc2626',
                            '#2563eb'
                        ],
                        borderWidth: 1,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Failed to create device usage chart:', error);
        }
    }

    async loadTopContent() {
        try {
            // Load top articles
            if (!this.urls.topArticles) {
                throw new Error('Top articles URL not configured');
            }
            const articlesResponse = await fetch(this.urls.topArticles);
            const articlesData = await articlesResponse.json();
            this.renderTopContent('top-articles', articlesData, 'article');

            // Load top events
            if (!this.urls.topEvents) {
                throw new Error('Top events URL not configured');
            }
            const eventsResponse = await fetch(this.urls.topEvents);
            const eventsData = await eventsResponse.json();
            this.renderTopContent('top-events', eventsData, 'event');
        } catch (error) {
            console.error('Failed to load top content:', error);
        }
    }

    renderTopContent(containerId, data, type) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        
        data.forEach((item, index) => {
            const itemElement = document.createElement('div');
            itemElement.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';
            
            itemElement.innerHTML = `
                <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-bhanjyangred text-white rounded-full flex items-center justify-center text-sm font-bold">
                        ${index + 1}
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900 line-clamp-1">${item.title}</h4>
                        <p class="text-sm text-gray-600">${item.category}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-sm font-semibold text-bhanjyangred">${item.views}</p>
                    <p class="text-xs text-gray-600">views</p>
                </div>
            `;
            
            container.appendChild(itemElement);
        });
    }

    startRealTimeUpdates() {
        // Update metrics every 30 seconds
        this.updateInterval = setInterval(() => {
            this.loadRealTimeMetrics();
        }, 30000);
    }

    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    destroy() {
        this.stopRealTimeUpdates();
        
        // Destroy all charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.isInitialized = false;
    }
}

// Global analytics dashboard instance
let analyticsDashboard = null;

// Initialize analytics dashboard
function initializeAnalyticsDashboard() {
    if (!analyticsDashboard) {
        analyticsDashboard = new AnalyticsDashboard();
        analyticsDashboard.initialize();
    }
}

// Start real-time updates
function startRealTimeUpdates() {
    if (analyticsDashboard && analyticsDashboard.isInitialized) {
        analyticsDashboard.startRealTimeUpdates();
    }
}

// Stop real-time updates
function stopRealTimeUpdates() {
    if (analyticsDashboard) {
        analyticsDashboard.stopRealTimeUpdates();
    }
}

// Export analytics data
function exportAnalytics(format) {
    // Note: If you have an export URL, add it to analytics-config data attributes
    // For now, using relative path - update if export endpoint is added
    const url = `/news-events/analytics/export/?format=${format}`;
    window.open(url, '_blank');
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (analyticsDashboard) {
        analyticsDashboard.destroy();
    }
});

// Handle visibility change to pause/resume updates
document.addEventListener('visibilitychange', () => {
    if (analyticsDashboard) {
        if (document.hidden) {
            analyticsDashboard.stopRealTimeUpdates();
        } else {
            analyticsDashboard.startRealTimeUpdates();
        }
    }
});
