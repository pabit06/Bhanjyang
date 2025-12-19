"""
Comprehensive tests for Dashboard views
"""
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

from apps.dashboard.models import (
    PageView, ErrorLog, PerformanceReport, AlertLog
)
from apps.dashboard.services import (
    DashboardAnalyticsService, DashboardReportingService,
    DashboardMonitoringService, DashboardWidgetService
)

User = get_user_model()


class DashboardViewTest(TestCase):
    """Test suite for DashboardView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
    
    def test_dashboard_view_requires_staff(self):
        """Test dashboard view requires staff status"""
        self.client.login(username='user', password='testpass123')
        
        response = self.client.get(reverse('dashboard:dashboard'))
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_view_staff_access(self):
        """Test dashboard view for staff user"""
        self.client.login(username='staff', password='testpass123')
        
        response = self.client.get(reverse('dashboard:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('breadcrumbs', response.context)
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.get_dashboard_summary')
    @patch('apps.dashboard.services.DashboardAnalyticsService.get_domain_stats')
    def test_dashboard_view_context(self, mock_domain, mock_summary):
        """Test dashboard view context data"""
        mock_summary.return_value = {
            'performance': {'today': 100, 'week': 200, 'month': 300, 'thresholds': {}},
            'views': {'today': 10, 'week': 50, 'month': 200},
            'errors': {'today': 1, 'week': 5, 'unresolved': 2},
            'pages': {'slowest': [], 'popular': []},
            'tech': {'browsers': []}
        }
        mock_domain.return_value = {
            'downloads': {'total': 10, 'active': 5, 'total_downloads': 100},
            'updates': {'total': 20, 'published': 15, 'recent': 5},
            'team': {'total': 5, 'active_staff': 3},
            'contacts': {'total': 30, 'new': 5}
        }
        
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('avg_load_time_today', response.context)
        self.assertIn('page_views_week', response.context)
        self.assertIn('total_downloads', response.context)
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.get_dashboard_summary')
    def test_dashboard_view_exception_handling(self, mock_summary):
        """Test dashboard view exception handling"""
        mock_summary.side_effect = Exception("Service error")
        
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Should still render even if service fails
        self.assertEqual(response.status_code, 200)


class PerformanceDashboardViewTest(TestCase):
    """Test suite for PerformanceDashboardView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_performance_dashboard_view_requires_staff(self):
        """Test performance dashboard requires staff"""
        response = self.client.get(reverse('dashboard:performance'))
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.get_dashboard_summary')
    def test_performance_dashboard_view(self, mock_summary):
        """Test performance dashboard view"""
        mock_summary.return_value = {
            'performance': {'today': 100, 'week': 200, 'month': 300},
            'pages': {'slowest': []}
        }
        
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('dashboard:performance'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('performance_metrics', response.context)
        self.assertIn('slowest_pages', response.context)


class AnalyticsDashboardViewTest(TestCase):
    """Test suite for AnalyticsDashboardView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_analytics_dashboard_view_requires_staff(self):
        """Test analytics dashboard requires staff"""
        response = self.client.get(reverse('dashboard:analytics'))
        
        self.assertEqual(response.status_code, 302)
    
    def test_analytics_dashboard_view_staff_access(self):
        """Test analytics dashboard for staff"""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('dashboard:analytics'))
        
        self.assertEqual(response.status_code, 200)


class ErrorDashboardViewTest(TestCase):
    """Test suite for ErrorDashboardView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_error_dashboard_view_requires_staff(self):
        """Test error dashboard requires staff"""
        response = self.client.get(reverse('dashboard:errors'))
        
        self.assertEqual(response.status_code, 302)
    
    def test_error_dashboard_view_staff_access(self):
        """Test error dashboard for staff"""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('dashboard:errors'))
        
        self.assertEqual(response.status_code, 200)


class ReportsDashboardViewTest(TestCase):
    """Test suite for ReportsDashboardView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_reports_dashboard_view_requires_staff(self):
        """Test reports dashboard requires staff"""
        response = self.client.get(reverse('dashboard:reports'))
        
        self.assertEqual(response.status_code, 302)
    
    def test_reports_dashboard_view_staff_access(self):
        """Test reports dashboard for staff"""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('dashboard:reports'))
        
        self.assertEqual(response.status_code, 200)


class DashboardDataViewTest(TestCase):
    """Test suite for DashboardDataView API"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    def test_dashboard_data_view_requires_auth(self):
        """Test dashboard data API requires authentication"""
        response = self.api_client.get(reverse('dashboard:api'))
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.get_chart_data')
    def test_dashboard_data_view_valid(self, mock_chart):
        """Test dashboard data API with valid request"""
        mock_chart.return_value = {'data': []}
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:api'), {'type': 'page_load', 'days': 7})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        mock_chart.assert_called_once()
    
    def test_dashboard_data_view_invalid_serializer(self):
        """Test dashboard data API with invalid data"""
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:api'), {'days': 'invalid'})
        
        self.assertEqual(response.status_code, 400)
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.get_chart_data')
    def test_dashboard_data_view_exception_handling(self, mock_chart):
        """Test dashboard data API exception handling"""
        mock_chart.side_effect = Exception("Service error")
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:api'), {'type': 'page_load'})
        
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.data)


