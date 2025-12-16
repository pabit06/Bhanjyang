document.addEventListener('DOMContentLoaded', function () {
    const dashboard = new ReportsDashboard();
    dashboard.init();
});

class ReportsDashboard {
    constructor() {
        this.refreshInterval = 30000; // 30 seconds
    }

    init() {
        this.initEventListeners();
        this.startAutoRefresh();
        this.setDefaultDates();
    }

    initEventListeners() {
        // Generate report form
        const form = document.getElementById('generate-report-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.generateReport();
            });
        }

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

    setDefaultDates() {
        const today = new Date();
        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

        const endDateEl = document.getElementById('end-date');
        const startDateEl = document.getElementById('start-date');

        if (endDateEl) endDateEl.value = today.toISOString().split('T')[0];
        if (startDateEl) startDateEl.value = weekAgo.toISOString().split('T')[0];
    }

    async generateReport() {
        const form = document.getElementById('generate-report-form');
        const formData = new FormData(form);
        const data = {
            type: formData.get('report_type'),
            start_date: formData.get('start_date'),
            end_date: formData.get('end_date')
        };
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

        try {
            const response = await fetch('/dashboard/report/generate/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                alert('Report generated successfully!');
                location.reload();
            } else {
                alert('Failed to generate report: ' + result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate report');
        }
    }

    async refreshData() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            // Refresh the page to get latest data
            location.reload();
        } catch (error) {
            console.error('Error refreshing data:', error);
        } finally {
            if (refreshBtn) refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }
    }
}

// Report management functions
function generateTemplateReport(type) {
    const today = new Date();
    let startDate, endDate;

    switch (type) {
        case 'performance':
        case 'analytics':
        case 'error':
            // Generate for last week
            startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            endDate = today;
            break;
        case 'custom':
            // Open custom form
            const reportTypeEl = document.getElementById('report-type');
            if (reportTypeEl) reportTypeEl.value = 'custom';
            return;
    }

    const reportTypeEl = document.getElementById('report-type');
    const startDateEl = document.getElementById('start-date');
    const endDateEl = document.getElementById('end-date');
    const formEl = document.getElementById('generate-report-form');

    if (reportTypeEl) reportTypeEl.value = type;
    if (startDateEl) startDateEl.value = startDate.toISOString().split('T')[0];
    if (endDateEl) endDateEl.value = endDate.toISOString().split('T')[0];

    if (formEl) formEl.dispatchEvent(new Event('submit'));
}

function generateQuickReport(type) {
    const today = new Date();
    let startDate, endDate;

    switch (type) {
        case 'weekly':
            startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            endDate = today;
            break;
        case 'monthly':
            startDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
            endDate = today;
            break;
        case 'error_summary':
            startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            endDate = today;
            break;
    }

    const data = {
        type: type,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
    };
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

    fetch('/dashboard/report/generate/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Report generated successfully!');
                location.reload();
            } else {
                alert('Failed to generate report: ' + result.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to generate report');
        });
}

function viewReport(reportId) {
    // This would open a modal or navigate to report details page
    console.log('View report:', reportId);
    window.open(`/dashboard/reports/${reportId}/`, '_blank');
}

function downloadReport(reportId) {
    // This would download the report file
    console.log('Download report:', reportId);
    window.open(`/dashboard/reports/${reportId}/download/`, '_blank');
}

function deleteReport(reportId) {
    if (confirm('Are you sure you want to delete this report?')) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';
        fetch(`/dashboard/reports/${reportId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
            },
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('Report deleted successfully!');
                    location.reload();
                } else {
                    alert('Failed to delete report');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to delete report');
            });
    }
}

function exportData(format) {
    const today = new Date();
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

    const params = new URLSearchParams({
        format: format,
        start_date: weekAgo.toISOString().split('T')[0],
        end_date: today.toISOString().split('T')[0]
    });

    window.open(`/dashboard/export/?${params}`, '_blank');
}
