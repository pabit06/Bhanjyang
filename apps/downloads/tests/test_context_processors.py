"""
Tests for downloads app context processors
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from apps.downloads.context_processors import admin_stats
from apps.downloads.models import DownloadableFile
from apps.news_events.models import NewsArticle


class ContextProcessorsTest(TestCase):
    """Test context processors"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
    
    def test_admin_stats_admin_path(self):
        """Test admin_stats for admin path"""
        request = self.factory.get('/admin/')
        request.user = self.admin_user
        context = admin_stats(request)
        self.assertIsInstance(context, dict)
        self.assertIn('downloads_count', context)
        self.assertIn('updates_count', context)
        self.assertIn('team_count', context)
        self.assertIn('services_count', context)
    
    def test_admin_stats_non_admin_path(self):
        """Test admin_stats for non-admin path"""
        request = self.factory.get('/about/')
        request.user = self.admin_user
        context = admin_stats(request)
        self.assertEqual(context, {})
    
    def test_admin_stats_with_downloads(self):
        """Test admin_stats with downloads"""
        DownloadableFile.objects.create(
            title="Test File",
            file='test.pdf',
            is_active=True
        )
        request = self.factory.get('/admin/')
        request.user = self.admin_user
        context = admin_stats(request)
        self.assertEqual(context['downloads_count'], 1)
    
    def test_admin_stats_with_news_articles(self):
        """Test admin_stats with news articles"""
        NewsArticle.objects.create(
            title="Test Article",
            content="Test content",
            status='PB'
        )
        request = self.factory.get('/admin/')
        request.user = self.admin_user
        context = admin_stats(request)
        self.assertEqual(context['updates_count'], 1)
    
    def test_admin_stats_error_handling(self):
        """Test admin_stats error handling"""
        # Should handle missing models gracefully
        request = self.factory.get('/admin/')
        request.user = self.admin_user
        context = admin_stats(request)
        # Should return dict with default values
        self.assertIsInstance(context, dict)
        self.assertIn('downloads_count', context)

