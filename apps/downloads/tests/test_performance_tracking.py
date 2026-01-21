"""
Tests for Downloads app performance tracking utilities.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

from apps.downloads.utils.performance import (
    track_performance,
    track_download_performance,
    track_bulk_download_performance,
    track_api_response_time,
    track_cache_performance,
    get_client_ip_from_meta,
    SLOW_OPERATION_THRESHOLD_MS
)


class PerformanceTrackingTest(TestCase):
    """Test cases for performance tracking utilities"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_get_client_ip_from_meta(self):
        """Test get_client_ip_from_meta function"""
        meta = {'REMOTE_ADDR': '192.168.1.100'}
        ip = get_client_ip_from_meta(meta)
        self.assertEqual(ip, '192.168.1.100')
    
    def test_get_client_ip_from_meta_x_forwarded_for(self):
        """Test get_client_ip_from_meta with X-Forwarded-For"""
        meta = {
            'HTTP_X_FORWARDED_FOR': '203.0.113.1, 192.168.1.1',
            'REMOTE_ADDR': '192.168.1.100'
        }
        ip = get_client_ip_from_meta(meta)
        self.assertEqual(ip, '203.0.113.1')
    
    @patch('apps.downloads.utils.performance.PERFORMANCE_METRIC_AVAILABLE', False)
    def test_track_performance_decorator_no_metric_model(self):
        """Test track_performance decorator when PerformanceMetric not available"""
        @track_performance('test_operation')
        def test_function():
            return "result"
        
        result = test_function()
        self.assertEqual(result, "result")
    
    @patch('apps.downloads.utils.performance.PERFORMANCE_METRIC_AVAILABLE', False)
    def test_track_download_performance_no_metric_model(self):
        """Test track_download_performance when PerformanceMetric not available"""
        request_meta = {'REMOTE_ADDR': '192.168.1.100', 'HTTP_USER_AGENT': 'Test Browser'}
        
        # Should not raise exception
        track_download_performance(
            100.0,  # download_time
            1024000,  # file_size
            request_meta,
            self.user,
            'session123',
            1  # file_id
        )
    
    @patch('apps.downloads.utils.performance.PERFORMANCE_METRIC_AVAILABLE', True)
    @patch('apps.downloads.utils.performance.PerformanceMetric')
    def test_track_download_performance_with_metric_model(self, mock_performance_metric):
        """Test track_download_performance with PerformanceMetric available"""
        mock_performance_metric.objects.create = MagicMock()
        request_meta = {'REMOTE_ADDR': '192.168.1.100', 'HTTP_USER_AGENT': 'Test Browser'}
        
        track_download_performance(
            100.0,
            1024000,
            request_meta,
            self.user,
            'session123',
            1
        )
        
        # Should create performance metric
        mock_performance_metric.objects.create.assert_called_once()
        call_args = mock_performance_metric.objects.create.call_args[1]
        self.assertEqual(call_args['metric_type'], 'file_download')
        self.assertEqual(call_args['value'], 100.0)
        self.assertEqual(call_args['unit'], 'ms')
        self.assertIn('file_size', call_args['additional_data'])
        self.assertIn('file_id', call_args['additional_data'])
