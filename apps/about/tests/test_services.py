"""
Comprehensive tests for About services
"""
from django.test import TestCase
from django.core.cache import cache
from django.core import mail
from django.conf import settings
from django.utils import timezone
from unittest.mock import patch
from datetime import timedelta

from apps.about.services import AboutService
from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Committee, Staff, Person
)


class AboutServiceTest(TestCase):
    """Test cases for AboutService"""

    def setUp(self):
        """Set up test data"""
        cache.clear()
        
        self.cooperative_info = CooperativeInfo.objects.create(
            cooperative_name="Test Cooperative",
            description="Test description",
            mission="Test mission",
            vision="Test vision",
            values="Test values",
            established_date=timezone.now().date(),
            is_active=True
        )
        
        self.timeline = CooperativeTimeline.objects.create(
            title="Test Timeline",
            description="Test description",
            event_date=timezone.now().date(),
            event_type="milestone",
            is_active=True,
            is_featured=True
        )
        
        self.achievement = CooperativeAchievement.objects.create(
            title="Test Achievement",
            description="Test description",
            achievement_type="award",
            received_date=timezone.now().date(),
            is_active=True,
            is_featured=True
        )
        
        self.statistic = CooperativeStatistic.objects.create(
            title="Test Stat",
            value="100",
            order=0,
            is_active=True
        )
        
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Affiliation",
            description="Test",
            affiliation_type="partner",
            is_active=True,
            is_featured=True
        )
        
        self.message = LeadershipMessage.objects.create(
            title="Test Message",
            content="Test content",
            author_name="Test Author",
            is_active=True
        )
        
        self.person = Person.objects.create(
            full_name="Test Person",
            bio="Test bio",
            is_active=True
        )
        
        self.committee = Committee.objects.create(
            name="Test Committee",
            description="Test",
            is_active=True
        )
        
        self.staff = Staff.objects.create(
            person=self.person,
            position="Manager",
            department="Operations",
            is_active=True
        )

    def test_get_about_home_data_basic(self):
        """Test basic get_about_home_data"""
        data = AboutService.get_about_home_data(is_staff=False)
        
        self.assertIn('cooperative_info', data)
        self.assertIn('timeline_events', data)
        self.assertIn('achievements', data)
        self.assertIn('statistics', data)
        self.assertIn('affiliations', data)
        self.assertIn('leadership_messages', data)
        self.assertIn('total_committees', data)
        self.assertIn('total_staff', data)
        self.assertIn('breadcrumbs', data)
        
        self.assertEqual(data['cooperative_info'], self.cooperative_info)
        self.assertEqual(len(data['timeline_events']), 1)
        self.assertEqual(len(data['achievements']), 1)
        self.assertEqual(data['total_committees'], 1)
        self.assertEqual(data['total_staff'], 1)

    def test_get_about_home_data_caching(self):
        """Test that get_about_home_data uses caching"""
        # First call
        data1 = AboutService.get_about_home_data(is_staff=False)
        
        # Delete cooperative info
        self.cooperative_info.delete()
        
        # Second call should use cache
        data2 = AboutService.get_about_home_data(is_staff=False)
        
        # Should return cached data
        self.assertIsNotNone(data2['cooperative_info'])

    def test_get_about_home_data_no_cache_for_staff(self):
        """Test that staff users don't get cached data"""
        # First call
        data1 = AboutService.get_about_home_data(is_staff=True)
        
        # Delete cooperative info
        self.cooperative_info.delete()
        
        # Second call for staff should get fresh data
        data2 = AboutService.get_about_home_data(is_staff=True)
        
        # Should return None since info was deleted
        self.assertIsNone(data2['cooperative_info'])

    def test_get_timeline_events(self):
        """Test get_timeline_events"""
        events = AboutService.get_timeline_events()
        
        self.assertIn(self.timeline, events)
        # Should only return active events
        self.assertTrue(all(e.is_active for e in events))

    def test_get_achievements(self):
        """Test get_achievements"""
        achievements = AboutService.get_achievements()
        
        self.assertIn(self.achievement, achievements)
        # Should only return active achievements
        self.assertTrue(all(a.is_active for a in achievements))

    def test_get_affiliations(self):
        """Test get_affiliations"""
        affiliations = AboutService.get_affiliations()
        
        self.assertIn(self.affiliation, affiliations)
        # Should only return active affiliations
        self.assertTrue(all(a.is_active for a in affiliations))

    def test_get_leadership_messages(self):
        """Test get_leadership_messages"""
        messages = AboutService.get_leadership_messages()
        
        self.assertIn(self.message, messages)
        # Should only return active messages
        self.assertTrue(all(m.is_active for m in messages))

    def test_get_active_team(self):
        """Test get_active_team"""
        committees, staff = AboutService.get_active_team()
        
        self.assertIn(self.committee, committees)
        self.assertIn(self.staff, staff)
        # Should only return active items
        self.assertTrue(all(c.is_active for c in committees))
        self.assertTrue(all(s.is_active for s in staff))

    def test_get_past_committees(self):
        """Test get_past_committees"""
        # Create inactive committee
        past_committee = Committee.objects.create(
            name="Past Committee",
            description="Past",
            is_active=False
        )
        
        past_committees = AboutService.get_past_committees()
        
        self.assertIn(past_committee, past_committees)
        # Should only return inactive committees
        self.assertTrue(all(not c.is_active for c in past_committees))

    def test_send_contact_emails_mock_mode(self):
        """Test send_contact_emails in mock mode"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        
        with self.settings(SEND_REAL_EMAILS=False):
            result = AboutService.send_contact_emails(data)
            
            self.assertTrue(result)
            # Should not send real email
            self.assertEqual(len(mail.outbox), 0)

    def test_send_contact_emails_real_mode(self):
        """Test send_contact_emails in real mode"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        
        with self.settings(SEND_REAL_EMAILS=True):
            with patch('apps.about.services.send_mail') as mock_send:
                result = AboutService.send_contact_emails(data)
                
                self.assertTrue(result)
                mock_send.assert_called_once()

    def test_send_newsletter_welcome_email_mock_mode(self):
        """Test send_newsletter_welcome_email in mock mode"""
        data = {
            'name': 'Subscriber',
            'email': 'sub@example.com'
        }
        
        with self.settings(SEND_REAL_EMAILS=False):
            result = AboutService.send_newsletter_welcome_email(data)
            
            self.assertTrue(result)

    def test_send_newsletter_welcome_email_real_mode(self):
        """Test send_newsletter_welcome_email in real mode"""
        data = {
            'name': 'Subscriber',
            'email': 'sub@example.com'
        }
        
        with self.settings(SEND_REAL_EMAILS=True):
            with patch('apps.about.services.send_mail') as mock_send:
                result = AboutService.send_newsletter_welcome_email(data)
                
                self.assertTrue(result)
                mock_send.assert_called_once()

    def test_send_feedback_email_mock_mode(self):
        """Test send_feedback_email in mock mode"""
        data = {
            'feedback_type': 'Bug',
            'rating': 1,
            'comments': 'Fix it!',
            'email': 'user@example.com'
        }
        
        with self.settings(SEND_REAL_EMAILS=False):
            result = AboutService.send_feedback_email(data)
            
            self.assertTrue(result)

    def test_send_feedback_email_real_mode(self):
        """Test send_feedback_email in real mode"""
        data = {
            'feedback_type': 'Bug',
            'rating': 1,
            'comments': 'Fix it!',
            'email': 'user@example.com'
        }
        
        with self.settings(SEND_REAL_EMAILS=True):
            with patch('apps.about.services.send_mail') as mock_send:
                result = AboutService.send_feedback_email(data)
                
                self.assertTrue(result)
                mock_send.assert_called_once()

    def test_send_contact_emails_error_handling(self):
        """Test send_contact_emails error handling"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        
        with self.settings(SEND_REAL_EMAILS=True):
            with patch('apps.about.services.send_mail') as mock_send:
                mock_send.side_effect = Exception("SMTP error")
                
                result = AboutService.send_contact_emails(data)
                
                self.assertFalse(result)

