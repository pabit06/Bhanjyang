document.addEventListener('DOMContentLoaded', function () {
    const dashboard = new PerformanceDashboard();
    dashboard.init();
});

class PerformanceDashboard {
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

        // Memory Chart
        const memoryCtx = document.getElementById('memoryChart');
        if (memoryCtx) {
            this.charts.memory = new Chart(memoryCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Memory Usage (MB)',
                        data: [],
                        borderColor: 'rgb(16, 185, 129)',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
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
            await this.loadChartData('load_time');
            await this.loadChartData('memory_usage');
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadChartData(metricType) {
        const loadingEl = document.getElementById(metricType === 'memory_usage' || metricType === 'cpu_usage' ? 'memory-chart-loading' : 'chart-loading');
        if (loadingEl) loadingEl.classList.remove('hidden');

        try {
            const response = await fetch(`/dashboard/api/performance/?metric=${metricType}&days=7`);
            const data = await response.json();

            if (metricType === 'load_time' || metricType === 'db_performance' || metricType === 'api_performance') {
                this.updatePerformanceChart(data);
            } else if (metricType === 'memory_usage' || metricType === 'cpu_usage') {
                this.updateMemoryChart(data);
            }
        } catch (error) {
            console.error(`Error loading ${metricType} data:`, error);
        } finally {
            if (loadingEl) loadingEl.classList.add('hidden');
        }
    }

    updatePerformanceChart(data) {
        if (this.charts.performance) {
            this.charts.performance.data.labels = data.labels || [];
            this.charts.performance.data.datasets[0].data = data.data || [];
            this.charts.performance.update();
        }
    }

    updateMemoryChart(data) {
        if (this.charts.memory) {
            this.charts.memory.data.labels = data.labels || [];
            this.charts.memory.data.datasets[0].data = data.data || [];
            this.charts.memory.update();
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
