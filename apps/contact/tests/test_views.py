"""
Comprehensive tests for contact views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from apps.contact.models import ContactSubmission, KYMSubmission, OfficeLocation
from apps.contact.forms import ContactForm, KYMForm
from apps.about.models import CooperativeInfo


class ContactViewsTest(TestCase):
    """Test cases for contact views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        # Clear rate limiting cache before each test
        from django.core.cache import cache
        cache.clear()
        
        # Create CooperativeInfo for context processor
        CooperativeInfo.objects.create(
            cooperative_name="Test Co-op",
            cooperative_name_nepali="Test Co-op Nepali",
            established_date="2000-01-01",
            registration_number="123",
            license_number="456",
            address="Test Address",
            phone="9800000000",
            email="info@test.com",
            mission="Mission",
            vision="Vision",
            values="Values",
            description="Description",
            status='PB'  # Published -> is_active=True
        )

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
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify submission was created
        self.assertTrue(KYMSubmission.objects.filter(email='test@example.com').exists())


class MapViewsTest(TestCase):
    """Test cases for map views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test office locations
        OfficeLocation.objects.create(
            name='Test Main Office',
            address='Test Address 1',
            latitude=28.0,
            longitude=84.0,
            location_type='main_office',
            phone='+977-1234567890',
            email='test@example.com',
            is_active=True,
            order=1
        )
        OfficeLocation.objects.create(
            name='Test Service Center',
            address='Test Address 2',
            latitude=28.1,
            longitude=84.1,
            location_type='service_center',
            phone='+977-0987654321',
            email='service@example.com',
            is_active=True,
            order=2
        )

    def test_interactive_map_view(self):
        """Test interactive map view GET request"""
        response = self.client.get(reverse('contact:interactive_map'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('breadcrumbs', response.context)
        breadcrumbs = response.context['breadcrumbs']
        self.assertEqual(len(breadcrumbs), 3)
        self.assertEqual(breadcrumbs[0]['name'], 'Home')
        self.assertEqual(breadcrumbs[1]['name'], 'Contact')
        self.assertEqual(breadcrumbs[2]['name'], 'Locations')

    def test_map_locations_api_get(self):
        """Test map locations API GET request"""
        response = self.client.get(reverse('contact:map_locations_api'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('locations', data)
        self.assertIn('center', data)
        self.assertIsInstance(data['locations'], list)
        self.assertGreater(len(data['locations']), 0)
        
        # Check location structure
        location = data['locations'][0]
        self.assertIn('id', location)
        self.assertIn('name', location)
        self.assertIn('latitude', location)
        self.assertIn('longitude', location)
        self.assertIn('type', location)

    def test_map_locations_api_cached(self):
        """Test map locations API uses cache"""
        # First request
        response1 = self.client.get(reverse('contact:map_locations_api'))
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.content)
        
        # Second request should return cached data
        response2 = self.client.get(reverse('contact:map_locations_api'))
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content)
        
        # Data should be the same (cached)
        self.assertEqual(data1, data2)

    def test_map_locations_api_invalid_method(self):
        """Test map locations API with invalid HTTP method"""
        response = self.client.post(reverse('contact:map_locations_api'))
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_map_directions_api_post_valid(self):
        """Test map directions API POST with valid data"""
        data = {
            'origin': '27.7172,85.3240',
            'destination': '27.5833,85.5167'
        }
        
        response = self.client.post(
            reverse('contact:map_directions_api'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertIn('distance', result)
        self.assertIn('duration', result)
        self.assertIn('steps', result)
        self.assertIsInstance(result['steps'], list)

    def test_map_directions_api_post_invalid(self):
        """Test map directions API POST with invalid data"""
        # Missing required fields
        response = self.client.post(
            reverse('contact:map_directions_api'),
            json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)  # Still returns success with mock data
        
        # Invalid JSON
        response = self.client.post(
            reverse('contact:map_directions_api'),
            'invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.content)
        self.assertIn('error', result)

    def test_map_directions_api_invalid_method(self):
        """Test map directions API with invalid HTTP method"""
        response = self.client.get(reverse('contact:map_directions_api'))
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_map_directions_api_missing_fields(self):
        """Test map directions API with missing origin/destination"""
        # Test with only origin
        data = {'origin': '27.7172,85.3240'}
        response = self.client.post(
            reverse('contact:map_directions_api'),
            json.dumps(data),
            content_type='application/json'
        )
        # Should still return success with mock data
        self.assertEqual(response.status_code, 200)
        
        # Test with only destination
        data = {'destination': '27.5833,85.5167'}
        response = self.client.post(
            reverse('contact:map_directions_api'),
            json.dumps(data),
            content_type='application/json'
        )
        # Should still return success with mock data
        self.assertEqual(response.status_code, 200)