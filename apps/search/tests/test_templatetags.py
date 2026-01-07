"""
Tests for search app template tags
"""
from django.test import TestCase
from django.template import Context, Template

from apps.search.templatetags.search_extras import model_name
from apps.about.models import CooperativeInfo


class SearchTemplateTagsTest(TestCase):
    """Test search template tags"""
    
    def test_model_name_with_object(self):
        """Test model_name with object"""
        cooperative = CooperativeInfo.objects.create(
            cooperative_name="Test",
            cooperative_name_nepali="Test Nepali",
            established_date="2020-01-01",
            registration_number="123",
            license_number="456",
            address="Test Address",
            phone="1234567890",
            email="test@example.com",
            mission="Test Mission",
            vision="Test Vision",
            values="Test Values",
            description="Test Description",
            is_active=True
        )
        result = model_name(cooperative)
        self.assertEqual(result, 'cooperativeinfo')
    
    def test_model_name_with_none(self):
        """Test model_name with None"""
        result = model_name(None)
        self.assertEqual(result, '')
    
    def test_template_usage_model_name(self):
        """Test using model_name in template"""
        cooperative = CooperativeInfo.objects.create(
            cooperative_name="Test",
            cooperative_name_nepali="Test Nepali",
            established_date="2020-01-01",
            registration_number="123",
            license_number="456",
            address="Test Address",
            phone="1234567890",
            email="test@example.com",
            mission="Test Mission",
            vision="Test Vision",
            values="Test Values",
            description="Test Description",
            is_active=True
        )
        template = Template(
            '{% load search_extras %}'
            '{{ object|model_name }}'
        )
        context = Context({'object': cooperative})
        result = template.render(context)
        self.assertEqual(result.strip(), 'cooperativeinfo')
    
    def test_template_usage_model_name_none(self):
        """Test using model_name with None in template"""
        template = Template(
            '{% load search_extras %}'
            '{{ object|model_name }}'
        )
        context = Context({'object': None})
        result = template.render(context)
        self.assertEqual(result.strip(), '')

