"""
Comprehensive tests for Contact services
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch, MagicMock
import time

from apps.contact.models import ContactSubmission, KYMSubmission
from apps.contact.services import (
    ContactService, KYMService, ContactAnalyticsService
)
from apps.contact.forms import ContactForm, KYMForm


class ContactServiceTest(TestCase):
    """Test suite for ContactService"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'message': 'Test message',
            'subject': 'Test Subject'
        }
        self.files = {}
        self.request_meta = {
            'REMOTE_ADDR': '192.168.1.1',
            'HTTP_USER_AGENT': 'Test Agent'
        }
    
    def test_get_contact_page_context(self):
        """Test getting contact page context"""
        context = ContactService.get_contact_page_context()
        self.assertIn('form', context)
        self.assertIn('breadcrumbs', context)
        self.assertIsInstance(context['form'], ContactForm)
        self.assertEqual(len(context['breadcrumbs']), 2)
    
    def test_create_contact_submission_with_subject(self):
        """Test creating contact submission with subject"""
        submission = ContactService.create_contact_submission(
            self.form_data, self.files, self.request_meta
        )
        self.assertIsNotNone(submission)
        self.assertEqual(submission.name, 'John Doe')
        self.assertEqual(submission.email, 'john@example.com')
        self.assertEqual(submission.subject, 'Test Subject')
        self.assertEqual(submission.ip_address, '192.168.1.1')
    
    def test_create_contact_submission_without_subject(self):
        """Test creating contact submission without subject"""
        form_data = self.form_data.copy()
        del form_data['subject']
        form_data['message'] = 'This is a long message that should be truncated for subject'
        
        submission = ContactService.create_contact_submission(
            form_data, self.files, self.request_meta
        )
        self.assertIsNotNone(submission)
        self.assertTrue(submission.subject.startswith('This is a long message'))
        self.assertIn('...', submission.subject)
    
    def test_create_contact_submission_with_attachment(self):
        """Test creating contact submission with attachment"""
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            "test.txt", file_content, content_type="text/plain"
        )
        files = {'attachment': uploaded_file}
        
        submission = ContactService.create_contact_submission(
            self.form_data, files, self.request_meta
        )
        self.assertIsNotNone(submission.attachment)
    
    def test_create_contact_submission_without_phone(self):
        """Test creating contact submission without phone"""
        form_data = self.form_data.copy()
        del form_data['phone']
        
        submission = ContactService.create_contact_submission(
            form_data, self.files, self.request_meta
        )
        self.assertEqual(submission.phone, '')
    
    @patch('apps.contact.services.send_contact_email')
    @patch('apps.contact.services.send_auto_response_email')
    def test_send_contact_notification_emails_with_celery(self, mock_auto, mock_contact):
        """Test sending notification emails with Celery"""
        submission = ContactSubmission.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Test',
            message='Test message',
            ip_address='192.168.1.1'
        )
        
        # Mock Celery delay method
        mock_contact.delay = MagicMock()
        mock_auto.delay = MagicMock()
        
        ContactService.send_contact_notification_emails(submission)
        
        # Check that delay was called (Celery available)
        try:
            mock_contact.delay.assert_called_once()
            mock_auto.delay.assert_called_once()
        except AttributeError:
            # Celery not available, should call synchronously
            mock_contact.assert_called_once()
            mock_auto.assert_called_once()
    
    @patch('apps.contact.services.send_contact_email')
    @patch('apps.contact.services.send_auto_response_email')
    def test_send_contact_notification_emails_without_celery(self, mock_auto, mock_contact):
        """Test sending notification emails without Celery"""
        submission = ContactSubmission.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Test',
            message='Test message',
            ip_address='192.168.1.1'
        )
        
        # Remove delay method to simulate no Celery
        if hasattr(mock_contact, 'delay'):
            delattr(mock_contact, 'delay')
        if hasattr(mock_auto, 'delay'):
            delattr(mock_auto, 'delay')
        
        ContactService.send_contact_notification_emails(submission)
        
        # Should call synchronously
        mock_contact.assert_called_once()
        mock_auto.assert_called_once()
    
    def test_get_performance_metrics(self):
        """Test getting performance metrics"""
        from django.db import connection
        start_time = time.time()
        db_queries_start = len(connection.queries)
        
        # Do some work
        ContactSubmission.objects.create(
            name='Test', email='test@example.com',
            subject='Test', message='Test',
            ip_address='192.168.1.1'
        )
        
        processing_time, db_queries_count = ContactService.get_performance_metrics(
            start_time, db_queries_start
        )
        
        self.assertGreater(processing_time, 0)
        self.assertGreaterEqual(db_queries_count, 0)


