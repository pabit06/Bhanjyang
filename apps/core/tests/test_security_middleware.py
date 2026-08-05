"""
Comprehensive tests for security middleware
"""
from django.test import TestCase, RequestFactory, Client, override_settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from unittest.mock import patch, MagicMock
import re

from apps.core.security_middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
    CSRFProtectionMiddleware,
    ContentTypeMiddleware,
    SecurityLoggingMiddleware
)


class SecurityHeadersMiddlewareTest(TestCase):
    """Test cases for SecurityHeadersMiddleware"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(lambda r: HttpResponse())

    def test_process_response_adds_security_headers(self):
        """Test that security headers are added to response"""
        request = self.factory.get('/')
        response = HttpResponse()
        
        result = self.middleware.process_response(request, response)
        
        self.assertEqual(result['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(result['X-Frame-Options'], 'DENY')
        self.assertEqual(result['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(result['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertEqual(result['Cross-Origin-Embedder-Policy'], 'require-corp')
        self.assertEqual(result['Cross-Origin-Opener-Policy'], 'same-origin')
        self.assertEqual(result['Cross-Origin-Resource-Policy'], 'same-origin')

    def test_process_response_hsts_for_secure_request(self):
        """Test HSTS header for secure requests"""
        request = self.factory.get('/')
        request.is_secure = lambda: True
        response = HttpResponse()
        
        result = self.middleware.process_response(request, response)
        
        self.assertIn('Strict-Transport-Security', result)
        self.assertIn('max-age=31536000', result['Strict-Transport-Security'])

    def test_process_response_no_hsts_for_insecure_request(self):
        """Test no HSTS header for insecure requests"""
        request = self.factory.get('/')
        request.is_secure = lambda: False
        response = HttpResponse()
        
        result = self.middleware.process_response(request, response)
        
        self.assertNotIn('Strict-Transport-Security', result)

    def test_get_permissions_policy(self):
        """Test permissions policy generation"""
        policy = self.middleware.get_permissions_policy()
        
        self.assertIsNotNone(policy)
        self.assertIn('camera=()', policy)
        self.assertIn('microphone=()', policy)
        self.assertIn('geolocation=()', policy)

    def test_remove_server_header(self):
        """Test that Server header is removed"""
        request = self.factory.get('/')
        response = HttpResponse()
        response['Server'] = 'TestServer'
        
        result = self.middleware.process_response(request, response)
        
        self.assertNotIn('Server', result)


class RateLimitMiddlewareTest(TestCase):
    """Test cases for RateLimitMiddleware"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(lambda r: HttpResponse())

    def test_get_client_ip_direct(self):
        """Test getting client IP directly"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_ignores_untrusted_forwarded_for(self):
        """X-Forwarded-For is ignored when no proxy is trusted"""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        request.META['REMOTE_ADDR'] = '203.0.113.9'

        with override_settings(TRUSTED_PROXY_COUNT=0):
            self.assertEqual(self.middleware.get_client_ip(request), '203.0.113.9')

    def test_get_client_ip_uses_trusted_proxy_entry(self):
        """With one proxy in front, its appended entry is the client"""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        request.META['REMOTE_ADDR'] = '203.0.113.9'

        with override_settings(TRUSTED_PROXY_COUNT=1):
            self.assertEqual(self.middleware.get_client_ip(request), '10.0.0.1')

    def test_get_rate_limit_type_api(self):
        """Test determining rate limit type for API"""
        request = self.factory.get('/api/test/')
        rate_limit_type = self.middleware.get_rate_limit_type(request.path)
        self.assertEqual(rate_limit_type, 'api')

    def test_get_rate_limit_type_contact(self):
        """Test determining rate limit type for contact"""
        request = self.factory.get('/about/contact/')
        rate_limit_type = self.middleware.get_rate_limit_type(request.path)
        self.assertEqual(rate_limit_type, 'contact')

    def test_get_rate_limit_type_search(self):
        """Test determining rate limit type for search"""
        request = self.factory.get('/search/')
        rate_limit_type = self.middleware.get_rate_limit_type(request.path)
        self.assertEqual(rate_limit_type, 'search')

    def test_get_rate_limit_type_none(self):
        """Test determining rate limit type for non-limited path"""
        request = self.factory.get('/')
        rate_limit_type = self.middleware.get_rate_limit_type(request.path)
        self.assertIsNone(rate_limit_type)

    def test_is_rate_limited_below_limit(self):
        """Test rate limiting when below limit"""
        client_ip = '192.168.1.1'
        rate_limit_type = 'api'
        
        # Make requests below limit
        for i in range(50):
            is_limited = self.middleware.is_rate_limited(client_ip, rate_limit_type)
            self.assertFalse(is_limited)

    def test_is_rate_limited_exceeds_limit(self):
        """Test rate limiting when limit is exceeded"""
        client_ip = '192.168.1.1'
        rate_limit_type = 'contact'  # Limit is 5 per 5 minutes
        
        # Make requests exceeding limit
        results = []
        for i in range(10):
            results.append(self.middleware.is_rate_limited(client_ip, rate_limit_type))
        
        # First 5 should not be limited, rest should be
        self.assertFalse(results[0])
        self.assertFalse(results[4])
        # After limit, should be rate limited
        self.assertTrue(any(results[5:]))

    def test_process_request_rate_limited(self):
        """Test process_request when rate limited"""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        # Exceed rate limit
        for i in range(150):  # API limit is 100 per minute
            self.middleware.is_rate_limited('192.168.1.1', 'api')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 429)

    def test_process_request_not_rate_limited(self):
        """Test process_request when not rate limited"""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)  # Should pass through

    def test_clean_old_entries(self):
        """Test cleaning old rate limit entries"""
        import time
        
        client_ip = '192.168.1.1'
        rate_limit_type = 'api'
        
        # Add old entry
        key = f"{client_ip}:{rate_limit_type}"
        self.middleware.request_counts[key] = [time.time() - 200]  # 200 seconds ago
        
        # Clean old entries (window is 60 seconds)
        self.middleware.clean_old_entries(time.time(), 60)
        
        # Entry should be removed
        self.assertNotIn(key, self.middleware.request_counts)


class SecurityMiddlewareTest(TestCase):
    """Test cases for SecurityMiddleware"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = SecurityMiddleware(lambda r: HttpResponse())

    def test_is_suspicious_user_agent(self):
        """Test detecting suspicious user agents"""
        suspicious_agents = [
            'sqlmap',
            'nmap',
            'nikto',
            'havij',
            'w3af',
            'zap',
            'burp',
            'nessus',
            'openvas',
            'acunetix'
        ]
        
        for agent in suspicious_agents:
            result = self.middleware.is_suspicious_user_agent(f'Test {agent} scanner')
            self.assertTrue(result, f"Should detect {agent} as suspicious")

    def test_is_suspicious_user_agent_normal(self):
        """Test normal user agents are not suspicious"""
        normal_agents = [
            'Mozilla/5.0',
            'Chrome/91.0',
            'Safari/14.0'
        ]
        
        for agent in normal_agents:
            result = self.middleware.is_suspicious_user_agent(agent)
            self.assertFalse(result, f"Should not detect {agent} as suspicious")

    def test_is_suspicious_path(self):
        """Test detecting suspicious paths"""
        suspicious_paths = [
            '../../../etc/passwd',
            '<script>alert(1)</script>',
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            'vbscript:msgbox(1)',
            'onload=alert(1)',
            'onerror=alert(1)'
        ]
        
        for path in suspicious_paths:
            result = self.middleware.is_suspicious_path(path)
            self.assertTrue(result, f"Should detect {path} as suspicious")

    def test_is_suspicious_path_normal(self):
        """Test normal paths are not suspicious"""
        normal_paths = [
            '/',
            '/about/',
            '/contact/',
            '/services/'
        ]
        
        for path in normal_paths:
            result = self.middleware.is_suspicious_path(path)
            self.assertFalse(result, f"Should not detect {path} as suspicious")

    def test_has_suspicious_params(self):
        """Test detecting suspicious query parameters"""
        request = self.factory.get('/?q=<script>alert(1)</script>')
        result = self.middleware.has_suspicious_params(request.GET)
        self.assertTrue(result)

    def test_has_suspicious_params_sql_injection(self):
        """Test detecting SQL injection in params"""
        request = self.factory.get('/?q=1 UNION SELECT * FROM users')
        result = self.middleware.has_suspicious_params(request.GET)
        self.assertTrue(result)

    def test_has_suspicious_params_normal(self):
        """Test normal query parameters are not suspicious"""
        request = self.factory.get('/?q=test&page=1')
        result = self.middleware.has_suspicious_params(request.GET)
        self.assertFalse(result)

    def test_process_request_suspicious_user_agent(self):
        """Test blocking suspicious user agent"""
        request = self.factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'sqlmap scanner'
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)

    def test_process_request_suspicious_path(self):
        """Test blocking suspicious path"""
        request = self.factory.get('/../../../etc/passwd')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)

    def test_process_request_suspicious_params(self):
        """Test blocking suspicious query parameters"""
        request = self.factory.get('/?q=<script>alert(1)</script>')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)

    def test_process_request_normal(self):
        """Test normal requests pass through"""
        request = self.factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)  # Should pass through


