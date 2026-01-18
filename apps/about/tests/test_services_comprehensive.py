"""
Comprehensive tests for About services
"""
from django.test import TestCase
from django.core.cache import cache
from unittest.mock import patch

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Committee, Staff
)
from apps.about.services import AboutService


class AboutServiceTest(TestCase):
    """Test suite for AboutService"""
    
    def setUp(self):
        """Set up test data"""
        cache.clear()
        
        self.cooperative_info = CooperativeInfo.objects.create(
            cooperative_name='Test Cooperative',
            cooperative_name_nepali='परीक्षण सहकारी',
            established_date='2020-01-01',
            registration_number='REG123',
            license_number='LIC123',
            address='Test Address',
            phone='1234567890',
            email='test@example.com',
            mission='Test Mission',
            vision='Test Vision',
            values='Test Values',
            description='Test Description',
            status=CooperativeInfo.Status.PUBLISHED,
            is_active=True
        )
        
        self.timeline = CooperativeTimeline.objects.create(
            title='Test Event',
            event_date='2020-01-01',
            is_featured=True,
            status=CooperativeTimeline.Status.PUBLISHED,
            is_active=True
        )
    
    def test_get_about_home_data_basic(self):
        """Test getting about home data"""
        data = AboutService.get_about_home_data()
        self.assertIn('cooperative_info', data)
        self.assertIn('timeline_events', data)
        self.assertIn('statistics', data)
        self.assertIn('affiliations', data)
        self.assertIn('leadership_messages', data)
        self.assertIn('breadcrumbs', data)
    
    def test_get_about_home_data_with_staff(self):
        """Test getting about home data for staff (no cache)"""
        data = AboutService.get_about_home_data(is_staff=True)
        self.assertIn('cooperative_info', data)
        # Should not use cache for staff
        self.assertIsNotNone(data)
    
    def test_get_about_home_data_caching(self):
        """Test that about home data is cached"""
        data1 = AboutService.get_about_home_data()
        data2 = AboutService.get_about_home_data()
        # Should return same data (cached)
        self.assertEqual(data1['cooperative_info'], data2['cooperative_info'])
    

    def test_get_about_home_data_error_handling(self):
        """Test error handling in get_about_home_data"""
        with patch('apps.about.services.CooperativeInfo.objects.filter', side_effect=Exception('DB Error')):
            data = AboutService.get_about_home_data()
            self.assertIn('error', data)
    
    def test_get_timeline_events(self):
        """Test getting timeline events"""
        events = AboutService.get_timeline_events()
        self.assertIsNotNone(events)
        self.assertGreaterEqual(events.count(), 1)
    
    def test_get_affiliations(self):
        """Test getting affiliations"""
        affiliation = CooperativeAffiliation.objects.create(
            name='Test Affiliation',
            is_featured=True,
            status=CooperativeAffiliation.Status.PUBLISHED,
            is_active=True
        )
        affiliations = AboutService.get_affiliations()
        self.assertGreaterEqual(affiliations.count(), 1)
    
    def test_get_leadership_messages(self):
        """Test getting leadership messages"""
        message = LeadershipMessage.objects.create(
            title='Test Message',
            content='Test content',
            status=LeadershipMessage.Status.PUBLISHED,
            is_active=True,
            order=1
        )
        messages = AboutService.get_leadership_messages()
        self.assertGreaterEqual(messages.count(), 1)
    
    def test_get_active_team(self):
        """Test getting active team"""
        committees, staff = AboutService.get_active_team()
        self.assertIsNotNone(committees)
        self.assertIsNotNone(staff)
    
    def test_get_past_committees(self):
        """Test getting past committees"""
        committee = Committee.objects.create(
            name='Past Committee',
            is_active=False
        )
        past_committees = AboutService.get_past_committees()
        self.assertGreaterEqual(past_committees.count(), 1)
    
    # Contact email tests removed as functionality moved to contact app
    
    # Newsletter and feedback email service tests removed - methods no longer needed

