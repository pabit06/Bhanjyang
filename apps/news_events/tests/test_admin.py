"""
Tests for news_events app admin classes
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.utils import timezone

from apps.news_events.models import (
    Category, NewsArticle, Event, Subscriber, Comment,
    Newsletter, ContentAnalytics
)
from apps.news_events.admin import (
    CategoryAdmin, NewsArticleAdmin, EventAdmin,
    SubscriberAdmin, CommentAdmin, NewsletterAdmin, ContentAnalyticsAdmin
)


class NewsEventsAdminTestCase(TestCase):
    """Base test case for news_events admin tests"""
    
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
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            is_active=True
        )


class CategoryAdminTest(NewsEventsAdminTestCase):
    """Test CategoryAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = CategoryAdmin(Category, self.site)
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('slug', self.admin.list_display)
        self.assertIn('article_count', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('is_active', self.admin.list_filter)
        self.assertIn('created_at', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('name', self.admin.search_fields)
        self.assertIn('description', self.admin.search_fields)
    
    def test_prepopulated_fields(self):
        """Test prepopulated fields"""
        self.assertIn('slug', self.admin.prepopulated_fields)
    
    def test_article_count(self):
        """Test article_count method"""
        article = NewsArticle.objects.create(
            title='Test Article',
            content='Test content',
            category=self.category,
            author=self.admin_user,
            status=NewsArticle.Status.PUBLISHED
        )
        count = self.admin.article_count(self.category)
        self.assertGreaterEqual(count, 1)
    
    def test_color_preview(self):
        """Test color_preview method"""
        self.category.color = '#FF0000'
        self.category.save()
        result = self.admin.color_preview(self.category)
        self.assertIsNotNone(result)
        self.assertIn('#FF0000', result)


class NewsArticleAdminTest(NewsEventsAdminTestCase):
    """Test NewsArticleAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = NewsArticleAdmin(NewsArticle, self.site)
        self.article = NewsArticle.objects.create(
            title='Test Article',
            content='Test content',
            category=self.category,
            author=self.admin_user,
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('title', self.admin.list_display)
        self.assertIn('author', self.admin.list_display)
        self.assertIn('category', self.admin.list_display)
        self.assertIn('status', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('status', self.admin.list_filter)
        self.assertIn('priority', self.admin.list_filter)
        self.assertIn('is_featured', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('title', self.admin.search_fields)
        self.assertIn('content', self.admin.search_fields)
    
    def test_prepopulated_fields(self):
        """Test prepopulated fields"""
        self.assertIn('slug', self.admin.prepopulated_fields)
    
    def test_readonly_fields(self):
        """Test readonly fields"""
        self.assertIn('view_count', self.admin.readonly_fields)
        self.assertIn('share_count', self.admin.readonly_fields)
        self.assertIn('comment_count', self.admin.readonly_fields)


class EventAdminTest(NewsEventsAdminTestCase):
    """Test EventAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = EventAdmin(Event, self.site)
        self.event = Event.objects.create(
            title='Test Event',
            content='Test content',
            category=self.category,
            event_date=timezone.now() + timezone.timedelta(days=7),
            status=Event.Status.PUBLISHED
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('title', self.admin.list_display)
        self.assertIn('event_date', self.admin.list_display)
        self.assertIn('status', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('status', self.admin.list_filter)
        self.assertIn('event_date', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('title', self.admin.search_fields)
        self.assertIn('content', self.admin.search_fields)


class SubscriberAdminTest(NewsEventsAdminTestCase):
    """Test SubscriberAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = SubscriberAdmin(Subscriber, self.site)
        self.subscriber = Subscriber.objects.create(
            email='test@example.com',
            name='Test User',
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('email', self.admin.list_display)
        self.assertIn('name', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)


class CommentAdminTest(NewsEventsAdminTestCase):
    """Test CommentAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = CommentAdmin(Comment, self.site)
        self.comment = Comment.objects.create(
            article=self.article,
            author_name='Test User',
            content='Test comment',
            is_approved=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('author_name', self.admin.list_display)
        self.assertIn('article', self.admin.list_display)
        self.assertIn('is_approved', self.admin.list_display)


class NewsletterAdminTest(NewsEventsAdminTestCase):
    """Test NewsletterAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = NewsletterAdmin(Newsletter, self.site)
        self.newsletter = Newsletter.objects.create(
            subject='Test Newsletter',
            content='Test content',
            is_sent=False
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('subject', self.admin.list_display)
        self.assertIn('is_sent', self.admin.list_display)
        self.assertIn('sent_at', self.admin.list_display)


class ContentAnalyticsAdminTest(NewsEventsAdminTestCase):
    """Test ContentAnalyticsAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = ContentAnalyticsAdmin(ContentAnalytics, self.site)
        self.analytics = ContentAnalytics.objects.create(
            content_type='article',
            content_id=self.article.id,
            view_count=100
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('content_type', self.admin.list_display)
        self.assertIn('view_count', self.admin.list_display)