class TrackPageViewTest(TestCase):
    """Test suite for TrackPageView API"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.record_page_view')
    def test_track_page_view_success(self, mock_record):
        """Test tracking page view successfully"""
        mock_record.return_value = True
        
        data = {
            'page_url': '/test/',
            'page_title': 'Test Page',
            'load_time': 1000
        }
        response = self.api_client.post(reverse('dashboard:track_page_view'), data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        mock_record.assert_called_once()
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.record_page_view')
    def test_track_page_view_failure(self, mock_record):
        """Test tracking page view failure"""
        mock_record.return_value = False
        
        data = {'page_url': '/test/'}
        response = self.api_client.post(reverse('dashboard:track_page_view'), data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.record_page_view')
    def test_track_page_view_with_json_string(self, mock_record):
        """Test tracking page view with JSON string in data field"""
        mock_record.return_value = True
        
        data = {
            'data': json.dumps({
                'page_url': '/test/',
                'page_title': 'Test Page'
            })
        }
        response = self.api_client.post(reverse('dashboard:track_page_view'), data, format='json')
        
        self.assertEqual(response.status_code, 200)
        mock_record.assert_called_once()
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.record_page_view')
    def test_track_page_view_exception_handling(self, mock_record):
        """Test tracking page view exception handling"""
        mock_record.side_effect = Exception("Service error")
        
        data = {'page_url': '/test/'}
        response = self.api_client.post(reverse('dashboard:track_page_view'), data, format='json')
        
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.data['success'])


class TrackErrorViewTest(TestCase):
    """Test suite for TrackErrorView API"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.record_error')
    def test_track_error_success(self, mock_record):
        """Test tracking error successfully"""
        mock_record.return_value = True
        
        data = {
            'error_type': '500',
            'error_message': 'Test error',
            'page_url': '/test/'
        }
        response = self.api_client.post(reverse('dashboard:track_error'), data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        mock_record.assert_called_once()
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.record_error')
    def test_track_error_failure(self, mock_record):
        """Test tracking error failure"""
        mock_record.return_value = False
        
        data = {'error_type': '500'}
        response = self.api_client.post(reverse('dashboard:track_error'), data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.record_error')
    def test_track_error_exception_handling(self, mock_record):
        """Test tracking error exception handling"""
        mock_record.side_effect = Exception("Service error")
        
        data = {'error_type': '500'}
        response = self.api_client.post(reverse('dashboard:track_error'), data, format='json')
        
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.data['success'])


class DashboardReportViewTest(TestCase):
    """Test suite for DashboardReportView API"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    def test_dashboard_report_view_requires_auth(self):
        """Test dashboard report API requires authentication"""
        response = self.api_client.post(reverse('dashboard:generate_report'))
        
        self.assertEqual(response.status_code, 403)
    
    @patch('apps.dashboard.services.DashboardReportingService.generate_report')
    def test_dashboard_report_view_success(self, mock_generate):
        """Test generating dashboard report successfully"""
        mock_report = MagicMock()
        mock_report.id = 1
        mock_report.report_data = {'total_views': 100}
        mock_generate.return_value = mock_report
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        data = {
            'type': 'weekly',
            'start_date': (datetime.now() - timedelta(days=7)).isoformat(),
            'end_date': datetime.now().isoformat()
        }
        response = self.api_client.post(reverse('dashboard:generate_report'), data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertIn('report_id', response.data)
    
    def test_dashboard_report_view_invalid_date(self):
        """Test generating report with invalid date"""
        self.api_client.force_authenticate(user=self.admin_user)
        
        data = {
            'type': 'weekly',
            'start_date': 'invalid-date',
            'end_date': datetime.now().isoformat()
        }
        response = self.api_client.post(reverse('dashboard:generate_report'), data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)


class ExportDashboardDataViewTest(TestCase):
    """Test suite for ExportDashboardDataView API"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    def test_export_dashboard_data_requires_auth(self):
        """Test export data API requires authentication"""
        response = self.api_client.get(reverse('dashboard:export_data'))
        
        self.assertEqual(response.status_code, 403)
    
    @patch('apps.dashboard.services.DashboardReportingService.export_data_csv')
    def test_export_dashboard_data_page_views(self, mock_export):
        """Test exporting page views data"""
        mock_export.return_value = 'Timestamp,URL,Load Time\n2024-01-01,/,1000'
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:export_data'), {'data_type': 'page_views', 'days': 7})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('Content-Disposition', response)
        mock_export.assert_called_once_with('page_views', 7)
    
    @patch('apps.dashboard.services.DashboardReportingService.export_data_csv')
    def test_export_dashboard_data_errors(self, mock_export):
        """Test exporting errors data"""
        mock_export.return_value = 'Timestamp,Error Type,Message\n2024-01-01,500,Error'
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:export_data'), {'data_type': 'errors', 'days': 7})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        mock_export.assert_called_once_with('errors', 7)
    
    @patch('apps.dashboard.services.DashboardReportingService.export_data_csv')
    def test_export_dashboard_data_exception_handling(self, mock_export):
        """Test export data exception handling"""
        mock_export.side_effect = Exception("Export error")
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:export_data'), {'data_type': 'page_views'})
        
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.data)


