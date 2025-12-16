document.addEventListener('DOMContentLoaded', function () {
    const dashboard = new ErrorDashboard();
    dashboard.init();
});

class ErrorDashboard {
    constructor() {
        this.charts = {};
        this.refreshInterval = 30000; // 30 seconds
    }

    init() {
        this.initCharts();
        this.initEventListeners();
        this.startAutoRefresh();
        this.loadInitialData();
    }

    initCharts() {
        // Error Trends Chart
        const trendsCtx = document.getElementById('errorTrendsChart');
        if (trendsCtx) {
            this.charts.trends = new Chart(trendsCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Errors',
                        data: [],
                        borderColor: 'rgb(239, 68, 68)',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
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

        // Error Types Chart
        const typesCtx = document.getElementById('errorTypesChart');
        if (typesCtx) {
            this.charts.types = new Chart(typesCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            'rgba(239, 68, 68, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(139, 92, 246, 0.8)'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }

    initEventListeners() {
        // Chart button clicks
        document.querySelectorAll('.chart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.loadChartData(e.target.dataset.metric);
            });
        });

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            this.refreshData();
        }, this.refreshInterval);
    }

    async loadInitialData() {
        try {
            await this.loadChartData('error_trends');
            await this.loadChartData('error_types');
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadChartData(metricType) {
        const loadingEl = document.getElementById(metricType === 'error_types' || metricType === 'error_prone_pages' ? 'types-chart-loading' : 'chart-loading');
        if (loadingEl) loadingEl.classList.remove('hidden');

        try {
            const response = await fetch(`/dashboard/api/errors/?metric=${metricType}&days=7`);
            const data = await response.json();

            if (metricType === 'error_trends') {
                this.updateTrendsChart(data);
            } else if (metricType === 'error_types') {
                this.updateTypesChart(data);
            }
        } catch (error) {
            console.error(`Error loading ${metricType} data:`, error);
        } finally {
            if (loadingEl) loadingEl.classList.add('hidden');
        }
    }

    updateTrendsChart(data) {
        if (this.charts.trends) {
            this.charts.trends.data.labels = data.labels || [];
            this.charts.trends.data.datasets[0].data = data.data || [];
            this.charts.trends.update();
        }
    }

    updateTypesChart(data) {
        if (this.charts.types) {
            this.charts.types.data.labels = data.labels || [];
            this.charts.types.data.datasets[0].data = data.data || [];
            this.charts.types.update();
        }
    }

    async refreshData() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            await this.loadInitialData();
        } catch (error) {
            console.error('Error refreshing data:', error);
        } finally {
            if (refreshBtn) refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }
    }
}

// Error management functions
function resolveError(errorId) {
    if (confirm('Are you sure you want to mark this error as resolved?')) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';
        fetch(`/dashboard/alerts/${errorId}/resolve/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to resolve error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to resolve error');
            });
    }
}

function viewErrorDetails(errorId) {
    // This would open a modal or navigate to error details page
    console.log('View error details for:', errorId);
}
