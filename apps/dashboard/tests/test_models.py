"""
Comprehensive tests for dashboard app models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from apps.dashboard.models import (
    PerformanceMetric, PageView, ErrorLog, UserSession,
    PerformanceReport, PerformanceAlert, AlertLog,
    DashboardWidget, UserDashboardPreference, AuditLog
)

User = get_user_model()


class PerformanceMetricModelTest(TestCase):
    """Test suite for PerformanceMetric model"""
    
    def setUp(self):
        """Set up test data"""
        self.metric = PerformanceMetric.objects.create(
            metric_type='page_load',
            page_url='https://example.com/test',
            value=150.5,
            unit='ms',
            ip_address='192.168.1.1'
        )
    
    def test_metric_creation(self):
        """Test basic metric creation"""
        self.assertEqual(self.metric.metric_type, 'page_load')
        self.assertEqual(self.metric.value, 150.5)
        self.assertEqual(self.metric.unit, 'ms')
        self.assertIsNotNone(self.metric.timestamp)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('page_load', str(self.metric))
        self.assertIn('150.5', str(self.metric))
        self.assertIn('ms', str(self.metric))
    
    def test_metric_type_choices(self):
        """Test metric type choices"""
        types = ['page_load', 'image_load', 'search_time', 'form_submit',
                 'api_response', 'database_query', 'memory_usage', 'cpu_usage']
        for metric_type in types:
            metric = PerformanceMetric.objects.create(
                metric_type=metric_type,
                value=100.0,
                ip_address='192.168.1.1'
            )
            self.assertEqual(metric.metric_type, metric_type)
    
    def test_ordering(self):
        """Test model ordering"""
        metric2 = PerformanceMetric.objects.create(
            metric_type='image_load',
            value=200.0,
            ip_address='192.168.1.2'
        )
        metrics = list(PerformanceMetric.objects.all())
        # Should be ordered by -timestamp (newest first)
        self.assertEqual(metrics[0], metric2)
        self.assertEqual(metrics[1], self.metric)
    
    def test_additional_data_json(self):
        """Test additional_data JSON field"""
        metric = PerformanceMetric.objects.create(
            metric_type='page_load',
            value=100.0,
            ip_address='192.168.1.1',
            additional_data={'browser': 'Chrome', 'version': '91'}
        )
        self.assertEqual(metric.additional_data['browser'], 'Chrome')


class PageViewModelTest(TestCase):
    """Test suite for PageView model"""
    
    def setUp(self):
        """Set up test data"""
        self.page_view = PageView.objects.create(
            page_url='https://example.com/test',
            page_title='Test Page',
            load_time=250.5,
            ip_address='192.168.1.1'
        )
    
    def test_page_view_creation(self):
        """Test basic page view creation"""
        self.assertEqual(self.page_view.page_url, 'https://example.com/test')
        self.assertEqual(self.page_view.page_title, 'Test Page')
        self.assertEqual(self.page_view.load_time, 250.5)
        self.assertIsNotNone(self.page_view.timestamp)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('Test Page', str(self.page_view))
        self.assertIn('250.5ms', str(self.page_view))
    
    def test_ordering(self):
        """Test model ordering"""
        page_view2 = PageView.objects.create(
            page_url='https://example.com/test2',
            page_title='Test Page 2',
            load_time=300.0,
            ip_address='192.168.1.2'
        )
        page_views = list(PageView.objects.all())
        # Should be ordered by -timestamp (newest first)
        self.assertEqual(page_views[0], page_view2)
        self.assertEqual(page_views[1], self.page_view)


class ErrorLogModelTest(TestCase):
    """Test suite for ErrorLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.error_log = ErrorLog.objects.create(
            error_type='404',
            error_message='Page not found',
            page_url='https://example.com/missing',
            ip_address='192.168.1.1'
        )
    
    def test_error_log_creation(self):
        """Test basic error log creation"""
        self.assertEqual(self.error_log.error_type, '404')
        self.assertEqual(self.error_log.error_message, 'Page not found')
        self.assertFalse(self.error_log.resolved)
        self.assertIsNotNone(self.error_log.timestamp)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('404', str(self.error_log))
        self.assertIn('Page not found', str(self.error_log))
    
    def test_error_type_choices(self):
        """Test error type choices"""
        types = ['404', '500', 'template', 'database', 'validation', 
                 'permission', 'timeout']
        for error_type in types:
            error = ErrorLog.objects.create(
                error_type=error_type,
                error_message=f'Test {error_type} error',
                ip_address='192.168.1.1'
            )
            self.assertEqual(error.error_type, error_type)
    
    def test_ordering(self):
        """Test model ordering"""
        error2 = ErrorLog.objects.create(
            error_type='500',
            error_message='Server error',
            ip_address='192.168.1.2'
        )
        errors = list(ErrorLog.objects.all())
        # Should be ordered by -timestamp (newest first)
        self.assertEqual(errors[0], error2)
        self.assertEqual(errors[1], self.error_log)


