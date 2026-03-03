"""
Comprehensive tests for Contact services
"""
from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta

from apps.contact.services import ContactService, ContactAnalyticsService
from apps.contact.models import ContactSubmission


class ContactServiceTest(TestCase):
    """Test cases for ContactService"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

    def test_get_contact_page_context(self):
        """Test get_contact_page_context returns correct structure"""
        from django.utils.translation import activate
        # Ensure English language for consistent test results
        activate('en')
        
        context = ContactService.get_contact_page_context()
        
        self.assertIn('form', context)
        self.assertIn('breadcrumbs', context)
        self.assertEqual(len(context['breadcrumbs']), 2)
        # Check that breadcrumbs exist and have correct structure
        self.assertIn('name', context['breadcrumbs'][0])
        self.assertIn('url', context['breadcrumbs'][0])
        self.assertEqual(context['breadcrumbs'][0]['url'], '/')
        self.assertEqual(context['breadcrumbs'][1]['url'], '/contact/')

    def test_create_contact_submission_basic(self):
        """Test creating a basic contact submission"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test message content'
        }
        files = {}
        request_meta = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        submission = ContactService.create_contact_submission(form_data, files, request_meta)
        
        self.assertIsNotNone(submission)
        self.assertEqual(submission.name, 'Test User')
        self.assertEqual(submission.email, 'test@example.com')
        self.assertEqual(submission.subject, 'Test Subject')
        self.assertEqual(submission.ip_address, '127.0.0.1')
        self.assertEqual(submission.user_agent, 'Test Browser')

    def test_create_contact_submission_without_subject(self):
        """Test creating submission without subject (auto-generated)"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'message': 'This is a long message that will be truncated for the subject line'
        }
        files = {}
        request_meta = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        submission = ContactService.create_contact_submission(form_data, files, request_meta)
        
        self.assertIsNotNone(submission.subject)
        self.assertIn('This is a long message', submission.subject)
        self.assertIn('...', submission.subject)

    def test_create_contact_submission_with_attachment(self):
        """Test creating submission with file attachment"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        files = {
            'attachment': SimpleUploadedFile('test.pdf', b'file content', content_type='application/pdf')
        }
        request_meta = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        submission = ContactService.create_contact_submission(form_data, files, request_meta)
        
        self.assertIsNotNone(submission.attachment)
        self.assertTrue(submission.has_attachment())

    def test_create_contact_submission_without_phone(self):
        """Test creating contact submission without phone"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        files = {}
        request_meta = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Agent'
        }
        
        submission = ContactService.create_contact_submission(form_data, files, request_meta)
        
        self.assertEqual(submission.phone, '')

    def test_send_contact_notification_emails(self):
        """Test sending notification emails with improved mocking"""
        submission = ContactSubmission.objects.create(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            subject='Test Subject',
            message='Test message',
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        
        with patch('apps.contact.services.send_contact_email') as mock_contact, \
             patch('apps.contact.services.send_auto_response_email') as mock_auto:
            
            # Mock delay attribute to simulate Celery if present
            mock_contact.delay = MagicMock()
            mock_auto.delay = MagicMock()
            
            ContactService.send_contact_notification_emails(submission)
            
            # Verify attempts to call (either via delay or direct)
            # Verify attempts to call (either via delay or direct)
            try:
                mock_contact.delay.assert_called()
            except AssertionError:
                try:
                    mock_contact.assert_called()
                except AssertionError:
                    raise AssertionError("Neither send_contact_email.delay() nor send_contact_email() was called.")


class ContactAnalyticsServiceTest(TestCase):
    """Test cases for ContactAnalyticsService"""

    def setUp(self):
        """Set up test data"""
        # Create submissions with different statuses
        ContactSubmission.objects.create(
            name='User 1',
            email='user1@example.com',
            subject='Test 1',
            message='Message 1',
            status='new',
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        ContactSubmission.objects.create(
            name='User 2',
            email='user2@example.com',
            subject='Test 2',
            message='Message 2',
            status='resolved',
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        ContactSubmission.objects.create(
            name='User 3',
            email='user3@example.com',
            subject='Test 3',
            message='Message 3',
            status='spam',
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        # Recent submission
        recent = ContactSubmission.objects.create(
            name='User 4',
            email='user4@example.com',
            subject='Test 4',
            message='Message 4',
            status='new',
            created_at=timezone.now() - timedelta(hours=12),
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )

    def test_get_submission_stats(self):
        """Test getting submission statistics"""
        stats = ContactAnalyticsService.get_submission_stats()
        
        self.assertIn('total_submissions', stats)
        self.assertIn('new_submissions', stats)
        self.assertIn('resolved_submissions', stats)
        self.assertIn('spam_submissions', stats)
        self.assertIn('recent_submissions', stats)
        
        self.assertEqual(stats['total_submissions'], 4)
        self.assertEqual(stats['new_submissions'], 2)  # User 1 and User 4
        self.assertEqual(stats['resolved_submissions'], 1)
        self.assertEqual(stats['spam_submissions'], 1)
        self.assertGreaterEqual(stats['recent_submissions'], 1)

