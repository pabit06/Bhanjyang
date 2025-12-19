"""
Comprehensive tests for contact views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from apps.contact.models import ContactSubmission, KYMSubmission
from apps.contact.forms import ContactForm, KYMForm


class ContactViewsTest(TestCase):
    """Test cases for contact views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

    def test_contact_view_get(self):
        """Test contact view GET request"""
        response = self.client.get(reverse('contact:contact_view'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('breadcrumbs', response.context)

    def test_contact_view_post_valid(self):
        """Test contact view POST with valid data"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        
        response = self.client.post(
            reverse('contact:contact_view'),
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify submission was created
        self.assertTrue(ContactSubmission.objects.filter(email='test@example.com').exists())

    def test_contact_view_post_with_attachment(self):
        """Test contact view POST with file attachment"""
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file content",
            content_type="application/pdf"
        )
        
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test message',
            'attachment': test_file
        }
        
        response = self.client.post(
            reverse('contact:contact_view'),
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_contact_view_post_invalid(self):
        """Test contact view POST with invalid data"""
        form_data = {
            'name': '',  # Invalid
            'email': 'invalid-email',  # Invalid
            'subject': '',
            'message': ''
        }
        
        response = self.client.post(
            reverse('contact:contact_view'),
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_kym_view_get(self):
        """Test KYM view GET request"""
        response = self.client.get(reverse('contact:kym_form'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_kym_view_post_valid(self):
        """Test KYM view POST with valid data"""
        form_data = {
            'full_name': 'Test User',
            'dob': '1990-01-01',
            'gender': 'male',  # Valid choice: 'male', 'female', or 'other'
            'marital_status': 'single',  # Valid choice: 'single', 'married', 'divorced', 'widowed'
            'nationality': 'Nepali',  # Required field
            'district': 'Kaski',  # Required field
            'province': 'Gandaki Province',  # Required field
            'phone': '1234567890',
            'email': 'test@example.com',
            'permanent_address': 'Test Address',
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
        
        response = self.client.post(
            reverse('contact:kym_form'),
            form_data
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify submission was created
        self.assertTrue(KYMSubmission.objects.filter(email='test@example.com').exists())

