"""
Comprehensive tests for security decorators
"""
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from unittest.mock import patch, Mock
from datetime import timedelta
import json

from apps.core.security_decorators import (
    SecurityManager,
    api_key_required,
    rate_limit,
    require_https,
    _check_api_key_rate_limit
)
from apps.core.models import APIKey, SecurityLog

User = get_user_model()


class SecurityManagerTest(TestCase):
    """Test suite for SecurityManager"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_get_client_ip_direct(self):
        """Test getting client IP directly"""
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        ip = SecurityManager.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_ignores_untrusted_forwarded_for(self):
        """X-Forwarded-For is ignored when no proxy is trusted"""
        request = self.factory.get('/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        request.META['REMOTE_ADDR'] = '203.0.113.9'
        with override_settings(TRUSTED_PROXY_COUNT=0):
            self.assertEqual(SecurityManager.get_client_ip(request), '203.0.113.9')

    def test_get_client_ip_uses_trusted_proxy_entry(self):
        """With one proxy in front, its appended entry is the client"""
        request = self.factory.get('/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        request.META['REMOTE_ADDR'] = '203.0.113.9'
        with override_settings(TRUSTED_PROXY_COUNT=1):
            self.assertEqual(SecurityManager.get_client_ip(request), '10.0.0.1')
    
    def test_get_client_ip_empty(self):
        """Test getting client IP when not present"""
        request = self.factory.get('/test/')
        # Remove REMOTE_ADDR if it exists (RequestFactory may set a default)
        if 'REMOTE_ADDR' in request.META:
            del request.META['REMOTE_ADDR']
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            del request.META['HTTP_X_FORWARDED_FOR']
        ip = SecurityManager.get_client_ip(request)
        # Should return empty string or default IP
        self.assertIsInstance(ip, str)
    
    def test_log_security_event(self):
        """Test logging security event"""
        SecurityManager.log_security_event(
            'login_success',
            '192.168.1.1',
            user=self.user,
            details={'test': 'data'},
            user_agent='Test Agent'
        )
        log = SecurityLog.objects.get(event_type='login_success')
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.details, {'test': 'data'})
    
    def test_log_security_event_without_user(self):
        """Test logging security event without user"""
        SecurityManager.log_security_event(
            'suspicious_input',
            '192.168.1.1'
        )
        log = SecurityLog.objects.get(event_type='suspicious_input')
        self.assertIsNone(log.user)
    
    def test_log_security_event_handles_exception(self):
        """Test that logging handles exceptions gracefully"""
        with patch('apps.core.security_decorators.SecurityLog.objects.create', side_effect=Exception('DB Error')):
            # Should not raise exception
            SecurityManager.log_security_event('test', '192.168.1.1')


class APIKeyRequiredDecoratorTest(TestCase):
    """Test suite for api_key_required decorator"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.api_key = APIKey.objects.create(
            name='Test Key',
            user=self.user
        )
    
    def test_api_key_required_missing_key(self):
        """Test decorator with missing API key"""
        @api_key_required
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        response = test_view(request)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_api_key_required_invalid_key(self):
        """Test decorator with invalid API key"""
        @api_key_required
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.META['HTTP_X_API_KEY'] = 'invalid_key'
        response = test_view(request)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_api_key_required_expired_key(self):
        """Test decorator with expired API key"""
        expired_key = APIKey.objects.create(
            name='Expired Key',
            user=self.user,
            is_active=True,
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        @api_key_required
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.META['HTTP_X_API_KEY'] = expired_key.key
        response = test_view(request)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_api_key_required_inactive_key(self):
        """Test decorator with inactive API key"""
        inactive_key = APIKey.objects.create(
            name='Inactive Key',
            user=self.user,
            is_active=False
        )
        
        @api_key_required
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.META['HTTP_X_API_KEY'] = inactive_key.key
        response = test_view(request)
        self.assertEqual(response.status_code, 401)
    
    @patch('apps.core.security_decorators._check_api_key_rate_limit')
    def test_api_key_required_rate_limit_exceeded(self, mock_rate_limit):
        """Test decorator with rate limit exceeded"""
        mock_rate_limit.return_value = (False, 'Rate limit exceeded')
        
        @api_key_required
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.META['HTTP_X_API_KEY'] = self.api_key.key
        response = test_view(request)
        self.assertEqual(response.status_code, 429)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    @patch('apps.core.security_decorators._check_api_key_rate_limit')
    def test_api_key_required_success(self, mock_rate_limit):
        """Test decorator with valid API key"""
        mock_rate_limit.return_value = (True, 'OK')
        
        @api_key_required
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.META['HTTP_X_API_KEY'] = self.api_key.key
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(hasattr(request, 'api_key'))
        self.assertEqual(request.api_key, self.api_key)
    
    @patch('apps.core.security_decorators._check_api_key_rate_limit')
    def test_api_key_required_updates_last_used(self, mock_rate_limit):
        """Test that decorator updates last_used timestamp"""
        mock_rate_limit.return_value = (True, 'OK')
        
        @api_key_required
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.META['HTTP_X_API_KEY'] = self.api_key.key
        self.assertIsNone(self.api_key.last_used)
        test_view(request)
        self.api_key.refresh_from_db()
        self.assertIsNotNone(self.api_key.last_used)


class RateLimitDecoratorTest(TestCase):
    """Test suite for rate_limit decorator"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        cache.clear()
    
    def test_rate_limit_below_limit(self):
        """Test rate limit when below limit"""
        @rate_limit(requests_per_minute=10)
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_rate_limit_exceeded(self):
        """Test rate limit when exceeded"""
        @rate_limit(requests_per_minute=2)
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        # Make requests up to limit
        test_view(request)
        test_view(request)
        
        # This should be rate limited
        response = test_view(request)
        self.assertEqual(response.status_code, 429)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_rate_limit_logs_event(self):
        """Test that rate limit logs security event"""
        @rate_limit(requests_per_minute=1)
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        
        # Make requests to exceed limit
        test_view(request)
        test_view(request)
        
        # Check that security event was logged
        logs = SecurityLog.objects.filter(event_type='rate_limit_exceeded')
        self.assertGreater(len(logs), 0)


class RequireHttpsDecoratorTest(TestCase):
    """Test suite for require_https decorator"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
    
    def test_require_https_allows_https(self):
        """Test decorator allows HTTPS requests"""
        @require_https
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.is_secure = Mock(return_value=True)
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_require_https_blocks_http(self):
        """Test decorator blocks HTTP requests"""
        @require_https
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.is_secure = Mock(return_value=False)
        request.META.pop('HTTP_X_FORWARDED_PROTO', None)
        response = test_view(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_require_https_allows_forwarded_proto(self):
        """Test decorator allows requests with X-Forwarded-Proto header"""
        @require_https
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.is_secure = Mock(return_value=False)
        request.META['HTTP_X_FORWARDED_PROTO'] = 'https'
        response = test_view(request)
        self.assertEqual(response.status_code, 200)


class CheckAPIKeyRateLimitTest(TestCase):
    """Test suite for _check_api_key_rate_limit function"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.api_key = APIKey.objects.create(
            name='Test Key',
            user=self.user,
            requests_per_hour=10,
            requests_per_day=100
        )
        cache.clear()
    
    def test_check_rate_limit_below_hourly(self):
        """Test rate limit check when below hourly limit"""
        is_allowed, message = _check_api_key_rate_limit(self.api_key)
        self.assertTrue(is_allowed)
        self.assertEqual(message, 'OK')
    
    def test_check_rate_limit_exceeds_hourly(self):
        """Test rate limit check when hourly limit exceeded"""
        # Set hourly count to limit
        now = timezone.now()
        hour_bucket = now.strftime('%Y%m%d%H')
        hour_key = f"api_rate:{self.api_key.key}:h:{hour_bucket}"
        cache.set(hour_key, self.api_key.requests_per_hour, timeout=3600)
        
        is_allowed, message = _check_api_key_rate_limit(self.api_key)
        self.assertFalse(is_allowed)
        self.assertIn('Hourly rate limit exceeded', message)
    
    def test_check_rate_limit_exceeds_daily(self):
        """Test rate limit check when daily limit exceeded"""
        # Set daily count to limit
        now = timezone.now()
        day_bucket = now.strftime('%Y%m%d')
        day_key = f"api_rate:{self.api_key.key}:d:{day_bucket}"
        cache.set(day_key, self.api_key.requests_per_day, timeout=86400)
        
        is_allowed, message = _check_api_key_rate_limit(self.api_key)
        self.assertFalse(is_allowed)
        self.assertIn('Daily rate limit exceeded', message)
    
    def test_check_rate_limit_increments_counters(self):
        """Test that rate limit check increments counters"""
        now = timezone.now()
        hour_bucket = now.strftime('%Y%m%d%H')
        day_bucket = now.strftime('%Y%m%d')
        hour_key = f"api_rate:{self.api_key.key}:h:{hour_bucket}"
        day_key = f"api_rate:{self.api_key.key}:d:{day_bucket}"
        
        initial_hourly = cache.get(hour_key, 0)
        initial_daily = cache.get(day_key, 0)
        
        _check_api_key_rate_limit(self.api_key)
        
        self.assertEqual(cache.get(hour_key, 0), initial_hourly + 1)
        self.assertEqual(cache.get(day_key, 0), initial_daily + 1)

