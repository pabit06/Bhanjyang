"""
Tests for about app template tags
"""
from django.test import TestCase, RequestFactory
from django.template import Context, Template
from unittest.mock import MagicMock

from apps.about.templatetags.about_extras import build_absolute_uri


class TemplateTagsTest(TestCase):
    """Test template tags"""
    
    def setUp(self):
        # Use a mock request to have full control over properties
        self.request = MagicMock()
        self.request.scheme = 'http'
        self.request.get_host.return_value = 'example.com'
    
    def test_build_absolute_uri_with_path(self):
        """Test build_absolute_uri with path"""
        result = build_absolute_uri(self.request, '/about/')
        self.assertEqual(result, 'http://example.com/about/')
    
    def test_build_absolute_uri_with_full_url(self):
        """Test build_absolute_uri with full URL"""
        result = build_absolute_uri(self.request, 'https://example.com/about/')
        self.assertEqual(result, 'https://example.com/about/')
    
    def test_build_absolute_uri_empty_path(self):
        """Test build_absolute_uri with empty path"""
        result = build_absolute_uri(self.request, '')
        self.assertEqual(result, '')
    
    def test_build_absolute_uri_none_path(self):
        """Test build_absolute_uri with None path"""
        result = build_absolute_uri(self.request, None)
        self.assertEqual(result, '')
    
    def test_template_usage_build_absolute_uri(self):
        """Test using build_absolute_uri in template"""
        template = Template(
            '{% load about_extras %}'
            '{{ request|build_absolute_uri:"/about/" }}'
        )
        context = Context({'request': self.request})
        result = template.render(context)
        self.assertEqual(result.strip(), 'http://example.com/about/')

