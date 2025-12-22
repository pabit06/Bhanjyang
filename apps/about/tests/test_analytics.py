"""
Tests for about app analytics module
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from apps.about.analytics import (
    AnalyticsTracker, AnalyticsAPI, AnalyticsMiddleware,
    UserSession, PageView, UserEvent, UserDevice, UserLocation, AnalyticsSummary
)


class AnalyticsTrackerTest(TestCase):
    """Test AnalyticsTracker"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.request = self.factory.get('/')
        self.request.session = {}
        self.request.session.create()
        self.request.user = self.user
        self.request.META['HTTP_USER_AGENT'] = 'Test Agent'
        self.request.META['REMOTE_ADDR'] = '127.0.0.1'
    
    def test_get_or_create_session(self):
        """Test getting or creating session"""
        tracker = AnalyticsTracker(self.request)
        self.assertIsNotNone(tracker.session_id)
        self.assertIsInstance(tracker.session_id, UserSession)
    
    def test_get_client_ip(self):
        """Test getting client IP"""
        tracker = AnalyticsTracker(self.request)
        ip = tracker.get_client_ip()
        self.assertEqual(ip, '127.0.0.1')
    
    def test_get_client_ip_with_proxy(self):
        """Test getting client IP with proxy"""
        self.request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 127.0.0.1'
        tracker = AnalyticsTracker(self.request)
        ip = tracker.get_client_ip()
        self.assertEqual(ip, '192.168.1.1')
    
    def test_track_page_view(self):
        """Test tracking page view"""
        tracker = AnalyticsTracker(self.request)
        initial_count = tracker.session_id.page_views
        tracker.track_page_view('/test/', 'Test Page')
        tracker.session_id.refresh_from_db()
        self.assertEqual(tracker.session_id.page_views, initial_count + 1)
        self.assertTrue(PageView.objects.filter(path='/test/').exists())
    
    def test_track_event(self):
        """Test tracking user event"""
        tracker = AnalyticsTracker(self.request)
        tracker.track_event('click', element_id='button1', element_text='Submit')
        self.assertTrue(UserEvent.objects.filter(
            event_type='click',
            element_id='button1'
        ).exists())
    
    def test_track_device_info(self):
        """Test tracking device info"""
        tracker = AnalyticsTracker(self.request)
        device_data = {
            'device_type': 'desktop',
            'browser': 'Chrome',
            'browser_version': '100',
            'operating_system': 'Windows',
            'screen_resolution': '1920x1080',
            'viewport_size': '1920x1080',
            'is_mobile': False,
            'is_tablet': False,
            'is_desktop': True
        }
        tracker.track_device_info(device_data)
        self.assertTrue(UserDevice.objects.filter(
            session=tracker.session_id,
            device_type='desktop'
        ).exists())
    
    def test_track_location(self):
        """Test tracking location"""
        tracker = AnalyticsTracker(self.request)
        location_data = {
            'country': 'Nepal',
            'country_code': 'NP',
            'region': 'Bagmati',
            'city': 'Kathmandu',
            'latitude': 27.7172,
            'longitude': 85.3240
        }
        tracker.track_location(location_data)
        self.assertTrue(UserLocation.objects.filter(
            session=tracker.session_id,
            country='Nepal'
        ).exists())
    
    def test_end_session(self):
        """Test ending session"""
        tracker = AnalyticsTracker(self.request)
        tracker.end_session()
        tracker.session_id.refresh_from_db()
        self.assertIsNotNone(tracker.session_id.end_time)
        self.assertFalse(tracker.session_id.is_active)


