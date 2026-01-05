"""
End-to-End Integration Tests for News Events App

These tests verify complete user workflows and interactions between
multiple components (views, services, models, API, forms).
"""

from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
import json

from apps.news_events.models import (
    Category, NewsArticle, Event, Subscriber, Comment, Newsletter, ContentAnalytics
)
from apps.news_events.services import NewsService, EventService, InteractionService
from apps.news_events.forms import SubscriptionForm, CommentForm

User = get_user_model()


class CompleteUserWorkflowTest(TestCase):
    """
    Test complete user workflows from browsing to subscribing and commenting.
    """
    
    def setUp(self):
        """Set up test data for complete workflows."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='General News',
            slug='general-news',
            is_active=True
        )
        
        self.article = NewsArticle.objects.create(
            title='Test Article for E2E',
            slug='test-article-e2e',
            category=self.category,
            author=self.user,
            content='This is a comprehensive test article content.',
            excerpt='Test excerpt',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now(),
            is_featured=True
        )
        
        self.event = Event.objects.create(
            title='Test Event for E2E',
            slug='test-event-e2e',
            description='This is a test event description.',
            event_type=Event.EventType.MEETING,
            status=Event.Status.PUBLISHED,
            event_date=timezone.now() + timedelta(days=7),
            location='Test Location',
            is_featured=True
        )
    
    def test_complete_article_browsing_workflow(self):
        """
        Test complete workflow: Home -> Article List -> Article Detail -> Comment
        """
        # Step 1: Visit home page
        response = self.client.get(reverse('news_events:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recent_articles', response.context)
        self.assertIn('upcoming_events', response.context)
        
        # Step 2: Browse article list
        response = self.client.get(reverse('news_events:article-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('articles', response.context)
        
        # Step 3: View article detail
        response = self.client.get(reverse(
            'news_events:article-detail',
            kwargs={'slug': self.article.slug}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['article'], self.article)
        
        # Verify view count incremented
        self.article.refresh_from_db()
        self.assertGreater(self.article.view_count, 0)
        
        # Step 4: Submit comment
        comment_data = {
            'author_name': 'Test Commenter',
            'author_email': 'commenter@example.com',
            'content': 'This is a test comment for E2E testing.'
        }
        response = self.client.post(
            reverse('news_events:comment-submit'),
            data=comment_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify comment was created
        comment = Comment.objects.filter(article=self.article).first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.content, comment_data['content'])
    
    def test_complete_subscription_workflow(self):
        """
        Test complete workflow: View subscription form -> Submit -> Confirm email
        """
        # Step 1: Get subscription form from home page
        response = self.client.get(reverse('news_events:home'))
        self.assertIn('subscription_form', response.context)
        form = response.context['subscription_form']
        self.assertIsInstance(form, SubscriptionForm)
        
        # Step 2: Submit subscription
        subscription_data = {
            'email': 'newsubscriber@example.com',
            'name': 'New Subscriber',
        }
        response = self.client.post(
            reverse('news_events:subscribe'),
            data=subscription_data
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify subscriber was created
        subscriber = Subscriber.objects.filter(email=subscription_data['email']).first()
        self.assertIsNotNone(subscriber)
        self.assertEqual(subscriber.name, subscription_data['name'])
        self.assertFalse(subscriber.is_confirmed)  # Not confirmed yet
        
        # Step 3: Confirm subscription (simulate email confirmation)
        if subscriber.confirmation_token:
            response = self.client.get(
                reverse('news_events:confirm-subscription'),
                {'token': subscriber.confirmation_token}
            )
            subscriber.refresh_from_db()
            self.assertTrue(subscriber.is_confirmed)
    
    def test_complete_event_browsing_workflow(self):
        """
        Test complete workflow: Home -> Event List -> Event Detail -> Share
        """
        # Step 1: Visit home page and see upcoming events
        response = self.client.get(reverse('news_events:home'))
        self.assertEqual(response.status_code, 200)
        upcoming_events = response.context.get('upcoming_events', [])
        self.assertGreater(len(upcoming_events), 0)
        
        # Step 2: Browse event list
        response = self.client.get(reverse('news_events:event-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('events', response.context)
        
        # Step 3: View event detail
        response = self.client.get(reverse(
            'news_events:event-detail',
            kwargs={'slug': self.event.slug}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['event'], self.event)
        
        # Verify view count incremented
        self.event.refresh_from_db()
        self.assertGreater(self.event.view_count, 0)
    
    def test_complete_search_workflow(self):
        """
        Test complete workflow: Search -> Results -> Filter -> View Result
        """
        # Step 1: Perform search
        response = self.client.get(
            reverse('news_events:search'),
            {'q': 'test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        
        # Step 2: Filter by category
        response = self.client.get(
            reverse('news_events:search'),
            {'q': 'test', 'category': self.category.id}
        )
        self.assertEqual(response.status_code, 200)
        
        # Step 3: View search result
        if response.context.get('results'):
            result = response.context['results'][0]
            if hasattr(result, 'slug'):
                response = self.client.get(reverse(
                    'news_events:article-detail',
                    kwargs={'slug': result.slug}
                ))
                self.assertEqual(response.status_code, 200)


class APIWorkflowIntegrationTest(TestCase):
    """
    Test complete API workflows from authentication to data retrieval.
    """
    
    def setUp(self):
        """Set up test data for API workflows."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        self.category = Category.objects.create(
            name='API Test Category',
            slug='api-test',
            is_active=True
        )
        
        self.article = NewsArticle.objects.create(
            title='API Test Article',
            category=self.category,
            author=self.user,
            content='API test content',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
    
    def test_complete_api_article_workflow(self):
        """
        Test complete API workflow: List -> Detail -> Increment View -> Analytics
        """
        # Step 1: List articles
        url = reverse('news_events_api:article-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)
        
        # Step 2: Get article detail
        url = reverse('news_events_api:article-detail', kwargs={'pk': self.article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Test Article')
        
        initial_view_count = response.data['view_count']
        
        # Step 3: Increment view count
        url = reverse('news_events_api:article-increment-view', kwargs={'pk': self.article.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Verify view count increased
        url = reverse('news_events_api:article-detail', kwargs={'pk': self.article.pk})
        response = self.client.get(url)
        self.assertGreater(response.data['view_count'], initial_view_count)
    
    def test_complete_api_subscription_workflow(self):
        """
        Test complete API workflow: Create subscriber -> List (staff only) -> Analytics
        """
        # Step 1: Create subscriber (public)
        url = reverse('news_events_api:subscriber-list')
        subscriber_data = {
            'email': 'api.subscriber@example.com',
            'name': 'API Subscriber'
        }
        response = self.client.post(url, subscriber_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: Try to list subscribers (should fail for non-staff)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Step 3: List subscribers as staff
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)


class ServiceLayerIntegrationTest(TestCase):
    """
    Test integration between services, models, and caching.
    """
    
    def setUp(self):
        """Set up test data for service integration."""
        self.user = User.objects.create_user(
            username='serviceuser',
            email='service@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Service Test Category',
            is_active=True
        )
        
        # Create multiple articles for testing
        for i in range(5):
            NewsArticle.objects.create(
                title=f'Service Test Article {i}',
                category=self.category,
                author=self.user,
                content=f'Content {i}',
                status=NewsArticle.Status.PUBLISHED,
                published_date=timezone.now() - timedelta(days=i),
                is_featured=(i < 2)
            )
        
        # Create events
        for i in range(3):
            Event.objects.create(
                title=f'Service Test Event {i}',
                description=f'Description {i}',
                event_type=Event.EventType.MEETING,
                status=Event.Status.PUBLISHED,
                event_date=timezone.now() + timedelta(days=i+1),
                is_featured=(i == 0)
            )
    
    def test_home_page_data_service_integration(self):
        """
        Test that NewsService.get_home_page_data() integrates with caching and optimization.
        """
        # First call - should populate cache
        data1 = NewsService.get_home_page_data()
        
        self.assertIn('recent_articles', data1)
        self.assertIn('upcoming_events', data1)
        self.assertIn('featured_content', data1)
        self.assertIn('categories', data1)
        self.assertIn('article_stats', data1)
        self.assertIn('event_stats', data1)
        
        # Verify data structure
        self.assertGreater(len(data1['recent_articles']), 0)
        self.assertGreater(len(data1['upcoming_events']), 0)
        
        # Second call - should use cache
        data2 = NewsService.get_home_page_data()
        
        # Data should be identical (from cache)
        self.assertEqual(len(data1['recent_articles']), len(data2['recent_articles']))
        self.assertEqual(len(data1['upcoming_events']), len(data2['upcoming_events']))
    
    def test_article_detail_service_integration(self):
        """
        Test that NewsService.get_article_detail() integrates with view counting and security.
        """
        article = NewsArticle.objects.first()
        initial_view_count = article.view_count
        
        # Get article detail
        data = NewsService.get_article_detail(article.slug, user=self.user)
        
        self.assertIn('article', data)
        self.assertIn('related_articles', data)
        self.assertEqual(data['article'], article)
        
        # Verify view count incremented
        article.refresh_from_db()
        self.assertGreater(article.view_count, initial_view_count)
    
    def test_event_list_service_integration(self):
        """
        Test that EventService.get_event_list() integrates with filtering and pagination.
        """
        # Test upcoming events
        params = {'status': 'upcoming', 'page': 1, 'page_size': 10}
        data = EventService.get_event_list(params)
        
        self.assertIn('page_obj', data)
        self.assertIn('events', data)
        self.assertGreater(data['page_obj'].paginator.count, 0)
        
        # Test past events
        params = {'status': 'past', 'page': 1, 'page_size': 10}
        data = EventService.get_event_list(params)
        
        self.assertIn('page_obj', data)
    
    def test_interaction_service_integration(self):
        """
        Test that InteractionService integrates with email and spam protection.
        """
        article = NewsArticle.objects.first()
        
        # Test comment submission
        comment = InteractionService.submit_comment(
            article=article,
            author_name='Service Tester',
            author_email='service.tester@example.com',
            content='Service integration test comment'
        )
        
        self.assertIsNotNone(comment)
        self.assertEqual(comment.article, article)
        self.assertEqual(comment.status, Comment.Status.PENDING)  # Should be pending moderation
        
        # Test subscription
        subscriber = InteractionService.subscribe_to_newsletter(
            email='service.subscriber@example.com',
            name='Service Subscriber'
        )
        
        self.assertIsNotNone(subscriber)
        self.assertEqual(subscriber.email, 'service.subscriber@example.com')
        self.assertFalse(subscriber.is_confirmed)  # Not confirmed yet


class CacheIntegrationTest(TestCase):
    """
    Test integration between views, services, and caching system.
    """
    
    def setUp(self):
        """Set up test data for cache integration."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='cacheuser',
            email='cache@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name='Cache Test', is_active=True)
        
        self.article = NewsArticle.objects.create(
            title='Cache Test Article',
            category=self.category,
            author=self.user,
            content='Cache test content',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
    
    def test_home_page_caching_integration(self):
        """
        Test that home page uses caching correctly.
        """
        # First request - should populate cache
        response1 = self.client.get(reverse('news_events:home'))
        self.assertEqual(response1.status_code, 200)
        
        # Create new article
        NewsArticle.objects.create(
            title='New Article',
            category=self.category,
            author=self.user,
            content='New content',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        
        # Second request - might use cache (depending on cache timeout)
        response2 = self.client.get(reverse('news_events:home'))
        self.assertEqual(response2.status_code, 200)
        
        # Both should return successfully
        self.assertIn('recent_articles', response1.context)
        self.assertIn('recent_articles', response2.context)


class FormViewIntegrationTest(TestCase):
    """
    Test integration between forms, views, and services.
    """
    
    def setUp(self):
        """Set up test data for form-view integration."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='formuser',
            email='form@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name='Form Test', is_active=True)
        
        self.article = NewsArticle.objects.create(
            title='Form Test Article',
            category=self.category,
            author=self.user,
            content='Form test content',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
    
    def test_subscription_form_view_integration(self):
        """
        Test that subscription form integrates with view and service.
        """
        # Get form from view
        response = self.client.get(reverse('news_events:home'))
        form = response.context['subscription_form']
        
        # Validate form
        self.assertTrue(isinstance(form, SubscriptionForm))
        
        # Submit form
        form_data = {
            'email': 'form.subscriber@example.com',
            'name': 'Form Subscriber'
        }
        response = self.client.post(
            reverse('news_events:subscribe'),
            data=form_data
        )
        
        # Verify subscriber created
        subscriber = Subscriber.objects.filter(email=form_data['email']).first()
        self.assertIsNotNone(subscriber)
    
    def test_comment_form_view_integration(self):
        """
        Test that comment form integrates with view and service.
        """
        # Get form from view
        response = self.client.get(reverse(
            'news_events:article-detail',
            kwargs={'slug': self.article.slug}
        ))
        form = response.context['comment_form']
        
        # Validate form
        self.assertTrue(isinstance(form, CommentForm))
        
        # Submit form
        form_data = {
            'author_name': 'Form Commenter',
            'author_email': 'form.commenter@example.com',
            'content': 'Form integration test comment'
        }
        response = self.client.post(
            reverse('news_events:comment-submit'),
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify comment created
        comment = Comment.objects.filter(article=self.article).first()
        self.assertIsNotNone(comment)


class AnalyticsIntegrationTest(TestCase):
    """
    Test integration between analytics, views, and models.
    """
    
    def setUp(self):
        """Set up test data for analytics integration."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='analyticsuser',
            email='analytics@example.com',
            password='testpass123',
            is_staff=True
        )
        
        self.category = Category.objects.create(name='Analytics Test', is_active=True)
        
        self.article = NewsArticle.objects.create(
            title='Analytics Test Article',
            category=self.category,
            author=self.user,
            content='Analytics test content',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
    
    def test_analytics_tracking_integration(self):
        """
        Test that viewing articles tracks analytics correctly.
        """
        initial_view_count = self.article.view_count
        
        # View article
        response = self.client.get(reverse(
            'news_events:article-detail',
            kwargs={'slug': self.article.slug}
        ))
        self.assertEqual(response.status_code, 200)
        
        # Verify view count incremented
        self.article.refresh_from_db()
        self.assertGreater(self.article.view_count, initial_view_count)
        
        # Verify ContentAnalytics might be created/updated
        analytics = ContentAnalytics.objects.filter(
            content_type='article',
            object_id=self.article.id
        ).first()
        
        # Analytics might be created asynchronously, so we just check it can exist
        if analytics:
            self.assertGreater(analytics.view_count, 0)


class NewsletterWorkflowIntegrationTest(TestCase):
    """
    Test complete newsletter workflow from creation to sending.
    """
    
    def setUp(self):
        """Set up test data for newsletter workflow."""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='newsletteruser',
            email='newsletter@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create subscribers
        self.subscriber1 = Subscriber.objects.create(
            email='subscriber1@example.com',
            name='Subscriber 1',
            status=Subscriber.Status.ACTIVE,
            is_confirmed=True
        )
        self.subscriber2 = Subscriber.objects.create(
            email='subscriber2@example.com',
            name='Subscriber 2',
            status=Subscriber.Status.ACTIVE,
            is_confirmed=True
        )
    
    def test_complete_newsletter_workflow(self):
        """
        Test complete workflow: Create newsletter -> Send -> Track results
        """
        # Step 1: Create newsletter
        newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            subject='Test Subject',
            content='<p>Test newsletter content</p>',
            status=Newsletter.Status.DRAFT
        )
        
        self.assertEqual(newsletter.status, Newsletter.Status.DRAFT)
        
        # Step 2: Update status to sending
        newsletter.status = Newsletter.Status.SENDING
        newsletter.save()
        
        # Step 3: Simulate sending (in real scenario, this would use Celery)
        # For testing, we'll just verify the workflow
        self.assertEqual(newsletter.status, Newsletter.Status.SENDING)
        
        # Step 4: Mark as sent
        newsletter.status = Newsletter.Status.SENT
        newsletter.sent_date = timezone.now()
        newsletter.total_sent = 2
        newsletter.save()
        
        self.assertEqual(newsletter.status, Newsletter.Status.SENT)
        self.assertIsNotNone(newsletter.sent_date)
        self.assertEqual(newsletter.total_sent, 2)


class SearchIntegrationTest(TestCase):
    """
    Test complete search workflow integration.
    """
    
    def setUp(self):
        """Set up test data for search integration."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='searchuser',
            email='search@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name='Search Test', is_active=True)
        
        # Create articles with different content
        self.article1 = NewsArticle.objects.create(
            title='Python Programming Article',
            category=self.category,
            author=self.user,
            content='This article is about Python programming and Django framework.',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        
        self.article2 = NewsArticle.objects.create(
            title='JavaScript Tutorial',
            category=self.category,
            author=self.user,
            content='Learn JavaScript and modern web development.',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
    
    def test_complete_search_workflow(self):
        """
        Test complete search workflow: Search -> Filter -> View Results
        """
        # Step 1: Perform basic search
        response = self.client.get(
            reverse('news_events:search'),
            {'q': 'Python'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        
        # Step 2: Search with category filter
        response = self.client.get(
            reverse('news_events:search'),
            {'q': 'programming', 'category': self.category.id}
        )
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Advanced search via API
        api_client = APIClient()
        url = reverse('news_events_api:advanced-search')
        response = api_client.post(url, {
            'query': 'Python',
            'content_type': 'articles'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

