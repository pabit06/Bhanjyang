"""
Tests for search app forms
"""
from django.test import TestCase

from apps.search.forms import SearchForm, QuickSearchForm


class SearchFormTest(TestCase):
    """Test SearchForm"""
    
    def test_valid_form(self):
        """Test valid form submission"""
        form_data = {
            'query': 'test search',
            'content_type': 'all'
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_required_query(self):
        """Test required query field"""
        form = SearchForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('query', form.errors)
    
    def test_optional_content_type(self):
        """Test optional content_type field"""
        form_data = {
            'query': 'test search'
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        # When not provided, should use initial value 'all' or be empty string
        # Check that form is valid and handles missing content_type gracefully
        content_type = form.cleaned_data.get('content_type', '')
        # Form should be valid even if content_type is not provided
        self.assertIn(content_type, ['all', ''])
    
    def test_content_type_choices(self):
        """Test content_type choices"""
        valid_types = ['all', 'news', 'services', 'team']
        for content_type in valid_types:
            form_data = {
                'query': 'test search',
                'content_type': content_type
            }
            form = SearchForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Failed for content_type: {content_type}")
    
    def test_invalid_content_type(self):
        """Test invalid content_type"""
        form_data = {
            'query': 'test search',
            'content_type': 'invalid'
        }
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content_type', form.errors)
    
    def test_query_max_length(self):
        """Test query max length"""
        long_query = 'x' * 300  # Exceeds max_length of 255
        form_data = {
            'query': long_query
        }
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('query', form.errors)
    
    def test_query_whitespace_handling(self):
        """Test query whitespace handling"""
        form_data = {
            'query': '  test  search  '
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        # Django forms should handle whitespace
        self.assertIn('test', form.cleaned_data['query'])


class QuickSearchFormTest(TestCase):
    """Test QuickSearchForm"""
    
    def test_valid_form(self):
        """Test valid form submission"""
        form_data = {
            'q': 'quick search'
        }
        form = QuickSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_optional_query(self):
        """Test optional query field"""
        form = QuickSearchForm(data={})
        self.assertTrue(form.is_valid())
        # Empty query should be valid
        self.assertEqual(form.cleaned_data.get('q', ''), '')
    
    def test_query_max_length(self):
        """Test query max length"""
        long_query = 'x' * 300  # Exceeds max_length of 255
        form_data = {
            'q': long_query
        }
        form = QuickSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('q', form.errors)
    
    def test_empty_query(self):
        """Test empty query"""
        form_data = {
            'q': ''
        }
        form = QuickSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_query_with_special_characters(self):
        """Test query with special characters"""
        form_data = {
            'q': 'test@example.com & special-chars!'
        }
        form = QuickSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

