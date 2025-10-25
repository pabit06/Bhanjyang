# apps/news_events/tests.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from .models import NewsArticle, Event, Category, Subscriber, Comment

class NewsEventsViewsTestCase(TestCase):
    """Smoke tests for news_events app views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        # Create category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            is_active=True
        )
        
        # Create published article
        self.article = NewsArticle.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content for the article',
            excerpt='Test excerpt',
            author=self.user,
            category=self.category,
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        
        # Create draft article
        self.draft_article = NewsArticle.objects.create(
            title='Draft Article',
            slug='draft-article',
            content='Draft content',
            author=self.user,
            category=self.category,
            status=NewsArticle.Status.DRAFT
        )
        
        # Create upcoming event
        self.event = Event.objects.create(
            title='Test Event',
            slug='test-event',
            description='Test event description',
            short_description='Short description',
            event_date=timezone.now() + timedelta(days=7),
            status=Event.Status.PUBLISHED
        )
    
    def test_home_view_renders(self):
        """Test news_events home page renders without error"""
        response = self.client.get(reverse('news_events:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'News & Events')
    
    def test_article_list_view_renders(self):
        """Test article list view renders"""
        response = self.client.get(reverse('news_events:article-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        # Draft articles should not be visible
        self.assertNotContains(response, self.draft_article.title)
    
    def test_article_detail_view_published(self):
        """Test published article detail view"""
        response = self.client.get(reverse('news_events:article-detail', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.article.content)
    
    def test_event_list_view_renders(self):
        """Test event list view renders"""
        response = self.client.get(reverse('news_events:event-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)
    
    def test_event_detail_view(self):
        """Test event detail view"""
        response = self.client.get(reverse('news_events:event-detail', kwargs={'slug': self.event.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)
    
    def test_article_list_with_category_filter(self):
        """Test article list with category filter"""
        response = self.client.get(f"{reverse('news_events:article-list')}?category={self.category.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
    
    def test_article_list_with_search(self):
        """Test article list with search query"""
        response = self.client.get(f"{reverse('news_events:article-list')}?q=Test")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
    
    def test_article_list_with_advanced_filters(self):
        """Test article list with advanced filters"""
        # Test author filter
        response = self.client.get(f"{reverse('news_events:article-list')}?author={self.user.id}")
        self.assertEqual(response.status_code, 200)
        
        # Test featured filter
        response = self.client.get(f"{reverse('news_events:article-list')}?featured=true")
        self.assertEqual(response.status_code, 200)
        
        # Test has_image filter
        response = self.client.get(f"{reverse('news_events:article-list')}?has_image=true")
        self.assertEqual(response.status_code, 200)
    
    def test_search_view_renders(self):
        """Test search view renders"""
        response = self.client.get(f"{reverse('news_events:search')}?query=Test")
        self.assertEqual(response.status_code, 200)
    
    def test_rss_feed_view(self):
        """Test RSS feed renders valid XML"""
        response = self.client.get(reverse('news_events:rss-feed'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rss+xml; charset=utf-8')
        self.assertContains(response, '<?xml version="1.0"')
        self.assertContains(response, self.article.title)
    
    def test_analytics_dashboard_requires_staff(self):
        """Test analytics dashboard requires staff login"""
        # Unauthenticated user should be redirected
        response = self.client.get(reverse('news_events:analytics-dashboard'))
        self.assertEqual(response.status_code, 302)
        
        # Regular user should be redirected
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news_events:analytics-dashboard'))
        self.assertEqual(response.status_code, 302)
        self.client.logout()
        
        # Staff user should access
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(reverse('news_events:analytics-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()


class NewsEventsModelsTestCase(TestCase):
    """Smoke tests for news_events models"""
    
    def setUp(self):
        """Set up test data"""
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
    
    def test_create_article(self):
        """Test creating a news article"""
        article = NewsArticle.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            author=self.user,
            category=self.category,
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        self.assertEqual(article.title, 'Test Article')
        self.assertEqual(str(article), 'Test Article')
        self.assertIsNotNone(article.get_absolute_url())
    
    def test_create_event(self):
        """Test creating an event"""
        event = Event.objects.create(
            title='Test Event',
            slug='test-event',
            description='Test description',
            event_date=timezone.now() + timedelta(days=7),
            status=Event.Status.PUBLISHED
        )
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(str(event), 'Test Event')
        self.assertIsNotNone(event.get_absolute_url())
    
    def test_create_category(self):
        """Test creating a category"""
        category = Category.objects.create(
            name='New Category',
            slug='new-category',
            is_active=True
        )
        self.assertEqual(category.name, 'New Category')
        self.assertEqual(str(category), 'New Category')
    
    def test_create_subscriber(self):
        """Test creating a subscriber"""
        subscriber = Subscriber.objects.create(
            email='subscriber@example.com',
            first_name='Test',
            last_name='Subscriber',
            is_confirmed=True
        )
        self.assertEqual(subscriber.email, 'subscriber@example.com')
        self.assertTrue(subscriber.is_confirmed)
    
    def test_create_comment(self):
        """Test creating a comment"""
        article = NewsArticle.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            author=self.user,
            category=self.category,
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        
        comment = Comment.objects.create(
            article=article,
            author_name='Test Commenter',
            author_email='commenter@example.com',
            content='Test comment content',
            status=Comment.Status.APPROVED
        )
        self.assertEqual(comment.author_name, 'Test Commenter')
        self.assertEqual(comment.article, article)


class NewsEventsManagementCommandsTestCase(TestCase):
    """Smoke tests for management commands"""
    
    def test_seed_news_events_command(self):
        """Test seed_news_events command runs without error"""
        from django.core.management import call_command
        
        # This should create sample data without errors
        call_command('seed_news_events')
        
        # Verify some data was created
        self.assertGreater(Category.objects.count(), 0)
        self.assertGreater(NewsArticle.objects.count(), 0)
        self.assertGreater(Event.objects.count(), 0)
