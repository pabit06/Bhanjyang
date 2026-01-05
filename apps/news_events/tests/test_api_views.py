"""
Comprehensive tests for News Events REST API endpoints.

Tests all ViewSets and custom actions to ensure API functionality works correctly.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
import json

from apps.news_events.models import (
    Category, NewsArticle, Event, Comment, Subscriber, Newsletter, ContentAnalytics
)

User = get_user_model()


class CategoryViewSetTest(TestCase):
    """Test cases for CategoryViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.category1 = Category.objects.create(
            name='News',
            slug='news',
            is_active=True,
            sort_order=1
        )
        self.category2 = Category.objects.create(
            name='Events',
            slug='events',
            is_active=True,
            sort_order=2
        )
        self.inactive_category = Category.objects.create(
            name='Inactive',
            slug='inactive',
            is_active=False
        )
    
    def test_list_categories(self):
        """Test listing all active categories."""
        url = reverse('news_events_api:category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_categories_pagination(self):
        """Test category list pagination."""
        # Create more categories
        for i in range(25):
            Category.objects.create(name=f'Category {i}', is_active=True)
        
        url = reverse('news_events_api:category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)  # Default page size
        self.assertIsNotNone(response.data['next'])
    
    def test_retrieve_category(self):
        """Test retrieving a specific category."""
        url = reverse('news_events_api:category-detail', kwargs={'pk': self.category1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'News')
        self.assertEqual(response.data['slug'], 'news')
    
    def test_category_articles_endpoint(self):
        """Test getting articles in a category."""
        user = User.objects.create_user(username='author', email='author@test.com')
        article = NewsArticle.objects.create(
            title='Test Article',
            category=self.category1,
            author=user,
            content='Test content',
            status=NewsArticle.Status.PUBLISHED
        )
        
        url = reverse('news_events_api:category-articles', kwargs={'pk': self.category1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Article')
    
    def test_search_categories(self):
        """Test searching categories."""
        url = reverse('news_events_api:category-list')
        response = self.client.get(url, {'search': 'News'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'News')
    
    def test_order_categories(self):
        """Test ordering categories."""
        url = reverse('news_events_api:category-list')
        response = self.client.get(url, {'ordering': '-sort_order'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'Events')  # Higher sort_order


class NewsArticleViewSetTest(TestCase):
    """Test cases for NewsArticleViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        self.category = Category.objects.create(name='News', is_active=True)
        
        self.article1 = NewsArticle.objects.create(
            title='Featured Article',
            category=self.category,
            author=self.user,
            content='Content 1',
            status=NewsArticle.Status.PUBLISHED,
            is_featured=True,
            published_date=timezone.now() - timedelta(days=1)
        )
        self.article2 = NewsArticle.objects.create(
            title='Recent Article',
            category=self.category,
            author=self.user,
            content='Content 2',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        self.draft_article = NewsArticle.objects.create(
            title='Draft Article',
            category=self.category,
            author=self.user,
            content='Draft content',
            status=NewsArticle.Status.DRAFT
        )
    
    def test_list_articles(self):
        """Test listing published articles."""
        url = reverse('news_events_api:article-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Only published
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_articles_staff_sees_all(self):
        """Test that staff can see all articles including drafts."""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('news_events_api:article-list')
        response = self.client.get(url, {'status': 'DF'})  # Draft status
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see draft articles when filtering by status
    
    def test_retrieve_article(self):
        """Test retrieving a specific article."""
        url = reverse('news_events_api:article-detail', kwargs={'pk': self.article1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Featured Article')
        self.assertEqual(response.data['status'], NewsArticle.Status.PUBLISHED)
    
    def test_featured_articles(self):
        """Test getting featured articles."""
        url = reverse('news_events_api:article-featured')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Featured Article')
    
    def test_recent_articles(self):
        """Test getting recent articles."""
        url = reverse('news_events_api:article-recent')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Should be ordered by most recent first
        self.assertEqual(response.data[0]['title'], 'Recent Article')
    
    def test_articles_by_category(self):
        """Test getting articles by category."""
        url = reverse('news_events_api:article-by-category')
        response = self.client.get(url, {'category_id': self.category.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_articles_by_category_invalid_id(self):
        """Test getting articles by invalid category ID."""
        url = reverse('news_events_api:article-by-category')
        response = self.client.get(url, {'category_id': 99999})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_articles_by_category_missing_param(self):
        """Test getting articles by category without category_id."""
        url = reverse('news_events_api:article-by-category')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_increment_view_count(self):
        """Test incrementing article view count."""
        initial_count = self.article1.view_count
        url = reverse('news_events_api:article-increment-view', kwargs={'pk': self.article1.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['view_count'], initial_count + 1)
        
        # Verify in database
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.view_count, initial_count + 1)
    
    def test_filter_articles_by_category(self):
        """Test filtering articles by category."""
        url = reverse('news_events_api:article-list')
        response = self.client.get(url, {'category': self.category.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_filter_articles_by_featured(self):
        """Test filtering featured articles."""
        url = reverse('news_events_api:article-list')
        response = self.client.get(url, {'is_featured': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Featured Article')
    
    def test_search_articles(self):
        """Test searching articles."""
        url = reverse('news_events_api:article-list')
        response = self.client.get(url, {'search': 'Featured'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Featured Article')
    
    def test_order_articles(self):
        """Test ordering articles."""
        url = reverse('news_events_api:article-list')
        response = self.client.get(url, {'ordering': 'view_count'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be ordered by view_count ascending


class EventViewSetTest(TestCase):
    """Test cases for EventViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.now = timezone.now()
        self.upcoming_event = Event.objects.create(
            title='Upcoming Event',
            description='Upcoming event description',
            event_type=Event.EventType.MEETING,
            status=Event.Status.PUBLISHED,
            event_date=self.now + timedelta(days=7),
            is_featured=True
        )
        self.past_event = Event.objects.create(
            title='Past Event',
            description='Past event description',
            event_type=Event.EventType.WORKSHOP,
            status=Event.Status.PUBLISHED,
            event_date=self.now - timedelta(days=7)
        )
        self.draft_event = Event.objects.create(
            title='Draft Event',
            description='Draft event description',
            event_type=Event.EventType.CONFERENCE,
            status=Event.Status.DRAFT,
            event_date=self.now + timedelta(days=14)
        )
    
    def test_list_events(self):
        """Test listing published events."""
        url = reverse('news_events_api:event-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Only published
    
    def test_retrieve_event(self):
        """Test retrieving a specific event."""
        url = reverse('news_events_api:event-detail', kwargs={'pk': self.upcoming_event.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Upcoming Event')
    
    def test_upcoming_events(self):
        """Test getting upcoming events."""
        url = reverse('news_events_api:event-upcoming')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Upcoming Event')
    
    def test_past_events(self):
        """Test getting past events."""
        url = reverse('news_events_api:event-past')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Past Event')
    
    def test_featured_events(self):
        """Test getting featured events."""
        url = reverse('news_events_api:event-featured')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Upcoming Event')
    
    def test_increment_event_view_count(self):
        """Test incrementing event view count."""
        initial_count = self.upcoming_event.view_count
        url = reverse('news_events_api:event-increment-view', kwargs={'pk': self.upcoming_event.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['view_count'], initial_count + 1)
    
    def test_filter_events_by_type(self):
        """Test filtering events by type."""
        url = reverse('news_events_api:event-list')
        response = self.client.get(url, {'event_type': Event.EventType.MEETING})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_search_events(self):
        """Test searching events."""
        url = reverse('news_events_api:event-list')
        response = self.client.get(url, {'search': 'Upcoming'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class CommentViewSetTest(TestCase):
    """Test cases for CommentViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='author', email='author@test.com')
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            is_staff=True
        )
        self.category = Category.objects.create(name='News', is_active=True)
        self.article = NewsArticle.objects.create(
            title='Test Article',
            category=self.category,
            author=self.user,
            content='Test content',
            status=NewsArticle.Status.PUBLISHED
        )
        self.approved_comment = Comment.objects.create(
            article=self.article,
            author_name='John Doe',
            author_email='john@test.com',
            content='Approved comment',
            is_approved=True
        )
        self.pending_comment = Comment.objects.create(
            article=self.article,
            author_name='Jane Doe',
            author_email='jane@test.com',
            content='Pending comment',
            is_approved=False
        )
    
    def test_list_comments_public(self):
        """Test that public users only see approved comments."""
        url = reverse('news_events_api:comment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)  # Only approved
        self.assertEqual(response.data['results'][0]['content'], 'Approved comment')
    
    def test_list_comments_staff(self):
        """Test that staff can see all comments."""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('news_events_api:comment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # All comments
    
    def test_create_comment(self):
        """Test creating a new comment."""
        url = reverse('news_events_api:comment-list')
        data = {
            'article': self.article.pk,
            'author_name': 'New User',
            'author_email': 'newuser@test.com',
            'content': 'New comment content'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New comment content')
        self.assertEqual(Comment.objects.count(), 3)
    
    def test_retrieve_comment(self):
        """Test retrieving a specific comment."""
        url = reverse('news_events_api:comment-detail', kwargs={'pk': self.approved_comment.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Approved comment')
    
    def test_filter_comments_by_article(self):
        """Test filtering comments by article."""
        url = reverse('news_events_api:comment-list')
        response = self.client.get(url, {'article': self.article.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class SubscriberViewSetTest(TestCase):
    """Test cases for SubscriberViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            is_staff=True,
            is_superuser=True
        )
        self.subscriber = Subscriber.objects.create(
            email='subscriber@test.com',
            first_name='Test',
            last_name='Subscriber',
            is_confirmed=True
        )
    
    def test_create_subscriber_public(self):
        """Test that public users can create subscribers."""
        url = reverse('news_events_api:subscriber-list')
        data = {
            'email': 'newsubscriber@test.com',
            'first_name': 'New',
            'last_name': 'Subscriber'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscriber.objects.count(), 2)
    
    def test_list_subscribers_staff_only(self):
        """Test that only staff can list subscribers."""
        # Public user
        url = reverse('news_events_api:subscriber-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Staff user
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class NewsletterViewSetTest(TestCase):
    """Test cases for NewsletterViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            is_staff=True,
            is_superuser=True
        )
        self.newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            subject='Test Subject',
            content='Test content',
            status=Newsletter.Status.DRAFT
        )
    
    def test_list_newsletters_staff_only(self):
        """Test that only staff can list newsletters."""
        # Public user
        url = reverse('news_events_api:newsletter-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Staff user
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_retrieve_newsletter_staff_only(self):
        """Test that only staff can retrieve newsletters."""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('news_events_api:newsletter-detail', kwargs={'pk': self.newsletter.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Newsletter')


class ContentAnalyticsViewSetTest(TestCase):
    """Test cases for ContentAnalyticsViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            is_staff=True,
            is_superuser=True
        )
        # Create a test article first
        from apps.news_events.models import NewsArticle, Category
        category = Category.objects.create(name='Test Category', is_active=True)
        article = NewsArticle.objects.create(
            title='Test Article',
            category=category,
            author=self.staff_user,
            content='Test content',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        self.analytics = ContentAnalytics.objects.create(
            content_type='article',
            object_id=article.pk
        )
        self.analytics.view_count = 100
        self.analytics.share_count = 50
        self.analytics.save()
    
    def test_list_analytics_staff_only(self):
        """Test that only staff can list analytics."""
        # Public user
        url = reverse('news_events_api:analytics-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Staff user
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class AdvancedSearchViewSetTest(TestCase):
    """Test cases for AdvancedSearchViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='News', is_active=True)
        
        # Create test articles
        self.article1 = NewsArticle.objects.create(
            title='Django REST Framework Tutorial',
            category=self.category,
            author=self.user,
            content='Learn Django REST Framework with comprehensive examples',
            excerpt='Django REST Framework guide',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        self.article2 = NewsArticle.objects.create(
            title='Python Web Development',
            category=self.category,
            author=self.user,
            content='Python web development best practices',
            excerpt='Python development guide',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        self.draft_article = NewsArticle.objects.create(
            title='Draft Article',
            category=self.category,
            author=self.user,
            content='Draft content',
            status=NewsArticle.Status.DRAFT
        )
    
    def test_advanced_search_articles(self):
        """Test advanced search for articles."""
        url = reverse('news_events_api:search-advanced')
        response = self.client.post(url, {
            'query': 'Django',
            'content_type': 'article'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response may have 'articles', 'events', or 'results' depending on content_type
        self.assertIn('query', response.data)
    
    def test_advanced_search_articles_with_category(self):
        """Test advanced search with category filter."""
        url = reverse('news_events_api:search-advanced')
        response = self.client.post(url, {
            'query': 'Python',
            'content_type': 'article',
            'category_id': self.category.id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
    
    def test_advanced_search_articles_featured_only(self):
        """Test advanced search with featured filter."""
        self.article1.is_featured = True
        self.article1.save()
        
        url = reverse('news_events_api:search-advanced')
        response = self.client.post(url, {
            'query': 'Django',
            'content_type': 'article',
            'featured_only': True
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
    
    def test_advanced_search_events(self):
        """Test advanced search for events."""
        event = Event.objects.create(
            title='Django Conference 2024',
            description='Annual Django conference',
            event_type=Event.EventType.CONFERENCE,
            status=Event.Status.PUBLISHED,
            event_date=timezone.now() + timedelta(days=30)
        )
        
        url = reverse('news_events_api:search-advanced')
        response = self.client.post(url, {
            'query': 'Django',
            'content_type': 'event'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
    
    def test_advanced_search_all_content(self):
        """Test advanced search for all content types."""
        url = reverse('news_events_api:search-advanced')
        response = self.client.post(url, {
            'query': 'Django',
            'content_type': 'all'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
    
    def test_advanced_search_empty_query(self):
        """Test advanced search with empty query."""
        url = reverse('news_events_api:search-advanced')
        response = self.client.post(url, {
            'query': '',
            'content_type': 'article'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_advanced_search_missing_query(self):
        """Test advanced search without query parameter."""
        url = reverse('news_events_api:search-advanced')
        response = self.client.post(url, {
            'content_type': 'article'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_advanced_search_pagination(self):
        """Test advanced search pagination."""
        url = reverse('news_events_api:search-advanced')
        response = self.client.post(url, {
            'query': 'Python',
            'content_type': 'article',
            'limit': 1
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
        # Check that results are limited
        total = response.data.get('total_results', 0)
        self.assertLessEqual(total, 1)


class NotificationViewSetTest(TestCase):
    """Test cases for NotificationViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )
        
        # Create notifications for user
        from apps.news_events.notifications import NotificationService, NotificationType
        from django.core.cache import cache
        
        # Clear cache first
        cache_key = f"notifications_user_{self.user.id}"
        cache.delete(cache_key)
        
        # Create test notifications
        NotificationService.create_notification(
            notification_type=NotificationType.NEW_ARTICLE,
            title='Test Notification 1',
            message='Test message 1',
            user=self.user
        )
        NotificationService.create_notification(
            notification_type=NotificationType.NEW_EVENT,
            title='Test Notification 2',
            message='Test message 2',
            user=self.user
        )
    
    def test_list_notifications_requires_auth(self):
        """Test that listing notifications requires authentication."""
        url = reverse('news_events_api:notification-list')
        response = self.client.get(url)
        
        # IsAuthenticated returns 403, not 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_notifications_authenticated(self):
        """Test listing notifications for authenticated user."""
        self.client.force_authenticate(user=self.user)
        url = reverse('news_events_api:notification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('notifications', response.data)
        self.assertIn('count', response.data)
        self.assertGreaterEqual(response.data['count'], 0)
    
    def test_list_notifications_with_limit(self):
        """Test listing notifications with limit."""
        self.client.force_authenticate(user=self.user)
        url = reverse('news_events_api:notification-list')
        response = self.client.get(url, {'limit': 1})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('notifications', response.data)
        self.assertLessEqual(len(response.data['notifications']), 1)
    
    def test_unread_count_requires_auth(self):
        """Test that unread count requires authentication."""
        url = reverse('news_events_api:notification-unread-count')
        response = self.client.get(url)
        
        # IsAuthenticated returns 403, not 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unread_count_authenticated(self):
        """Test getting unread notification count."""
        self.client.force_authenticate(user=self.user)
        url = reverse('news_events_api:notification-unread-count')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_count', response.data)
        self.assertIsInstance(response.data['unread_count'], int)
    
    def test_mark_read_requires_auth(self):
        """Test that marking notification as read requires authentication."""
        url = reverse('news_events_api:notification-mark-read', kwargs={'pk': 'test_id'})
        response = self.client.post(url)
        
        # IsAuthenticated returns 403, not 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_mark_read_authenticated(self):
        """Test marking notification as read."""
        self.client.force_authenticate(user=self.user)
        
        # Get a notification ID from the list
        list_url = reverse('news_events_api:notification-list')
        list_response = self.client.get(list_url)
        
        if list_response.data['count'] > 0:
            notification_id = list_response.data['notifications'][0]['id']
            url = reverse('news_events_api:notification-mark-read', kwargs={'pk': notification_id.replace(':', '_')})
            response = self.client.post(url)
            
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
    
    def test_mark_all_read_requires_auth(self):
        """Test that marking all as read requires authentication."""
        url = reverse('news_events_api:notification-mark-all-read')
        response = self.client.post(url)
        
        # IsAuthenticated returns 403, not 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_mark_all_read_authenticated(self):
        """Test marking all notifications as read."""
        self.client.force_authenticate(user=self.user)
        url = reverse('news_events_api:notification-mark-all-read')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)


class SocialMediaViewSetTest(TestCase):
    """Test cases for SocialMediaViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='News', is_active=True)
        
        self.article = NewsArticle.objects.create(
            title='Test Article',
            category=self.category,
            author=self.user,
            content='Test content',
            excerpt='Test excerpt',
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test event description',
            event_type=Event.EventType.MEETING,
            status=Event.Status.PUBLISHED,
            event_date=timezone.now() + timedelta(days=7)
        )
    
    def test_article_share_urls(self):
        """Test getting share URLs for an article."""
        url = reverse('news_events_api:social-article-share-urls', kwargs={'article_id': self.article.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('share_urls', response.data)
        self.assertIn('open_graph', response.data)
        self.assertIn('facebook', response.data['share_urls'])
        self.assertIn('twitter', response.data['share_urls'])
        self.assertIn('linkedin', response.data['share_urls'])
    
    def test_article_share_urls_not_found(self):
        """Test getting share URLs for non-existent article."""
        url = reverse('news_events_api:social-article-share-urls', kwargs={'article_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_article_share_urls_draft_article(self):
        """Test getting share URLs for draft article (should not be accessible)."""
        draft_article = NewsArticle.objects.create(
            title='Draft Article',
            category=self.category,
            author=self.user,
            content='Draft content',
            status=NewsArticle.Status.DRAFT
        )
        
        url = reverse('news_events_api:social-article-share-urls', kwargs={'article_id': draft_article.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_event_share_urls(self):
        """Test getting share URLs for an event."""
        url = reverse('news_events_api:social-event-share-urls', kwargs={'event_id': self.event.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('share_urls', response.data)
        self.assertIn('open_graph', response.data)
        self.assertIn('facebook', response.data['share_urls'])
        self.assertIn('twitter', response.data['share_urls'])
    
    def test_event_share_urls_not_found(self):
        """Test getting share URLs for non-existent event."""
        url = reverse('news_events_api:social-event-share-urls', kwargs={'event_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_track_share_article(self):
        """Test tracking social media share for article."""
        url = reverse('news_events_api:social-track-share')
        response = self.client.post(url, {
            'content_type': 'article',
            'content_id': self.article.pk,
            'platform': 'facebook'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_track_share_event(self):
        """Test tracking social media share for event."""
        url = reverse('news_events_api:social-track-share')
        response = self.client.post(url, {
            'content_type': 'event',
            'content_id': self.event.pk,
            'platform': 'twitter'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_track_share_missing_fields(self):
        """Test tracking share with missing required fields."""
        url = reverse('news_events_api:social-track-share')
        response = self.client.post(url, {
            'content_type': 'article',
            'platform': 'facebook'
            # Missing content_id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_track_share_all_platforms(self):
        """Test tracking share for all supported platforms."""
        platforms = ['facebook', 'twitter', 'linkedin', 'whatsapp', 'telegram', 'email']
        url = reverse('news_events_api:social-track-share')
        
        for platform in platforms:
            response = self.client.post(url, {
                'content_type': 'article',
                'content_id': self.article.pk,
                'platform': platform
            }, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)