class CSRFProtectionMiddlewareTest(TestCase):
    """Test cases for CSRFProtectionMiddleware"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = CSRFProtectionMiddleware(lambda r: HttpResponse())

    def test_process_request_safe_methods(self):
        """Test that safe methods skip CSRF check"""
        safe_methods = ['GET', 'HEAD', 'OPTIONS', 'TRACE']
        
        for method in safe_methods:
            request = getattr(self.factory, method.lower())('/')
            response = self.middleware.process_request(request)
            self.assertIsNone(response, f"{method} should skip CSRF check")

    def test_process_request_api_endpoints(self):
        """Test that API endpoints skip CSRF check"""
        request = self.factory.post('/api/test/')
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @patch('apps.core.security_middleware.get_token')
    def test_has_valid_csrf_token_valid(self, mock_get_token):
        """Test valid CSRF token"""
        mock_get_token.return_value = 'valid_token'
        request = self.factory.post('/')
        request.META['HTTP_X_CSRFTOKEN'] = 'valid_token'
        
        result = self.middleware.has_valid_csrf_token(request)
        self.assertTrue(result)

    @patch('apps.core.security_middleware.get_token')
    def test_has_valid_csrf_token_invalid(self, mock_get_token):
        """Test invalid CSRF token"""
        mock_get_token.return_value = 'valid_token'
        request = self.factory.post('/')
        request.META['HTTP_X_CSRFTOKEN'] = 'invalid_token'
        
        result = self.middleware.has_valid_csrf_token(request)
        self.assertFalse(result)

    def test_has_valid_csrf_token_missing(self):
        """Test missing CSRF token"""
        request = self.factory.post('/')
        result = self.middleware.has_valid_csrf_token(request)
        self.assertFalse(result)

    def test_process_request_missing_csrf_token(self):
        """Test blocking request without CSRF token"""
        request = self.factory.post('/')
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)


class ContentTypeMiddlewareTest(TestCase):
    """Test cases for ContentTypeMiddleware"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = ContentTypeMiddleware(lambda r: HttpResponse())

    def test_process_request_get_method(self):
        """Test GET requests pass through"""
        request = self.factory.get('/')
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_process_request_multipart_form_data(self):
        """Test multipart/form-data is allowed"""
        request = self.factory.post('/')
        request.META['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundary'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_process_request_form_urlencoded(self):
        """Test application/x-www-form-urlencoded is allowed"""
        request = self.factory.post('/')
        request.META['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_process_request_json(self):
        """Test application/json is allowed"""
        request = self.factory.post('/')
        request.META['CONTENT_TYPE'] = 'application/json'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_process_request_invalid_content_type(self):
        """Test invalid content type is blocked"""
        request = self.factory.post('/')
        request.META['CONTENT_TYPE'] = 'text/plain'
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 415)


class SecurityLoggingMiddlewareTest(TestCase):
    """Test cases for SecurityLoggingMiddleware"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = SecurityLoggingMiddleware(lambda r: HttpResponse())

    def test_is_suspicious_user_agent(self):
        """Test detecting suspicious user agents"""
        result = self.middleware.is_suspicious_user_agent('sqlmap scanner')
        self.assertTrue(result)

    def test_is_suspicious_path(self):
        """Test detecting suspicious paths"""
        result = self.middleware.is_suspicious_path('../../../etc/passwd')
        self.assertTrue(result)

    def test_get_client_ip(self):
        """Test getting client IP"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    @patch('apps.core.security_middleware.logging')
    def test_log_security_event(self, mock_logging):
        """Test logging security events"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        request.path = '/test/'
        request.method = 'GET'
        
        self.middleware.log_security_event('test_event', request)
        
        # Verify logger was called
        mock_logging.getLogger.assert_called_with('security')

    def test_process_request_logs_suspicious_user_agent(self):
        """Test logging suspicious user agent"""
        request = self.factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'sqlmap scanner'
        
        with patch.object(self.middleware, 'log_security_event') as mock_log:
            self.middleware.process_request(request)
            mock_log.assert_called_with('suspicious_user_agent', request)

    def test_process_request_logs_suspicious_path(self):
        """Test logging suspicious path"""
        request = self.factory.get('/../../../etc/passwd')
        
        with patch.object(self.middleware, 'log_security_event') as mock_log:
            self.middleware.process_request(request)
            mock_log.assert_called_with('suspicious_path', request)



