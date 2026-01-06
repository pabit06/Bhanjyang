from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
from apps.news_events.views import (
    AnalyticsDashboardView, SubscriptionConfirmationView, UnsubscribeView, RSSFeedView, SubscriptionView
)
from django.contrib.auth.models import User, AnonymousUser
from apps.news_events.models import Subscriber

class NewsEventsRefactorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='staff', password='password', is_staff=True)
        self.subscriber = Subscriber.objects.create(email='test@example.com', confirmation_token='valid-token')

    def test_analytics_dashboard_access(self):
        # Requires staff
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('news_events:analytics-dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_analytics_dashboard_forbidden(self):
        self.client.logout()
        response = self.client.get(reverse('news_events:analytics-dashboard'))
        # Should redirect to login or 403?
        # @staff_member_required usually redirects to admin login.
        self.assertEqual(response.status_code, 302)

    def test_confirm_subscription(self):
        self.client.login(username='staff', password='password') # View requires login?
        # My refactor added LoginRequiredMixin to SubscriptionConfirmationView?
        # Original was @login_required? Yes (line 335 in original).
        response = self.client.get(reverse('news_events:confirm-subscription', args=['valid-token']))
        self.assertEqual(response.status_code, 302) # Redirects to home
        self.subscriber.refresh_from_db()
        self.assertTrue(self.subscriber.is_confirmed)

    def test_unsubscribe(self):
        self.client.login(username='staff', password='password') # View requires login
        response = self.client.get(reverse('news_events:unsubscribe', args=['valid-token']))
        self.assertEqual(response.status_code, 302) # Redirects to home
        self.subscriber.refresh_from_db()
        self.assertEqual(self.subscriber.status, Subscriber.Status.UNSUBSCRIBED)

    def test_rss_feed(self):
        response = self.client.get(reverse('news_events:rss-feed'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rss+xml; charset=utf-8')

    @patch('apps.news_events.views.InteractionService')
    def test_subscription_view(self, MockService):
        MockService.handle_subscription.return_value = (True, 'Success')
        from apps.news_events.models import Category
        category = Category.objects.create(name='Test Category', slug='test-category')
        
        response = self.client.post(reverse('news_events:subscribe'), {
            'email': 'new@example.com',
            'frequency': 'daily',
            'categories': [category.id]
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

