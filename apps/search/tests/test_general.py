from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

from apps.search.services import SearchService
from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeAffiliation, LeadershipMessage, Person
)

class SearchServiceTestCase(TestCase):
    """Test functionality of SearchService"""
    
    def setUp(self):
        # Create dummy data
        self.timeline_event = CooperativeTimeline.objects.create(
            title="Migration to New Office",
            description="We moved to a larger office.",
            event_date="2023-01-01",
            is_active=True
        )
        self.person = Person.objects.create(
            full_name="Ram Bahadur",
            bio="Experienced manager.",
            position_general="Manager",
            is_active=True
        )
        
    def test_search_all_content(self):
        """Test searching across all content"""
        results = SearchService.search_all_content("Migration")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Migration to New Office")
        
        results = SearchService.search_all_content("Ram")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].full_name, "Ram Bahadur")
        
    def test_search_specific_types(self):
        """Test searching specific content types"""
        # Timeline
        results = SearchService.search_timeline("Migration")
        self.assertEqual(len(results), 1)
        
        # Team
        results = SearchService.search_team("Ram")
        self.assertEqual(len(results), 1)
        
        # Negative test
        results = SearchService.search_timeline("Ram")
        self.assertEqual(len(results), 0)

    def test_get_search_suggestions(self):
        """Test search suggestions"""
        suggestions = SearchService.get_search_suggestions("Mig")
        self.assertIn("Migration to New Office", suggestions)


class SearchViewsTestCase(TestCase):
    """Test search views"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('search:advanced_search')
        
        # Create dummy data
        self.timeline_event = CooperativeTimeline.objects.create(
            title="Annual General Meeting",
            description="Our AGM was huge success.",
            event_date="2023-12-01",
            is_active=True
        )

    def test_advanced_search_view_renders(self):
        """Test search page renders"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/advanced_search.html')

    def test_search_query(self):
        """Test search with query"""
        response = self.client.get(self.url, {'q': 'AGM'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), 1)
        self.assertEqual(response.context['results'][0].title, "Annual General Meeting")

    def test_search_type_filter(self):
        """Test search type filtering"""
        # Search for AGM in Team (should fail)
        response = self.client.get(self.url, {'q': 'AGM', 'type': 'team'})
        self.assertEqual(len(response.context['results']), 0)
        
        # Search for AGM in Events/Timeline (should succeed)
        # Note: Code maps 'events' to search_timeline
        response = self.client.get(self.url, {'q': 'AGM', 'type': 'events'})
        self.assertEqual(len(response.context['results']), 1)

    def test_search_api(self):
        """Test search API endpoint"""
        api_url = reverse('search:search_api')
        response = self.client.get(api_url, {'q': 'Ann'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('suggestions', data)
        # Check if we got results
        found = any(s['text'] == "Annual General Meeting" for s in data['suggestions'])
        self.assertTrue(found)
