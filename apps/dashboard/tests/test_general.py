from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta

from .models import PageView, ErrorLog, PerformanceMetric
from .services import DashboardAnalyticsService
from .views import DashboardView

User = get_user_model()

class DashboardAnalyticsServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', password='password', is_staff=True)
        # Create dummy data
        PageView.objects.create(
            page_url='/', page_title='Home', load_time=100.0, 
            is_mobile=False, browser='Chrome'
        )
        PageView.objects.create(
            page_url='/about', page_title='About', load_time=200.0, 
            is_mobile=True, browser='Firefox'
        )
        ErrorLog.objects.create(
            error_type='500', error_message='Test Error', resolved=False
        )

    def test_get_dashboard_summary(self):
        summary = DashboardAnalyticsService.get_dashboard_summary()
        
        # Check structure
        self.assertIn('performance', summary)
        self.assertIn('views', summary)
        self.assertIn('errors', summary)
        self.assertIn('pages', summary)
        self.assertIn('tech', summary)
        
        # Check values
        self.assertEqual(summary['views']['week'], 2)
        self.assertEqual(summary['errors']['week'], 1)
        self.assertEqual(summary['performance']['week'], 150.0) # (100+200)/2

    def test_record_page_view(self):
        data = {
            'page_url': '/new-page',
            'load_time': 300,
            'is_mobile': True
        }
        meta = {
            'HTTP_USER_AGENT': 'TestAgent',
            'REMOTE_ADDR': '127.0.0.1',
            'user': self.user
        }
        
        success = DashboardAnalyticsService.record_page_view(data, meta)
        self.assertTrue(success)
        self.assertTrue(PageView.objects.filter(page_url='/new-page').exists())

class DashboardViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='staff', password='pass', is_staff=True)

    def test_dashboard_view_access(self):
        request = self.factory.get('/dashboard/')
        request.user = self.user
        response = DashboardView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        # Check if context has our data
        # Note: TemplateResponse might not render context immediately in unit test unless using Client
        # But we can check response.context_data if we use TemplateView directly? 
        # Actually simplest is just Client test
        
    def test_client_access(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_views_week', response.context)
