"""
Comprehensive tests for News Events services
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta

from apps.news_events.models import (
    NewsArticle, Event, Category, Comment, Subscriber
)
from apps.news_events.services import (
    NewsService, EventService, InteractionService, SearchService
)

User = get_user_model()


class NewsServiceTest(TestCase):
    """Test suite for NewsService"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
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
        
        self.article = NewsArticle.objects.create(
            title='Test Article',
            slug='test-article',
            category=self.category,
            author=self.user,
            content='Test content',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
    
    @patch('apps.news_events.services.NewsEventsCache.get_cached_article_list')
    def test_get_home_page_data_uses_cache(self, mock_cache):
        """Test that home page data uses cache when available"""
        mock_cache.return_value = {'cached': True}
        
        data = NewsService.get_home_page_data()
        
        self.assertEqual(data, {'cached': True})
        mock_cache.assert_called_once()
    
    @patch('apps.news_events.services.NewsEventsCache.get_cached_article_list')
    def test_get_home_page_data_fetches_data(self, mock_cache):
        """Test that home page data fetches when cache is empty"""
        mock_cache.return_value = None
        
        data = NewsService.get_home_page_data()
        
        self.assertIn('recent_articles', data)
        self.assertIn('upcoming_events', data)
        self.assertIn('featured_content', data)
        self.assertIn('categories', data)
        self.assertIn('article_stats', data)
        self.assertIn('event_stats', data)
    
    def test_get_article_detail_success(self):
        """Test getting article detail successfully"""
        request = self.factory.get('/')
        request.user = self.user
        
        result = NewsService.get_article_detail('test-article', self.user, request)
        
        self.assertIn('article', result)
        self.assertEqual(result['article'], self.article)
        self.assertIn('related_articles', result)
        self.assertIn('comments', result)
        self.assertFalse(result['login_required'])
    
    def test_get_article_detail_requires_login(self):
        """Test article detail with login requirement"""
        self.article.require_login = True
        self.article.save()
        
        request = self.factory.get('/')
        request.user = MagicMock(is_authenticated=False)
        
        result = NewsService.get_article_detail('test-article', None, request)
        
        self.assertTrue(result['login_required'])
    
    def test_get_article_detail_increments_view_count(self):
        """Test that article detail increments view count"""
        initial_count = self.article.view_count
        
        NewsService.get_article_detail('test-article', self.user)
        
        self.article.refresh_from_db()
        self.assertEqual(self.article.view_count, initial_count + 1)
    
    def test_get_article_list_basic(self):
        """Test getting article list"""
        params = {}
        result = NewsService.get_article_list(params)
        
        self.assertIn('page_obj', result)
        self.assertIn('articles', result)
        self.assertIn('categories', result)
    
    def test_get_article_list_with_category(self):
        """Test getting article list with category filter"""
        params = {'category': 'test-category'}
        result = NewsService.get_article_list(params)
        
        self.assertEqual(result['selected_category'], 'test-category')
    
    def test_get_article_list_with_search(self):
        """Test getting article list with search query"""
        params = {'q': 'Test'}
        result = NewsService.get_article_list(params)
        
        self.assertEqual(result['search_query'], 'Test')
    
    def test_get_article_list_featured_only(self):
        """Test getting article list with featured filter"""
        self.article.is_featured = True
        self.article.save()
        
        params = {'featured': 'true'}
        result = NewsService.get_article_list(params)
        
        self.assertTrue(result['featured_only'])
    
    def test_get_article_list_pagination(self):
        """Test article list pagination"""
        params = {'page': 1, 'page_size': 5}
        result = NewsService.get_article_list(params)
        
        self.assertIsNotNone(result['page_obj'])
        self.assertLessEqual(len(result['page_obj']), 5)


class EventServiceTest(TestCase):
    """Test suite for EventService"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            slug='test-event',
            description='Test content',
            event_date=timezone.now() + timedelta(days=7),
            status=Event.Status.PUBLISHED
        )
    
    def test_get_event_detail_success(self):
        """Test getting event detail successfully"""
        request = self.factory.get('/')
        
        result = EventService.get_event_detail('test-event', request)
        
        self.assertIn('event', result)
        self.assertEqual(result['event'], self.event)
        self.assertIn('related_events', result)
    
    def test_get_event_detail_increments_view_count(self):
        """Test that event detail increments view count"""
        initial_count = self.event.view_count
        
        EventService.get_event_detail('test-event')
        
        self.event.refresh_from_db()
        self.assertEqual(self.event.view_count, initial_count + 1)
    
    def test_get_event_list_basic(self):
        """Test getting event list"""
        params = {}
        result = EventService.get_event_list(params)
        
        self.assertIn('page_obj', result)
        self.assertIn('events', result)
        self.assertIn('event_types', result)
    
    def test_get_event_list_upcoming_only(self):
        """Test getting upcoming events only"""
        params = {'upcoming': 'true'}
        result = EventService.get_event_list(params)
        
        self.assertTrue(result['upcoming_only'])
        for event in result['events']:
            self.assertGreater(event.event_date, timezone.now())
    
    def test_get_event_list_past_events(self):
        """Test getting past events"""
        self.event.event_date = timezone.now() - timedelta(days=1)
        self.event.save()
        
        params = {'upcoming': 'false'}
        result = EventService.get_event_list(params)
        
        self.assertFalse(result['upcoming_only'])


class InteractionServiceTest(TestCase):
    """Test suite for InteractionService"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
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
        
        self.article = NewsArticle.objects.create(
            title='Test Article',
            slug='test-article',
            category=self.category,
            author=self.user,
            content='Test content',
            status=NewsArticle.Status.PUBLISHED,
            allow_comments=True
        )
    
    @patch('apps.news_events.services.EmailSecurityManager.send_confirmation_email')
    @patch('apps.news_events.services.SecurityAuditLogger.log_subscription_attempt')
    def test_handle_subscription_new(self, mock_log, mock_email):
        """Test handling new subscription"""
        mock_email.return_value = True
        
        data = {
            'email': 'new@example.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        success, message = InteractionService.handle_subscription(data, request)
        
        self.assertTrue(success)
        self.assertIn('Thank you', message)
        self.assertTrue(Subscriber.objects.filter(email='new@example.com').exists())
    
    def test_handle_subscription_existing(self):
        """Test handling existing subscription"""
        Subscriber.objects.create(
            email='existing@example.com',
            status=Subscriber.Status.ACTIVE
        )
        
        data = {'email': 'existing@example.com'}
        success, message = InteractionService.handle_subscription(data)
        
        self.assertFalse(success)
        self.assertIn('already subscribed', message)
    
    def test_handle_subscription_reactivate(self):
        """Test reactivating unsubscribed user"""
        Subscriber.objects.create(
            email='unsubscribed@example.com',
            status=Subscriber.Status.UNSUBSCRIBED
        )
        
        data = {'email': 'unsubscribed@example.com'}
        success, message = InteractionService.handle_subscription(data)
        
        self.assertTrue(success)
        self.assertIn('reactivated', message)
        
        subscriber = Subscriber.objects.get(email='unsubscribed@example.com')
        self.assertEqual(subscriber.status, Subscriber.Status.ACTIVE)
    
    @patch('apps.news_events.services.SpamProtectionManager.check_spam_indicators')
    @patch('apps.news_events.services.SecurityAuditLogger.log_content_action')
    def test_handle_comment_submission_success(self, mock_log, mock_spam):
        """Test handling comment submission successfully"""
        mock_spam.return_value = {'is_spam': False, 'reasons': []}
        
        data = {
            'author_name': 'John Doe',
            'author_email': 'john@example.com',
            'content': 'Great article!'
        }
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        success, message = InteractionService.handle_comment_submission(
            data, 'test-article', request
        )
        
        self.assertTrue(success)
        self.assertIn('submitted', message)
        self.assertTrue(Comment.objects.filter(article=self.article).exists())
    
    @patch('apps.news_events.services.SpamProtectionManager.check_spam_indicators')
    def test_handle_comment_submission_spam(self, mock_spam):
        """Test handling spam comment"""
        mock_spam.return_value = {'is_spam': True, 'reasons': ['Suspicious content']}
        
        data = {
            'author_name': 'Spam',
            'author_email': 'spam@example.com',
            'content': 'Buy now!'
        }
        
        success, message = InteractionService.handle_comment_submission(
            data, 'test-article'
        )
        
        self.assertTrue(success)
        comment = Comment.objects.get(article=self.article)
        self.assertEqual(comment.status, Comment.Status.SPAM)
    
    def test_handle_comment_submission_disabled(self):
        """Test comment submission when comments are disabled"""
        self.article.allow_comments = False
        self.article.save()
        
        data = {
            'author_name': 'John',
            'author_email': 'john@example.com',
            'content': 'Test'
        }
        
        success, message = InteractionService.handle_comment_submission(
            data, 'test-article'
        )
        
        self.assertFalse(success)
        self.assertIn('disabled', message)
    
    @patch('apps.news_events.services.SecurityAuditLogger.log_content_action')
    def test_handle_share(self, mock_log):
        """Test handling article share"""
        initial_count = self.article.share_count
        request = self.factory.post('/')
        
        success, message = InteractionService.handle_share('test-article', request)
        
        self.assertTrue(success)
        self.article.refresh_from_db()
        self.assertEqual(self.article.share_count, initial_count + 1)
        mock_log.assert_called_once()


class SearchServiceTest(TestCase):
    """Test suite for SearchService"""
    
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
        
        self.article = NewsArticle.objects.create(
            title='Test Article',
            slug='test-article',
            category=self.category,
            author=self.user,
            content='Test content with search terms',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
    
    def test_perform_search_basic(self):
        """Test basic search"""
        params = {'query': 'Test'}
        result = SearchService.perform_search(params)
        
        self.assertIn('results', result)
        self.assertIn('page_obj', result)
        self.assertIn('query', result)
        self.assertIn('results_count', result)
    
    def test_perform_search_articles_only(self):
        """Test search for articles only"""
        params = {'query': 'Test', 'content_type': 'articles'}
        result = SearchService.perform_search(params)
        
        self.assertGreaterEqual(result['results_count'], 1)
        self.assertGreaterEqual(len(result['results']), 1)
    
    def test_perform_search_with_category(self):
        """Test search with category filter"""
        params = {
            'query': 'Test',
            'content_type': 'articles',
            'category': self.category.id
        }
        result = SearchService.perform_search(params)
        
        for item in result['results']:
            if hasattr(item, 'category'):
                self.assertEqual(item.category, self.category)
    
    def test_perform_search_featured_only(self):
        """Test search with featured filter"""
        self.article.is_featured = True
        self.article.save()
        
        params = {'query': 'Test', 'featured_only': True, 'content_type': 'articles'}
        result = SearchService.perform_search(params)
        
        for item in result['results']:
            if hasattr(item, 'is_featured'):
                self.assertTrue(item.is_featured)

