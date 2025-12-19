"""
Comprehensive tests for Dashboard services
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta

from apps.dashboard.models import (
    PerformanceMetric, PageView, ErrorLog, UserSession,
    PerformanceReport, PerformanceAlert, AlertLog,
    DashboardWidget, UserDashboardPreference, AuditLog
)
from apps.dashboard.services import (
    DashboardAnalyticsService, DashboardReportingService,
    DashboardMonitoringService, DashboardWidgetService
)
from apps.downloads.models import DownloadableFile
from apps.news_events.models import NewsArticle
from apps.about.models import Person, Staff
from apps.contact.models import ContactSubmission

User = get_user_model()


class DashboardAnalyticsServiceTest(TestCase):
    """Test suite for DashboardAnalyticsService"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test page views
        PageView.objects.create(
            page_url='/test/',
            page_title='Test Page',
            load_time=1000,
            timestamp=timezone.now(),
            is_mobile=False,
            browser='Chrome'
        )
        
        # Create test error log
        ErrorLog.objects.create(
            error_type='500',
            error_message='Test error',
            page_url='/test/',
            resolved=False
        )
    
    def test_get_dashboard_summary(self):
        """Test getting dashboard summary"""
        summary = DashboardAnalyticsService.get_dashboard_summary()
        
        self.assertIn('performance', summary)
        self.assertIn('views', summary)
        self.assertIn('errors', summary)
        self.assertIn('pages', summary)
        self.assertIn('tech', summary)
        
        self.assertIn('today', summary['performance'])
        self.assertIn('week', summary['performance'])
        self.assertIn('month', summary['performance'])
    
    def test_get_domain_stats(self):
        """Test getting domain statistics"""
        stats = DashboardAnalyticsService.get_domain_stats()
        
        self.assertIn('downloads', stats)
        self.assertIn('updates', stats)
        self.assertIn('team', stats)
        self.assertIn('contacts', stats)
    
    def test_get_chart_data_page_load(self):
        """Test getting chart data for page load"""
        data = DashboardAnalyticsService.get_chart_data('page_load', days=7)
        
        self.assertIn('labels', data)
        self.assertIn('data', data)
        self.assertIn('meta', data)
        self.assertIsInstance(data['labels'], list)
        self.assertIsInstance(data['data'], list)
    
    def test_get_chart_data_errors(self):
        """Test getting chart data for errors"""
        data = DashboardAnalyticsService.get_chart_data('errors', days=7)
        
        self.assertIn('labels', data)
        self.assertIn('data', data)
        self.assertIsInstance(data['labels'], list)
        self.assertIsInstance(data['data'], list)
    
    def test_get_chart_data_traffic(self):
        """Test getting chart data for traffic"""
        data = DashboardAnalyticsService.get_chart_data('traffic', days=7)
        
        self.assertIn('labels', data)
        self.assertIn('data', data)
        self.assertIn('meta', data)
        self.assertIn('unique', data['meta'])
    
    def test_get_chart_data_with_filters(self):
        """Test getting chart data with filters"""
        filters = {'device_type': 'mobile', 'browser': 'Chrome'}
        data = DashboardAnalyticsService.get_chart_data('page_load', days=7, filters=filters)
        
        self.assertIn('labels', data)
        self.assertIn('data', data)
    
    def test_record_page_view(self):
        """Test recording page view"""
        data = {
            'page_url': '/test/',
            'page_title': 'Test',
            'load_time': 500
        }
        request_meta = {
            'HTTP_USER_AGENT': 'Test Agent',
            'REMOTE_ADDR': '192.168.1.1',
            'session_id': 'test_session',
            'user': self.user
        }
        
        success = DashboardAnalyticsService.record_page_view(data, request_meta)
        
        self.assertTrue(success)
        self.assertTrue(PageView.objects.filter(page_url='/test/').exists())
    
    def test_record_page_view_anonymous(self):
        """Test recording page view for anonymous user"""
        data = {
            'page_url': '/test-anonymous/',
            'page_title': 'Test Anonymous',
            'load_time': 500
        }
        request_meta = {
            'HTTP_USER_AGENT': 'Test Agent',
            'REMOTE_ADDR': '192.168.1.1',
            'session_id': 'test_session_anon',
            'user': MagicMock(is_authenticated=False)
        }
        
        success = DashboardAnalyticsService.record_page_view(data, request_meta)
        
        self.assertTrue(success)
        page_view = PageView.objects.filter(page_url='/test-anonymous/').first()
        self.assertIsNotNone(page_view)
        self.assertIsNone(page_view.user)
    
    def test_record_error(self):
        """Test recording error"""
        data = {
            'error_type': '500',
            'error_message': 'Test error',
            'page_url': '/test/',
            'stack_trace': 'Traceback...'
        }
        request_meta = {
            'HTTP_USER_AGENT': 'Test Agent',
            'REMOTE_ADDR': '192.168.1.1',
            'session_id': 'test_session',
            'user': self.user
        }
        
        success = DashboardAnalyticsService.record_error(data, request_meta)
        
        self.assertTrue(success)
        self.assertTrue(ErrorLog.objects.filter(error_message='Test error').exists())
    
    def test_record_error_handles_exception(self):
        """Test error handling in record_error"""
        data = {'error_type': '500'}
        request_meta = {}
        
        with patch('apps.dashboard.services.ErrorLog.objects.create', side_effect=Exception('DB Error')):
            success = DashboardAnalyticsService.record_error(data, request_meta)
            self.assertFalse(success)