class AlertsViewTest(TestCase):
    """Test suite for AlertsView API"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    def test_alerts_view_requires_auth(self):
        """Test alerts API requires authentication"""
        response = self.api_client.get(reverse('dashboard:get_alerts'))
        
        self.assertEqual(response.status_code, 403)
    
    @patch('apps.dashboard.services.DashboardMonitoringService.get_active_alerts')
    def test_alerts_view_success(self, mock_get):
        """Test getting active alerts"""
        mock_get.return_value = []
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:get_alerts'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('alerts', response.data)
        mock_get.assert_called_once()


class ResolveAlertViewTest(TestCase):
    """Test suite for ResolveAlertView API"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    def test_resolve_alert_view_requires_auth(self):
        """Test resolve alert API requires authentication"""
        response = self.api_client.post(reverse('dashboard:resolve_alert', args=[1]))
        
        self.assertEqual(response.status_code, 403)
    
    @patch('apps.dashboard.services.DashboardMonitoringService.resolve_alert')
    def test_resolve_alert_success(self, mock_resolve):
        """Test resolving alert successfully"""
        mock_resolve.return_value = True
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.post(reverse('dashboard:resolve_alert', args=[1]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        mock_resolve.assert_called_once_with(1, self.admin_user)
    
    @patch('apps.dashboard.services.DashboardMonitoringService.resolve_alert')
    def test_resolve_alert_not_found(self, mock_resolve):
        """Test resolving non-existent alert"""
        mock_resolve.return_value = False
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.post(reverse('dashboard:resolve_alert', args=[999]))
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)


class DashboardWidgetsViewTest(TestCase):
    """Test suite for DashboardWidgetsView API"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    def test_dashboard_widgets_view_requires_auth(self):
        """Test dashboard widgets API requires authentication"""
        response = self.api_client.get(reverse('dashboard:dashboard_widgets'))
        
        self.assertEqual(response.status_code, 403)
    
    @patch('apps.dashboard.services.DashboardWidgetService.get_user_config')
    def test_dashboard_widgets_view_success(self, mock_get):
        """Test getting dashboard widgets"""
        mock_get.return_value = {'widgets': []}
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:dashboard_widgets'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('widgets', response.data)
        mock_get.assert_called_once_with(self.admin_user)


class UserPreferenceViewTest(TestCase):
    """Test suite for UserPreferenceView API"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    def test_user_preference_view_requires_auth(self):
        """Test user preference API requires authentication"""
        response = self.api_client.post(reverse('dashboard:update_preferences'))
        
        self.assertEqual(response.status_code, 403)
    
    @patch('apps.dashboard.services.DashboardWidgetService.update_preferences')
    def test_user_preference_view_success(self, mock_update):
        """Test updating user preferences successfully"""
        mock_update.return_value = True
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        data = {'theme': 'dark', 'layout': 'grid'}
        response = self.api_client.post(reverse('dashboard:update_preferences'), data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        mock_update.assert_called_once_with(self.admin_user, data)
    
    @patch('apps.dashboard.services.DashboardWidgetService.update_preferences')
    def test_user_preference_view_failure(self, mock_update):
        """Test updating user preferences failure"""
        mock_update.return_value = False
        
        self.api_client.force_authenticate(user=self.admin_user)
        
        data = {'theme': 'dark'}
        response = self.api_client.post(reverse('dashboard:update_preferences'), data, format='json')
        
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.data)


class SpecializedDataViewsTest(TestCase):
    """Test suite for specialized data views"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.get_chart_data')
    def test_performance_data_view(self, mock_chart):
        """Test PerformanceDataView"""
        mock_chart.return_value = {'data': []}
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:performance_api'))
        
        self.assertEqual(response.status_code, 200)
        # Should call with type='page_load'
        mock_chart.assert_called_once()
        call_args = mock_chart.call_args[0]
        self.assertEqual(call_args[0], 'page_load')
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.get_chart_data')
    def test_analytics_data_view(self, mock_chart):
        """Test AnalyticsDataView"""
        mock_chart.return_value = {'data': []}
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:analytics_api'))
        
        self.assertEqual(response.status_code, 200)
        # Should call with type='traffic'
        call_args = mock_chart.call_args[0]
        self.assertEqual(call_args[0], 'traffic')
    
    @patch('apps.dashboard.services.DashboardAnalyticsService.get_chart_data')
    def test_errors_data_view(self, mock_chart):
        """Test ErrorsDataView"""
        mock_chart.return_value = {'data': []}
        self.api_client.force_authenticate(user=self.admin_user)
        
        response = self.api_client.get(reverse('dashboard:errors_api'))
        
        self.assertEqual(response.status_code, 200)
        # Should call with type='errors'
        call_args = mock_chart.call_args[0]
        self.assertEqual(call_args[0], 'errors')

