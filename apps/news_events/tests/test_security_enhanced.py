"""
Tests for Enhanced Security Features

Tests for:
- IP blacklisting
- Honeypot protection
- File upload security
- Request signatures
- Security headers
- Session security
"""

import hashlib
import io
from datetime import timedelta
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.utils import timezone
from django.http import HttpRequest

from ..security_enhanced import (
    IPBlacklistManager,
    HoneypotProtection,
    FileUploadSecurity,
    RequestSignatureValidator,
    SecurityHeadersManager,
    SessionSecurityManager,
    log_security_event,
    get_recent_security_events
)
from ..middleware import NewsEventsSecurityMiddleware, RateLimitMiddleware


class IPBlacklistManagerTest(TestCase):
    """Tests for IP blacklist management"""
    
    def setUp(self):
        cache.clear()
    
    def test_add_to_blacklist(self):
        """Test adding IP to blacklist"""
        ip = '192.168.1.100'
        reason = 'Test blacklist'
        
        IPBlacklistManager.add_to_blacklist(ip, reason)
        
        is_blacklisted, stored_reason = IPBlacklistManager.is_blacklisted(ip)
        self.assertTrue(is_blacklisted)
        self.assertEqual(stored_reason, reason)
    
    def test_remove_from_blacklist(self):
        """Test removing IP from blacklist"""
        ip = '192.168.1.100'
        
        IPBlacklistManager.add_to_blacklist(ip, 'Test')
        IPBlacklistManager.remove_from_blacklist(ip)
        
        is_blacklisted, _ = IPBlacklistManager.is_blacklisted(ip)
        self.assertFalse(is_blacklisted)
    
    def test_record_violation(self):
        """Test recording security violations"""
        ip = '192.168.1.100'
        
        count1 = IPBlacklistManager.record_violation(ip, 'spam')
        self.assertEqual(count1, 1)
        
        count2 = IPBlacklistManager.record_violation(ip, 'spam')
        self.assertEqual(count2, 2)
    
    def test_auto_blacklist_after_violations(self):
        """Test auto-blacklisting after 5 violations"""
        ip = '192.168.1.100'
        
        for i in range(5):
            IPBlacklistManager.record_violation(ip, 'spam')
        
        is_blacklisted, reason = IPBlacklistManager.is_blacklisted(ip)
        self.assertTrue(is_blacklisted)
        self.assertIn('Auto-blacklisted', reason)
    
    def test_violation_count(self):
        """Test getting violation count"""
        ip = '192.168.1.100'
        
        IPBlacklistManager.record_violation(ip, 'spam')
        IPBlacklistManager.record_violation(ip, 'spam')
        
        count = IPBlacklistManager.get_violation_count(ip)
        self.assertEqual(count, 2)


class HoneypotProtectionTest(TestCase):
    """Tests for honeypot protection"""
    
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()
    
    def test_validate_honeypot_empty(self):
        """Test honeypot validation with empty field (legitimate)"""
        request = self.factory.post('/test/', {'website': ''})
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        is_valid = HoneypotProtection.validate_honeypot(request, 'website')
        self.assertTrue(is_valid)
    
    def test_validate_honeypot_filled(self):
        """Test honeypot validation with filled field (bot)"""
        request = self.factory.post('/test/', {'website': 'http://spam.com'})
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        is_valid = HoneypotProtection.validate_honeypot(request, 'website')
        self.assertFalse(is_valid)
    
    def test_add_honeypot_to_form(self):
        """Test adding honeypot field to form HTML"""
        form_html = '<form><input name="email"></form>'
        
        enhanced_html = HoneypotProtection.add_honeypot_to_form(form_html)
        
        self.assertIn('website', enhanced_html)
        self.assertIn('hidden', enhanced_html)
        self.assertIn('position:absolute', enhanced_html)


