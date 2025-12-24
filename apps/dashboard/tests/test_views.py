"""
Comprehensive tests for dashboard app views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import json

from apps.dashboard.models import (
    PerformanceMetric, PageView, ErrorLog, UserSession,
    PerformanceAlert, AlertLog, DashboardWidget
)

User = get_user_model()


class DashboardViewsTest(TestCase):
    """Test cases for dashboard views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpass123'
        )
        
        # Create test data
        self.metric = PerformanceMetric.objects.create(
            metric_type='page_load',
            value=150.5,
            unit='ms',
            ip_address='192.168.1.1'
        )
        
        self.page_view = PageView.objects.create(
            page_url='https://example.com/test',
            page_title='Test Page',
            load_time=250.5,
            ip_address='192.168.1.1'
        )
        
        self.error_log = ErrorLog.objects.create(
            error_type='404',
            error_message='Page not found',
            ip_address='192.168.1.1'
        )
    
    def test_dashboard_view_staff(self):
        """Test DashboardView with staff user"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
        self.assertIn('breadcrumbs', response.context)
    
    def test_dashboard_view_non_staff(self):
        """Test DashboardView with non-staff user"""
        self.client.login(username='regularuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Should redirect or return 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_performance_dashboard_view(self):
        """Test PerformanceDashboardView"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:performance'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/performance.html')
    
    def test_analytics_dashboard_view(self):
        """Test AnalyticsDashboardView"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:analytics'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/analytics.html')
    
    def test_error_dashboard_view(self):
        """Test ErrorDashboardView"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:errors'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/errors.html')
    
    def test_reports_dashboard_view(self):
        """Test ReportsDashboardView"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:reports'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/reports.html')
    
    def test_dashboard_data_api_get(self):
        """Test DashboardDataView API GET request"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:api'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('summary', data)
    
    def test_dashboard_data_api_with_filters(self):
        """Test DashboardDataView API with filters"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('dashboard:api'),
            {
                'start_date': (timezone.now() - timedelta(days=7)).isoformat(),
                'end_date': timezone.now().isoformat()
            }
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_performance_data_api(self):
        """Test PerformanceDataView API"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:performance_api'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('performance', data)
    
    def test_analytics_data_api(self):
        """Test AnalyticsDataView API"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:analytics_api'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('analytics', data)
    
    def test_errors_data_api(self):
        """Test ErrorsDataView API"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:errors_api'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('errors', data)
    
    def test_track_page_view_post(self):
        """Test TrackPageView POST request"""
        data = {
            'page_url': 'https://example.com/test',
            'page_title': 'Test Page',
            'load_time': 200.5
        }
        
        response = self.client.post(
            reverse('dashboard:track_page_view'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success', False))
    
    def test_track_error_post(self):
        """Test TrackErrorView POST request"""
        data = {
            'error_type': '404',
            'error_message': 'Page not found',
            'page_url': 'https://example.com/missing'
        }
        
        response = self.client.post(
            reverse('dashboard:track_error'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success', False))
    
    def test_generate_report_post(self):
        """Test DashboardReportView POST request"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'report_type': 'daily',
            'start_date': (timezone.now() - timedelta(days=1)).isoformat(),
            'end_date': timezone.now().isoformat()
        }
        
        response = self.client.post(
            reverse('dashboard:generate_report'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('report', data)
    
    def test_get_alerts(self):
        """Test AlertsView GET request"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create an alert
        alert = PerformanceAlert.objects.create(
            alert_type='load_time',
            threshold_value=500.0,
            created_by=self.user
        )
        
        response = self.client.get(reverse('dashboard:get_alerts'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('alerts', data)
    
    def test_resolve_alert_post(self):
        """Test ResolveAlertView POST request"""
        self.client.login(username='testuser', password='testpass123')
        
        alert = PerformanceAlert.objects.create(
            alert_type='load_time',
            threshold_value=500.0,
            created_by=self.user
        )
        
        alert_log = AlertLog.objects.create(
            alert=alert,
            current_value=600.0,
            message='Test alert'
        )
        
        response = self.client.post(
            reverse('dashboard:resolve_alert', kwargs={'alert_id': alert_log.id})
        )
        
        self.assertEqual(response.status_code, 200)
        alert_log.refresh_from_db()
        self.assertTrue(alert_log.is_resolved)
    
    def test_export_data(self):
        """Test ExportDashboardDataView GET request"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:export_data'))
        
        # Should return CSV or JSON export
        self.assertIn(response.status_code, [200, 302])
    
    def test_dashboard_widgets_get(self):
        """Test DashboardWidgetsView GET request"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dashboard:dashboard_widgets'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('widgets', data)
    
    def test_update_preferences_post(self):
        """Test UserPreferenceView POST request"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'theme': 'dark',
            'refresh_interval': 60
        }
        
        response = self.client.post(
            reverse('dashboard:update_preferences'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success', False))

