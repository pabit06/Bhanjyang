from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.about.models import Person, CooperativeTimeline

class ContentSearchAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('search:content_search_api')
        
        # Create test data
        self.person = Person.objects.create(
            full_name="Test Person",
            bio="Unique Bio Content",
            is_active=True
        )
        
        self.event = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Event Description",
            event_date=timezone.now(),
            is_active=True
        )

    def test_search_no_query(self):
        """Test search with no query returns empty results"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_results'], 0)
        self.assertEqual(data['results'], [])

    def test_search_all_content(self):
        """Test search across all content types"""
        response = self.client.get(self.url, {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Both person and event have "Test" in their fields
        self.assertEqual(data['total_results'], 2)
        
    def test_search_type_filter(self):
        """Test filtering by content type"""
        # Test team filter
        response = self.client.get(self.url, {'q': 'Test', 'type': 'team'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_results'], 1)
        self.assertEqual(data['results'][0]['model_type'], 'person')
        
        # Test events filter
        response = self.client.get(self.url, {'q': 'Test', 'type': 'events'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_results'], 1)
        self.assertEqual(data['results'][0]['model_type'], 'cooperativetimeline')

    def test_pagination(self):
        """Test pagination logic"""
        response = self.client.get(self.url, {'q': 'Test', 'limit': 1, 'page': 1})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertTrue(data['has_next'])
        self.assertFalse(data['has_previous'])
        
        # Get second page
        response = self.client.get(self.url, {'q': 'Test', 'limit': 1, 'page': 2})
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertFalse(data['has_next'])
        self.assertTrue(data['has_previous'])
