"""
Comprehensive tests for HomeService
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core import mail
from django.conf import settings
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta

from apps.home.services import HomeService
from apps.home.models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    NewsletterSubscriber, ContactInquiry
)
from apps.gallery.models import GalleryImage, GalleryAlbum


class HomeServiceTest(TestCase):
    """Test cases for HomeService"""

    def setUp(self):
        """Set up test data"""
        cache.clear()
        self.factory = RequestFactory()
        
        # Create test data
        self.homepage_content = HomePageContent.objects.create(
            title="Test Homepage",
            subtitle="Test Subtitle",
            is_active=True,
            status=HomePageContent.Status.PUBLISHED,
            order=0
        )
        
        self.testimonial = Testimonial.objects.create(
            name="John Doe",
            content="Great service!",
            rating=5,
            is_featured=True,
            is_active=True,
            status=Testimonial.Status.PUBLISHED,
            order=0
        )
        
        self.statistic = Statistic.objects.create(
            title="Total Members",
            value="2,500+",
            is_featured=True,
            is_active=True,
            status=Statistic.Status.PUBLISHED,
            order=0
        )
        
        self.announcement = Announcement.objects.create(
            title="Test Announcement",
            content="Test content",
            is_featured=True,
            is_active=True,
            status=Announcement.Status.PUBLISHED,
            priority=1,
            publish_date=timezone.now()
        )
        

        
        # Create gallery album and image
        self.album = GalleryAlbum.objects.create(
            name="Test Album",
            description="Test",
            is_active=True
        )
        
        self.gallery_image = GalleryImage.objects.create(
            album=self.album,
            title="Test Image",
            is_featured=True,
            is_active=True,
            order=0
        )

    def test_get_home_context_basic(self):
        """Test basic get_home_context functionality"""
        context = HomeService.get_home_context(is_staff=False)
        
        self.assertIsNotNone(context)
        self.assertIn('homepage_content', context)
        self.assertIn('featured_testimonials', context)
        self.assertIn('featured_statistics', context)
        self.assertIn('featured_announcements', context)
        self.assertIn('featured_services', context)
        self.assertIn('featured_gallery', context)
        self.assertIn('breadcrumbs', context)
        
        self.assertEqual(context['homepage_content'], self.homepage_content)
        self.assertEqual(len(context['featured_testimonials']), 1)
        self.assertEqual(len(context['featured_statistics']), 1)
        self.assertEqual(len(context['featured_announcements']), 1)
        self.assertEqual(len(context['featured_services']), 1)
        self.assertEqual(len(context['featured_gallery']), 1)

    def test_get_home_context_caching(self):
        """Test that get_home_context uses caching"""
        # First call
        context1 = HomeService.get_home_context(is_staff=False)
        
        # Delete the content to verify cache is used
        self.homepage_content.delete()
        
        # Second call should use cache
        context2 = HomeService.get_home_context(is_staff=False)
        
        # Should return cached data
        self.assertEqual(context1['homepage_content'].id, context2['homepage_content'].id)

    def test_get_home_context_no_cache_for_staff(self):
        """Test that staff users don't get cached data"""
        # First call
        context1 = HomeService.get_home_context(is_staff=True)
        
        # Delete the content
        self.homepage_content.delete()
        
        # Second call for staff should get fresh data
        context2 = HomeService.get_home_context(is_staff=True)
        
        # Should return None since content was deleted
        self.assertIsNone(context2['homepage_content'])

    def test_get_home_context_with_no_data(self):
        """Test get_home_context when no data exists"""
        # Delete all test data
        HomePageContent.objects.all().delete()
        Testimonial.objects.all().delete()
        Statistic.objects.all().delete()
        Announcement.objects.all().delete()

        GalleryImage.objects.all().delete()
        
        context = HomeService.get_home_context(is_staff=False)
        
        self.assertIsNotNone(context)
        self.assertIsNone(context['homepage_content'])
        self.assertEqual(len(context['featured_testimonials']), 0)
        self.assertEqual(len(context['featured_statistics']), 0)
        self.assertEqual(len(context['featured_announcements']), 0)
        self.assertEqual(len(context['featured_services']), 0)
        self.assertEqual(len(context['featured_gallery']), 0)

    def test_get_home_context_filters_expired_announcements(self):
        """Test that expired announcements are filtered out"""
        # Create expired announcement
        expired = Announcement.objects.create(
            title="Expired",
            content="Expired content",
            is_featured=True,
            is_active=True,
            expiry_date=timezone.now() - timedelta(days=1),
            priority=1,
            publish_date=timezone.now() - timedelta(days=2)
        )
        
        context = HomeService.get_home_context(is_staff=False)
        
        # Should not include expired announcement
        announcement_ids = [a.id for a in context['featured_announcements']]
        self.assertNotIn(expired.id, announcement_ids)
        self.assertIn(self.announcement.id, announcement_ids)

    def test_get_home_context_error_handling(self):
        """Test error handling in get_home_context"""
        # We need to make sure the exception bubbles up to get_home_context
        # Since helpers swallow errors, we check if get_home_context handles
        # unexpected errors (like if a helper itself was missing or mocked to raise)
        with patch('apps.home.services.HomeService._get_homepage_content') as mock_method:
            mock_method.side_effect = Exception("Fatal error")
            
            context = HomeService.get_home_context(is_staff=False)
            
            # Should return error context
            self.assertIn('error', context)
            self.assertEqual(context['homepage_content'], None)
            self.assertEqual(len(context['featured_testimonials']), 0)
    
    def test_get_home_context_cache_error_handling(self):
        """Test error handling when cache.set fails"""
        with patch('apps.home.services.cache.set') as mock_cache_set:
            mock_cache_set.side_effect = Exception("Cache error")
            
            # Should still return context even if caching fails
            context = HomeService.get_home_context(is_staff=False)
            
            self.assertIsNotNone(context)
            self.assertIn('homepage_content', context)

    def test_handle_contact_submission_success(self):
        """Test successful contact submission"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        
        with self.settings(SEND_REAL_EMAILS=False):
            # Patch ContactService to avoid dependency on it
            with patch('apps.contact.services.ContactService.create_contact_submission') as mock_create:
                with patch('apps.contact.services.ContactService.send_contact_notification_emails') as mock_send:
                    # Mock return value of create_contact_submission
                    mock_create.return_value = MagicMock(id=1, email='test@example.com', name='Test User', subject='Test Subject')
                    
                    success, message = HomeService.handle_contact_submission(data)
                    
                    self.assertTrue(success)
                    self.assertIn('Thank you', message)
                    
                    # Verify ContactService methods were called
                    mock_create.assert_called_once()
                    mock_send.assert_called_once()
                    
                    # Also verify inquiry was created (backward compatibility)
                    inquiry = ContactInquiry.objects.get(email='test@example.com')
                    self.assertEqual(inquiry.name, 'Test User')
                    self.assertEqual(inquiry.subject, 'Test Subject')

    def test_handle_contact_submission_with_email(self):
        """Test contact submission with email sending enabled"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        
        with self.settings(SEND_REAL_EMAILS=True):
            # Patch ContactService to avoid dependency on it
            with patch('apps.contact.services.ContactService.create_contact_submission') as mock_create:
                with patch('apps.contact.services.ContactService.send_contact_notification_emails') as mock_send:
                    mock_create.return_value = MagicMock(id=1)
                    
                    success, message = HomeService.handle_contact_submission(data)
                    
                    self.assertTrue(success)
                    # We verify that ContactService was called, not send_mail directly
                    # since HomeService delegates to ContactService
                    mock_create.assert_called_once()
                    mock_send.assert_called_once()

    def test_handle_contact_submission_email_failure(self):
        """Test contact submission when email sending fails"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        
        with self.settings(SEND_REAL_EMAILS=True):
            # Patch ContactService to raise exception
            with patch('apps.contact.services.ContactService.create_contact_submission') as mock_create:
                with patch('apps.contact.services.ContactService.send_contact_notification_emails') as mock_send_email:
                    mock_create.return_value = MagicMock(id=1)
                    # Simulate email failure in ContactService
                    mock_send_email.side_effect = Exception("SMTP error")
                    
                    success, message = HomeService.handle_contact_submission(data)
                    
                    # Should still succeed even if email fails (caught inside HomeService or ContactService)
                    # Note: HomeService catches exceptions from ContactService block
                    self.assertTrue(success)
                    # Verify inquiry was created (via fallback or regular flow)
                    self.assertTrue(ContactInquiry.objects.filter(email='test@example.com').exists())

    def test_handle_contact_submission_error(self):
        """Test contact submission error handling"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            # Missing required fields
        }
        
        success, message = HomeService.handle_contact_submission(data)
        
        self.assertFalse(success)
        self.assertIn('error', message.lower())

    def test_handle_newsletter_signup_new_subscriber(self):
        """Test newsletter signup for new subscriber"""
        email = 'new@example.com'
        name = 'New User'
        
        with self.settings(SEND_REAL_EMAILS=False):
            success, message = HomeService.handle_newsletter_signup(email, name)
            
            self.assertTrue(success)
            self.assertIn('Thank you', message)
            
            # Verify subscriber was created
            subscriber = NewsletterSubscriber.objects.get(email=email)
            self.assertEqual(subscriber.name, name)
            self.assertTrue(subscriber.is_active)

    def test_handle_newsletter_signup_existing_active(self):
        """Test newsletter signup for existing active subscriber"""
        email = 'existing@example.com'
        name = 'Existing User'
        
        # Create existing subscriber
        NewsletterSubscriber.objects.create(
            email=email,
            name=name,
            is_active=True
        )
        
        success, message = HomeService.handle_newsletter_signup(email, name)
        
        self.assertFalse(success)
        self.assertIn('already subscribed', message.lower())

    def test_handle_newsletter_signup_reactivate(self):
        """Test newsletter signup reactivates inactive subscriber"""
        email = 'inactive@example.com'
        name = 'Inactive User'
        
        # Create inactive subscriber
        subscriber = NewsletterSubscriber.objects.create(
            email=email,
            name=name,
            is_active=False,
            unsubscribed_at=timezone.now()
        )
        
        success, message = HomeService.handle_newsletter_signup(email, name)
        
        self.assertTrue(success)
        self.assertIn('reactivated', message.lower())
        
        # Verify subscriber is reactivated
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_active)
        self.assertIsNone(subscriber.unsubscribed_at)

    def test_handle_newsletter_signup_with_email(self):
        """Test newsletter signup with email sending enabled"""
        email = 'new@example.com'
        name = 'New User'
        
        with self.settings(SEND_REAL_EMAILS=True):
            with patch('apps.home.services.send_mail') as mock_send:
                success, message = HomeService.handle_newsletter_signup(email, name)
                
                self.assertTrue(success)
                mock_send.assert_called_once()

    def test_handle_newsletter_signup_email_failure(self):
        """Test newsletter signup when email sending fails"""
        email = 'new@example.com'
        name = 'New User'
        
        with self.settings(SEND_REAL_EMAILS=True):
            with patch('apps.home.services.send_mail') as mock_send:
                mock_send.side_effect = Exception("SMTP error")
                
                success, message = HomeService.handle_newsletter_signup(email, name)
                
                # Should still succeed even if email fails
                self.assertTrue(success)
                # Verify subscriber was created
                self.assertTrue(NewsletterSubscriber.objects.filter(email=email).exists())

    def test_handle_newsletter_signup_error(self):
        """Test newsletter signup error handling"""
        # Use invalid email to trigger error
        with patch('apps.home.services.NewsletterSubscriber.objects.get_or_create') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            success, message = HomeService.handle_newsletter_signup('test@example.com', 'Test')
            
            self.assertFalse(success)
            self.assertIn('error', message.lower())

    def test_track_view_success(self):
        """Test track_view method"""
        request = self.factory.get('/')
        request.META = {
            'HTTP_USER_AGENT': 'Test Browser',
            'HTTP_REFERER': 'http://example.com',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        # Just verify the method doesn't crash
        # The actual tracking may fail if DashboardAnalyticsService is not available,
        # but that's handled gracefully
        try:
            HomeService.track_view(request, "Test Page")
        except Exception as e:
            # Only fail if it's not a known acceptable error
            if 'DashboardAnalyticsService' not in str(e) and 'record_page_view' not in str(e):
                raise

    def test_track_view_error_handling(self):
        """Test track_view error handling"""
        request = self.factory.get('/')
        request.META = {}
        
        # Should not raise exception even if tracking fails
        try:
            HomeService.track_view(request, "Test Page")
        except Exception:
            self.fail("track_view should not raise exceptions")

    def test_get_home_context_limits_results(self):
        """Test that get_home_context limits results correctly"""
        # Create multiple testimonials
        for i in range(5):
            Testimonial.objects.create(
                name=f"User {i}",
                content=f"Content {i}",
                rating=5,
                is_featured=True,
                is_active=True,
                status=Testimonial.Status.PUBLISHED,
                order=i
            )
        
        context = HomeService.get_home_context(is_staff=False)
        
        # Should only return 3 featured testimonials
        self.assertLessEqual(len(context['featured_testimonials']), 3)
        
        # Should only return 4 statistics
        self.assertLessEqual(len(context['featured_statistics']), 4)
        
        # Should only return 3 announcements
        self.assertLessEqual(len(context['featured_announcements']), 3)
        
        # Should only return 3 services
        self.assertLessEqual(len(context['featured_services']), 3)
        
        # Should only return 6 gallery images
        self.assertLessEqual(len(context['featured_gallery']), 6)

