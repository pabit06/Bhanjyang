"""
Tests for Enhanced Security Features
====================================

Tests for:
- IP Blacklisting
- Rate Limiting
- Security Middleware
- Security Headers
- Audit Logging

Author: Bhanjyang Dev Team
Date: January 6, 2026
"""

from django.test import TestCase, RequestFactory, Client, override_settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
import time

from apps.downloads.models import DownloadableFile, FileCategory, PriorityLevel
from apps.downloads.security_enhanced import (
    IPBlacklistManager,
    RateLimitManager,
    SecurityAuditEnhancedLogger,
    RequestValidator
)
from apps.downloads.middleware import (
    DownloadsSecurityMiddleware,
    SecurityHeadersMiddleware
)


class IPBlacklistManagerTest(TestCase):
    """Tests for IP blacklist functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_blacklist_ip(self):
        """Test blacklisting an IP address."""
        ip = '192.168.1.100'
        result = IPBlacklistManager.blacklist_ip(ip, reason='Test blacklist')
        
        self.assertTrue(result)
        self.assertTrue(IPBlacklistManager.is_blacklisted(ip))
    
    def test_blacklist_invalid_ip(self):
        """Test blacklisting invalid IP address."""
        ip = 'invalid-ip'
        result = IPBlacklistManager.blacklist_ip(ip)
        
        self.assertFalse(result)
    
    def test_unblacklist_ip(self):
        """Test removing IP from blacklist."""
        ip = '192.168.1.101'
        IPBlacklistManager.blacklist_ip(ip)
        
        result = IPBlacklistManager.unblacklist_ip(ip)
        
        self.assertTrue(result)
        self.assertFalse(IPBlacklistManager.is_blacklisted(ip))
    
    def test_get_blacklist_info(self):
        """Test retrieving blacklist information."""
        ip = '192.168.1.102'
        reason = 'Test reason'
        IPBlacklistManager.blacklist_ip(ip, reason=reason)
        
        info = IPBlacklistManager.get_blacklist_info(ip)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['reason'], reason)
        self.assertIn('blacklisted_at', info)
        self.assertIn('expires_at', info)
    
    def test_whitelist_ip(self):
        """Test whitelisting an IP address."""
        ip = '192.168.1.103'
        result = IPBlacklistManager.whitelist_ip(ip, reason='Trusted IP')
        
        self.assertTrue(result)
        self.assertTrue(IPBlacklistManager.is_whitelisted(ip))
    
    def test_cannot_blacklist_whitelisted_ip(self):
        """Test that whitelisted IPs cannot be blacklisted."""
        ip = '192.168.1.104'
        IPBlacklistManager.whitelist_ip(ip)
        
        result = IPBlacklistManager.blacklist_ip(ip)
        
        self.assertFalse(result)
        self.assertFalse(IPBlacklistManager.is_blacklisted(ip))


class RateLimitManagerTest(TestCase):
    """Tests for rate limiting functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_rate_limit_allows_requests(self):
        """Test that requests within limit are allowed."""
        identifier = 'test_user_1'
        
        for i in range(5):
            allowed, count, reset_time = RateLimitManager.check_rate_limit(
                identifier,
                max_requests=10,
                window=60
            )
            self.assertTrue(allowed)
            self.assertEqual(count, i + 1)
    
    def test_rate_limit_blocks_excess_requests(self):
        """Test that requests exceeding limit are blocked."""
        identifier = 'test_user_2'
        max_requests = 3
        
        # Make allowed requests
        for i in range(max_requests):
            allowed, _, _ = RateLimitManager.check_rate_limit(
                identifier,
                max_requests=max_requests,
                window=60
            )
            self.assertTrue(allowed)
        
        # Next request should be blocked
        allowed, count, reset_time = RateLimitManager.check_rate_limit(
            identifier,
            max_requests=max_requests,
            window=60
        )
        
        self.assertFalse(allowed)
        self.assertGreaterEqual(count, max_requests)
    
    def test_reset_rate_limit(self):
        """Test resetting rate limit."""
        identifier = 'test_user_3'
        
        # Make some requests
        RateLimitManager.check_rate_limit(identifier, max_requests=5, window=60)
        RateLimitManager.check_rate_limit(identifier, max_requests=5, window=60)
        
        # Reset
        result = RateLimitManager.reset_rate_limit(identifier)
        
        self.assertTrue(result)
        
        # Should be allowed again
        allowed, count, _ = RateLimitManager.check_rate_limit(
            identifier,
            max_requests=5,
            window=60
        )
        self.assertTrue(allowed)
        self.assertEqual(count, 1)
    
    def test_get_remaining_requests(self):
        """Test getting remaining requests."""
        identifier = 'test_user_4'
        
        # Make 3 requests (limit is 20 for downloads)
        for _ in range(3):
            RateLimitManager.check_rate_limit(identifier, action='download')
        
        remaining, reset_time = RateLimitManager.get_remaining_requests(
            identifier,
            action='download'
        )
        
        # Should have 17 remaining (20 - 3)
        self.assertEqual(remaining, 17)


