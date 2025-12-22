"""
Tests for contact app admin classes
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.utils import timezone

from apps.contact.models import ContactSubmission, KYMSubmission
from apps.contact.admin import ContactSubmissionAdmin, KYMSubmissionAdmin


class ContactAdminTestCase(TestCase):
    """Base test case for contact admin tests"""
    
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


class ContactSubmissionAdminTest(ContactAdminTestCase):
    """Test ContactSubmissionAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = ContactSubmissionAdmin(ContactSubmission, self.site)
        self.submission = ContactSubmission.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message",
            inquiry_type="general"
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('email', self.admin.list_display)
        self.assertIn('subject', self.admin.list_display)
        self.assertIn('status', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('status', self.admin.list_filter)
        self.assertIn('inquiry_type', self.admin.list_filter)
        self.assertIn('created_at', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('name', self.admin.search_fields)
        self.assertIn('email', self.admin.search_fields)
        self.assertIn('subject', self.admin.search_fields)
    
    def test_readonly_fields(self):
        """Test readonly fields"""
        self.assertIn('created_at', self.admin.readonly_fields)
        self.assertIn('updated_at', self.admin.readonly_fields)
    
    def test_get_queryset(self):
        """Test queryset optimization"""
        queryset = self.admin.get_queryset(self.request)
        self.assertIsNotNone(queryset)


class KYMSubmissionAdminTest(ContactAdminTestCase):
    """Test KYMSubmissionAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = KYMSubmissionAdmin(KYMSubmission, self.site)
        self.submission = KYMSubmission.objects.create(
            name="Test User",
            email="test@example.com",
            phone="9800000000",
            address="Test Address"
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('email', self.admin.list_display)
        self.assertIn('phone', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('created_at', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('name', self.admin.search_fields)
        self.assertIn('email', self.admin.search_fields)
    
    def test_has_delete_permission(self):
        """Test delete permission"""
        # KYM submissions should not be deletable
        self.assertFalse(self.admin.has_delete_permission(self.request, self.submission))

