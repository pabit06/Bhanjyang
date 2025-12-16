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
        from django.core.cache import cache
        cache.clear()
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
        
        # Check context
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj[0].title, self.article.title)
        
        # HTML check
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




class ManagerTestCase(TestCase):
    """Test cases for custom managers"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Cat', slug='test-cat')
        
        # Articles
        NewsArticle.objects.create(
            title="Published Article", content="Content", author=self.user, category=self.category,
            status=NewsArticle.Status.PUBLISHED, published_date=timezone.now()
        )
        NewsArticle.objects.create(
            title="Draft Article", content="Content", author=self.user, category=self.category,
            status=NewsArticle.Status.DRAFT, published_date=timezone.now()
        )
        NewsArticle.objects.create(
            title="Future Article", content="Content", author=self.user, category=self.category,
            status=NewsArticle.Status.PUBLISHED, published_date=timezone.now() + timedelta(days=1)
        )
        NewsArticle.objects.create(
            title="Featured Article", content="Content", author=self.user, category=self.category,
            status=NewsArticle.Status.PUBLISHED, published_date=timezone.now(), is_featured=True
        )

        # Events
        Event.objects.create(title="Published Event", status=Event.Status.PUBLISHED, event_date=timezone.now())
        Event.objects.create(title="Draft Event", status=Event.Status.DRAFT, event_date=timezone.now())
        Event.objects.create(title="Upcoming Event", status=Event.Status.PUBLISHED, event_date=timezone.now() + timedelta(days=1))
        Event.objects.create(title="Past Event", status=Event.Status.PUBLISHED, event_date=timezone.now() - timedelta(days=1))

    def test_article_manager_published(self):
        """Test ArticleManager.published()"""
        # Should exclude draft and future articles
        published = NewsArticle.objects.published()
        self.assertEqual(published.count(), 2) # Published Article + Featured Article
        for article in published:
            self.assertEqual(article.status, NewsArticle.Status.PUBLISHED)
            self.assertLessEqual(article.published_date, timezone.now())

    def test_article_manager_featured(self):
        """Test ArticleManager.featured()"""
        featured = NewsArticle.objects.featured()
        self.assertEqual(featured.count(), 1)
        self.assertEqual(featured.first().title, "Featured Article")

    def test_event_manager_published(self):
        """Test EventManager.published()"""
        published = Event.objects.published()
        self.assertEqual(published.count(), 3) # Published, Upcoming, Past

    def test_event_manager_upcoming(self):
        """Test EventManager.upcoming()"""
        upcoming = Event.objects.upcoming()
        self.assertEqual(upcoming.count(), 1)
        self.assertEqual(upcoming.first().title, "Upcoming Event")

    def test_event_manager_past(self):
        """Test EventManager.past()"""
        past = Event.objects.past()
        self.assertTrue(past.filter(title="Past Event").exists())
        # Note: "Published Event" has event_date=now(). Depending on exact microsecond, it might be past or not.
        # usually now() <= now() is True. So Past Event and Published Event might be in past().
        
class ServiceTestCase(TestCase):
    """Test cases for services"""

    def test_handle_subscription(self):
        """Test handle_subscription service"""
        from .services import InteractionService
        
        data = {'email': 'new@example.com', 'first_name': 'New', 'last_name': 'User'}
        success, message = InteractionService.handle_subscription(data)
        self.assertTrue(success)
        self.assertTrue(Subscriber.objects.filter(email='new@example.com').exists())

    def test_handle_comment_submission(self):
        """Test handle_comment_submission service"""
        from .services import InteractionService
        
        # Setup
        user = User.objects.create_user(username='commenter', password='password')
        category = Category.objects.create(name='Cat', slug='cat')
        article = NewsArticle.objects.create(
            title="Comment Article", slug="comment-article", content="Content",
            author=user, category=category, status=NewsArticle.Status.PUBLISHED,
            allow_comments=True
        )
        
        data = {
            'author_name': 'Commenter',
            'author_email': 'commenter@example.com',
            'content': 'Great article!'
        }
        
        success, message = InteractionService.handle_comment_submission(data, article.slug)
        self.assertTrue(success)
        self.assertTrue(Comment.objects.filter(article=article).exists())

