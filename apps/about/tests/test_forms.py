"""
Tests for about app forms
"""
from django.test import TestCase

from apps.about.forms import ContactForm, NewsletterSignupForm, FeedbackForm


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


class NewsletterSignupFormTest(TestCase):
    """Test NewsletterSignupForm"""
    
    def test_valid_form(self):
        """Test valid form submission"""
        form_data = {
            'email': 'test@example.com',
            'name': 'Test User'
        }
        form = NewsletterSignupForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_required_email(self):
        """Test required email field"""
        form = NewsletterSignupForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_optional_name(self):
        """Test optional name field"""
        form_data = {
            'email': 'test@example.com'
        }
        form = NewsletterSignupForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_email(self):
        """Test invalid email"""
        form_data = {
            'email': 'invalid-email'
        }
        form = NewsletterSignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_interests_field(self):
        """Test interests field"""
        form_data = {
            'email': 'test@example.com',
            'interests': ['news', 'services']
        }
        form = NewsletterSignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['interests'], ['news', 'services'])


class FeedbackFormTest(TestCase):
    """Test FeedbackForm"""
    
    def test_valid_form(self):
        """Test valid form submission"""
        form_data = {
            'rating': '5',
            'feedback_type': 'website',
            'comments': 'Great website!',
            'email': 'test@example.com'
        }
        form = FeedbackForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_required_fields(self):
        """Test required fields"""
        form = FeedbackForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        self.assertIn('feedback_type', form.errors)
    
    def test_optional_fields(self):
        """Test optional fields"""
        form_data = {
            'rating': '5',
            'feedback_type': 'website'
        }
        form = FeedbackForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_rating_choices(self):
        """Test rating choices"""
        valid_ratings = ['1', '2', '3', '4', '5']
        for rating in valid_ratings:
            form_data = {
                'rating': rating,
                'feedback_type': 'website'
            }
            form = FeedbackForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Failed for rating: {rating}")
    
    def test_feedback_type_choices(self):
        """Test feedback type choices"""
        valid_types = ['website', 'content', 'services', 'performance', 'mobile', 'other']
        for feedback_type in valid_types:
            form_data = {
                'rating': '5',
                'feedback_type': feedback_type
            }
            form = FeedbackForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Failed for feedback_type: {feedback_type}")