class UserSessionModelTest(TestCase):
    """Test suite for UserSession model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = UserSession.objects.create(
            session_id='test_session_123',
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Test Agent',
            page_views=5,
            total_load_time=1000.0
        )
    
    def test_session_creation(self):
        """Test basic session creation"""
        self.assertEqual(self.session.session_id, 'test_session_123')
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.page_views, 5)
        self.assertIsNotNone(self.session.start_time)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('test_session_123', str(self.session))
        self.assertIn('5 views', str(self.session))
    
    def test_unique_session_id(self):
        """Test that session_id must be unique"""
        with self.assertRaises(Exception):  # IntegrityError
            UserSession.objects.create(
                session_id='test_session_123',
                ip_address='192.168.1.2',
                user_agent='Test Agent'
            )
    
    def test_ordering(self):
        """Test model ordering"""
        session2 = UserSession.objects.create(
            session_id='test_session_456',
            ip_address='192.168.1.2',
            user_agent='Test Agent'
        )
        sessions = list(UserSession.objects.all())
        # Should be ordered by -start_time (newest first)
        self.assertEqual(sessions[0], session2)
        self.assertEqual(sessions[1], self.session)


class PerformanceReportModelTest(TestCase):
    """Test suite for PerformanceReport model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.report = PerformanceReport.objects.create(
            report_type='daily',
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now(),
            generated_by=self.user,
            report_data={'avg_load_time': 200.5, 'total_views': 1000}
        )
    
    def test_report_creation(self):
        """Test basic report creation"""
        self.assertEqual(self.report.report_type, 'daily')
        self.assertEqual(self.report.generated_by, self.user)
        self.assertIsNotNone(self.report.generated_at)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('daily', str(self.report))
        self.assertIn('Report', str(self.report))
    
    def test_report_type_choices(self):
        """Test report type choices"""
        types = ['daily', 'weekly', 'monthly', 'custom']
        for report_type in types:
            report = PerformanceReport.objects.create(
                report_type=report_type,
                start_date=timezone.now() - timedelta(days=1),
                end_date=timezone.now(),
                report_data={}
            )
            self.assertEqual(report.report_type, report_type)
    
    def test_ordering(self):
        """Test model ordering"""
        report2 = PerformanceReport.objects.create(
            report_type='weekly',
            start_date=timezone.now() - timedelta(days=7),
            end_date=timezone.now(),
            report_data={}
        )
        reports = list(PerformanceReport.objects.all())
        # Should be ordered by -generated_at (newest first)
        self.assertEqual(reports[0], report2)
        self.assertEqual(reports[1], self.report)


class PerformanceAlertModelTest(TestCase):
    """Test suite for PerformanceAlert model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.alert = PerformanceAlert.objects.create(
            alert_type='load_time',
            threshold_value=500.0,
            severity='high',
            description='Alert when load time exceeds 500ms',
            created_by=self.user
        )
    
    def test_alert_creation(self):
        """Test basic alert creation"""
        self.assertEqual(self.alert.alert_type, 'load_time')
        self.assertEqual(self.alert.threshold_value, 500.0)
        self.assertEqual(self.alert.severity, 'high')
        self.assertTrue(self.alert.is_active)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('load_time', str(self.alert))
        self.assertIn('500.0', str(self.alert))
        self.assertIn('high', str(self.alert))
    
    def test_check_threshold_method(self):
        """Test check_threshold method"""
        # Value below threshold
        self.assertFalse(self.alert.check_threshold(400.0))
        
        # Value above threshold
        self.assertTrue(self.alert.check_threshold(600.0))
    
    def test_alert_type_choices(self):
        """Test alert type choices"""
        types = ['load_time', 'error_rate', 'traffic_spike', 
                 'memory_usage', 'cpu_usage']
        for alert_type in types:
            alert = PerformanceAlert.objects.create(
                alert_type=alert_type,
                threshold_value=100.0,
                created_by=self.user
            )
            self.assertEqual(alert.alert_type, alert_type)
    
    def test_severity_choices(self):
        """Test severity choices"""
        severities = ['low', 'medium', 'high', 'critical']
        for severity in severities:
            alert = PerformanceAlert.objects.create(
                alert_type='load_time',
                threshold_value=100.0,
                severity=severity,
                created_by=self.user
            )
            self.assertEqual(alert.severity, severity)


class AlertLogModelTest(TestCase):
    """Test suite for AlertLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.alert = PerformanceAlert.objects.create(
            alert_type='load_time',
            threshold_value=500.0,
            created_by=self.user
        )
        self.alert_log = AlertLog.objects.create(
            alert=self.alert,
            current_value=600.0,
            message='Load time exceeded threshold'
        )
    
    def test_alert_log_creation(self):
        """Test basic alert log creation"""
        self.assertEqual(self.alert_log.alert, self.alert)
        self.assertEqual(self.alert_log.current_value, 600.0)
        self.assertFalse(self.alert_log.is_resolved)
        self.assertIsNotNone(self.alert_log.triggered_at)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('load_time', str(self.alert_log))
        self.assertIn(str(self.alert_log.triggered_at.date()), str(self.alert_log))
    
    def test_ordering(self):
        """Test model ordering"""
        alert_log2 = AlertLog.objects.create(
            alert=self.alert,
            current_value=700.0,
            message='Another alert'
        )
        logs = list(AlertLog.objects.all())
        # Should be ordered by -triggered_at (newest first)
        self.assertEqual(logs[0], alert_log2)
        self.assertEqual(logs[1], self.alert_log)


