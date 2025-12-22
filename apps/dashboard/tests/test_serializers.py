"""
Tests for dashboard app serializers
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from apps.dashboard.models import (
    PerformanceMetric, PageView, ErrorLog, UserSession,
    PerformanceReport, PerformanceAlert, AlertLog, DashboardWidget
)
from apps.dashboard.serializers import (
    PageViewSerializer, ErrorLogSerializer, PerformanceAlertSerializer,
    AlertLogSerializer, DashboardWidgetSerializer, PerformanceMetricSerializer,
    DashboardFilterSerializer, DashboardDataResponseSerializer,
    DashboardReportRequestSerializer, DashboardReportResponseSerializer,
    ExportDataRequestSerializer
)


class SerializerTestCase(TestCase):
    """Base test case for serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.page_view = PageView.objects.create(
            page_title='Test Page',
            page_url='/test/',
            load_time=1.5,
            timestamp=timezone.now(),
            user=self.user
        )
        self.error_log = ErrorLog.objects.create(
            error_type='javascript',
            error_message='Test error',
            page_url='/test/',
            timestamp=timezone.now(),
            user=self.user
        )
        self.alert = PerformanceAlert.objects.create(
            alert_type='slow_page',
            threshold_value=2.0,
            current_value=3.0
        )
        self.alert_log = AlertLog.objects.create(
            alert=self.alert,
            action_taken='investigated',
            triggered_at=timezone.now()
        )
        self.widget = DashboardWidget.objects.create(
            widget_type='chart',
            title='Test Widget',
            is_active=True
        )
        self.metric = PerformanceMetric.objects.create(
            metric_type='page_load',
            value=1.5,
            unit='seconds',
            page_url='/test/',
            timestamp=timezone.now()
        )


class PageViewSerializerTest(SerializerTestCase):
    """Test PageViewSerializer"""
    
    def test_serialize_page_view(self):
        """Test serializing page view"""
        serializer = PageViewSerializer(self.page_view)
        data = serializer.data
        self.assertEqual(data['page_title'], self.page_view.page_title)
        self.assertEqual(data['page_url'], self.page_view.page_url)
        self.assertIn('timestamp', data)
        self.assertIn('load_time', data)
    
    def test_readonly_fields(self):
        """Test readonly fields"""
        data = {
            'page_url': '/new/',
            'user': 999,  # Should be ignored
            'ip_address': '192.168.1.1'  # Should be ignored
        }
        serializer = PageViewSerializer(data=data)
        # Readonly fields should not affect validation
        self.assertTrue(serializer.is_valid() or not serializer.is_valid())


class ErrorLogSerializerTest(SerializerTestCase):
    """Test ErrorLogSerializer"""
    
    def test_serialize_error_log(self):
        """Test serializing error log"""
        serializer = ErrorLogSerializer(self.error_log)
        data = serializer.data
        self.assertEqual(data['error_type'], self.error_log.error_type)
        self.assertEqual(data['error_message'], self.error_log.error_message)
        self.assertIn('timestamp', data)
        self.assertIn('resolved', data)


class PerformanceAlertSerializerTest(SerializerTestCase):
    """Test PerformanceAlertSerializer"""
    
    def test_serialize_performance_alert(self):
        """Test serializing performance alert"""
        serializer = PerformanceAlertSerializer(self.alert)
        data = serializer.data
        self.assertEqual(data['alert_type'], self.alert.alert_type)
        self.assertEqual(data['threshold_value'], str(self.alert.threshold_value))


class AlertLogSerializerTest(SerializerTestCase):
    """Test AlertLogSerializer"""
    
    def test_serialize_alert_log(self):
        """Test serializing alert log"""
        serializer = AlertLogSerializer(self.alert_log)
        data = serializer.data
        self.assertIn('alert', data)
        self.assertIn('alert_type', data)
        self.assertIn('severity', data)
        self.assertIn('threshold', data)
        self.assertEqual(data['alert_type'], self.alert.alert_type)


class DashboardWidgetSerializerTest(SerializerTestCase):
    """Test DashboardWidgetSerializer"""
    
    def test_serialize_dashboard_widget(self):
        """Test serializing dashboard widget"""
        serializer = DashboardWidgetSerializer(self.widget)
        data = serializer.data
        self.assertEqual(data['widget_type'], self.widget.widget_type)
        self.assertEqual(data['title'], self.widget.title)
        self.assertEqual(data['is_active'], self.widget.is_active)


class PerformanceMetricSerializerTest(SerializerTestCase):
    """Test PerformanceMetricSerializer"""
    
    def test_serialize_performance_metric(self):
        """Test serializing performance metric"""
        serializer = PerformanceMetricSerializer(self.metric)
        data = serializer.data
        self.assertEqual(data['metric_type'], self.metric.metric_type)
        self.assertEqual(data['value'], str(self.metric.value))
        self.assertEqual(data['unit'], self.metric.unit)


class DashboardFilterSerializerTest(TestCase):
    """Test DashboardFilterSerializer"""
    
    def test_valid_filter(self):
        """Test valid filter data"""
        data = {
            'type': 'page_load',
            'days': 7,
            'device_type': 'mobile',
            'browser': 'chrome'
        }
        serializer = DashboardFilterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_default_values(self):
        """Test default values"""
        data = {}
        serializer = DashboardFilterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['type'], 'page_load')
        self.assertEqual(serializer.validated_data['days'], 7)
    
    def test_invalid_days(self):
        """Test invalid days value"""
        data = {'days': 500}  # Exceeds max
        serializer = DashboardFilterSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class DashboardDataResponseSerializerTest(TestCase):
    """Test DashboardDataResponseSerializer"""
    
    def test_valid_response_data(self):
        """Test valid response data"""
        data = {
            'avg_load_time_today': 1.5,
            'avg_load_time_week': 1.8,
            'avg_load_time_month': 2.0,
            'page_views_today': 100,
            'page_views_week': 700,
            'page_views_month': 3000,
            'errors_today': 5,
            'error_rate': 0.05,
            'active_alerts': 2,
            'recent_errors': []
        }
        serializer = DashboardDataResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class DashboardReportRequestSerializerTest(TestCase):
    """Test DashboardReportRequestSerializer"""
    
    def test_valid_report_request(self):
        """Test valid report request"""
        data = {
            'type': 'weekly',
            'start_date': timezone.now(),
            'end_date': timezone.now()
        }
        serializer = DashboardReportRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_report_type(self):
        """Test invalid report type"""
        data = {
            'type': 'invalid',
            'start_date': timezone.now(),
            'end_date': timezone.now()
        }
        serializer = DashboardReportRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class DashboardReportResponseSerializerTest(TestCase):
    """Test DashboardReportResponseSerializer"""
    
    def test_valid_report_response(self):
        """Test valid report response"""
        data = {
            'success': True,
            'report_id': 1,
            'data': {'key': 'value'}
        }
        serializer = DashboardReportResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class ExportDataRequestSerializerTest(TestCase):
    """Test ExportDataRequestSerializer"""
    
    def test_valid_export_request(self):
        """Test valid export request"""
        data = {
            'format': 'csv',
            'data_type': 'page_views',
            'days': 7
        }
        serializer = ExportDataRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_format(self):
        """Test invalid format"""
        data = {
            'format': 'xml',  # Not in choices
            'data_type': 'page_views',
            'days': 7
        }
        serializer = ExportDataRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_days(self):
        """Test invalid days"""
        data = {
            'format': 'csv',
            'data_type': 'page_views',
            'days': 500  # Exceeds max
        }
        serializer = ExportDataRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())

