"""
Tests for contact view error handling and edge cases
"""
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from unittest.mock import patch, Mock
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.contact.views import ContactView
from apps.about.models import CooperativeInfo


class ContactViewErrorHandlingTest(TestCase):
    """Test error handling in contact views"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.client = Client()
        
        # Create CooperativeInfo for context processor
        CooperativeInfo.objects.create(
            cooperative_name="Test Co-op",
            cooperative_name_nepali="Test Co-op Nepali",
            status='PB',
            email='info@test.com',
            phone='9800000000',
            established_date="2000-01-01"
        )

    def test_contact_view_get(self):
        """Test contact view GET request"""
        response = self.client.get(reverse('contact:contact_view'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contact")

    def test_contact_view_post_invalid_form(self):
        """Test contact view POST with invalid form data"""
        response = self.client.post(reverse('contact:contact_view'), {
            'name': '',  # Invalid: empty name
            'email': 'invalid-email',  # Invalid email
            'subject': '',
            'message': ''
        })
        
        # Contact view returns 400 for non-AJAX requests
        self.assertEqual(response.status_code, 400)

    def test_contact_view_post_missing_csrf(self):
        """Test contact view POST without CSRF token"""
        # Use client without CSRF
        from django.test import Client
        csrf_client = Client(enforce_csrf_checks=True)
        
        response = csrf_client.post(reverse('contact:contact_view'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test',
            'message': 'Test message'
        })
        
        # Should return 403 or 400 for CSRF failure
        self.assertIn(response.status_code, [403, 400])

    def test_contact_view_post_with_attachment(self):
        """Test contact view POST with file attachment"""
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file content",
            content_type="application/pdf"
        )
        
        response = self.client.post(
            reverse('contact:contact_view'),
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'subject': 'Test Subject',
                'message': 'Test message with attachment',
                'attachment': test_file
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Required for AJAX
        )
        
        # Should handle file upload (200 for success, 400 for invalid)
        self.assertIn(response.status_code, [200, 400])

