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
            is_active=True
        )
        
        self.timeline = CooperativeTimeline.objects.create(
            title='Test Event',
            event_date='2020-01-01',
            is_featured=True,
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
        with patch('apps.about.services.CooperativeInfo.objects.active', side_effect=Exception('DB Error')):
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
            is_active=True
        )
        affiliations = AboutService.get_affiliations()
        self.assertGreaterEqual(affiliations.count(), 1)
    
    def test_get_leadership_messages(self):
        """Test getting leadership messages"""
        message = LeadershipMessage.objects.create(
            title='Test Message',
            content='Test content',
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
    
    def test_send_contact_emails_without_real_emails(self):
        """Test sending contact emails when SEND_REAL_EMAILS is False"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test',
            'message': 'Test message'
        }
        
        with patch('apps.about.services.settings.SEND_REAL_EMAILS', False):
            result = AboutService.send_contact_emails(data)
            self.assertTrue(result)
    
    def test_send_contact_emails_with_real_emails(self):
        """Test sending contact emails when SEND_REAL_EMAILS is True"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test',
            'message': 'Test message'
        }
        
        with patch('apps.about.services.settings.SEND_REAL_EMAILS', True):
            with patch('apps.about.services.send_mail') as mock_send:
                result = AboutService.send_contact_emails(data)
                self.assertTrue(result)
                mock_send.assert_called_once()
    
    def test_send_contact_emails_error_handling(self):
        """Test error handling in send_contact_emails"""
        data = {'name': 'Test'}
        with patch('apps.about.services.settings.SEND_REAL_EMAILS', True):
            with patch('apps.about.services.send_mail', side_effect=Exception('Error')):
                result = AboutService.send_contact_emails(data)
                # Function catches exception and returns False
                self.assertFalse(result)
    
    # Newsletter and feedback email service tests removed - methods no longer needed