class FileUploadSecurityTest(TestCase):
    """Tests for file upload security"""
    
    def test_validate_valid_image(self):
        """Test validating a valid image upload"""
        # Create a minimal JPEG file
        image_content = b'\xff\xd8\xff\xe0\x00\x10JFIF'
        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            image_content,
            content_type="image/jpeg"
        )
        
        result = FileUploadSecurity.validate_file_upload(uploaded_file)
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_oversized_file(self):
        """Test rejecting oversized file"""
        # Create a large file (6MB, exceeds 5MB limit)
        large_content = b'x' * (6 * 1024 * 1024)
        uploaded_file = SimpleUploadedFile(
            "large.jpg",
            large_content,
            content_type="image/jpeg"
        )
        
        result = FileUploadSecurity.validate_file_upload(uploaded_file)
        self.assertFalse(result['is_valid'])
        self.assertTrue(any('size' in error.lower() for error in result['errors']))
    
    def test_validate_invalid_extension(self):
        """Test rejecting invalid file extension"""
        uploaded_file = SimpleUploadedFile(
            "test.exe",
            b'content',
            content_type="application/x-msdownload"
        )
        
        result = FileUploadSecurity.validate_file_upload(uploaded_file)
        self.assertFalse(result['is_valid'])
        self.assertTrue(any('extension' in error.lower() for error in result['errors']))
    
    def test_validate_invalid_mime_type(self):
        """Test rejecting invalid MIME type"""
        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            b'content',
            content_type="application/javascript"
        )
        
        result = FileUploadSecurity.validate_file_upload(uploaded_file)
        self.assertFalse(result['is_valid'])
        self.assertTrue(any('type' in error.lower() for error in result['errors']))
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        dangerous_filename = "../../../etc/passwd"
        safe_filename = FileUploadSecurity.sanitize_filename(dangerous_filename)
        
        self.assertNotIn('/', safe_filename)
        self.assertNotIn('..', safe_filename)
    
    def test_sanitize_filename_long(self):
        """Test sanitizing long filename"""
        long_filename = 'a' * 150 + '.jpg'
        safe_filename = FileUploadSecurity.sanitize_filename(long_filename)
        
        self.assertLessEqual(len(safe_filename), 100)
        self.assertTrue(safe_filename.endswith('.jpg'))


class RequestSignatureValidatorTest(TestCase):
    """Tests for request signature validation"""
    
    def test_generate_signature(self):
        """Test generating signature"""
        data = "test_data"
        signature = RequestSignatureValidator.generate_signature(data)
        
        self.assertEqual(len(signature), 64)  # SHA256 hex is 64 chars
        self.assertTrue(all(c in '0123456789abcdef' for c in signature))
    
    def test_validate_signature_valid(self):
        """Test validating a valid signature"""
        data = "test_data"
        signature = RequestSignatureValidator.generate_signature(data)
        
        is_valid = RequestSignatureValidator.validate_signature(data, signature)
        self.assertTrue(is_valid)
    
    def test_validate_signature_invalid(self):
        """Test rejecting invalid signature"""
        data = "test_data"
        wrong_signature = "0" * 64
        
        is_valid = RequestSignatureValidator.validate_signature(data, wrong_signature)
        self.assertFalse(is_valid)
    
    def test_sign_request_data(self):
        """Test signing request data dictionary"""
        request_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'action': 'subscribe'
        }
        
        signature = RequestSignatureValidator.sign_request_data(request_data)
        self.assertIsNotNone(signature)
        self.assertEqual(len(signature), 64)


class SecurityHeadersManagerTest(TestCase):
    """Tests for security headers management"""
    
    def test_get_security_headers(self):
        """Test getting security headers"""
        headers = SecurityHeadersManager.get_security_headers()
        
        self.assertIn('X-Frame-Options', headers)
        self.assertIn('X-Content-Type-Options', headers)
        self.assertIn('X-XSS-Protection', headers)
        self.assertIn('Content-Security-Policy', headers)
    
    def test_apply_security_headers(self):
        """Test applying headers to response"""
        from django.http import HttpResponse
        
        response = HttpResponse("Test")
        response = SecurityHeadersManager.apply_security_headers(response)
        
        self.assertEqual(response['X-Frame-Options'], 'SAMEORIGIN')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')