class AnalyticsAPITest(TestCase):
    """Test AnalyticsAPI"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = UserSession.objects.create(
            session_id='test_session',
            user=self.user,
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now(),
            duration=timedelta(hours=1),
            page_views=5
        )
        PageView.objects.create(
            session=self.session,
            url='http://test.com/page1',
            path='/page1',
            title='Page 1',
            timestamp=timezone.now()
        )
        UserDevice.objects.create(
            session=self.session,
            device_type='desktop',
            browser='Chrome',
            browser_version='100',
            operating_system='Windows',
            screen_resolution='1920x1080',
            viewport_size='1920x1080',
            is_desktop=True
        )
        UserLocation.objects.create(
            session=self.session,
            country='Nepal',
            country_code='NP',
            city='Kathmandu'
        )
        UserEvent.objects.create(
            session=self.session,
            event_type='click',
            url='http://test.com',
            timestamp=timezone.now()
        )
    
    def test_get_session_stats(self):
        """Test getting session statistics"""
        stats = AnalyticsAPI.get_session_stats(days=30)
        self.assertIn('total_sessions', stats)
        self.assertIn('unique_users', stats)
        self.assertIn('average_duration', stats)
        self.assertIn('total_page_views', stats)
        self.assertGreaterEqual(stats['total_sessions'], 1)
    
    def test_get_top_pages(self):
        """Test getting top pages"""
        pages = AnalyticsAPI.get_top_pages(days=30, limit=10)
        self.assertIsNotNone(pages)
        self.assertGreaterEqual(len(list(pages)), 1)
    
    def test_get_device_breakdown(self):
        """Test getting device breakdown"""
        breakdown = AnalyticsAPI.get_device_breakdown(days=30)
        self.assertIn('desktop', breakdown)
        self.assertIn('mobile', breakdown)
        self.assertIn('tablet', breakdown)
        self.assertGreaterEqual(breakdown['desktop'], 1)
    
    def test_get_browser_breakdown(self):
        """Test getting browser breakdown"""
        breakdown = list(AnalyticsAPI.get_browser_breakdown(days=30))
        self.assertGreaterEqual(len(breakdown), 1)
        self.assertIn('browser', breakdown[0])
        self.assertIn('count', breakdown[0])
    
    def test_get_country_breakdown(self):
        """Test getting country breakdown"""
        breakdown = list(AnalyticsAPI.get_country_breakdown(days=30))
        self.assertGreaterEqual(len(breakdown), 1)
        self.assertIn('country', breakdown[0])
        self.assertIn('count', breakdown[0])
    
    def test_get_event_stats(self):
        """Test getting event statistics"""
        stats = list(AnalyticsAPI.get_event_stats(days=30))
        self.assertGreaterEqual(len(stats), 1)
        self.assertIn('event_type', stats[0])
        self.assertIn('count', stats[0])
    
    def test_generate_daily_summary(self):
        """Test generating daily summary"""
        summary = AnalyticsAPI.generate_daily_summary()
        self.assertIsInstance(summary, AnalyticsSummary)
        self.assertGreaterEqual(summary.total_sessions, 1)
        self.assertIn('top_pages', summary.top_pages)
        self.assertIn('device_breakdown', summary.device_breakdown)
    
    def test_generate_daily_summary_specific_date(self):
        """Test generating daily summary for specific date"""
        date = timezone.now().date()
        summary = AnalyticsAPI.generate_daily_summary(date=date)
        self.assertIsInstance(summary, AnalyticsSummary)
        self.assertEqual(summary.date, date)


class AnalyticsMiddlewareTest(TestCase):
    """Test AnalyticsMiddleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda request: None
    
    def test_should_skip_tracking_admin(self):
        """Test skipping tracking for admin paths"""
        middleware = AnalyticsMiddleware(self.get_response)
        request = self.factory.get('/admin/')
        self.assertTrue(middleware.should_skip_tracking(request))
    
    def test_should_skip_tracking_static(self):
        """Test skipping tracking for static files"""
        middleware = AnalyticsMiddleware(self.get_response)
        request = self.factory.get('/static/css/style.css')
        self.assertTrue(middleware.should_skip_tracking(request))
    
    def test_should_skip_tracking_media(self):
        """Test skipping tracking for media files"""
        middleware = AnalyticsMiddleware(self.get_response)
        request = self.factory.get('/media/images/photo.jpg')
        self.assertTrue(middleware.should_skip_tracking(request))
    
    def test_should_not_skip_tracking_normal(self):
        """Test not skipping tracking for normal paths"""
        middleware = AnalyticsMiddleware(self.get_response)
        request = self.factory.get('/about/')
        self.assertFalse(middleware.should_skip_tracking(request))


class AnalyticsModelsTest(TestCase):
    """Test analytics models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = UserSession.objects.create(
            session_id='test_session',
            user=self.user,
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
    
    def test_user_session_str(self):
        """Test UserSession string representation"""
        self.assertIn('test_session', str(self.session))
    
    def test_page_view_str(self):
        """Test PageView string representation"""
        page_view = PageView.objects.create(
            session=self.session,
            url='http://test.com',
            path='/test',
            timestamp=timezone.now()
        )
        self.assertIn('/test', str(page_view))
    
    def test_user_event_str(self):
        """Test UserEvent string representation"""
        event = UserEvent.objects.create(
            session=self.session,
            event_type='click',
            url='http://test.com',
            timestamp=timezone.now()
        )
        self.assertIn('click', str(event))
    
    def test_user_device_str(self):
        """Test UserDevice string representation"""
        device = UserDevice.objects.create(
            session=self.session,
            device_type='desktop',
            browser='Chrome'
        )
        self.assertIn('desktop', str(device))
        self.assertIn('Chrome', str(device))
    
    def test_user_location_str(self):
        """Test UserLocation string representation"""
        location = UserLocation.objects.create(
            session=self.session,
            country='Nepal',
            city='Kathmandu'
        )
        self.assertIn('Kathmandu', str(location))
        self.assertIn('Nepal', str(location))
    
    def test_analytics_summary_str(self):
        """Test AnalyticsSummary string representation"""
        summary = AnalyticsSummary.objects.create(
            date=timezone.now().date(),
            total_sessions=10,
            unique_visitors=5
        )
        self.assertIn(str(summary.date), str(summary))

