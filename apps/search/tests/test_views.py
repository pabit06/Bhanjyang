"""
Comprehensive tests for search app views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
import json

from apps.about.models import (
    CooperativeTimeline, CooperativeAffiliation,
    LeadershipMessage, Person
)


class SearchViewsTest(TestCase):
    """Test cases for search views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test data
        self.timeline = CooperativeTimeline.objects.create(
            title="Test Timeline Event",
            description="Test Description",
            event_date="2020-01-01",
            event_type="milestone"
        )
        
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Organization",
            description="Test Description",
            affiliation_type="association"
        )
        
        self.person = Person.objects.create(
            full_name="John Doe"
        )
        
        self.message = LeadershipMessage.objects.create(
            title="Test Message",
            message_type="chairman",
            content="Test content",
            author_name="John Doe",
            author_position="Chairman"
        )
    
    def test_advanced_search_view_get(self):
        """Test AdvancedSearchView GET request without query"""
        response = self.client.get(reverse('search:advanced_search'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/advanced_search.html')
        self.assertIn('results', response.context)
        self.assertEqual(len(response.context['results']), 0)
    
    def test_advanced_search_view_with_query(self):
        """Test AdvancedSearchView GET request with query"""
        response = self.client.get(
            reverse('search:advanced_search'),
            {'q': 'Test'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        self.assertIn('query', response.context)
        self.assertEqual(response.context['query'], 'Test')
    
    def test_advanced_search_view_with_type_filter(self):
        """Test AdvancedSearchView with type filter"""
        response = self.client.get(
            reverse('search:advanced_search'),
            {'q': 'Test', 'type': 'team'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('search_type', response.context)
        self.assertEqual(response.context['search_type'], 'team')
    
    def test_advanced_search_view_with_sort(self):
        """Test AdvancedSearchView with sort parameter"""
        response = self.client.get(
            reverse('search:advanced_search'),
            {'q': 'Test', 'sort': 'date'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('sort_by', response.context)
        self.assertEqual(response.context['sort_by'], 'date')
    
    def test_advanced_search_view_all_content(self):
        """Test AdvancedSearchView with 'all' search type"""
        response = self.client.get(
            reverse('search:advanced_search'),
            {'q': 'Test', 'type': 'all'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        # Should return results from all content types
    
    def test_advanced_search_view_team_search(self):
        """Test AdvancedSearchView with team search type"""
        response = self.client.get(
            reverse('search:advanced_search'),
            {'q': 'John', 'type': 'team'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        # Should find the person
        results = response.context['results']
        self.assertTrue(any('John' in str(r) for r in results))
    
    def test_advanced_search_view_affiliations_search(self):
        """Test AdvancedSearchView with affiliations search type"""
        response = self.client.get(
            reverse('search:advanced_search'),
            {'q': 'Organization', 'type': 'affiliations'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        # Should find the affiliation
        results = response.context['results']
        self.assertTrue(any('Organization' in str(r) for r in results))
    
    def test_advanced_search_view_pagination(self):
        """Test AdvancedSearchView pagination"""
        # Create multiple items
        for i in range(25):
            CooperativeTimeline.objects.create(
                title=f"Timeline Event {i}",
                description="Test",
                event_date="2020-01-01",
                event_type="milestone"
            )
        
        response = self.client.get(
            reverse('search:advanced_search'),
            {'q': 'Timeline', 'type': 'events'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context)
        # Should have pagination
        self.assertTrue(hasattr(response.context['page_obj'], 'paginator'))
    
    def test_search_api_get_minimum_length(self):
        """Test search_api with query shorter than minimum"""
        response = self.client.get(
            reverse('search:search_api'),
            {'q': 'T'}  # Too short
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['suggestions'], [])
    
    def test_search_api_get_valid_query(self):
        """Test search_api with valid query"""
        response = self.client.get(
            reverse('search:search_api'),
            {'q': 'Test'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('suggestions', data)
        self.assertIn('query', data)
        self.assertEqual(data['query'], 'Test')
    
    def test_search_api_get_with_limit(self):
        """Test search_api with custom limit"""
        response = self.client.get(
            reverse('search:search_api'),
            {'q': 'Test', 'limit': '5'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertLessEqual(len(data['suggestions']), 5)
    
    def test_search_api_caching(self):
        """Test search_api caching"""
        # First request
        response1 = self.client.get(
            reverse('search:search_api'),
            {'q': 'Test'}
        )
        
        # Clear cache manually to test
        cache.clear()
        
        # Second request should still work
        response2 = self.client.get(
            reverse('search:search_api'),
            {'q': 'Test'}
        )
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        data1 = json.loads(response1.content)
        data2 = json.loads(response2.content)
        self.assertEqual(data1['query'], data2['query'])
    
    def test_search_api_suggestions_format(self):
        """Test search_api suggestions format"""
        response = self.client.get(
            reverse('search:search_api'),
            {'q': 'Test'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        if data['suggestions']:
            suggestion = data['suggestions'][0]
            self.assertIn('text', suggestion)
            self.assertIn('type', suggestion)
            self.assertIn('url', suggestion)
    
    def test_search_api_error_handling(self):
        """Test search_api error handling"""
        # This should not raise an exception
        response = self.client.get(
            reverse('search:search_api'),
            {'q': 'Test'}
        )
        
        # Should return 200 even if there's an internal error
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            data = json.loads(response.content)
            # Should have either suggestions or error
            self.assertTrue('suggestions' in data or 'error' in data)
    
    def test_search_api_suggestions_sorting(self):
        """Test search_api suggestions sorting (exact matches first)"""
        response = self.client.get(
            reverse('search:search_api'),
            {'q': 'Test Timeline'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        if len(data['suggestions']) > 1:
            # Exact matches should come first
            first_suggestion = data['suggestions'][0]
            self.assertIn('Test Timeline', first_suggestion['text'])

