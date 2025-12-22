"""
Tests for home app serializers
"""
from django.test import TestCase

from apps.home.models import Statistic, Testimonial
from apps.home.serializers import StatisticSerializer, TestimonialSerializer


class StatisticSerializerTest(TestCase):
    """Test StatisticSerializer"""
    
    def setUp(self):
        self.statistic = Statistic.objects.create(
            title='Test Statistic',
            value='100',
            description='Test description',
            icon='icon-test',
            color='blue',
            order=1
        )
    
    def test_serialize_statistic(self):
        """Test serializing statistic"""
        serializer = StatisticSerializer(self.statistic)
        data = serializer.data
        self.assertEqual(data['title'], self.statistic.title)
        self.assertEqual(data['value'], self.statistic.value)
        self.assertEqual(data['description'], self.statistic.description)
        self.assertIn('icon', data)
        self.assertIn('color', data)
        self.assertIn('order', data)
    
    def test_deserialize_statistic(self):
        """Test deserializing statistic"""
        data = {
            'title': 'New Statistic',
            'value': '200',
            'description': 'New description',
            'icon': 'icon-new',
            'color': 'red',
            'order': 2
        }
        serializer = StatisticSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.title, 'New Statistic')
        self.assertEqual(instance.value, '200')


class TestimonialSerializerTest(TestCase):
    """Test TestimonialSerializer"""
    
    def setUp(self):
        self.testimonial = Testimonial.objects.create(
            name='Test User',
            position='Manager',
            company='Test Company',
            content='Test testimonial content',
            rating=5,
            language='en',
            order=1
        )
    
    def test_serialize_testimonial(self):
        """Test serializing testimonial"""
        serializer = TestimonialSerializer(self.testimonial)
        data = serializer.data
        self.assertEqual(data['name'], self.testimonial.name)
        self.assertEqual(data['position'], self.testimonial.position)
        self.assertEqual(data['company'], self.testimonial.company)
        self.assertEqual(data['content'], self.testimonial.content)
        self.assertEqual(data['rating'], self.testimonial.rating)
        self.assertIn('photo', data)
        self.assertIn('language', data)
        self.assertIn('order', data)
    
    def test_deserialize_testimonial(self):
        """Test deserializing testimonial"""
        data = {
            'name': 'New User',
            'position': 'Director',
            'company': 'New Company',
            'content': 'New testimonial content',
            'rating': 4,
            'language': 'en',
            'order': 2
        }
        serializer = TestimonialSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.name, 'New User')
        self.assertEqual(instance.rating, 4)

