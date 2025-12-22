"""
Tests for home app production_config module
"""
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.utils import timezone
from unittest.mock import patch, MagicMock

from apps.home.production_config import (
    HomeAppConfig, SecurityUtils, PerformanceUtils, ContentUtils, EmailUtils
)
from apps.home.models import Announcement, HomePageContent


class HomeAppConfigTest(TestCase):
    """Test HomeAppConfig"""
    
    def test_cache_timeouts(self):
        """Test cache timeout constants"""
        self.assertIn('homepage', HomeAppConfig.CACHE_TIMEOUTS)
        self.assertIn('about_page', HomeAppConfig.CACHE_TIMEOUTS)
        self.assertIn('gallery', HomeAppConfig.CACHE_TIMEOUTS)
    
    def test_pagination_size(self):
        """Test pagination size constant"""
        self.assertIsInstance(HomeAppConfig.PAGINATION_SIZE, int)
        self.assertGreater(HomeAppConfig.PAGINATION_SIZE, 0)
    
    def test_max_featured_items(self):
        """Test max featured items constants"""
        self.assertIn('testimonials', HomeAppConfig.MAX_FEATURED_ITEMS)
        self.assertIn('statistics', HomeAppConfig.MAX_FEATURED_ITEMS)
        self.assertIn('announcements', HomeAppConfig.MAX_FEATURED_ITEMS)
    
    def test_get_cache_key(self):
        """Test getting cache key"""
        key = HomeAppConfig.get_cache_key('homepage')
        self.assertIn('home_', key)
        self.assertIn('homepage', key)
    
    def test_get_cache_key_with_staff(self):
        """Test getting cache key with staff user"""
        key = HomeAppConfig.get_cache_key('homepage', user_is_staff=True)
        self.assertIn('_staff', key)
    
    def test_get_cache_timeout(self):
        """Test getting cache timeout"""
        timeout = HomeAppConfig.get_cache_timeout('homepage')
        self.assertIsInstance(timeout, int)
        self.assertGreater(timeout, 0)
    
    def test_get_cache_timeout_default(self):
        """Test getting cache timeout with default"""
        timeout = HomeAppConfig.get_cache_timeout('nonexistent')
        self.assertEqual(timeout, 300)  # Default timeout
    
    @override_settings(DEBUG=False)
    def test_is_production(self):
        """Test is_production in production mode"""
        self.assertTrue(HomeAppConfig.is_production())
    
    @override_settings(DEBUG=True)
    def test_is_production_debug(self):
        """Test is_production in debug mode"""
        self.assertFalse(HomeAppConfig.is_production())
    
    @override_settings(DEBUG=False, SEND_REAL_EMAILS=True)
    def test_should_send_emails_production(self):
        """Test should_send_emails in production"""
        self.assertTrue(HomeAppConfig.should_send_emails())
    
    @override_settings(DEBUG=True)
    def test_should_send_emails_debug(self):
        """Test should_send_emails in debug mode"""
        self.assertFalse(HomeAppConfig.should_send_emails())


class SecurityUtilsTest(TestCase):
    """Test SecurityUtils"""
    
    def test_sanitize_input(self):
        """Test sanitizing input"""
        result = SecurityUtils.sanitize_input('  test input  ')
        self.assertEqual(result, 'test input')
    
    def test_sanitize_input_with_max_length(self):
        """Test sanitizing input with max length"""
        long_text = 'x' * 200
        result = SecurityUtils.sanitize_input(long_text, max_length=100)
        self.assertEqual(len(result), 100)
    
    def test_sanitize_input_empty(self):
        """Test sanitizing empty input"""
        result = SecurityUtils.sanitize_input('')
        self.assertEqual(result, '')
    
    def test_sanitize_input_none(self):
        """Test sanitizing None input"""
        result = SecurityUtils.sanitize_input(None)
        self.assertEqual(result, '')
    
    def test_validate_file_upload_no_file(self):
        """Test validating file upload with no file"""
        is_valid, error = SecurityUtils.validate_file_upload(None)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_file_upload_size(self):
        """Test validating file upload size"""
        file_mock = MagicMock()
        file_mock.size = 10 * 1024 * 1024  # 10MB
        is_valid, error = SecurityUtils.validate_file_upload(file_mock, max_size=5 * 1024 * 1024)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_file_upload_type(self):
        """Test validating file upload type"""
        file_mock = MagicMock()
        file_mock.content_type = 'application/pdf'
        is_valid, error = SecurityUtils.validate_file_upload(
            file_mock, allowed_types=['image/jpeg', 'image/png']
        )
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_check_rate_limit(self):
        """Test checking rate limit"""
        request = MagicMock()
        request.user.is_authenticated = False
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        cache.clear()
        
        # First request should pass
        is_allowed, error = SecurityUtils.check_rate_limit(request, 'test_action', limit=5)
        self.assertTrue(is_allowed)
        self.assertIsNone(error)
        
        # Multiple requests should eventually hit limit
        for i in range(6):
            is_allowed, error = SecurityUtils.check_rate_limit(request, 'test_action', limit=5)
        
        # Should be rate limited
        self.assertFalse(is_allowed)
        self.assertIsNotNone(error)


