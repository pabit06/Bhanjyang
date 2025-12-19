"""
Comprehensive tests for Home services
"""
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.utils import timezone
from unittest.mock import patch, MagicMock

from apps.home.models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    ServiceHighlight, NewsletterSubscriber, ContactInquiry
)
from apps.home.services import HomeService
from apps.gallery.models import GalleryImage


class HomeServiceTest(TestCase):
    """Test suite for HomeService"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        cache.clear()
        
        # Create test data
        self.homepage_content = HomePageContent.objects.create(
            title='Test Homepage',
            subtitle='Test Subtitle',
            description='Test description',
            is_active=True,
            order=1
        )
        
        self.testimonial = Testimonial.objects.create(
            name='John Doe',
            content='Great service!',
            rating=5,
            is_featured=True,
            is_active=True,
            order=1
        )
        
        self.statistic = Statistic.objects.create(
            title='Total Members',
            value='2,500+',
            is_featured=True,
            is_active=True,
            order=1
        )
    
    def test_get_home_context_basic(self):
        """Test getting home context"""
        context = HomeService.get_home_context()
        self.assertIn('homepage_content', context)
        self.assertIn('featured_testimonials', context)
        self.assertIn('featured_statistics', context)
        self.assertIn('featured_announcements', context)
        self.assertIn('featured_services', context)
        self.assertIn('featured_gallery', context)
        self.assertIn('breadcrumbs', context)
    
    def test_get_home_context_with_staff(self):
        """Test getting home context for staff (no cache)"""
        context = HomeService.get_home_context(is_staff=True)
        self.assertIn('homepage_content', context)
        # Should not use cache for staff
        self.assertIsNotNone(context)
    
    def test_get_home_context_caching(self):
        """Test that home context is cached"""
        context1 = HomeService.get_home_context()
        context2 = HomeService.get_home_context()
        # Should return same context (cached)
        self.assertEqual(context1['homepage_content'], context2['homepage_content'])
    
    def test_get_home_context_error_handling(self):
        """Test error handling in get_home_context"""
        with patch('apps.home.services.HomePageContent.objects.filter', side_effect=Exception('DB Error')):
            context = HomeService.get_home_context()
            self.assertIn('error', context)
            self.assertEqual(context['homepage_content'], None)
    
    def test_track_view(self):
        """Test tracking page view"""
        request = self.factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_REFERER'] = 'http://example.com'
        
        with patch('apps.home.services.DashboardAnalyticsService.record_page_view') as mock_track:
            HomeService.track_view(request, 'Test Page')
            mock_track.assert_called_once()
    
    def test_track_view_error_handling(self):
        """Test error handling in track_view"""
        request = self.factory.get('/')
        with patch('apps.home.services.DashboardAnalyticsService.record_page_view', side_effect=Exception('Error')):
            # Should not raise exception
            HomeService.track_view(request)
    
    def test_handle_contact_submission_success(self):
        """Test handling contact submission successfully"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        
        with patch('apps.home.services.settings.SEND_REAL_EMAILS', False):
            success, message = HomeService.handle_contact_submission(data)
            self.assertTrue(success)
            self.assertIn('Thank you', message)
            
            # Check that inquiry was created
            inquiry = ContactInquiry.objects.get(email='john@example.com')
            self.assertEqual(inquiry.name, 'John Doe')
    
    def test_handle_contact_submission_with_email(self):
        """Test handling contact submission with email sending"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        
        with patch('apps.home.services.settings.SEND_REAL_EMAILS', True):
            with patch('apps.home.services.send_mail') as mock_send:
                success, message = HomeService.handle_contact_submission(data)
                self.assertTrue(success)
                mock_send.assert_called_once()
    
    def test_handle_contact_submission_error(self):
        """Test error handling in contact submission"""
        data = {
            'name': 'John Doe',
            # Missing required fields
        }
        
        success, message = HomeService.handle_contact_submission(data)
        self.assertFalse(success)
        self.assertIn('error', message.lower())
    
    def test_handle_newsletter_signup_new(self):
        """Test newsletter signup for new subscriber"""
        email = 'new@example.com'
        name = 'New User'
        
        with patch('apps.home.services.settings.SEND_REAL_EMAILS', False):
            success, message = HomeService.handle_newsletter_signup(email, name)
            self.assertTrue(success)
            self.assertIn('Thank you', message)
            
            # Check subscriber was created
            subscriber = NewsletterSubscriber.objects.get(email=email)
            self.assertTrue(subscriber.is_active)
    
    def test_handle_newsletter_signup_existing(self):
        """Test newsletter signup for existing subscriber"""
        email = 'existing@example.com'
        NewsletterSubscriber.objects.create(
            email=email,
            name='Existing User',
            is_active=True
        )
        
        success, message = HomeService.handle_newsletter_signup(email)
        self.assertFalse(success)
        self.assertIn('already subscribed', message)
    
    def test_handle_newsletter_signup_reactivate(self):
        """Test reactivating unsubscribed user"""
        email = 'unsubscribed@example.com'
        NewsletterSubscriber.objects.create(
            email=email,
            name='Unsubscribed User',
            is_active=False
        )
        
        success, message = HomeService.handle_newsletter_signup(email)
        self.assertTrue(success)
        self.assertIn('reactivated', message)
        
        subscriber = NewsletterSubscriber.objects.get(email=email)
        self.assertTrue(subscriber.is_active)
    
    def test_handle_newsletter_signup_with_email(self):
        """Test newsletter signup with email sending"""
        email = 'email@example.com'
        
        with patch('apps.home.services.settings.SEND_REAL_EMAILS', True):
            with patch('apps.home.services.send_mail') as mock_send:
                success, message = HomeService.handle_newsletter_signup(email, 'Test User')
                self.assertTrue(success)
                mock_send.assert_called_once()
    
    def test_handle_newsletter_signup_error(self):
        """Test error handling in newsletter signup"""
        with patch('apps.home.services.NewsletterSubscriber.objects.get_or_create', side_effect=Exception('Error')):
            success, message = HomeService.handle_newsletter_signup('test@example.com')
            self.assertFalse(success)
            self.assertIn('error', message.lower())