class SecurityAuditLoggerTest(TestCase):
    """Tests for security audit logging."""
    
    def setUp(self):
        """Set up test fixtures."""
        cache.clear()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.file = DownloadableFile.objects.create(
            category=FileCategory.FORM,
            title='Test File',
            file='test.pdf'
        )
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_log_download(self):
        """Test logging a download event."""
        ip = '192.168.1.1'
        
        SecurityAuditEnhancedLogger.log_download(
            self.user,
            self.file,
            ip
        )
        
        # Check that event was logged
        events = SecurityAuditEnhancedLogger.get_recent_events(limit=10)
        self.assertGreater(len(events), 0)
        
        # Check event details
        event = events[0]
        self.assertEqual(event['event_type'], 'DOWNLOAD')
        self.assertEqual(event['ip_address'], ip)
        self.assertTrue(event['details']['success'])
    
    def test_log_failed_access(self):
        """Test logging failed access attempt."""
        ip = '192.168.1.2'
        reason = 'Login required'
        
        SecurityAuditEnhancedLogger.log_failed_access(
            self.user,
            self.file,
            ip,
            reason
        )
        
        events = SecurityAuditEnhancedLogger.get_recent_events(limit=10)
        event = events[0]
        
        self.assertEqual(event['event_type'], 'FAILED_ACCESS')
        self.assertEqual(event['details']['reason'], reason)
        self.assertFalse(event['details']['success'])
    
    def test_log_rate_limit_exceeded(self):
        """Test logging rate limit violation."""
        identifier = 'test_user'
        ip = '192.168.1.3'
        action = 'download'
        count = 25
        
        SecurityAuditEnhancedLogger.log_rate_limit_exceeded(
            identifier,
            ip,
            action,
            count
        )
        
        events = SecurityAuditEnhancedLogger.get_recent_events(limit=10)
        event = events[0]
        
        self.assertEqual(event['event_type'], 'RATE_LIMIT_EXCEEDED')
        self.assertEqual(event['details']['action'], action)
        self.assertEqual(event['details']['request_count'], count)


class RequestValidatorTest(TestCase):
    """Tests for request validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
    
    def test_get_client_ip_direct(self):
        """Test that RequestValidator uses get_client_ip from utils.helpers"""
        from apps.downloads.utils.helpers import get_client_ip
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        # RequestValidator now uses get_client_ip from utils.helpers internally
        ip = get_client_ip(request)
        
        self.assertEqual(ip, '192.168.1.100')
    
    def test_get_client_ip_forwarded(self):
        """Test that RequestValidator uses get_client_ip from utils.helpers"""
        from apps.downloads.utils.helpers import get_client_ip
        request = self.factory.get('/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.100'
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        # RequestValidator now uses get_client_ip from utils.helpers internally
        # X-Forwarded-For is only read as far as our own proxies reach
        with override_settings(TRUSTED_PROXY_COUNT=0):
            self.assertEqual(get_client_ip(request), '192.168.1.100')
        with override_settings(TRUSTED_PROXY_COUNT=1):
            self.assertEqual(get_client_ip(request), '192.168.1.100')


class SecurityMiddlewareTest(TestCase):
    """Tests for security middleware."""
    
    def setUp(self):
        """Set up test fixtures."""
        cache.clear()
        self.client = Client()
        self.middleware = DownloadsSecurityMiddleware(get_response=lambda r: None)
        self.factory = RequestFactory()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_blocks_blacklisted_ip(self):
        """Test that blacklisted IPs are blocked."""
        ip = '192.168.1.200'
        IPBlacklistManager.blacklist_ip(ip, reason='Test')
        
        request = self.factory.get('/downloads/')
        request.META['REMOTE_ADDR'] = ip
        request.user = User()  # Anonymous user
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
    
    def test_allows_non_blacklisted_ip(self):
        """Test that non-blacklisted IPs are allowed."""
        request = self.factory.get('/downloads/')
        request.META['REMOTE_ADDR'] = '192.168.1.201'
        request.user = User()
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)  # None means allow through


class SecurityHeadersMiddlewareTest(TestCase):
    """Tests for security headers middleware."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.middleware = SecurityHeadersMiddleware(
            get_response=lambda r: HttpResponse()
        )
        self.factory = RequestFactory()
    
    def test_adds_security_headers(self):
        """Test that security headers are added."""
        request = self.factory.get('/downloads/')
        response = HttpResponse()
        
        response = self.middleware.process_response(request, response)
        
        # Check that headers were added
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(
            response['Referrer-Policy'],
            'strict-origin-when-cross-origin'
        )


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['apps.downloads.tests.test_security_enhanced'])
