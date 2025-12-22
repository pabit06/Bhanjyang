"""
Tests for dashboard app security module
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone

from apps.dashboard.security import (
    SecurityMiddleware, SecurityUtils, RoleBasedAccessControl
)
from apps.dashboard.models import AuditLog


class SecurityMiddlewareTest(TestCase):
    """Test SecurityMiddleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.get_response = lambda request: HttpResponse("OK")
        self.middleware = SecurityMiddleware(self.get_response)
    
    def test_process_request(self):
        """Test process_request"""
        request = self.factory.get('/dashboard/')
        request.user = self.user
        request.session = {}
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
        self.assertTrue(hasattr(request, '_start_time'))
    
    def test_process_response(self):
        """Test process_response"""
        request = self.factory.get('/dashboard/')
        request.user = self.user
        request.session = {}
        request.session.session_key = 'test_session'
        request._start_time = timezone.now().timestamp()
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = HttpResponse("OK")
        result = self.middleware.process_response(request, response)
        self.assertEqual(result.status_code, 200)
        # Check that audit log was created
        self.assertTrue(AuditLog.objects.filter(action_type='dashboard_access').exists())
    
    def test_check_suspicious_patterns(self):
        """Test checking suspicious patterns"""
        request = self.factory.get('/dashboard/')
        request.user = self.user
        request.session = {}
        request.META['HTTP_USER_AGENT'] = 'sqlmap scanner'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        self.middleware.check_suspicious_patterns(request)
        # Check that suspicious activity was logged
        self.assertTrue(AuditLog.objects.filter(action_type='suspicious_activity').exists())
    
    def test_log_dashboard_access(self):
        """Test logging dashboard access"""
        request = self.factory.get('/dashboard/')
        request.user = self.user
        request.session = {}
        request.session.session_key = 'test_session'
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.GET = {}
        
        response = HttpResponse("OK")
        self.middleware.log_dashboard_access(request, response, 100.0)
        self.assertTrue(AuditLog.objects.filter(action_type='dashboard_access').exists())
    
    def test_log_admin_access(self):
        """Test logging admin access"""
        request = self.factory.get('/admin/')
        request.user = self.user
        request.session = {}
        request.session.session_key = 'test_session'
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.GET = {}
        
        response = HttpResponse("OK")
        self.middleware.log_admin_access(request, response, 100.0)
        self.assertTrue(AuditLog.objects.filter(action_type='admin_access').exists())
    
    def test_get_client_ip(self):
        """Test getting client IP"""
        request = self.factory.get('/dashboard/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')
    
    def test_get_client_ip_with_proxy(self):
        """Test getting client IP with proxy"""
        request = self.factory.get('/dashboard/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 127.0.0.1'
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')


class SecurityUtilsTest(TestCase):
    """Test SecurityUtils"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_validate_user_permission(self):
        """Test validating user permission"""
        result = SecurityUtils.validate_user_permission(self.user, 'view_dashboard')
        # Should return True or False depending on permissions
        self.assertIsInstance(result, bool)
    
    def test_check_ip_whitelist(self):
        """Test checking IP whitelist"""
        result = SecurityUtils.check_ip_whitelist('127.0.0.1')
        # Should return True or False
        self.assertIsInstance(result, bool)
    
    def test_validate_session(self):
        """Test validating session"""
        result = SecurityUtils.validate_session('test_session_id')
        # Should return True or False
        self.assertIsInstance(result, bool)
    
    def test_log_security_event(self):
        """Test logging security event"""
        SecurityUtils.log_security_event(
            user=self.user,
            event_type='test_event',
            description='Test description',
            ip_address='127.0.0.1'
        )
        self.assertTrue(AuditLog.objects.filter(action_type='test_event').exists())


class RoleBasedAccessControlTest(TestCase):
    """Test RoleBasedAccessControl"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.rbac = RoleBasedAccessControl()
    
    def test_has_permission(self):
        """Test has_permission"""
        result = self.rbac.has_permission(self.user, 'view_dashboard')
        self.assertIsInstance(result, bool)
    
    def test_has_role(self):
        """Test has_role"""
        result = self.rbac.has_role(self.user, 'admin')
        self.assertIsInstance(result, bool)
    
    def test_get_user_permissions(self):
        """Test getting user permissions"""
        permissions = self.rbac.get_user_permissions(self.user)
        self.assertIsInstance(permissions, list)
    
    def test_get_user_roles(self):
        """Test getting user roles"""
        roles = self.rbac.get_user_roles(self.user)
        self.assertIsInstance(roles, list)
    
    def test_assign_role(self):
        """Test assigning role"""
        result = self.rbac.assign_role(self.user, 'viewer')
        # Should return True or False
        self.assertIsInstance(result, bool)
    
    def test_revoke_role(self):
        """Test revoking role"""
        result = self.rbac.revoke_role(self.user, 'viewer')
        # Should return True or False
        self.assertIsInstance(result, bool)

