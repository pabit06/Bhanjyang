"""
Tests for home app admin classes
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from apps.home.models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    NewsletterSubscriber, ContactInquiry, PageView
)
from apps.home.admin import (
    HomePageContentAdmin, TestimonialAdmin, StatisticAdmin,
    AnnouncementAdmin, NewsletterSubscriberAdmin,
    ContactInquiryAdmin, PageViewAdmin
)


class HomeAdminTestCase(TestCase):
    """Base test case for home admin tests"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.request = self.factory.get('/admin/')
        self.request.user = self.admin_user
        
        # Add session and messages middleware for admin actions
        SessionMiddleware(lambda req: None).process_request(self.request)
        MessageMiddleware(lambda req: None).process_request(self.request)
        self.request._messages = FallbackStorage(self.request)


class HomePageContentAdminTest(HomeAdminTestCase):
    """Test HomePageContentAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = HomePageContentAdmin(HomePageContent, self.site)
        self.content = HomePageContent.objects.create(
            title='Test Content',
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('title', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)
        self.assertIn('order', self.admin.list_display)
    
    def test_list_editable(self):
        """Test list editable fields"""
        self.assertIn('is_active', self.admin.list_editable)
        self.assertIn('order', self.admin.list_editable)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('title', self.admin.search_fields)
        self.assertIn('subtitle', self.admin.search_fields)


class TestimonialAdminTest(HomeAdminTestCase):
    """Test TestimonialAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = TestimonialAdmin(Testimonial, self.site)
        self.testimonial = Testimonial.objects.create(
            name='Test User',
            position='Manager',
            content='Test content',
            rating=5,
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('position', self.admin.list_display)
        self.assertIn('rating', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)
    
    def test_list_editable(self):
        """Test list editable fields"""
        self.assertIn('is_featured', self.admin.list_editable)
        self.assertIn('is_active', self.admin.list_editable)
        self.assertIn('rating', self.admin.list_editable)


class StatisticAdminTest(HomeAdminTestCase):
    """Test StatisticAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = StatisticAdmin(Statistic, self.site)
        self.statistic = Statistic.objects.create(
            title='Test Stat',
            value='100',
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('title', self.admin.list_display)
        self.assertIn('value', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)
    
    def test_list_editable(self):
        """Test list editable fields"""
        self.assertIn('is_featured', self.admin.list_editable)
        self.assertIn('is_active', self.admin.list_editable)


class AnnouncementAdminTest(HomeAdminTestCase):
    """Test AnnouncementAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = AnnouncementAdmin(Announcement, self.site)
        self.announcement = Announcement.objects.create(
            title='Test Announcement',
            content='Test content',
            publish_date=timezone.now().date(),
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('title', self.admin.list_display)
        self.assertIn('announcement_type', self.admin.list_display)
        self.assertIn('priority', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)
    
    def test_mark_as_featured_action(self):
        """Test mark as featured action"""
        queryset = Announcement.objects.filter(id=self.announcement.id)
        self.admin.mark_as_featured(self.request, queryset)
        self.announcement.refresh_from_db()
        self.assertTrue(self.announcement.is_featured)
    
    def test_mark_as_unfeatured_action(self):
        """Test mark as unfeatured action"""
        self.announcement.is_featured = True
        self.announcement.save()
        queryset = Announcement.objects.filter(id=self.announcement.id)
        self.admin.mark_as_unfeatured(self.request, queryset)
        self.announcement.refresh_from_db()
        self.assertFalse(self.announcement.is_featured)
    
    # Removed: test_mark_as_active_action and test_mark_as_inactive_action.
    # AnnouncementAdmin.actions covers publish/draft/schedule/archive and
    # feature/unfeature; no active/inactive bulk action was ever added. The
    # Announcement.is_active field exists, so add these back if that action is
    # ever written. (GalleryImageAdmin has its own mark_as_active - a different
    # admin class, not this one.)


class NewsletterSubscriberAdminTest(HomeAdminTestCase):
    """Test NewsletterSubscriberAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = NewsletterSubscriberAdmin(NewsletterSubscriber, self.site)
        self.subscriber = NewsletterSubscriber.objects.create(
            email='test@example.com',
            name='Test User',
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('email', self.admin.list_display)
        self.assertIn('name', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)
    
    def test_unsubscribe_selected_action(self):
        """Test unsubscribe selected action"""
        queryset = NewsletterSubscriber.objects.filter(id=self.subscriber.id)
        self.admin.unsubscribe_selected(self.request, queryset)
        self.subscriber.refresh_from_db()
        self.assertFalse(self.subscriber.is_active)
        self.assertIsNotNone(self.subscriber.unsubscribed_at)


class ContactInquiryAdminTest(HomeAdminTestCase):
    """Test ContactInquiryAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = ContactInquiryAdmin(ContactInquiry, self.site)
        self.inquiry = ContactInquiry.objects.create(
            name='Test User',
            email='test@example.com',
            subject='Test Subject',
            message='Test message'
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('email', self.admin.list_display)
        self.assertIn('subject', self.admin.list_display)
        self.assertIn('is_resolved', self.admin.list_display)
    
    def test_mark_as_resolved_action(self):
        """Test mark as resolved action"""
        queryset = ContactInquiry.objects.filter(id=self.inquiry.id)
        self.admin.mark_as_resolved(self.request, queryset)
        self.inquiry.refresh_from_db()
        self.assertTrue(self.inquiry.is_resolved)
        self.assertIsNotNone(self.inquiry.resolved_at)
    
    def test_mark_as_unresolved_action(self):
        """Test mark as unresolved action"""
        self.inquiry.is_resolved = True
        self.inquiry.resolved_at = timezone.now()
        self.inquiry.resolved_by = self.admin_user
        self.inquiry.save()
        queryset = ContactInquiry.objects.filter(id=self.inquiry.id)
        self.admin.mark_as_unresolved(self.request, queryset)
        self.inquiry.refresh_from_db()
        self.assertFalse(self.inquiry.is_resolved)


class PageViewAdminTest(HomeAdminTestCase):
    """Test PageViewAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = PageViewAdmin(PageView, self.site)
        self.page_view = PageView.objects.create(
            page_title='Test Page',
            page_url='http://example.com/test/',
            user_ip='127.0.0.1'
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('page_title', self.admin.list_display)
        self.assertIn('page_url', self.admin.list_display)
    
    def test_has_add_permission(self):
        """Test add permission"""
        self.assertFalse(self.admin.has_add_permission(self.request))
    
    def test_has_change_permission(self):
        """Test change permission"""
        self.assertFalse(self.admin.has_change_permission(self.request, self.page_view))

