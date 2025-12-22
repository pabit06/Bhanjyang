"""
Tests for core app security admin classes
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.http import HttpResponse
from django.utils import timezone
import csv
import io

from apps.core.models import APIKey, SecurityLog
from apps.core.security_admin import APIKeyAdmin, SecurityLogAdmin


class SecurityAdminTestCase(TestCase):
    """Base test case for security admin tests"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.request = self.factory.get('/admin/')
        self.request.user = self.admin_user


class APIKeyAdminTest(SecurityAdminTestCase):
    """Test APIKeyAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = APIKeyAdmin(APIKey, self.site)
        self.api_key = APIKey.objects.create(
            name="Test API Key",
            user=self.admin_user,
            key=APIKey.generate_key(),
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('user', self.admin.list_display)
        self.assertIn('key_display', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('is_active', self.admin.list_filter)
        self.assertIn('created_at', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('name', self.admin.search_fields)
        self.assertIn('user__username', self.admin.search_fields)
    
    def test_readonly_fields(self):
        """Test readonly fields"""
        self.assertIn('key', self.admin.readonly_fields)
        self.assertIn('created_at', self.admin.readonly_fields)
        self.assertIn('last_used', self.admin.readonly_fields)
    
    def test_key_display(self):
        """Test key display masking"""
        display = self.admin.key_display(self.api_key)
        self.assertIn('...', display)
        self.assertEqual(len(display.split('...')[0]), 8)
        self.assertEqual(len(display.split('...')[1]), 4)
    
    def test_key_display_not_generated(self):
        """Test key display when key not generated"""
        api_key = APIKey.objects.create(
            name="No Key",
            user=self.admin_user
        )
        display = self.admin.key_display(api_key)
        self.assertEqual(display, "Not generated")
    
    def test_get_queryset(self):
        """Test queryset optimization"""
        queryset = self.admin.get_queryset(self.request)
        self.assertIsNotNone(queryset)
    
    def test_activate_keys_action(self):
        """Test activate keys action"""
        api_key = APIKey.objects.create(
            name="Inactive Key",
            user=self.admin_user,
            is_active=False
        )
        queryset = APIKey.objects.filter(id=api_key.id)
        self.admin.activate_keys(self.request, queryset)
        api_key.refresh_from_db()
        self.assertTrue(api_key.is_active)
    
    def test_deactivate_keys_action(self):
        """Test deactivate keys action"""
        queryset = APIKey.objects.filter(id=self.api_key.id)
        self.admin.deactivate_keys(self.request, queryset)
        self.api_key.refresh_from_db()
        self.assertFalse(self.api_key.is_active)
    
    def test_regenerate_keys_action(self):
        """Test regenerate keys action"""
        old_key = self.api_key.key
        queryset = APIKey.objects.filter(id=self.api_key.id)
        self.admin.regenerate_keys(self.request, queryset)
        self.api_key.refresh_from_db()
        self.assertNotEqual(self.api_key.key, old_key)


class SecurityLogAdminTest(SecurityAdminTestCase):
    """Test SecurityLogAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = SecurityLogAdmin(SecurityLog, self.site)
        self.security_log = SecurityLog.objects.create(
            event_type='login_attempt',
            ip_address='127.0.0.1',
            user=self.admin_user,
            details={'action': 'login'}
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('event_type', self.admin.list_display)
        self.assertIn('ip_address', self.admin.list_display)
        self.assertIn('user', self.admin.list_display)
        self.assertIn('timestamp', self.admin.list_display)
        self.assertIn('details_display', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('event_type', self.admin.list_filter)
        self.assertIn('timestamp', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('ip_address', self.admin.search_fields)
        self.assertIn('user__username', self.admin.search_fields)
    
    def test_readonly_fields(self):
        """Test readonly fields"""
        self.assertIn('timestamp', self.admin.readonly_fields)
    
    def test_details_display(self):
        """Test details display"""
        display = self.admin.details_display(self.security_log)
        self.assertIsNotNone(display)
    
    def test_details_display_long(self):
        """Test details display with long content"""
        long_details = {'data': 'x' * 200}
        log = SecurityLog.objects.create(
            event_type='test',
            ip_address='127.0.0.1',
            details=long_details
        )
        display = self.admin.details_display(log)
        self.assertIn('...', display)
        self.assertLessEqual(len(display), 103)  # 100 chars + "..."
    
    def test_details_display_empty(self):
        """Test details display with empty details"""
        log = SecurityLog.objects.create(
            event_type='test',
            ip_address='127.0.0.1'
        )
        display = self.admin.details_display(log)
        self.assertEqual(display, "-")
    
    def test_get_queryset(self):
        """Test queryset optimization"""
        queryset = self.admin.get_queryset(self.request)
        self.assertIsNotNone(queryset)
    
    def test_export_security_logs_action(self):
        """Test export security logs action"""
        queryset = SecurityLog.objects.filter(id=self.security_log.id)
        response = self.admin.export_security_logs(self.request, queryset)
        
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Check CSV content
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)
        self.assertEqual(len(rows), 2)  # Header + 1 data row
        self.assertIn('Event Type', rows[0])
        self.assertIn('IP Address', rows[0])
    
    def test_has_add_permission(self):
        """Test add permission"""
        # Security logs should only be created programmatically
        self.assertFalse(self.admin.has_add_permission(self.request))