class DashboardReportingServiceTest(TestCase):
    """Test suite for DashboardReportingService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test data
        PageView.objects.create(
            page_url='/test/',
            page_title='Test',
            load_time=1000,
            timestamp=timezone.now()
        )
        
        ErrorLog.objects.create(
            error_type='500',
            error_message='Test error',
            page_url='/test/'
        )
    
    def test_generate_report(self):
        """Test generating performance report"""
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        report = DashboardReportingService.generate_report(
            self.user, 'performance', start_date, end_date
        )
        
        self.assertIsNotNone(report)
        self.assertEqual(report.report_type, 'performance')
        self.assertEqual(report.generated_by, self.user)
        self.assertIn('total_views', report.report_data)
        self.assertIn('avg_load_time', report.report_data)
        self.assertIn('total_errors', report.report_data)
    
    def test_export_data_csv_page_views(self):
        """Test exporting page views as CSV"""
        csv_data = DashboardReportingService.export_data_csv('page_views', days=7)
        
        self.assertIsInstance(csv_data, str)
        self.assertIn('Timestamp', csv_data)
        self.assertIn('URL', csv_data)
        self.assertIn('Load Time', csv_data)
    
    def test_export_data_csv_errors(self):
        """Test exporting errors as CSV"""
        csv_data = DashboardReportingService.export_data_csv('errors', days=7)
        
        self.assertIsInstance(csv_data, str)
        self.assertIn('Timestamp', csv_data)
        self.assertIn('Type', csv_data)
        self.assertIn('Message', csv_data)


class DashboardMonitoringServiceTest(TestCase):
    """Test suite for DashboardMonitoringService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.alert = PerformanceAlert.objects.create(
            alert_type='load_time',
            threshold_value=5000.0,
            severity='high',
            is_active=True,
            description='Test Alert'
        )
        
        self.alert_log = AlertLog.objects.create(
            alert=self.alert,
            triggered_at=timezone.now(),
            current_value=6000.0,
            message='Test alert message',
            is_resolved=False
        )
    
    def test_get_active_alerts(self):
        """Test getting active alerts"""
        alerts = DashboardMonitoringService.get_active_alerts()
        
        self.assertIsNotNone(alerts)
        self.assertGreaterEqual(len(alerts), 1)
        self.assertIn(self.alert_log, alerts)
    
    def test_resolve_alert(self):
        """Test resolving an alert"""
        success = DashboardMonitoringService.resolve_alert(
            self.alert_log.id, self.user
        )
        
        self.assertTrue(success)
        self.alert_log.refresh_from_db()
        self.assertTrue(self.alert_log.is_resolved)
        self.assertIsNotNone(self.alert_log.resolved_at)
        self.assertEqual(self.alert_log.resolved_by, self.user)
    
    def test_resolve_alert_not_found(self):
        """Test resolving non-existent alert"""
        success = DashboardMonitoringService.resolve_alert(99999, self.user)
        
        self.assertFalse(success)


class DashboardWidgetServiceTest(TestCase):
    """Test suite for DashboardWidgetService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_get_user_config(self):
        """Test getting user dashboard configuration"""
        config = DashboardWidgetService.get_user_config(self.user)
        
        self.assertIn('theme', config)
        self.assertIn('refresh_interval', config)
        self.assertIn('widgets', config)
        self.assertIsInstance(config['widgets'], list)
    
    def test_update_preferences(self):
        """Test updating user preferences"""
        data = {
            'theme': 'dark',
            'refresh_interval': 30
        }
        
        success = DashboardWidgetService.update_preferences(self.user, data)
        
        self.assertTrue(success)
        pref = UserDashboardPreference.objects.get(user=self.user)
        self.assertEqual(pref.theme, 'dark')
        self.assertEqual(pref.refresh_interval, 30)
    
    def test_update_preferences_partial(self):
        """Test updating preferences with partial data"""
        data = {'theme': 'light'}
        
        success = DashboardWidgetService.update_preferences(self.user, data)
        
        self.assertTrue(success)
        pref = UserDashboardPreference.objects.get(user=self.user)
        self.assertEqual(pref.theme, 'light')

