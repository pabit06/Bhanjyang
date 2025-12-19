from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.contact.forms import ContactForm
from apps.contact.models import ContactSubmission


class ContactFormTest(TestCase):
    """Test cases for ContactForm"""
    
    def test_valid_form(self):
        """Test valid form submission"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+977-9812345678',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough content to pass validation.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_email(self):
        """Test invalid email"""
        form_data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough content to pass validation.'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_empty_required_fields(self):
        """Test empty required fields"""
        form_data = {
            'name': '',
            'email': '',
            'subject': '',
            'message': ''
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('subject', form.errors)
        self.assertIn('message', form.errors)
    
    def test_name_validation(self):
        """Test name field validation"""
        # Test invalid characters
        form_data = {
            'name': 'John123',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough content to pass validation.'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
        # Test too short name
        form_data['name'] = 'J'
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_phone_validation(self):
        """Test phone field validation"""
        # Test valid phone number
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+977-9812345678',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough content to pass validation.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid phone number (too short)
        form_data['phone'] = '123'
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
    
    def test_subject_validation(self):
        """Test subject field validation"""
        # Test spam keywords
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'spam message',
            'message': 'This is a test message with enough content to pass validation.'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)
        
        # Test too short subject
        form_data['subject'] = 'Hi'
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)
    
    def test_message_validation(self):
        """Test message field validation"""
        # Test too short message
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Hi'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        
        # Test excessive repetition
        form_data['message'] = 'test test test test test test test test test test test test test test test test'
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
    
    def test_clean_name_method(self):
        """Test clean_name method"""
        # Test valid name
        form_data = {'name': 'John Doe', 'email': 'test@example.com', 'subject': 'Test Subject', 'message': 'Test message with enough content'}
        form = ContactForm(data=form_data)
        if form.is_valid():
            cleaned_name = form.cleaned_data['name']
            self.assertEqual(cleaned_name, 'John Doe')
        
        # Test name with extra spaces
        form_data = {'name': '  John Doe  ', 'email': 'test@example.com', 'subject': 'Test Subject', 'message': 'Test message with enough content'}
        form = ContactForm(data=form_data)
        if form.is_valid():
            cleaned_name = form.cleaned_data['name']
            self.assertEqual(cleaned_name, 'John Doe')
    
    def test_clean_phone_method(self):
        """Test clean_phone method"""
        # Test valid phone number
        form_data = {'name': 'John Doe', 'email': 'test@example.com', 'phone': '+977-9812345678', 'subject': 'Test Subject', 'message': 'Test message with enough content'}
        form = ContactForm(data=form_data)
        if form.is_valid():
            cleaned_phone = form.cleaned_data['phone']
            self.assertEqual(cleaned_phone, '+9779812345678')
        
        # Test phone number without country code
        form_data = {'name': 'John Doe', 'email': 'test@example.com', 'phone': '9812345678', 'subject': 'Test Subject', 'message': 'Test message with enough content'}
        form = ContactForm(data=form_data)
        if form.is_valid():
            cleaned_phone = form.cleaned_data['phone']
            self.assertEqual(cleaned_phone, '9812345678')
    
    def test_clean_subject_method(self):
        """Test clean_subject method"""
        # Test valid subject
        form_data = {'name': 'John Doe', 'email': 'test@example.com', 'subject': 'Test Subject', 'message': 'Test message with enough content'}
        form = ContactForm(data=form_data)
        if form.is_valid():
            cleaned_subject = form.cleaned_data['subject']
            self.assertEqual(cleaned_subject, 'Test Subject')
        
        # Test subject with extra spaces
        form_data = {'name': 'John Doe', 'email': 'test@example.com', 'subject': '  Test Subject  ', 'message': 'Test message with enough content'}
        form = ContactForm(data=form_data)
        if form.is_valid():
            cleaned_subject = form.cleaned_data['subject']
            self.assertEqual(cleaned_subject, 'Test Subject')
    
    def test_clean_message_method(self):
        """Test clean_message method"""
        # Test valid message
        form_data = {'name': 'John Doe', 'email': 'test@example.com', 'subject': 'Test Subject', 'message': 'This is a test message with enough content to pass validation.'}
        form = ContactForm(data=form_data)
        if form.is_valid():
            cleaned_message = form.cleaned_data['message']
            self.assertEqual(cleaned_message, 'This is a test message with enough content to pass validation.')
        
        # Test message with extra spaces
        form_data = {'name': 'John Doe', 'email': 'test@example.com', 'subject': 'Test Subject', 'message': '  This is a test message with enough content to pass validation.  '}
        form = ContactForm(data=form_data)
        if form.is_valid():
            cleaned_message = form.cleaned_data['message']
            self.assertEqual(cleaned_message, 'This is a test message with enough content to pass validation.')


class ContactViewsTest(TestCase):
    """Test cases for contact views"""
    
    def setUp(self):
        self.client = Client()
    
    def test_contact_view_get(self):
        """Test contact view GET request"""
        response = self.client.get(reverse('contact:contact_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'name')
        self.assertContains(response, 'email')
        self.assertContains(response, 'subject')
        self.assertContains(response, 'message')
    
    def test_contact_view_post_valid(self):
        """Test contact view POST request with valid data"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+977-9812345678',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough content to pass validation.'
        }
        response = self.client.post(
            reverse('contact:contact_view'), 
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        # Should show success message
        self.assertContains(response, 'success')
    
    def test_contact_view_post_invalid(self):
        """Test contact view POST request with invalid data"""
        form_data = {
            'name': '',
            'email': 'invalid-email',
            'subject': '',
            'message': 'Hi'
        }
        response = self.client.post(
            reverse('contact:contact_view'), 
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        # Should return JSON with errors
        import json
        data = json.loads(response.content)
        self.assertIn('errors', data)


class ContactSubmissionModelTestCase(TestCase):
    """Test cases for ContactSubmission model"""
    
    def test_create_submission(self):
        """Test creating a contact submission"""
        submission = ContactSubmission.objects.create(
            name='John Doe',
            email='john@example.com',
            phone='+977-9812345678',
            subject='Test Subject',
            message='This is a test message with enough content.',
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        
        self.assertEqual(submission.name, 'John Doe')
        self.assertEqual(submission.email, 'john@example.com')
        self.assertEqual(submission.status, 'new')
        self.assertIsNotNone(submission.created_at)
        self.assertIsNotNone(submission.updated_at)
    
    def test_submission_str_representation(self):
        """Test string representation of submission"""
        submission = ContactSubmission.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            subject='Test Subject',
            message='Test message',
            ip_address='127.0.0.1'
        )
        
        expected_str = f"Jane Doe - Test Subject ({submission.created_at.strftime('%Y-%m-%d')})"
        self.assertEqual(str(submission), expected_str)
    
    def test_is_recent_method(self):
        """Test is_recent method"""
        submission = ContactSubmission.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message',
            ip_address='127.0.0.1'
        )
        
        # Should be recent (just created)
        self.assertTrue(submission.is_recent())
    
    def test_mark_as_resolved(self):
        """Test mark_as_resolved method"""
        submission = ContactSubmission.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message',
            ip_address='127.0.0.1'
        )
        
        submission.mark_as_resolved()
        
        self.assertEqual(submission.status, 'resolved')
        self.assertIsNotNone(submission.resolved_at)
    
    def test_mark_as_spam(self):
        """Test mark_as_spam method"""
        submission = ContactSubmission.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message',
            ip_address='127.0.0.1'
        )
        
        submission.mark_as_spam()
        
        self.assertEqual(submission.status, 'spam')
    
    def test_get_status_display_color(self):
        """Test get_status_display_color method"""
        submission = ContactSubmission.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message',
            ip_address='127.0.0.1'
        )
        
        # Test different status colors
        submission.status = 'new'
        self.assertEqual(submission.get_status_display_color(), 'text-blue-600')
        
        submission.status = 'resolved'
        self.assertEqual(submission.get_status_display_color(), 'text-green-600')
        
        submission.status = 'spam'
        self.assertEqual(submission.get_status_display_color(), 'text-red-600')
    
    def test_contact_view_post_spam(self):
        """Test contact view POST request with spam content"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'spam message',
            'message': 'This is a test message with enough content to pass validation.'
        }
        response = self.client.post(
            reverse('contact:contact_view'), 
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        # Should return JSON with errors
        import json
        data = json.loads(response.content)
        self.assertIn('errors', data)

