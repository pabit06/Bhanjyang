document.addEventListener('DOMContentLoaded', function () {
    const dashboard = new AnalyticsDashboard();
    dashboard.init();
});

class AnalyticsDashboard {
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
        // Traffic Chart
        const trafficCtx = document.getElementById('trafficChart');
        if (trafficCtx) {
            this.charts.traffic = new Chart(trafficCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Page Views',
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

        // Device Chart
        const deviceCtx = document.getElementById('deviceChart');
        if (deviceCtx) {
            this.charts.device = new Chart(deviceCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(239, 68, 68, 0.8)',
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
            await this.loadChartData('page_views');
            await this.loadChartData('devices');
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadChartData(metricType) {
        const loadingEl = document.getElementById(metricType === 'devices' || metricType === 'browsers' ? 'device-chart-loading' : 'chart-loading');
        if (loadingEl) loadingEl.classList.remove('hidden');

        try {
            const response = await fetch(`/dashboard/api/analytics/?metric=${metricType}&days=7`);
            const data = await response.json();

            if (metricType === 'page_views' || metricType === 'sessions') {
                this.updateTrafficChart(data);
            } else if (metricType === 'devices' || metricType === 'browsers') {
                this.updateDeviceChart(data);
            }
        } catch (error) {
            console.error(`Error loading ${metricType} data:`, error);
        } finally {
            if (loadingEl) loadingEl.classList.add('hidden');
        }
    }

    updateTrafficChart(data) {
        if (this.charts.traffic) {
            this.charts.traffic.data.labels = data.labels || [];
            this.charts.traffic.data.datasets[0].data = data.data || [];
            this.charts.traffic.update();
        }
    }

    updateDeviceChart(data) {
        if (this.charts.device) {
            this.charts.device.data.labels = data.labels || [];
            this.charts.device.data.datasets[0].data = data.data || [];
            this.charts.device.update();
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
