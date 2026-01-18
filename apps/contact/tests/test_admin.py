"""
Tests for contact app admin classes
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from unittest.mock import Mock, patch

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
            ip_address="127.0.0.1"
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('email', self.admin.list_display)
        self.assertIn('subject', self.admin.list_display)
        self.assertIn('status_badge', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('status', self.admin.list_filter)
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
            full_name="Test User",
            email="test@example.com",
            phone="9800000000",
            permanent_address="Test Address",
            dob="1990-01-01",
            gender="male",
            marital_status="single",
            father_name="Father",
            mother_name="Mother",
            grand_father_name="Grandfather",
            occupation="Job",
            income_source="Salary",
            ip_address="127.0.0.1"
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('full_name', self.admin.list_display)
        self.assertIn('email', self.admin.list_display)
        self.assertIn('phone', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('created_at', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('full_name', self.admin.search_fields)
        self.assertIn('email', self.admin.search_fields)
    
    def test_has_delete_permission(self):
        """Test delete permission"""
        # KYM submissions should not be deletable
        self.assertFalse(self.admin.has_delete_permission(self.request, self.submission))

    def test_contact_submission_actions(self):
        """Test admin actions for ContactSubmission"""
        admin = ContactSubmissionAdmin(ContactSubmission, self.site)
        admin.message_user = Mock()
        
        request = self.factory.get('/')
        request.user = self.admin_user
        
        submission = ContactSubmission.objects.create(
            name="Test", 
            email="t@e.com", 
            message="Msg",
            ip_address='127.0.0.1'
        )
        queryset = ContactSubmission.objects.filter(pk=submission.pk)
        
        # Test mark_as_resolved
        admin.mark_as_resolved(request, queryset)
        submission.refresh_from_db()
        self.assertEqual(submission.status, 'resolved')
        
        # Test mark_as_spam
        admin.mark_as_spam(request, queryset)
        submission.refresh_from_db()
        self.assertEqual(submission.status, 'spam')
        
        # Test mark_as_in_progress
        admin.mark_as_in_progress(request, queryset)
        submission.refresh_from_db()
        self.assertEqual(submission.status, 'in_progress')
        
        # Test mark_as_new
        admin.mark_as_new(request, queryset)
        submission.refresh_from_db()
        self.assertEqual(submission.status, 'new')

    def test_contact_submission_admin_methods(self):
        """Test custom methods of ContactSubmissionAdmin"""
        admin = ContactSubmissionAdmin(ContactSubmission, self.site)
        
        submission = ContactSubmission.objects.create(
            name="Test", 
            email="test@example.com", 
            subject="Sub", 
            message="Msg " * 50, # Long message
            status='new',
            ip_address='127.0.0.1'
        )
        
        # Test status_badge
        self.assertIn('background-color', admin.status_badge(submission))
        
        # Test is_recent_badge
        self.assertIn('NEW', admin.is_recent_badge(submission))
        
        # Test message_preview
        preview = admin.message_preview(submission)
        self.assertTrue(len(preview) <= 203) # 200 + '...'


class KYMSubmissionAdminTest(ContactAdminTestCase):
    """Test KYMSubmissionAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = KYMSubmissionAdmin(KYMSubmission, self.site)
        self.submission = KYMSubmission.objects.create(
            full_name="Test User",
            email="test@example.com",
            phone="9800000000",
            permanent_address="Test Address",
            dob="1990-01-01",
            gender="male",
            marital_status="single",
            father_name="Father",
            mother_name="Mother",
            grand_father_name="Grandfather",
            occupation="Job",
            income_source="Salary",
            ip_address="127.0.0.1"
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('full_name', self.admin.list_display)
        self.assertIn('email', self.admin.list_display)
        self.assertIn('phone', self.admin.list_display)
    
    def test_kym_admin_methods(self):
        """Test custom methods of KYMSubmissionAdmin"""
        # Test status_badge
        badge = self.admin.status_badge(self.submission)
        self.assertTrue('span' in str(badge) or 'style' in str(badge))
        
        # Test document_preview with no docs
        preview = self.admin.document_preview(self.submission)
        self.assertIn('No documents', preview)
    
    def test_kym_admin_actions(self):
        """Test admin actions for KYMSubmission"""
        self.admin.message_user = Mock()
        request = self.factory.get('/')
        request.user = self.admin_user
        queryset = KYMSubmission.objects.filter(pk=self.submission.pk)
        
        # Test mark_as_approved
        self.admin.mark_as_approved(request, queryset)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, 'approved')
        
        # Test mark_as_rejected
        self.admin.mark_as_rejected(request, queryset)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, 'rejected')
