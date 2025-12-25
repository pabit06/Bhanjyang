"""
Tests for contact app performance module
"""
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from apps.contact.performance import (
    ContactPerformanceMonitor, ContactAnalytics, monitor_contact_performance
)
from apps.contact.models import ContactSubmission


class ContactPerformanceMonitorTest(TestCase):
    """Test ContactPerformanceMonitor"""
    
    def setUp(self):
        cache.clear()
    
    def test_log_form_submission_performance(self):
        """Test logging form submission performance"""
        ContactPerformanceMonitor.log_form_submission_performance(
            submission_id='test_123',
            processing_time=0.5,
            db_queries_count=3,
            success=True
        )
        # Check cache
        cache_key = 'contact_performance_test_123'
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['processing_time'], 0.5)
        self.assertEqual(cached_data['db_queries'], 3)
        self.assertTrue(cached_data['success'])
    
    def test_log_form_submission_performance_error(self):
        """Test logging form submission performance with error"""
        ContactPerformanceMonitor.log_form_submission_performance(
            submission_id='test_456',
            processing_time=0.3,
            db_queries_count=2,
            success=False
        )
        cache_key = 'contact_performance_test_456'
        cached_data = cache.get(cache_key)
        self.assertFalse(cached_data['success'])
    
    def test_get_performance_stats(self):
        """Test getting performance statistics"""
        stats = ContactPerformanceMonitor.get_performance_stats(days=7)
        self.assertIn('avg_processing_time', stats)
        self.assertIn('avg_db_queries', stats)
        self.assertIn('success_rate', stats)
        self.assertIn('total_submissions', stats)
        self.assertIn('period', stats)
    
    def test_check_performance_thresholds(self):
        """Test checking performance thresholds"""
        result = ContactPerformanceMonitor.check_performance_thresholds()
        self.assertTrue(result)


class MonitorContactPerformanceDecoratorTest(TestCase):
    """Test monitor_contact_performance decorator"""
    
    def setUp(self):
        cache.clear()
    
    @monitor_contact_performance
    def decorated_function(self, request):
        """Test function for decorator"""
        return {'success': True}
    
    def test_decorator_success(self):
        """Test decorator with successful execution"""
        request = MagicMock()
        request.id = 'test_request_123'
        result = self.decorated_function(request)
        self.assertEqual(result['success'], True)
    
    def test_decorator_error(self):
        """Test decorator with error"""
        @monitor_contact_performance
        def failing_function(request):
            raise ValueError("Test error")
        
        request = MagicMock()
        request.id = 'test_request_456'
        with self.assertRaises(ValueError):
            failing_function(request)


class ContactAnalyticsTest(TestCase):
    """Test ContactAnalytics"""
    
    def setUp(self):
        self.submission = ContactSubmission.objects.create(
            name='Test User',
            email='test@example.com',
            subject='Test Subject',
            message='Test message',
            ip_address='127.0.0.1',
            created_at=timezone.now() - timedelta(days=1)
        )
    
    def test_get_submission_trends(self):
        """Test getting submission trends"""
        trends = ContactAnalytics.get_submission_trends(days=30)
        self.assertIn('daily_counts', trends)
        self.assertIn('total_submissions', trends)
        self.assertIn('period', trends)
        self.assertGreaterEqual(trends['total_submissions'], 1)
    
    def test_get_submission_trends_empty(self):
        """Test getting submission trends with no submissions"""
        ContactSubmission.objects.all().delete()
        trends = ContactAnalytics.get_submission_trends(days=30)
        self.assertEqual(trends['total_submissions'], 0)
    
    def test_get_response_time_analytics(self):
        """Test getting response time analytics"""
        # Create resolved submission
        self.submission.status = 'resolved'
        self.submission.resolved_at = timezone.now()
        self.submission.save()
        
        analytics = ContactAnalytics.get_response_time_analytics()
        self.assertIn('avg_response_hours', analytics)
        self.assertIn('resolved_count', analytics)
        self.assertGreaterEqual(analytics['resolved_count'], 1)
    
    def test_get_response_time_analytics_no_resolved(self):
        """Test getting response time analytics with no resolved submissions"""
        ContactSubmission.objects.filter(status='resolved').update(status='pending')
        analytics = ContactAnalytics.get_response_time_analytics()
        self.assertEqual(analytics['resolved_count'], 0)

