"""Tests for contact app middleware."""
from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings

from apps.contact.middleware import ContactRateLimitMiddleware


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)
class ContactRateLimitMiddlewareTest(TestCase):
    """Ensure contact rate limits apply to all submission endpoints."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = ContactRateLimitMiddleware(lambda request: None)

    @patch('apps.contact.middleware.IPBlacklistManager.is_blacklisted', return_value=False)
    @patch('apps.contact.middleware.RateLimitManager.check_rate_limit')
    def test_homepage_ajax_endpoint_is_rate_limited(self, mock_check_rate_limit, _mock_blacklist):
        """Homepage contact form must use the same strict limits as /contact/."""
        mock_check_rate_limit.return_value = (False, 6, 1800)

        request = self.factory.post(
            '/ajax/contact/submit/',
            data={
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': 'This is a test message with enough content.',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        response = self.middleware(request)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 429)
        mock_check_rate_limit.assert_called()

    @patch('apps.contact.middleware.IPBlacklistManager.is_blacklisted', return_value=False)
    @patch('apps.contact.middleware.RateLimitManager.check_rate_limit')
    def test_contact_page_endpoint_is_rate_limited(self, mock_check_rate_limit, _mock_blacklist):
        """Dedicated contact page submissions remain rate limited."""
        mock_check_rate_limit.return_value = (False, 6, 1800)

        request = self.factory.post(
            '/contact/',
            data={
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': 'This is a test message with enough content.',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        response = self.middleware(request)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 429)
