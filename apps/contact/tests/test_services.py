"""
Comprehensive tests for Contact services
"""
from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta

from apps.contact.services import ContactService, KYMService, ContactAnalyticsService
from apps.contact.models import ContactSubmission, KYMSubmission


class ContactServiceTest(TestCase):
    """Test cases for ContactService"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

    def test_get_contact_page_context(self):
        """Test get_contact_page_context returns correct structure"""
        context = ContactService.get_contact_page_context()
        
        self.assertIn('form', context)
        self.assertIn('breadcrumbs', context)
        self.assertEqual(len(context['breadcrumbs']), 2)
        self.assertEqual(context['breadcrumbs'][0]['name'], 'Home')
        self.assertEqual(context['breadcrumbs'][1]['name'], 'Contact')

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

class KYMServiceTest(TestCase):
    """Test cases for KYMService"""

    def setUp(self):
        self.form_data = {
            'full_name': 'Test User',
            'dob': '1990-01-01',
            'gender': 'M',
            'marital_status': 'Single',
            'phone': '1234567890',
            'email': 'test@example.com',
            'permanent_address': 'Test Address',
            'district': 'Kaski',
            'province': 'Gandaki Province',
            'father_name': 'Father Name',
            'mother_name': 'Mother Name',
            'grand_father_name': 'Grandfather Name',
            'occupation': 'Farmer',
            'income_source': 'Agriculture',
            'citizenship_front': SimpleUploadedFile('front.jpg', b'content', content_type='image/jpeg'),
            'citizenship_back': SimpleUploadedFile('back.jpg', b'content', content_type='image/jpeg'),
            'passport_photo_upload': SimpleUploadedFile('photo.jpg', b'content', content_type='image/jpeg'),
            'address_proof_upload': SimpleUploadedFile('proof.pdf', b'content', content_type='application/pdf'),
        }
        self.request_meta = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }

    def test_get_kym_page_context(self):
        """Test get_kym_page_context returns correct structure"""
        context = KYMService.get_kym_page_context()
        
        self.assertIn('form', context)
        self.assertIn('breadcrumbs', context)
        self.assertEqual(len(context['breadcrumbs']), 2)
        self.assertEqual(context['breadcrumbs'][1]['name'], 'KYM Form')

    def test_create_kym_submission(self):
        """Test creating a KYM submission"""
        submission = KYMService.create_kym_submission(self.form_data, {}, self.request_meta)
        
        self.assertIsNotNone(submission)
        self.assertEqual(submission.full_name, 'Test User')
        self.assertEqual(submission.email, 'test@example.com')
        self.assertEqual(submission.ip_address, '127.0.0.1')

    def test_create_kym_submission_with_optional_fields(self):
        """Test creating KYM submission with optional fields"""
        form_data = self.form_data.copy()
        form_data['nationality'] = 'Nepali'
        form_data['spouse_name'] = 'Spouse Name'
        form_data['estimated_income'] = 50000
        
        submission = KYMService.create_kym_submission(form_data, {}, self.request_meta)
        
        self.assertEqual(submission.nationality, 'Nepali')
        self.assertEqual(submission.spouse_name, 'Spouse Name')
        self.assertEqual(submission.estimated_income, 50000)


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

    def test_get_kym_stats(self):
        """Test getting KYM submission statistics"""
        # Create KYM submissions with different statuses
        KYMSubmission.objects.create(
            full_name='Test 1',
            dob='1990-01-01',
            gender='M',
            marital_status='Single',
            phone='1234567890',
            email='test1@example.com',
            permanent_address='Address 1',
            father_name='Father 1',
            mother_name='Mother 1',
            grand_father_name='Grandfather 1',
            occupation='Farmer',
            income_source='Agriculture',
            citizenship_front=SimpleUploadedFile('front1.jpg', b'content', content_type='image/jpeg'),
            citizenship_back=SimpleUploadedFile('back1.jpg', b'content', content_type='image/jpeg'),
            passport_photo=SimpleUploadedFile('photo1.jpg', b'content', content_type='image/jpeg'),
            address_proof=SimpleUploadedFile('proof1.pdf', b'content', content_type='application/pdf'),
            status='pending',
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        KYMSubmission.objects.create(
            full_name='Test 2',
            dob='1990-01-01',
            gender='F',
            marital_status='Married',
            phone='1234567891',
            email='test2@example.com',
            permanent_address='Address 2',
            father_name='Father 2',
            mother_name='Mother 2',
            grand_father_name='Grandfather 2',
            occupation='Teacher',
            income_source='Salary',
            citizenship_front=SimpleUploadedFile('front2.jpg', b'content', content_type='image/jpeg'),
            citizenship_back=SimpleUploadedFile('back2.jpg', b'content', content_type='image/jpeg'),
            passport_photo=SimpleUploadedFile('photo2.jpg', b'content', content_type='image/jpeg'),
            address_proof=SimpleUploadedFile('proof2.pdf', b'content', content_type='application/pdf'),
            status='approved',
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        
        stats = ContactAnalyticsService.get_kym_stats()
        
        self.assertIn('total_kym', stats)
        self.assertIn('pending_kym', stats)
        self.assertIn('approved_kym', stats)
        self.assertIn('rejected_kym', stats)
        
        self.assertEqual(stats['total_kym'], 2)
        self.assertEqual(stats['pending_kym'], 1)
        self.assertEqual(stats['approved_kym'], 1)
        self.assertEqual(stats['rejected_kym'], 0)

