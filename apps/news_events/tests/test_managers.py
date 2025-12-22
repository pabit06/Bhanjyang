"""
Tests for news_events app managers
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apps.news_events.models import NewsArticle, Event, Category
from apps.news_events.managers import ArticleManager, EventManager
from django.contrib.auth.models import User


class ArticleManagerTest(TestCase):
    """Test ArticleManager"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            is_active=True
        )
        self.published_article = NewsArticle.objects.create(
            title='Published Article',
            content='Test content',
            category=self.category,
            author=self.user,
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now() - timedelta(days=1),
            is_featured=False
        )
        self.draft_article = NewsArticle.objects.create(
            title='Draft Article',
            content='Test content',
            category=self.category,
            author=self.user,
            status=NewsArticle.Status.DRAFT,
            published_date=timezone.now() - timedelta(days=1)
        )
        self.future_article = NewsArticle.objects.create(
            title='Future Article',
            content='Test content',
            category=self.category,
            author=self.user,
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now() + timedelta(days=1)
        )
        self.featured_article = NewsArticle.objects.create(
            title='Featured Article',
            content='Test content',
            category=self.category,
            author=self.user,
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now() - timedelta(days=1),
            is_featured=True
        )
    
    def test_published(self):
        """Test published manager method"""
        published = NewsArticle.objects.published()
        self.assertIn(self.published_article, published)
        self.assertNotIn(self.draft_article, published)
        self.assertNotIn(self.future_article, published)
    
    def test_featured(self):
        """Test featured manager method"""
        featured = NewsArticle.objects.featured()
        self.assertIn(self.featured_article, featured)
        self.assertNotIn(self.published_article, featured)
        # Featured should only return published and featured
        for article in featured:
            self.assertTrue(article.is_featured)
            self.assertEqual(article.status, NewsArticle.Status.PUBLISHED)
    
    def test_recent(self):
        """Test recent manager method"""
        recent = NewsArticle.objects.recent()
        # Should be ordered by published_date descending
        self.assertIn(self.published_article, recent)
        self.assertIn(self.featured_article, recent)
        # Should be ordered
        if len(recent) > 1:
            dates = [article.published_date for article in recent]
            self.assertEqual(dates, sorted(dates, reverse=True))


class EventManagerTest(TestCase):
    """Test EventManager"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            is_active=True
        )
        self.upcoming_event = Event.objects.create(
            title='Upcoming Event',
            content='Test content',
            category=self.category,
            event_date=timezone.now() + timedelta(days=7),
            status=Event.Status.PUBLISHED,
            is_featured=False
        )
        self.past_event = Event.objects.create(
            title='Past Event',
            content='Test content',
            category=self.category,
            event_date=timezone.now() - timedelta(days=7),
            status=Event.Status.PUBLISHED
        )
        self.draft_event = Event.objects.create(
            title='Draft Event',
            content='Test content',
            category=self.category,
            event_date=timezone.now() + timedelta(days=7),
            status=Event.Status.DRAFT
        )
        self.featured_upcoming = Event.objects.create(
            title='Featured Upcoming',
            content='Test content',
            category=self.category,
            event_date=timezone.now() + timedelta(days=7),
            status=Event.Status.PUBLISHED,
            is_featured=True
        )
    
    def test_published(self):
        """Test published manager method"""
        published = Event.objects.published()
        self.assertIn(self.upcoming_event, published)
        self.assertIn(self.past_event, published)
        self.assertNotIn(self.draft_event, published)
    
    def test_upcoming(self):
        """Test upcoming manager method"""
        upcoming = Event.objects.upcoming()
        self.assertIn(self.upcoming_event, upcoming)
        self.assertNotIn(self.past_event, upcoming)
        self.assertNotIn(self.draft_event, upcoming)
        # Should be ordered by event_date ascending
        if len(upcoming) > 1:
            dates = [event.event_date for event in upcoming]
            self.assertEqual(dates, sorted(dates))
    
    def test_past(self):
        """Test past manager method"""
        past = Event.objects.past()
        self.assertIn(self.past_event, past)
        self.assertNotIn(self.upcoming_event, past)
        self.assertNotIn(self.draft_event, past)
        # Should be ordered by event_date descending
        if len(past) > 1:
            dates = [event.event_date for event in past]
            self.assertEqual(dates, sorted(dates, reverse=True))
    
    def test_featured(self):
        """Test featured manager method"""
        featured = Event.objects.featured()
        self.assertIn(self.featured_upcoming, featured)
        self.assertNotIn(self.upcoming_event, featured)
        # Featured should only return upcoming, published, and featured
        for event in featured:
            self.assertTrue(event.is_featured)
            self.assertEqual(event.status, Event.Status.PUBLISHED)
            self.assertGreater(event.event_date, timezone.now())

