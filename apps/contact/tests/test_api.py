from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from apps.contact.models import ContactSubmission, PrivacyPolicy
from apps.about.models import Staff, Person

class ContactAPITests(APITestCase):
    def setUp(self):
        # Create admin user for specific endpoints
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        
    def test_contact_submit_creates_submission(self):
        """Test submitting contact form via API."""
        url = reverse('contact_api:contact-submit')
        data = {
            'name': 'API User',
            'email': 'api@example.com',
            'subject': 'API Test',
            'message': 'This is a test message from API.'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertTrue(ContactSubmission.objects.filter(email='api@example.com').exists())
        
    def test_contact_stats_admin_only(self):
        """Test stats endpoint is protected and returns correct fields."""
        url = reverse('contact_api:contact-stats')
        
        # Unauthenticated
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Authenticated as Admin
        self.client.force_authenticate(user=self.admin)
        
        # Create some sample data
        ContactSubmission.objects.create(name='Test 1', message='Msg 1', email='t1@e.com', status='new', ip_address='127.0.0.1')
        ContactSubmission.objects.create(name='Test 2', message='Msg 2', email='t2@e.com', status='resolved', ip_address='127.0.0.1')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('new_count', response.data)
        self.assertIn('resolved_count', response.data)
        self.assertEqual(response.data['new_count'], 1)
        self.assertEqual(response.data['resolved_count'], 1)

    def test_privacy_policy_endpoint(self):
        """Test fetching privacy policy."""
        PrivacyPolicy.objects.create(title="Test Policy", content="<p>Content</p>", is_active=True)
        url = reverse('contact_api:contact-privacy')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Policy")
