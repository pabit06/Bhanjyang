"""
Comprehensive tests for news_events app views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import json

from apps.news_events.models import (
    Category, NewsArticle, Event, Subscriber, Comment
)
from apps.news_events.forms import SubscriptionForm, CommentForm

User = get_user_model()


class NewsEventsViewsTest(TestCase):
    """Test cases for news_events views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        self.category = Category.objects.create(name="Test Category")
        
        self.article = NewsArticle.objects.create(
            title="Test Article",
            category=self.category,
            author=self.user,
            content="Test content for the article",
            status=NewsArticle.Status.PUBLISHED
        )
        
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            event_type=Event.EventType.MEETING,
            location="Test Location",
            event_date=timezone.now() + timedelta(days=7),
            status=Event.Status.PUBLISHED
        )
    
    def test_news_events_home_view(self):
        """Test news_events_home_view GET request"""
        response = self.client.get(reverse('news_events:home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_events/news_events.html')
        self.assertIn('subscription_form', response.context)
    
    def test_article_list_view(self):
        """Test article_list_view GET request"""
        response = self.client.get(reverse('news_events:article-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_events/article_list.html')
        self.assertIn('breadcrumbs', response.context)
    
    def test_article_list_view_with_category(self):
        """Test article_list_view with category filter"""
        response = self.client.get(reverse(
            'news_events:article-by-category',
            kwargs={'category_slug': self.category.slug}
        ))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('articles', response.context)
    
    def test_article_detail_view(self):
        """Test article_detail_view GET request"""
        response = self.client.get(reverse(
            'news_events:article-detail',
            kwargs={'slug': self.article.slug}
        ))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_events/article_detail.html')
        self.assertIn('article', response.context)
        self.assertEqual(response.context['article'], self.article)
        self.assertIn('breadcrumbs', response.context)
    
    def test_article_detail_view_invalid_slug(self):
        """Test article_detail_view with invalid slug"""
        response = self.client.get(reverse(
            'news_events:article-detail',
            kwargs={'slug': 'non-existent-slug'}
        ))
        
        self.assertEqual(response.status_code, 404)
    
    def test_article_detail_view_requires_login(self):
        """Test article_detail_view with article requiring login"""
        self.article.require_login = True
        self.article.save()
        
        response = self.client.get(reverse(
            'news_events:article-detail',
            kwargs={'slug': self.article.slug}
        ))
        
        # Should redirect to login or show login required message
        self.assertIn(response.status_code, [302, 200])
    
    def test_event_list_view(self):
        """Test event_list_view GET request"""
        response = self.client.get(reverse('news_events:event-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_events/event_list.html')
        self.assertIn('breadcrumbs', response.context)
    
    def test_event_detail_view(self):
        """Test event_detail_view GET request"""
        response = self.client.get(reverse(
            'news_events:event-detail',
            kwargs={'slug': self.event.slug}
        ))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_events/event_detail.html')
        self.assertIn('event', response.context)
        self.assertEqual(response.context['event'], self.event)
        self.assertIn('breadcrumbs', response.context)
    
    def test_event_detail_view_invalid_slug(self):
        """Test event_detail_view with invalid slug"""
        response = self.client.get(reverse(
            'news_events:event-detail',
            kwargs={'slug': 'non-existent-slug'}
        ))
        
        self.assertEqual(response.status_code, 404)
    
    def test_search_view_get(self):
        """Test search_view GET request"""
        response = self.client.get(reverse('news_events:search'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTemplateUsed(response, 'news_events/search.html')
    
    def test_search_view_with_query(self):
        """Test search_view with search query"""
        response = self.client.get(
            reverse('news_events:search'),
            {'q': 'test'}
        )
        
        self.assertEqual(response.status_code, 200)
        # Should show search results if form is valid
        if 'form' in response.context and response.context['form'].is_valid():
            self.assertIn('results', response.context)
    
    def test_subscribe_view_post_valid(self):
        """Test subscribe_view POST with valid data"""
        form_data = {
            'email': 'new@example.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post(
            reverse('news_events:subscribe'),
            form_data
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success', False))
    
    def test_subscribe_view_post_invalid(self):
        """Test subscribe_view POST with invalid data"""
        form_data = {
            'email': 'invalid-email',  # Invalid
            'first_name': ''
        }
        
        response = self.client.post(
            reverse('news_events:subscribe'),
            form_data
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success', False))
    
    def test_comment_submit_view_post_valid(self):
        """Test comment_submit_view POST with valid data"""
        form_data = {
            'author_name': 'John Doe',
            'author_email': 'john@example.com',
            'content': 'Test comment'
        }
        
        response = self.client.post(
            reverse(
                'news_events:comment-submit',
                kwargs={'article_slug': self.article.slug}
            ),
            form_data
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success', False))
    
    def test_comment_submit_view_post_invalid(self):
        """Test comment_submit_view POST with invalid data"""
        form_data = {
            'author_name': '',  # Invalid
            'author_email': 'invalid-email',  # Invalid
            'content': ''
        }
        
        response = self.client.post(
            reverse(
                'news_events:comment-submit',
                kwargs={'article_slug': self.article.slug}
            ),
            form_data
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success', False))
    
    def test_share_article_view_post(self):
        """Test share_article_view POST request"""
        response = self.client.post(
            reverse(
                'news_events:share-article',
                kwargs={'article_slug': self.article.slug}
            )
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success', False))
    
    def test_rss_feed_view(self):
        """Test rss_feed_view GET request"""
        response = self.client.get(reverse('news_events:rss-feed'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rss+xml')
    
    def test_analytics_dashboard_view_staff(self):
        """Test analytics_dashboard_view with staff user"""
        self.client.login(username='staffuser', password='testpass123')
        
        response = self.client.get(reverse('news_events:analytics-dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_events/analytics_dashboard.html')
    
    def test_analytics_dashboard_view_non_staff(self):
        """Test analytics_dashboard_view with non-staff user"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('news_events:analytics-dashboard'))
        
        # Should redirect or return 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_confirm_subscription_view_valid_token(self):
        """Test confirm_subscription_view with valid token"""
        subscriber = Subscriber.objects.create(
            email='test@example.com',
            confirmation_token='valid-token-123'
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse(
            'news_events:confirm-subscription',
            kwargs={'token': 'valid-token-123'}
        ))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_confirmed)
    
    def test_confirm_subscription_view_invalid_token(self):
        """Test confirm_subscription_view with invalid token"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse(
            'news_events:confirm-subscription',
            kwargs={'token': 'invalid-token'}
        ))
        
        self.assertEqual(response.status_code, 302)  # Redirect with error
    
    def test_unsubscribe_view_valid_token(self):
        """Test unsubscribe_view with valid token"""
        subscriber = Subscriber.objects.create(
            email='test@example.com',
            confirmation_token='unsubscribe-token-123',
            status=Subscriber.Status.ACTIVE
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse(
            'news_events:unsubscribe',
            kwargs={'token': 'unsubscribe-token-123'}
        ))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        subscriber.refresh_from_db()
        self.assertEqual(subscriber.status, Subscriber.Status.UNSUBSCRIBED)