class DashboardWidgetModelTest(TestCase):
    """Test suite for DashboardWidget model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.widget = DashboardWidget.objects.create(
            name='Test Widget',
            widget_type='metric_card',
            position_x=0,
            position_y=0,
            width=4,
            height=3,
            config={'metric': 'page_views'},
            created_by=self.user
        )
    
    def test_widget_creation(self):
        """Test basic widget creation"""
        self.assertEqual(self.widget.name, 'Test Widget')
        self.assertEqual(self.widget.widget_type, 'metric_card')
        self.assertTrue(self.widget.is_active)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('Test Widget', str(self.widget))
        self.assertIn('metric_card', str(self.widget))
    
    def test_widget_type_choices(self):
        """Test widget type choices"""
        types = ['metric_card', 'chart', 'table', 'gauge', 'map']
        for widget_type in types:
            widget = DashboardWidget.objects.create(
                name=f'Test {widget_type}',
                widget_type=widget_type,
                created_by=self.user
            )
            self.assertEqual(widget.widget_type, widget_type)
    
    def test_ordering(self):
        """Test model ordering"""
        widget2 = DashboardWidget.objects.create(
            name='Test Widget 2',
            widget_type='chart',
            position_x=4,
            position_y=0,
            created_by=self.user
        )
        widgets = list(DashboardWidget.objects.all())
        # Should be ordered by position_y, position_x
        self.assertEqual(widgets[0], self.widget)  # y=0, x=0
        self.assertEqual(widgets[1], widget2)  # y=0, x=4


class UserDashboardPreferenceModelTest(TestCase):
    """Test suite for UserDashboardPreference model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.preference = UserDashboardPreference.objects.create(
            user=self.user,
            theme='dark',
            refresh_interval=60
        )
    
    def test_preference_creation(self):
        """Test basic preference creation"""
        self.assertEqual(self.preference.user, self.user)
        self.assertEqual(self.preference.theme, 'dark')
        self.assertEqual(self.preference.refresh_interval, 60)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('testuser', str(self.preference))
        self.assertIn('Dashboard Preferences', str(self.preference))
    
    def test_one_to_one_relationship(self):
        """Test that one user can only have one preference"""
        with self.assertRaises(Exception):  # IntegrityError
            UserDashboardPreference.objects.create(
                user=self.user,
                theme='light'
            )
    
    def test_theme_choices(self):
        """Test theme choices"""
        themes = ['light', 'dark', 'auto']
        for theme in themes:
            user = User.objects.create_user(
                username=f'testuser{theme}',
                email=f'test{theme}@example.com',
                password='testpass123'
            )
            preference = UserDashboardPreference.objects.create(
                user=user,
                theme=theme
            )
            self.assertEqual(preference.theme, theme)
    
    def test_widgets_many_to_many(self):
        """Test widgets many-to-many relationship"""
        widget1 = DashboardWidget.objects.create(
            name='Widget 1',
            widget_type='metric_card'
        )
        widget2 = DashboardWidget.objects.create(
            name='Widget 2',
            widget_type='chart'
        )
        
        self.preference.widgets.add(widget1, widget2)
        self.assertEqual(self.preference.widgets.count(), 2)


class AuditLogModelTest(TestCase):
    """Test suite for AuditLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.audit_log = AuditLog.objects.create(
            user=self.user,
            action_type='login',
            description='User logged in',
            ip_address='192.168.1.1',
            user_agent='Test Agent'
        )
    
    def test_audit_log_creation(self):
        """Test basic audit log creation"""
        self.assertEqual(self.audit_log.user, self.user)
        self.assertEqual(self.audit_log.action_type, 'login')
        self.assertIsNotNone(self.audit_log.timestamp)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn('login', str(self.audit_log))
        self.assertIn('testuser', str(self.audit_log))
    
    def test_action_type_choices(self):
        """Test action type choices"""
        types = ['login', 'logout', 'dashboard_access', 'data_export',
                 'alert_resolve', 'preference_update', 'admin_access', 
                 'suspicious_activity']
        for action_type in types:
            log = AuditLog.objects.create(
                user=self.user,
                action_type=action_type,
                description=f'Test {action_type}',
                ip_address='192.168.1.1'
            )
            self.assertEqual(log.action_type, action_type)
    
    def test_ordering(self):
        """Test model ordering"""
        log2 = AuditLog.objects.create(
            user=self.user,
            action_type='logout',
            description='User logged out',
            ip_address='192.168.1.1'
        )
        logs = list(AuditLog.objects.all())
        # Should be ordered by -timestamp (newest first)
        self.assertEqual(logs[0], log2)
        self.assertEqual(logs[1], self.audit_log)

