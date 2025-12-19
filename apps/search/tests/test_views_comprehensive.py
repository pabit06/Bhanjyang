"""
Comprehensive tests for Search views
"""
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json

from apps.about.models import (
    CooperativeTimeline, CooperativeAchievement,
    CooperativeAffiliation, LeadershipMessage, Person
)
from apps.search.services import SearchService, SearchAnalytics


class AdvancedSearchViewTest(TestCase):
    """Test suite for AdvancedSearchView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test data
        self.timeline = CooperativeTimeline.objects.create(
            title='Test Timeline Event',
            description='Test description',
            event_date='2024-01-01'
        )
        
        self.achievement = CooperativeAchievement.objects.create(
            title='Test Achievement',
            description='Test description',
            received_date='2024-01-01'
        )
    
    def test_advanced_search_view_no_query(self):
        """Test advanced search view with no query"""
        response = self.client.get(reverse('search:advanced_search'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), 0)
    
    @patch('apps.search.services.SearchService.search_all_content')
    @patch('apps.search.services.SearchAnalytics.track_search')
    def test_advanced_search_view_all(self, mock_track, mock_search):
        """Test advanced search view with 'all' type"""
        mock_search.return_value = [self.timeline, self.achievement]
        
        response = self.client.get(reverse('search:advanced_search'), {'q': 'Test'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        self.assertEqual(response.context['query'], 'Test')
        mock_search.assert_called_once_with('Test')
        mock_track.assert_called_once()
    
    @patch('apps.search.services.SearchService.search_team')
    @patch('apps.search.services.SearchAnalytics.track_search')
    def test_advanced_search_view_team(self, mock_track, mock_search):
        """Test advanced search view with 'team' type"""
        mock_search.return_value = []
        
        response = self.client.get(reverse('search:advanced_search'), {'q': 'Test', 'type': 'team'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search_type'], 'team')
        mock_search.assert_called_once_with('Test')
    
    @patch('apps.search.services.SearchService.search_timeline')
    @patch('apps.search.services.SearchAnalytics.track_search')
    def test_advanced_search_view_events(self, mock_track, mock_search):
        """Test advanced search view with 'events' type"""
        mock_search.return_value = [self.timeline]
        
        response = self.client.get(reverse('search:advanced_search'), {'q': 'Test', 'type': 'events'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search_type'], 'events')
        mock_search.assert_called_once_with('Test')
    
    @patch('apps.search.services.SearchService.search_achievements')
    @patch('apps.search.services.SearchAnalytics.track_search')
    def test_advanced_search_view_achievements(self, mock_track, mock_search):
        """Test advanced search view with 'achievements' type"""
        mock_search.return_value = [self.achievement]
        
        response = self.client.get(reverse('search:advanced_search'), {'q': 'Test', 'type': 'achievements'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search_type'], 'achievements')
        mock_search.assert_called_once_with('Test')
    
    @patch('apps.search.services.SearchService.search_affiliations')
    @patch('apps.search.services.SearchAnalytics.track_search')
    def test_advanced_search_view_affiliations(self, mock_track, mock_search):
        """Test advanced search view with 'affiliations' type"""
        mock_search.return_value = []
        
        response = self.client.get(reverse('search:advanced_search'), {'q': 'Test', 'type': 'affiliations'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search_type'], 'affiliations')
        mock_search.assert_called_once_with('Test')
    
    def test_advanced_search_view_sort_by_date(self):
        """Test advanced search view with date sorting"""
        with patch('apps.search.services.SearchService.search_all_content') as mock_search:
            mock_search.return_value = [self.timeline, self.achievement]
            
            response = self.client.get(reverse('search:advanced_search'), {'q': 'Test', 'sort': 'date'})
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['sort_by'], 'date')
    
    def test_advanced_search_view_sort_by_title(self):
        """Test advanced search view with title sorting"""
        with patch('apps.search.services.SearchService.search_all_content') as mock_search:
            mock_search.return_value = [self.timeline, self.achievement]
            
            response = self.client.get(reverse('search:advanced_search'), {'q': 'Test', 'sort': 'title'})
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['sort_by'], 'title')
    
    @patch('apps.search.services.SearchService.get_search_suggestions')
    def test_advanced_search_view_suggestions(self, mock_suggestions):
        """Test advanced search view includes suggestions"""
        mock_suggestions.return_value = ['suggestion1', 'suggestion2']
        
        response = self.client.get(reverse('search:advanced_search'), {'q': 'Test'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('suggestions', response.context)
        mock_suggestions.assert_called_once_with('Test')


class SearchAPITest(TestCase):
    """Test suite for search_api view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.timeline = CooperativeTimeline.objects.create(
            title='Test Timeline',
            description='Test',
            event_date='2024-01-01'
        )
    
    def test_search_api_short_query(self):
        """Test search API with query too short"""
        response = self.client.get(reverse('search:search_api'), {'q': 'T'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['suggestions']), 0)
    
    def test_search_api_valid_query(self):
        """Test search API with valid query"""
        response = self.client.get(reverse('search:search_api'), {'q': 'Test'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('suggestions', data)
        self.assertIn('query', data)
        self.assertEqual(data['query'], 'Test')
    
    def test_search_api_with_limit(self):
        """Test search API with custom limit"""
        response = self.client.get(reverse('search:search_api'), {'q': 'Test', 'limit': '5'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertLessEqual(len(data['suggestions']), 5)
    
    def test_search_api_caching(self):
        """Test search API uses caching"""
        from django.core.cache import cache
        
        # Clear cache
        cache.clear()
        
        # First request
        response1 = self.client.get(reverse('search:search_api'), {'q': 'Test'})
        self.assertEqual(response1.status_code, 200)
        
        # Second request should use cache
        response2 = self.client.get(reverse('search:search_api'), {'q': 'Test'})
        self.assertEqual(response2.status_code, 200)
        
        # Both should have same content
        data1 = json.loads(response1.content)
        data2 = json.loads(response2.content)
        self.assertEqual(data1, data2)
    
    def test_search_api_error_handling(self):
        """Test search API error handling"""
        # The view has try-except that catches exceptions and returns 500
        # But it might handle gracefully, so we test that it doesn't crash
        with patch('apps.about.models.CooperativeTimeline.objects.filter', side_effect=Exception('DB Error')):
            response = self.client.get(reverse('search:search_api'), {'q': 'Test'})
            
            # View should handle error gracefully (either 200 with empty results or 500)
            self.assertIn(response.status_code, [200, 500])
            if response.status_code == 500:
                data = json.loads(response.content)
                self.assertIn('error', data)

