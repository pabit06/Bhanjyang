"""
Tests for dashboard app admin classes
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from apps.dashboard.models import (
    PerformanceMetric, PageView, ErrorLog, UserSession,
    PerformanceReport, PerformanceAlert, AlertLog, DashboardWidget, AuditLog
)
from apps.dashboard.admin import (
    PerformanceMetricAdmin, PageViewAdmin, ErrorLogAdmin,
    UserSessionAdmin, PerformanceReportAdmin, PerformanceAlertAdmin,
    AlertLogAdmin, DashboardWidgetAdmin, AuditLogAdmin
)


class DashboardAdminTestCase(TestCase):
    """Base test case for dashboard admin tests"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.request = self.factory.get('/admin/')
        self.request.user = self.admin_user
        
        # Add session and messages middleware for admin actions
        SessionMiddleware(lambda req: None).process_request(self.request)
        MessageMiddleware(lambda req: None).process_request(self.request)
        self.request._messages = FallbackStorage(self.request)


class PerformanceMetricAdminTest(DashboardAdminTestCase):
    """Test PerformanceMetricAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = PerformanceMetricAdmin(PerformanceMetric, self.site)
        self.metric = PerformanceMetric.objects.create(
            metric_type='page_load',
            value=1.5,
            unit='seconds',
            page_url='/test/',
            timestamp=timezone.now()
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('metric_type', self.admin.list_display)
        self.assertIn('value', self.admin.list_display)
        self.assertIn('timestamp', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('metric_type', self.admin.list_filter)
        self.assertIn('timestamp', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('page_url', self.admin.search_fields)
        self.assertIn('user_agent', self.admin.search_fields)


class PageViewAdminTest(DashboardAdminTestCase):
    """Test PageViewAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = PageViewAdmin(PageView, self.site)
        self.page_view = PageView.objects.create(
            page_title='Test Page',
            page_url='/test/',
            load_time=1.5,
            timestamp=timezone.now()
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('page_title', self.admin.list_display)
        self.assertIn('page_url', self.admin.list_display)
        self.assertIn('load_time', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('is_mobile', self.admin.list_filter)
        self.assertIn('timestamp', self.admin.list_filter)


class ErrorLogAdminTest(DashboardAdminTestCase):
    """Test ErrorLogAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = ErrorLogAdmin(ErrorLog, self.site)
        self.error_log = ErrorLog.objects.create(
            error_type='404',
            error_message='Test error',
            page_url='/test/',
            resolved=False
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('error_type', self.admin.list_display)
        self.assertIn('error_message', self.admin.list_display)
        self.assertIn('resolved', self.admin.list_display)
    
    def test_mark_as_resolved_action(self):
        """Test mark as resolved action"""
        queryset = ErrorLog.objects.filter(id=self.error_log.id)
        self.admin.mark_as_resolved(self.request, queryset)
        self.error_log.refresh_from_db()
        self.assertTrue(self.error_log.resolved)
    
    def test_actions(self):
        """Test admin actions"""
        self.assertIn('mark_as_resolved', self.admin.actions)


class UserSessionAdminTest(DashboardAdminTestCase):
    """Test UserSessionAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = UserSessionAdmin(UserSession, self.site)
        self.session = UserSession.objects.create(
            session_id='test_session',
            user=self.admin_user,
            ip_address='127.0.0.1',
            start_time=timezone.now()
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('session_id', self.admin.list_display)
        self.assertIn('user', self.admin.list_display)
        self.assertIn('start_time', self.admin.list_display)


class PerformanceReportAdminTest(DashboardAdminTestCase):
    """Test PerformanceReportAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = PerformanceReportAdmin(PerformanceReport, self.site)
        self.report = PerformanceReport.objects.create(
            report_type='daily',
            start_date=timezone.now(),
            end_date=timezone.now(),
            generated_at=timezone.now(),
            generated_by=self.admin_user,
            report_data={'total_requests': 100, 'avg_load_time': 1.5}
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('report_type', self.admin.list_display)
        self.assertIn('generated_at', self.admin.list_display)
        self.assertIn('generated_by', self.admin.list_display)


class PerformanceAlertAdminTest(DashboardAdminTestCase):
    """Test PerformanceAlertAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = PerformanceAlertAdmin(PerformanceAlert, self.site)
        self.alert = PerformanceAlert.objects.create(
            alert_type='load_time',
            threshold_value=2.0,
            severity='high',
            is_active=True,
            created_by=self.admin_user
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('alert_type', self.admin.list_display)
        self.assertIn('threshold_value', self.admin.list_display)
        self.assertIn('severity', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)


class AlertLogAdminTest(DashboardAdminTestCase):
    """Test AlertLogAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = AlertLogAdmin(AlertLog, self.site)
        self.alert = PerformanceAlert.objects.create(
            alert_type='load_time',
            threshold_value=2.0,
            severity='high',
            is_active=True
        )
        self.alert_log = AlertLog.objects.create(
            alert=self.alert,
            current_value=3.0,
            message='Page load time exceeded threshold'
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('alert', self.admin.list_display)
        self.assertIn('current_value', self.admin.list_display)
        self.assertIn('triggered_at', self.admin.list_display)
        self.assertIn('is_resolved', self.admin.list_display)


class DashboardWidgetAdminTest(DashboardAdminTestCase):
    """Test DashboardWidgetAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = DashboardWidgetAdmin(DashboardWidget, self.site)
        self.widget = DashboardWidget.objects.create(
            name='Test Widget',
            widget_type='chart',
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('widget_type', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)


class AuditLogAdminTest(DashboardAdminTestCase):
    """Test AuditLogAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = AuditLogAdmin(AuditLog, self.site)
        self.audit_log = AuditLog.objects.create(
            user=self.admin_user,
            action_type='dashboard_access',
            description='User accessed dashboard',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('user', self.admin.list_display)
        self.assertIn('action_type', self.admin.list_display)
        self.assertIn('timestamp', self.admin.list_display)
        self.assertIn('description', self.admin.list_display)
    
    def test_get_queryset(self):
        """Test queryset optimization"""
        queryset = self.admin.get_queryset(self.request)
        self.assertIsNotNone(queryset)