class PerformanceUtilsTest(TestCase):
    """Test PerformanceUtils"""
    
    def setUp(self):
        self.queryset = HomePageContent.objects.all()
    
    def test_optimize_queryset_with_select_related(self):
        """Test optimizing queryset with select_related"""
        result = PerformanceUtils.optimize_queryset(
            self.queryset, select_related=['user']
        )
        self.assertIsNotNone(result)
    
    def test_optimize_queryset_with_prefetch_related(self):
        """Test optimizing queryset with prefetch_related"""
        result = PerformanceUtils.optimize_queryset(
            self.queryset, prefetch_related=['testimonials']
        )
        self.assertIsNotNone(result)
    
    def test_paginate_queryset(self):
        """Test paginating queryset"""
        # Create some test data
        for i in range(15):
            HomePageContent.objects.create(
                title=f'Content {i}',
                is_active=True
            )
        
        page, paginator = PerformanceUtils.paginate_queryset(self.queryset, page_number=1)
        self.assertIsNotNone(page)
        self.assertIsNotNone(paginator)
        self.assertEqual(len(page), 12)  # Default pagination size
    
    def test_paginate_queryset_custom_per_page(self):
        """Test paginating queryset with custom per_page"""
        # Create test data first
        for i in range(10):
            HomePageContent.objects.create(
                title=f'Content {i}',
                is_active=True
            )
        # Use fresh queryset
        queryset = HomePageContent.objects.all()
        page, paginator = PerformanceUtils.paginate_queryset(
            queryset, page_number=1, per_page=5
        )
        self.assertEqual(len(page), 5)
    
    def test_get_featured_content(self):
        """Test getting featured content"""
        # Create featured content
        HomePageContent.objects.create(
            title='Featured Content',
            is_featured=True,
            is_active=True,
            order=1
        )
        
        content = PerformanceUtils.get_featured_content(HomePageContent, limit=3)
        self.assertGreaterEqual(len(content), 1)


class ContentUtilsTest(TestCase):
    """Test ContentUtils"""
    
    def setUp(self):
        self.announcement = Announcement.objects.create(
            title='Test Announcement',
            content='Test content',
            is_featured=True,
            is_active=True,
            publish_date=timezone.now().date()
        )
    
    def test_get_active_announcements(self):
        """Test getting active announcements"""
        announcements = ContentUtils.get_active_announcements()
        self.assertGreaterEqual(len(announcements), 1)
    
    def test_get_active_announcements_excludes_expired(self):
        """Test getting active announcements excludes expired"""
        expired = Announcement.objects.create(
            title='Expired Announcement',
            is_featured=True,
            is_active=True,
            publish_date=timezone.now().date(),
            expiry_date=timezone.now().date() - timezone.timedelta(days=1)
        )
        announcements = ContentUtils.get_active_announcements()
        self.assertNotIn(expired, announcements)
    
    def test_get_homepage_content(self):
        """Test getting homepage content"""
        content = HomePageContent.objects.create(
            title='Homepage Content',
            is_active=True,
            order=1
        )
        result = ContentUtils.get_homepage_content()
        self.assertIsNotNone(result)
        self.assertEqual(result.title, 'Homepage Content')


class EmailUtilsTest(TestCase):
    """Test EmailUtils"""
    
    def setUp(self):
        from apps.home.models import ContactInquiry, NewsletterSubscriber
        self.inquiry = ContactInquiry.objects.create(
            name='Test User',
            email='test@example.com',
            subject='Test Subject',
            message='Test message',
            inquiry_type='general'
        )
        self.subscriber = NewsletterSubscriber.objects.create(
            email='test@example.com',
            name='Test User'
        )
    
    @override_settings(DEBUG=False, SEND_REAL_EMAILS=True)
    @patch('apps.home.production_config.send_mail')
    def test_send_contact_notification(self, mock_send_mail):
        """Test sending contact notification"""
        result = EmailUtils.send_contact_notification(self.inquiry)
        # In production with SEND_REAL_EMAILS=True, should send email
        # But in test, we mock it
        self.assertIsInstance(result, bool)
    
    @override_settings(DEBUG=True)
    def test_send_contact_notification_debug(self):
        """Test sending contact notification in debug mode"""
        result = EmailUtils.send_contact_notification(self.inquiry)
        # In debug mode, should not send
        self.assertFalse(result)
    
    @override_settings(DEBUG=False, SEND_REAL_EMAILS=True)
    @patch('apps.home.production_config.send_mail')
    def test_send_newsletter_confirmation(self, mock_send_mail):
        """Test sending newsletter confirmation"""
        result = EmailUtils.send_newsletter_confirmation(self.subscriber)
        self.assertIsInstance(result, bool)
    
    @override_settings(DEBUG=True)
    def test_send_newsletter_confirmation_debug(self):
        """Test sending newsletter confirmation in debug mode"""
        result = EmailUtils.send_newsletter_confirmation(self.subscriber)
        self.assertFalse(result)

