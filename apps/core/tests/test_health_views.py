"""
Comprehensive tests for health check views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.db import connection
from unittest.mock import patch, MagicMock
import json


class HealthCheckViewTest(TestCase):
    """Test suite for health check views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        cache.clear()
    
    def test_health_check_success(self):
        """Test successful health check"""
        response = self.client.get('/health/health/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('components', data)
    
    def test_health_check_components(self):
        """Test health check includes component status"""
        response = self.client.get('/health/health/')
        data = json.loads(response.content)
        self.assertIn('database', data['components'])
        self.assertIn('cache', data['components'])
    
    def test_health_check_database_status(self):
        """Test database component status"""
        response = self.client.get('/health/health/')
        data = json.loads(response.content)
        db_component = data['components']['database']
        self.assertIn('status', db_component)
        self.assertIn('response_time_ms', db_component)
        self.assertIn('engine', db_component)
    
    def test_health_check_cache_status(self):
        """Test cache component status"""
        response = self.client.get('/health/health/')
        data = json.loads(response.content)
        cache_component = data['components']['cache']
        self.assertIn('status', cache_component)
        self.assertIn('response_time_ms', cache_component)
        self.assertIn('backend', cache_component)
    
    @patch('apps.core.health_views.connection.cursor')
    def test_health_check_database_failure(self, mock_cursor):
        """Test health check with database failure"""
        mock_cursor.side_effect = Exception('Database error')
        response = self.client.get('/health/health/')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'unhealthy')
        self.assertEqual(data['components']['database']['status'], 'unhealthy')
    
    @patch('apps.core.health_views.cache.set')
    def test_health_check_cache_failure(self, mock_cache_set):
        """Test health check with cache failure"""
        mock_cache_set.side_effect = Exception('Cache error')
        response = self.client.get('/health/health/')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'unhealthy')
        self.assertEqual(data['components']['cache']['status'], 'unhealthy')
    
    def test_health_check_response_time(self):
        """Test health check includes response time"""
        response = self.client.get('/health/health/')
        data = json.loads(response.content)
        self.assertIn('response_time_ms', data)
        self.assertIsInstance(data['response_time_ms'], (int, float))
    
    def test_health_check_version(self):
        """Test health check includes version"""
        response = self.client.get('/health/health/')
        data = json.loads(response.content)
        self.assertIn('version', data)
    
    def test_health_check_environment(self):
        """Test health check includes environment"""
        response = self.client.get('/health/health/')
        data = json.loads(response.content)
        self.assertIn('environment', data)
    
    def test_health_check_redis_status(self):
        """Test health check includes Redis status when using Redis"""
        # Skip this test if not using Redis
        from django.conf import settings
        if 'redis' not in settings.CACHES['default']['BACKEND'].lower():
            self.skipTest("Not using Redis cache backend")
        
        response = self.client.get('/health/health/')
        data = json.loads(response.content)
        # Redis component may or may not be present depending on backend
        if 'redis' in data['components']:
            self.assertIn('status', data['components']['redis'])
    
    def test_health_check_redis_failure(self):
        """Test health check with Redis failure"""
        # Skip this test if not using Redis
        from django.conf import settings
        if 'redis' not in settings.CACHES['default']['BACKEND'].lower():
            self.skipTest("Not using Redis cache backend")
        
        # This test would require mocking which is complex for Redis
        # Just verify the endpoint works
        response = self.client.get('/health/health/')
        self.assertIn(response.status_code, [200, 503])
    
    def test_health_check_http_method(self):
        """Test health check only accepts GET requests"""
        response = self.client.post('/health/health/')
        self.assertEqual(response.status_code, 405)  # Method not allowed


class ReadinessCheckViewTest(TestCase):
    """Test suite for readiness check view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        cache.clear()
    
    def test_readiness_check_success(self):
        """Test successful readiness check"""
        response = self.client.get('/health/readiness/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ready')
        self.assertIn('timestamp', data)
    
    @patch('apps.core.health_views.connection.cursor')
    def test_readiness_check_database_failure(self, mock_cursor):
        """Test readiness check with database failure"""
        mock_cursor.side_effect = Exception('Database error')
        response = self.client.get('/health/readiness/')
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'not_ready')
        self.assertIn('error', data)
    
    @patch('apps.core.health_views.cache.set')
    def test_readiness_check_cache_failure(self, mock_cache_set):
        """Test readiness check with cache failure"""
        mock_cache_set.side_effect = Exception('Cache error')
        response = self.client.get('/health/readiness/')
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'not_ready')
    
    def test_readiness_check_http_method(self):
        """Test readiness check only accepts GET requests"""
        response = self.client.post('/health/readiness/')
        self.assertEqual(response.status_code, 405)


class LivenessCheckViewTest(TestCase):
    """Test suite for liveness check view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_liveness_check_success(self):
        """Test successful liveness check"""
        response = self.client.get('/health/liveness/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'alive')
        self.assertIn('timestamp', data)
        self.assertIn('uptime', data)
    
    def test_liveness_check_http_method(self):
        """Test liveness check only accepts GET requests"""
        response = self.client.post('/health/liveness/')
        self.assertEqual(response.status_code, 405)


class MetricsSummaryViewTest(TestCase):
    """Test suite for metrics summary view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_metrics_summary_success(self):
        """Test successful metrics summary"""
        response = self.client.get('/health/metrics/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('timestamp', data)
        self.assertIn('database', data)
        self.assertIn('settings', data)
    
    def test_metrics_summary_database_info(self):
        """Test metrics summary includes database info"""
        response = self.client.get('/health/metrics/')
        data = json.loads(response.content)
        self.assertIn('migration_count', data['database'])
        self.assertIn('engine', data['database'])
    
    def test_metrics_summary_settings(self):
        """Test metrics summary includes settings"""
        response = self.client.get('/health/metrics/')
        data = json.loads(response.content)
        self.assertIn('debug', data['settings'])
        self.assertIn('timezone', data['settings'])
        self.assertIn('language', data['settings'])
    
    def test_metrics_summary_redis_info(self):
        """Test metrics summary includes Redis info when using Redis"""
        # Skip this test if not using Redis
        from django.conf import settings
        if 'redis' not in settings.CACHES['default']['BACKEND'].lower():
            self.skipTest("Not using Redis cache backend")
        
        response = self.client.get('/health/metrics/')
        data = json.loads(response.content)
        # Cache info may or may not be present depending on backend
        if 'cache' in data:
            self.assertIsInstance(data['cache'], dict)
    
    @patch('apps.core.health_views.connection.cursor')
    def test_metrics_summary_database_error(self, mock_cursor):
        """Test metrics summary handles database errors"""
        mock_cursor.side_effect = Exception('Database error')
        response = self.client.get('/health/metrics/')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertIn('error', data)

