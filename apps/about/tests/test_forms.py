"""
Tests for about app forms
"""
from django.test import TestCase

from apps.about.forms import ContactForm
# NewsletterSignupForm and FeedbackForm removed - no longer needed


class ContactFormTest(TestCase):
    """Test ContactForm"""
    
    def test_valid_form(self):
        """Test valid form submission"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_required_fields(self):
        """Test required fields"""
        form = ContactForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('subject', form.errors)
        self.assertIn('message', form.errors)
        self.assertIn('inquiry_type', form.errors)
    
    def test_invalid_email(self):
        """Test invalid email"""
        form_data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'subject': 'Test Subject',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_phone_validation(self):
        """Test phone number validation"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': 'invalid-phone',
            'subject': 'Test Subject',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
    
    def test_valid_phone(self):
        """Test valid phone number"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+977-98-1234567',
            'subject': 'Test Subject',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_optional_phone(self):
        """Test optional phone field"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_inquiry_type_choices(self):
        """Test inquiry type choices"""
        valid_types = ['general', 'membership', 'loan', 'savings', 'complaint', 'other']
        for inquiry_type in valid_types:
            form_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': 'Test message',
                'inquiry_type': inquiry_type
            }
            form = ContactForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Failed for inquiry_type: {inquiry_type}")


# NewsletterSignupFormTest and FeedbackFormTest removed - forms no longer needed