class SessionSecurityManagerTest(TestCase):
    """Tests for session security"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_validate_session_integrity_new_session(self):
        """Test validating new session"""
        request = self.factory.get('/test/')
        request.user = self.user
        request.session = {}
        request.META['HTTP_USER_AGENT'] = 'Test Browser'
        
        is_valid = SessionSecurityManager.validate_session_integrity(request)
        self.assertTrue(is_valid)
        self.assertIn('_auth_user_agent', request.session)
    
    def test_validate_session_integrity_user_agent_mismatch(self):
        """Test detecting user agent mismatch"""
        request = self.factory.get('/test/')
        request.user = self.user
        request.session = {'_auth_user_agent': 'Original Browser'}
        request.META['HTTP_USER_AGENT'] = 'Different Browser'
        
        is_valid = SessionSecurityManager.validate_session_integrity(request)
        self.assertFalse(is_valid)
    
    def test_check_session_timeout_valid(self):
        """Test session within timeout period"""
        request = self.factory.get('/test/')
        request.user = self.user
        request.session = {
            '_last_activity': timezone.now().isoformat()
        }
        
        is_valid = SessionSecurityManager.check_session_timeout(request, timeout_minutes=30)
        self.assertTrue(is_valid)
    
    def test_check_session_timeout_expired(self):
        """Test expired session"""
        request = self.factory.get('/test/')
        request.user = self.user
        old_time = timezone.now() - timedelta(minutes=60)
        request.session = {
            '_last_activity': old_time.isoformat()
        }
        
        is_valid = SessionSecurityManager.check_session_timeout(request, timeout_minutes=30)
        self.assertFalse(is_valid)


class SecurityEventLoggingTest(TestCase):
    """Tests for security event logging"""
    
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()
    
    def test_log_security_event(self):
        """Test logging security event"""
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.user = User.objects.create_user('test', password='pass')
        
        log_security_event('test_event', {'detail': 'test'}, request)
        
        events = get_recent_security_events(days=1)
        self.assertGreater(len(events), 0)
        self.assertEqual(events[-1]['event_type'], 'test_event')
    
    def test_get_recent_security_events(self):
        """Test retrieving recent security events"""
        for i in range(3):
            log_security_event(f'event_{i}', {'detail': i})
        
        events = get_recent_security_events(days=1)
        self.assertEqual(len(events), 3)


class SecurityMiddlewareTest(TestCase):
    """Tests for security middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = NewsEventsSecurityMiddleware(lambda x: None)
        cache.clear()
    
    def test_middleware_allows_normal_request(self):
        """Test middleware allows normal requests"""
        request = self.factory.get('/news-events/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.user = User()
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
    
    def test_middleware_blocks_blacklisted_ip(self):
        """Test middleware blocks blacklisted IP"""
        ip = '192.168.1.100'
        IPBlacklistManager.add_to_blacklist(ip, 'Test')
        
        request = self.factory.get('/news-events/')
        request.META['REMOTE_ADDR'] = ip
        request.user = User()
        
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
    
    def test_middleware_adds_security_headers(self):
        """Test middleware adds security headers to response"""
        from django.http import HttpResponse
        
        request = self.factory.get('/news-events/')
        response = HttpResponse("Test")
        
        response = self.middleware.process_response(request, response)
        
        self.assertIn('X-Frame-Options', response)
        self.assertIn('X-Content-Type-Options', response)


class RateLimitMiddlewareTest(TestCase):
    """Tests for rate limiting middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(lambda x: None)
        cache.clear()
    
    def test_rate_limit_allows_under_limit(self):
        """Test rate limiting allows requests under limit"""
        request = self.factory.post('/news-events/subscribe/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
    
    def test_rate_limit_blocks_over_limit(self):
        """Test rate limiting blocks requests over limit"""
        ip = '192.168.1.100'
        
        # Make 4 requests (limit is 3)
        for i in range(4):
            request = self.factory.post('/news-events/subscribe/')
            request.META['REMOTE_ADDR'] = ip
            response = self.middleware.process_request(request)
            
            if i < 3:
                self.assertIsNone(response)
            else:
                self.assertIsNotNone(response)
                self.assertEqual(response.status_code, 429)


# Integration tests

class SecurityIntegrationTest(TestCase):
    """Integration tests for security features"""
    
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()
    
    def test_complete_security_flow(self):
        """Test complete security flow"""
        from ..security_enhanced import check_request_security
        
        @check_request_security
        def test_view(request):
            return "success"
        
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.user = User()
        
        result = test_view(request)
        self.assertEqual(result, "success")
    
    def test_honeypot_protection_integration(self):
        """Test honeypot protection in integration"""
        from ..security_enhanced import honeypot_protected
        
        @honeypot_protected
        def test_view(request):
            return "success"
        
        # Valid request
        request = self.factory.post('/test/', {'website': ''})
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        result = test_view(request)
        self.assertEqual(result, "success")
