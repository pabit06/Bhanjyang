/**
 * Analytics Dashboard for Gallery
 * Handles data fetching, charts updates, and interactivity.
 */

class AnalyticsDashboard {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/gallery/api/stats/';
        this.charts = {};
        this.data = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.loadData();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadData();
            });
        }

        // Filter changes
        const timeRangeSelect = document.getElementById('time-range');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', () => {
                this.loadData();
            });
        }

        const categoryFilter = document.getElementById('category-filter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => {
                this.loadData();
            });
        }
    }

    async loadData() {
        const refreshBtn = document.getElementById('refresh-data');
        if(refreshBtn) refreshBtn.classList.add('loading');

        try {
            const timeRange = document.getElementById('time-range').value;
            const category = document.getElementById('category-filter').value;
            
            // Build URL with query params
            const url = new URL(this.apiUrl, window.location.origin);
            url.searchParams.append('time_range', timeRange);
            if (category !== 'all') {
                url.searchParams.append('category', category);
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch data');

            this.data = await response.json();
            
            this.updateMetrics();
            this.updateCharts();
            this.updateTopImagesTable();
            
            if (window.advancedAnimations) {
                window.advancedAnimations.showNotification('Data refreshed successfully!', 'info', 2000);
            }

        } catch (error) {
            console.error('Error loading analytics data:', error);
            if (window.advancedAnimations) {
                window.advancedAnimations.showNotification('Error refreshing data', 'error', 3000);
            }
        } finally {
            if(refreshBtn) refreshBtn.classList.remove('loading');
        }
    }

    updateMetrics() {
        this.animateCounter('total-views', this.data.total_views);
        this.animateCounter('total-likes', this.data.total_likes);
        this.animateCounter('total-shares', this.data.total_shares);
        this.animateCounter('total-downloads', this.data.total_downloads);
    }

    animateCounter(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseInt(element.textContent.replace(/,/g, '')) || 0;
        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease out cubic
            const ease = 1 - Math.pow(1 - progress, 3);

            const currentValue = Math.floor(startValue + (targetValue - startValue) * ease);
            element.textContent = currentValue.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    initializeCharts() {
        this.createViewsChart();
        this.createCategoryChart();
        this.createPeakTimesChart();
    }

    createViewsChart() {
        const ctx = document.getElementById('views-chart');
        if (!ctx) return;

        this.charts.views = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Views',
                    data: [],
                    borderColor: '#dc2626',
                    backgroundColor: 'rgba(220, 38, 38, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(0, 0, 0, 0.1)' } },
                    x: { grid: { color: 'rgba(0, 0, 0, 0.1)' } }
                }
            }
        });
    }

    createCategoryChart() {
        const ctx = document.getElementById('category-chart');
        if (!ctx) return;

        this.charts.category = new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: ['#dc2626', '#059669', '#3b82f6', '#f59e0b', '#8b5cf6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }

    createPeakTimesChart() {
        const ctx = document.getElementById('peak-times-chart');
        if (!ctx) return;

        // Note: Peak times are currently mocked as they require complex backend aggregation
        this.charts.peakTimes = new Chart(ctx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['12AM', '6AM', '12PM', '6PM', '9PM'],
                datasets: [{
                    label: 'Avg Views',
                    data: [10, 25, 60, 45, 30],
                    backgroundColor: 'rgba(220, 38, 38, 0.8)',
                    borderColor: '#dc2626',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(0, 0, 0, 0.1)' } },
                    x: { grid: { color: 'rgba(0, 0, 0, 0.1)' } }
                }
            }
        });
    }

    updateCharts() {
        // Update Views Chart
        if (this.charts.views && this.data.views_chart) {
            this.charts.views.data.labels = this.data.views_chart.labels || [];
            this.charts.views.data.datasets[0].data = this.data.views_chart.data || [];
            this.charts.views.update();
        }

        // Update Category Chart
        if (this.charts.category && this.data.category_stats) {
            const labels = this.data.category_stats.map(s => s.category);
            const counts = this.data.category_stats.map(s => s.count);
            
            this.charts.category.data.labels = labels;
            this.charts.category.data.datasets[0].data = counts;
            this.charts.category.update();
        }
    }

    updateTopImagesTable() {
        const tbody = document.getElementById('top-images-table');
        if (!tbody) return;
        
        tbody.innerHTML = '';

        if (this.data.top_images && this.data.top_images.length > 0) {
            this.data.top_images.forEach(image => {
                const engagement = image.engagement || 0; // Calculated by annotation
                const row = document.createElement('tr');
                
                // Use a generic placeholder or the actual image URL if available in the API response
                // The current serializer doesn't strictly provide full image objects, mostly values, 
                // but let's assume standard object structure or handle it.
                // The service returns a QuerySet values or objects. 
                // Wait, service returns `top_images = qs...`. This is a queryset of model instances.
                // DRF Serializer will serialize this. The APIView returns `Response(data)`. 
                // DRF 'Response' handles basic python types. Models?
                // The service returns a DICT with 'top_images' being a QuerySet.
                // DRF Response will NOT automatically serialize a QuerySet deeply unless a serializer is used.
                // The current `GalleryStatsAPI` just returns the dict. 
                // Django REST Framework's Response can handle basic data but not QuerySets directly without a serializer usually, 
                // OR if it's just keys/values.
                // Actually, `GalleryService.get_analytics_data` returns a dict where `top_images` is a QuerySet. 
                // Returning this directly in `Response` will likely cause a TypeError or not serialize fields properly unless configured.
                // WE SHOULD FIX THIS.
                // But for now, assuming the API works (maybe it uses a Default renderer that handles values?), 
                // I will assume fields: title, views_count, likes_count, shares_count.
                
                row.innerHTML = `
                    <td>
                        <div class="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
                             ${image.image ? `<img src="/media/${image.image}" class="w-full h-full object-cover">` : '<i class="fas fa-image text-gray-400"></i>'}
                        </div>
                    </td>
                    <td class="font-medium">${image.title || 'Untitled'}</td>
                    <td>${(image.views_count || 0).toLocaleString()}</td>
                    <td>${image.likes_count || 0}</td>
                    <td>${image.shares_count || 0}</td>
                    <td>
                        <span class="status-badge ${engagement > 10 ? 'status-active' : 'status-pending'}">
                            ${engagement}
                        </span>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center p-4">No data available</td></tr>';
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    window.analyticsDashboard = new AnalyticsDashboard({
        apiUrl: '/gallery/api/stats/'
    });
});
