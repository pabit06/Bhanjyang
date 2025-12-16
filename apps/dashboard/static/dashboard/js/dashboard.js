document.addEventListener('DOMContentLoaded', function () {
    // Initialize dashboard
    const dashboard = new DashboardManager();
    dashboard.init();
});

class DashboardManager {
    constructor() {
        this.charts = {};
        this.refreshInterval = 30000; // 30 seconds
        this.isDarkMode = false;
        this.filters = {
            timeRange: '7d',
            deviceType: '',
            browser: ''
        };
    }

    init() {
        this.initCharts();
        this.initEventListeners();
        this.startAutoRefresh();
        this.loadInitialData();
    }

    initCharts() {
        // Performance Chart
        const perfCtx = document.getElementById('performanceChart');
        if (perfCtx) {
            this.charts.performance = new Chart(perfCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Load Time (ms)',
                        data: [],
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
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
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        }
                    }
                }
            });
        }

        // Error Chart
        const errorCtx = document.getElementById('errorChart');
        if (errorCtx) {
            this.charts.error = new Chart(errorCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Errors',
                        data: [],
                        backgroundColor: 'rgba(239, 68, 68, 0.8)',
                        borderColor: 'rgb(239, 68, 68)',
                        borderWidth: 1
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
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        }
                    }
                }
            });
        }
    }

    initEventListeners() {
        // Theme toggle
        const themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // Filter controls
        const applyBtn = document.getElementById('apply-filters');
        if (applyBtn) {
            applyBtn.addEventListener('click', () => {
                this.applyFilters();
            });
        }

        // Chart buttons
        document.querySelectorAll('.chart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchChartMetric(e.target.dataset.metric);
            });
        });
    }

    async loadInitialData() {
        try {
            await this.loadChartData('page_load');
            await this.loadChartData('errors');
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadChartData(metricType) {
        const loadingEl = document.getElementById(metricType === 'errors' ? 'error-chart-loading' : 'chart-loading');
        if (loadingEl) loadingEl.classList.remove('hidden');

        try {
            const response = await fetch(`/dashboard/api/?type=${metricType}&days=7`);
            const data = await response.json();

            if (metricType === 'page_load') {
                this.updatePerformanceChart(data);
            } else if (metricType === 'errors') {
                this.updateErrorChart(data);
            }
        } catch (error) {
            console.error(`Error loading ${metricType} data:`, error);
        } finally {
            if (loadingEl) loadingEl.classList.add('hidden');
        }
    }

    updatePerformanceChart(data) {
        if (this.charts.performance && data.labels && data.data) {
            this.charts.performance.data.labels = data.labels;
            this.charts.performance.data.datasets[0].data = data.data;
            this.charts.performance.update();
        }
    }

    updateErrorChart(data) {
        if (this.charts.error && data.labels && data.data) {
            this.charts.error.data.labels = data.labels;
            this.charts.error.data.datasets[0].data = data.data;
            this.charts.error.update();
        }
    }

    async refreshData() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            await this.loadInitialData();
            this.updateMetricCards();
        } catch (error) {
            console.error('Error refreshing data:', error);
        } finally {
            if (refreshBtn) refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }
    }

    updateMetricCards() {
        // Update metric cards with real-time data
        // This would typically fetch fresh data and update the DOM
        console.log('Updating metric cards...');
    }

    applyFilters() {
        const timeRange = document.getElementById('time-range');
        const deviceFilter = document.getElementById('device-filter');
        const browserFilter = document.getElementById('browser-filter');

        if (timeRange) this.filters.timeRange = timeRange.value;
        if (deviceFilter) this.filters.deviceType = deviceFilter.value;
        if (browserFilter) this.filters.browser = browserFilter.value;

        this.refreshData();
    }

    switchChartMetric(metric) {
        document.querySelectorAll('.chart-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        if (event && event.target) {
            event.target.classList.add('active');
        }

        this.loadChartData(metric);
    }

    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        const container = document.getElementById('dashboard-container');
        const themeBtn = document.getElementById('theme-toggle');

        if (this.isDarkMode) {
            container.classList.add('dark-mode');
            themeBtn.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            container.classList.remove('dark-mode');
            themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            this.refreshData();
        }, this.refreshInterval);
    }
}
