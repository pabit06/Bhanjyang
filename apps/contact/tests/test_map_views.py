"""
Tests for contact app map views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
import json

from apps.contact.models import OfficeLocation


class MapViewsTest(TestCase):
    """Test map views"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
        
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
        """Test interactive map view"""
        url = reverse('contact:interactive_map')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact/interactive_map.html')
        self.assertIn('breadcrumbs', response.context)
    
    def test_map_locations_api_get(self):
        """Test map locations API GET request"""
        url = reverse('contact:map_locations_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('locations', data)
        self.assertIn('center', data)
        self.assertIsInstance(data['locations'], list)
        self.assertGreater(len(data['locations']), 0)
    
    def test_map_locations_api_caching(self):
        """Test map locations API caching"""
        url = reverse('contact:map_locations_api')
        # First request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        # Second request should use cache
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.content, response2.content)
    
    def test_map_locations_api_structure(self):
        """Test map locations API response structure"""
        url = reverse('contact:map_locations_api')
        response = self.client.get(url)
        data = json.loads(response.content)
        
        # Check location structure
        if len(data['locations']) > 0:
            location = data['locations'][0]
            self.assertIn('id', location)
            self.assertIn('name', location)
            self.assertIn('address', location)
            self.assertIn('latitude', location)
            self.assertIn('longitude', location)
            self.assertIn('type', location)
        
        # Check center structure
        center = data['center']
        self.assertIn('latitude', center)
        self.assertIn('longitude', center)
        self.assertIn('zoom', center)
    
    def test_map_directions_api_post(self):
        """Test map directions API POST request"""
        url = reverse('contact:map_directions_api')
        data = {
            'origin': 'Kathmandu',
            'destination': 'Bhanjyang'
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('status', response_data)
        self.assertIn('distance', response_data)
        self.assertIn('duration', response_data)
        self.assertIn('steps', response_data)
    
    def test_map_directions_api_invalid_request(self):
        """Test map directions API with invalid request"""
        url = reverse('contact:map_directions_api')
        response = self.client.post(
            url,
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_map_directions_api_missing_data(self):
        """Test map directions API with missing data"""
        url = reverse('contact:map_directions_api')
        data = {}
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        # Should handle missing data gracefully
        self.assertIn(response.status_code, [200, 400])
    

