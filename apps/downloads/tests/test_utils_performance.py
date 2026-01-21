"""
Tests for downloads utils performance module
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock
import time

from apps.downloads.utils.performance import (
    get_client_ip_from_meta,
    track_performance,
    track_download_performance,
    track_bulk_download_performance,
    track_api_response_time,
    track_cache_performance,
    SLOW_OPERATION_THRESHOLD_MS
)

class UtilsPerformanceTest(TestCase):
    """Test utils/performance.py functions"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.request = self.factory.get('/')
        self.request.user = self.user

    def test_get_client_ip_from_meta(self):
        # Test X-Forwarded-For
        meta = {'HTTP_X_FORWARDED_FOR': '10.0.0.1, 192.168.1.1'}
        self.assertEqual(get_client_ip_from_meta(meta), '10.0.0.1')
        
        # Test Remote-Addr
        meta = {'REMOTE_ADDR': '127.0.0.1'}
        self.assertEqual(get_client_ip_from_meta(meta), '127.0.0.1')
        
        # Test empty
        self.assertEqual(get_client_ip_from_meta({}), '')

    @patch('apps.downloads.utils.performance.logger')
    @patch('apps.downloads.utils.performance.connection')
    def test_track_performance_decorator(self, mock_connection, mock_logger):
        # Mock connection.queries
        mock_connection.queries = []
        
        @track_performance(metric_type='test_metric')
        def test_func():
            time.sleep(0.01) # Small delay
            return "success"
            
        result = test_func()
        self.assertEqual(result, "success")
        
        # Verify metric creation attempt (even if PerformanceMetric is mocked/None)
        # We can simulate PerformanceMetric being available or not
        
    @patch('apps.downloads.utils.performance.PerformanceMetric')
    def test_track_download_performance(self, mock_metric):
        # Mock availability
        with patch('apps.downloads.utils.performance.PERFORMANCE_METRIC_AVAILABLE', True):
            track_download_performance(
                download_time=100.0,
                file_size=1024,
                request_meta=self.request.META,
                user=self.user,
                file_id=1
            )
            mock_metric.objects.create.assert_called_once()
            
    @patch('apps.downloads.utils.performance.PerformanceMetric')
    def test_track_bulk_download_performance(self, mock_metric):
        with patch('apps.downloads.utils.performance.PERFORMANCE_METRIC_AVAILABLE', True):
            track_bulk_download_performance(
                total_time=200.0,
                file_count=5,
                total_size=5000,
                request_meta=self.request.META,
                user=self.user
            )
            mock_metric.objects.create.assert_called_once()
            
    @patch('apps.downloads.utils.performance.PerformanceMetric')
    def test_track_api_response_time(self, mock_metric):
        with patch('apps.downloads.utils.performance.PERFORMANCE_METRIC_AVAILABLE', True):
            track_api_response_time(
                response_time=50.0,
                endpoint='/api/test',
                request_meta=self.request.META
            )
            mock_metric.objects.create.assert_called_once()

    @patch('apps.downloads.utils.performance.PerformanceMetric')
    def test_track_cache_performance(self, mock_metric):
        with patch('apps.downloads.utils.performance.PERFORMANCE_METRIC_AVAILABLE', True):
            track_cache_performance(
                operation='get',
                cache_key='test_key',
                hit=True,
                lookup_time=5.0,
                request_meta=self.request.META
            )
            mock_metric.objects.create.assert_called_once()

    def test_performance_metric_unavailable(self):
        """Test behavior when performance metric is not available"""
        with patch('apps.downloads.utils.performance.PERFORMANCE_METRIC_AVAILABLE', False):
            # Should not raise any errors
            track_download_performance(
                download_time=100.0,
                file_size=1024,
                request_meta=self.request.META,
                user=self.user,
                file_id=1
            )
            
            track_bulk_download_performance(
                total_time=200.0,
                file_count=5,
                total_size=5000,
                request_meta=self.request.META,
                user=self.user
            )
            
            track_cache_performance(
                operation='get',
                cache_key='key',
                hit=True,
                lookup_time=1.0
            ) 