class KYMServiceTest(TestCase):
    """Test suite for KYMService"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'full_name': 'John Doe',
            'dob': '1990-01-01',
            'gender': 'male',
            'marital_status': 'single',
            'phone': '1234567890',
            'email': 'john@example.com',
            'permanent_address': '123 Main St',
            'father_name': 'Father Name',
            'mother_name': 'Mother Name',
            'grand_father_name': 'Grandfather Name',
            'occupation': 'Engineer',
            'income_source': 'Salary',
            'citizenship_front': SimpleUploadedFile("front.jpg", b"content"),
            'citizenship_back': SimpleUploadedFile("back.jpg", b"content"),
            'passport_photo_upload': SimpleUploadedFile("photo.jpg", b"content"),
            'address_proof_upload': SimpleUploadedFile("address.pdf", b"content"),
        }
        self.request_meta = {
            'REMOTE_ADDR': '192.168.1.1',
            'HTTP_USER_AGENT': 'Test Agent'
        }
    
    def test_get_kym_page_context(self):
        """Test getting KYM page context"""
        context = KYMService.get_kym_page_context()
        self.assertIn('form', context)
        self.assertIn('breadcrumbs', context)
        self.assertIsInstance(context['form'], KYMForm)
    
    def test_create_kym_submission(self):
        """Test creating KYM submission"""
        submission = KYMService.create_kym_submission(
            self.form_data, {}, self.request_meta
        )
        self.assertIsNotNone(submission)
        self.assertEqual(submission.full_name, 'John Doe')
        self.assertEqual(submission.email, 'john@example.com')
        self.assertEqual(submission.ip_address, '192.168.1.1')
    
    def test_create_kym_submission_with_optional_fields(self):
        """Test creating KYM submission with optional fields"""
        form_data = self.form_data.copy()
        form_data['nationality'] = 'Nepali'
        form_data['district'] = 'Kaski'
        form_data['province'] = 'Gandaki'
        form_data['spouse_name'] = 'Spouse Name'
        form_data['nominee_name'] = 'Nominee Name'
        form_data['estimated_income'] = 50000
        form_data['income_proof_upload'] = SimpleUploadedFile("income.pdf", b"content")
        
        submission = KYMService.create_kym_submission(
            form_data, {}, self.request_meta
        )
        self.assertEqual(submission.nationality, 'Nepali')
        self.assertEqual(submission.district, 'Kaski')
        self.assertEqual(submission.spouse_name, 'Spouse Name')
        self.assertIsNotNone(submission.estimated_income)


class ContactAnalyticsServiceTest(TestCase):
    """Test suite for ContactAnalyticsService"""
    
    def setUp(self):
        """Set up test data"""
        # Create test submissions
        ContactSubmission.objects.create(
            name='Test 1', email='test1@example.com',
            subject='Test', message='Test', status='new',
            ip_address='192.168.1.1'
        )
        ContactSubmission.objects.create(
            name='Test 2', email='test2@example.com',
            subject='Test', message='Test', status='resolved',
            ip_address='192.168.1.2'
        )
        ContactSubmission.objects.create(
            name='Test 3', email='test3@example.com',
            subject='Test', message='Test', status='spam',
            ip_address='192.168.1.3'
        )
        # Recent submission
        recent = ContactSubmission.objects.create(
            name='Recent', email='recent@example.com',
            subject='Test', message='Test', status='new',
            ip_address='192.168.1.4'
        )
        recent.created_at = timezone.now() - timezone.timedelta(hours=12)
        recent.save()
    
    def test_get_submission_stats(self):
        """Test getting submission statistics"""
        stats = ContactAnalyticsService.get_submission_stats()
        self.assertIn('total_submissions', stats)
        self.assertIn('new_submissions', stats)
        self.assertIn('resolved_submissions', stats)
        self.assertIn('spam_submissions', stats)
        self.assertIn('recent_submissions', stats)
        self.assertGreaterEqual(stats['total_submissions'], 4)
        self.assertGreaterEqual(stats['new_submissions'], 2)
    
    def test_get_kym_stats(self):
        """Test getting KYM statistics"""
        # Create test KYM submissions
        KYMSubmission.objects.create(
            full_name='Test 1', email='test1@example.com',
            dob='1990-01-01', gender='male', marital_status='single',
            phone='1234567890', permanent_address='Test',
            father_name='Father', mother_name='Mother',
            grand_father_name='Grandfather', occupation='Test',
            income_source='Test', status='pending',
            ip_address='192.168.1.1',
            citizenship_front=SimpleUploadedFile("front.jpg", b"content"),
            citizenship_back=SimpleUploadedFile("back.jpg", b"content"),
            passport_photo=SimpleUploadedFile("photo.jpg", b"content"),
            address_proof=SimpleUploadedFile("address.pdf", b"content")
        )
        KYMSubmission.objects.create(
            full_name='Test 2', email='test2@example.com',
            dob='1990-01-01', gender='male', marital_status='single',
            phone='1234567890', permanent_address='Test',
            father_name='Father', mother_name='Mother',
            grand_father_name='Grandfather', occupation='Test',
            income_source='Test', status='approved',
            ip_address='192.168.1.2',
            citizenship_front=SimpleUploadedFile("front2.jpg", b"content"),
            citizenship_back=SimpleUploadedFile("back2.jpg", b"content"),
            passport_photo=SimpleUploadedFile("photo2.jpg", b"content"),
            address_proof=SimpleUploadedFile("address2.pdf", b"content")
        )
        
        stats = ContactAnalyticsService.get_kym_stats()
        self.assertIn('total_kym', stats)
        self.assertIn('pending_kym', stats)
        self.assertIn('approved_kym', stats)
        self.assertIn('rejected_kym', stats)
        self.assertGreaterEqual(stats['total_kym'], 2)
        self.assertGreaterEqual(stats['pending_kym'], 1)
        self.assertGreaterEqual(stats['approved_kym'], 1)

