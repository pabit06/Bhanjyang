"""
Tests for contact app tasks
"""
from django.test import TestCase, override_settings
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from apps.contact.tasks import (
    send_contact_email,
    send_auto_response_email,
    cleanup_old_contact_submissions
)
from apps.contact.models import ContactSubmission


class ContactTasksTest(TestCase):
    """Test contact tasks"""
    
    def setUp(self):
        self.submission_data = {
            'subject': 'Test Subject',
            'message': 'Test message',
            'name': 'Test User',
            'email': 'test@example.com',
            'submission_id': 'test_123'
        }
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_contact_email(self):
        """Test sending contact email"""
        result = send_contact_email(self.submission_data)
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertIn('admin@bhanjyang.coop.np', mail.outbox[0].recipients())
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_contact_email_with_submission_id(self):
        """Test sending contact email with submission ID"""
        result = send_contact_email(self.submission_data)
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
    
    @patch('apps.contact.tasks.send_mail')
    @patch('apps.contact.tasks.CELERY_AVAILABLE', False)
    def test_send_contact_email_failure(self, mock_send_mail, *_):
        """Test contact email failure handling (sync path: returns False)"""
        mock_send_mail.side_effect = Exception("Email error")
        result = send_contact_email(self.submission_data)
        self.assertFalse(result)

    @patch('apps.contact.tasks.send_mail')
    @patch('apps.contact.tasks.CELERY_AVAILABLE', True)
    def test_send_contact_email_failure_sync_fallback_with_celery_installed(
        self, mock_send_mail, *_
    ):
        """Sync fallback must return False when Celery is installed but not in a worker."""
        mock_send_mail.side_effect = Exception("Email error")
        # Direct call mimics ContactService sync fallback when broker is unavailable.
        result = send_contact_email(self.submission_data)
        self.assertFalse(result)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_auto_response_email(self):
        """Test sending auto-response email"""
        result = send_auto_response_email(
            user_email='test@example.com',
            user_name='Test User',
            subject='Test Subject',
            submission_id='test_123'
        )
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Thank you for contacting', mail.outbox[0].subject)
        self.assertIn('test@example.com', mail.outbox[0].recipients())
        self.assertIn('Test User', mail.outbox[0].body)
        self.assertIn('test_123', mail.outbox[0].body)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_auto_response_email_content(self):
        """Test auto-response email content"""
        send_auto_response_email(
            user_email='test@example.com',
            user_name='Test User',
            subject='Test Subject',
            submission_id='test_123'
        )
        email_body = mail.outbox[0].body
        self.assertIn('Test User', email_body)
        self.assertIn('Test Subject', email_body)
        self.assertIn('test_123', email_body)
        self.assertIn('24-48 hours', email_body)
    
    @patch('apps.contact.tasks.send_mail')
    @patch('apps.contact.tasks.CELERY_AVAILABLE', False)
    def test_send_auto_response_email_failure(self, mock_send_mail, *_):
        """Test auto-response email failure handling (sync path: returns False)"""
        mock_send_mail.side_effect = Exception("Email error")
        result = send_auto_response_email(
            user_email='test@example.com',
            user_name='Test User',
            subject='Test Subject',
            submission_id='test_123'
        )
        self.assertFalse(result)

    @patch('apps.contact.tasks.send_mail')
    @patch('apps.contact.tasks.CELERY_AVAILABLE', True)
    def test_send_auto_response_email_failure_sync_fallback_with_celery_installed(
        self, mock_send_mail, *_
    ):
        """Sync fallback must return False when Celery is installed but not in a worker."""
        mock_send_mail.side_effect = Exception("Email error")
        result = send_auto_response_email(
            user_email='test@example.com',
            user_name='Test User',
            subject='Test Subject',
            submission_id='test_123'
        )
        self.assertFalse(result)
    
    def test_cleanup_old_contact_submissions(self):
        """Test cleaning up old contact submissions"""
        # Create old resolved submission
        old_submission = ContactSubmission.objects.create(
            name='Old User',
            email='old@example.com',
            subject='Old Subject',
            message='Old message',
            status='resolved',
            ip_address='127.0.0.1'
        )
        ContactSubmission.objects.filter(pk=old_submission.pk).update(created_at=timezone.now() - timedelta(days=400))
        
        # Create recent submission (should not be deleted)
        recent_submission = ContactSubmission.objects.create(
            name='Recent User',
            email='recent@example.com',
            subject='Recent Subject',
            message='Recent message',
            status='resolved',
            ip_address='127.0.0.1'
        )
        ContactSubmission.objects.filter(pk=recent_submission.pk).update(created_at=timezone.now() - timedelta(days=100))
        
        # Create unresolved old submission (should not be deleted)
        unresolved_old = ContactSubmission.objects.create(
            name='Unresolved User',
            email='unresolved@example.com',
            subject='Unresolved Subject',
            message='Unresolved message',
            status='pending',
            ip_address='127.0.0.1'
        )
        ContactSubmission.objects.filter(pk=unresolved_old.pk).update(created_at=timezone.now() - timedelta(days=400))
        
        count = cleanup_old_contact_submissions()
        self.assertEqual(count, 1)
        self.assertFalse(ContactSubmission.objects.filter(id=old_submission.id).exists())
        self.assertTrue(ContactSubmission.objects.filter(id=recent_submission.id).exists())
        self.assertTrue(ContactSubmission.objects.filter(id=unresolved_old.id).exists())
    
    def test_cleanup_old_contact_submissions_no_old(self):
        """Test cleanup when no old submissions exist"""
        # Create only recent submissions
        ContactSubmission.objects.create(
            name='Recent User',
            email='recent@example.com',
            subject='Recent Subject',
            message='Recent message',
            status='resolved',
            ip_address='127.0.0.1',
            created_at=timezone.now() - timedelta(days=100)
        )
        
        count = cleanup_old_contact_submissions()
        self.assertEqual(count, 0)
    
    def test_cleanup_old_contact_submissions_error_handling(self):
        """Test cleanup error handling"""
        with patch('apps.contact.models.ContactSubmission.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")
            count = cleanup_old_contact_submissions()
            self.assertEqual(count, 0)

