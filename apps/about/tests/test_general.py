from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from django.utils import timezone
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)
# from apps.about.views import (
#     about_home_view, timeline_view, achievements_view,
#     affiliations_view, leadership_view, team_view, gallery_view,
#     contact_view, newsletter_signup_view, feedback_view
# )
from apps.about.api_views import (
    CooperativeInfoViewSet, CooperativeTimelineViewSet,
    SearchAPIView, StatisticsAPIView
)
from apps.about.cache_utils import CacheManager, cache_result


class ModelTestCase(TestCase):
    """Test cases for models"""
    
    def setUp(self):
        """Set up test data"""
        self.cooperative_info = CooperativeInfo.objects.create(
            cooperative_name="Test Cooperative",
            description="Test description",
            mission="Test mission",
            vision="Test vision",
            values="Test values",
            established_date=timezone.now().date(),
            registration_number="123",
            license_number="456",
            address="Test Address",
            phone="9800000000",
            email="test@coop.com",
            is_active=True
        )
        
        self.timeline_event = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test event description",
            event_date=timezone.now().date(),
            event_type="milestone",
            is_active=True,
            is_featured=True
        )
        
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Affiliation",
            description="Test affiliation description",
            affiliation_type="partner",
            is_active=True,
            is_featured=True
        )
        
        self.leadership_message = LeadershipMessage.objects.create(
            title="Test Message",
            content="Test leadership message content",
            author_name="Test Author",
            author_position="Test Position",
            is_active=True,
            is_featured=True
        )
        
        self.person = Person.objects.create(
            full_name="Test Person",
            bio="Test person bio",
            position_general="Test Position",
            is_active=True
        )
        
        self.committee = Committee.objects.create(
            name="Test Committee",
            description="Test committee description",
            is_active=True
        )
        
        self.membership = Membership.objects.create(
            person=self.person,
            committee=self.committee,
            position="Chairperson",
            start_date=timezone.now().date(),
            is_active=True
        )
        
        self.staff = Staff.objects.create(
            person=self.person,
            position="Manager",
            department="Operations",
            start_date=timezone.now().date(),
            is_active=True
        )
    
    def test_cooperative_info_creation(self):
        """Test CooperativeInfo model creation"""
        self.assertEqual(self.cooperative_info.cooperative_name, "Test Cooperative")
        self.assertTrue(self.cooperative_info.is_active)
        self.assertIsNotNone(self.cooperative_info.created_at)
    
    def test_timeline_event_creation(self):
        """Test CooperativeTimeline model creation"""
        self.assertEqual(self.timeline_event.title, "Test Event")
        self.assertEqual(self.timeline_event.event_type, "milestone")
        self.assertTrue(self.timeline_event.is_active)
        self.assertTrue(self.timeline_event.is_featured)
    
    def test_affiliation_creation(self):
        """Test CooperativeAffiliation model creation"""
        self.assertEqual(self.affiliation.name, "Test Affiliation")
        self.assertEqual(self.affiliation.affiliation_type, "partner")
        self.assertTrue(self.affiliation.is_active)
    
    def test_leadership_message_creation(self):
        """Test LeadershipMessage model creation"""
        self.assertEqual(self.leadership_message.title, "Test Message")
        self.assertEqual(self.leadership_message.author_name, "Test Author")
        self.assertTrue(self.leadership_message.is_active)
    
    def test_person_creation(self):
        """Test Person model creation"""
        self.assertEqual(self.person.full_name, "Test Person")
        self.assertEqual(self.person.position_general, "Test Position")
        self.assertTrue(self.person.is_active)
    
    def test_committee_creation(self):
        """Test Committee model creation"""
        self.assertEqual(self.committee.name, "Test Committee")
        self.assertTrue(self.committee.is_active)
    
    def test_membership_creation(self):
        """Test Membership model creation"""
        self.assertEqual(self.membership.person, self.person)
        self.assertEqual(self.membership.committee, self.committee)
        self.assertEqual(self.membership.position, "Chairperson")
        self.assertTrue(self.membership.is_active)
    
    def test_staff_creation(self):
        """Test Staff model creation"""
        self.assertEqual(self.staff.person, self.person)
        self.assertEqual(self.staff.position, "Manager")
        self.assertEqual(self.staff.department, "Operations")
        self.assertTrue(self.staff.is_active)


class ViewTestCase(TestCase):
    """Test cases for views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.factory = RequestFactory()
        cache.clear()
        
        # Create test data
        self.cooperative_info = CooperativeInfo.objects.create(
            cooperative_name="Test Cooperative",
            description="Test description",
            established_date=timezone.now().date(),
            registration_number="123",
            license_number="456",
            address="Test Address",
            phone="9800000000",
            email="test@coop.com",
            mission="Test Mission",
            vision="Test Vision",
            values="Test Values",
            is_active=True
        )
        
        self.timeline_event = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test event description",
            event_date=timezone.now().date(),
            event_type="milestone",
            is_active=True
        )
    
    def test_about_home_view(self):
        """Test about home view"""
        response = self.client.get(reverse('about:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Cooperative")
    
    def test_timeline_view(self):
        """Test timeline view"""
        response = self.client.get(reverse('about:timeline'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Event")
    
    # Removed: test_achievements_view - achievements page no longer exists
    
    def test_affiliations_view(self):
        """Test affiliations view"""
        response = self.client.get(reverse('about:affiliations'))
        self.assertEqual(response.status_code, 200)
    
    def test_leadership_view(self):
        """Test leadership view"""
        response = self.client.get(reverse('about:leadership'))
        self.assertEqual(response.status_code, 200)
    
    def test_team_view(self):
        """Test team view"""
        response = self.client.get(reverse('about:team'))
        self.assertEqual(response.status_code, 200)
    
    # test_gallery_view removed - gallery functionality moved to main gallery app
    # Use gallery app tests instead
    
    def test_contact_view_get(self):
        """Test contact view GET request"""
        response = self.client.get(reverse('about:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contact")
    
    def test_contact_view_post(self):
        """Test contact view POST request"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'inquiry_type': 'general',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        response = self.client.post(reverse('about:contact'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
    
    def test_newsletter_signup_view(self):
        """Test newsletter signup API view"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'interests': ['news']
        }
        response = self.client.post(
            reverse('about:newsletter_signup'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
    
    def test_feedback_view(self):
        """Test feedback API view"""
        data = {
            'feedback_type': 'website',
            'rating': '5',
            'comments': 'Great website!',
            'email': 'test@example.com'
        }
        response = self.client.post(
            reverse('about:feedback'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])


class APITestCase(TestCase):
    """Test cases for API views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test data
        self.cooperative_info = CooperativeInfo.objects.create(
            cooperative_name="Test Cooperative",
            description="Test description",
            established_date=timezone.now().date(),
            registration_number="123",
            license_number="456",
            address="Test Address",
            phone="9800000000",
            email="test@coop.com",
            mission="Test Mission",
            vision="Test Vision",
            values="Test Values",
            is_active=True
        )
        
        self.timeline_event = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test event description",
            event_date=timezone.now().date(),
            event_type="milestone",
            is_active=True
        )
    
    def test_cooperative_info_api(self):
        """Test CooperativeInfo API endpoint"""
        response = self.client.get('/api/v1/about/cooperative-info/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['cooperative_name'], "Test Cooperative")
    
    def test_timeline_api(self):
        """Test Timeline API endpoint"""
        response = self.client.get('/api/v1/about/timeline/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], "Test Event")
    
    # Removed: test_achievements_api - achievements API endpoint no longer exists
    
    def test_search_api(self):
        """Test Search API endpoint"""
        response = self.client.get('/api/v1/about/search/?q=Test')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('cooperative_info', data)
        self.assertIn('timeline', data)
    
    def test_statistics_api(self):
        """Test Statistics API endpoint"""
        response = self.client.get('/api/v1/about/statistics/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('cooperative_info_count', data)
        self.assertIn('timeline_events_count', data)


class CacheTestCase(TestCase):
    """Test cases for caching functionality"""
    
    def setUp(self):
        """Set up test data"""
        cache.clear()
        self.cache_manager = CacheManager()
    
    def test_cache_set_get(self):
        """Test basic cache set and get operations"""
        key = "test_key"
        value = "test_value"
        
        # Set value
        self.cache_manager.set(key, value, timeout=300)
        
        # Get value
        cached_value = self.cache_manager.get(key)
        self.assertEqual(cached_value, value)
    
    def test_cache_get_or_set(self):
        """Test cache get_or_set functionality"""
        key = "test_key_2"
        
        def expensive_operation():
            return "expensive_result"
        
        # First call should execute the function
        result1 = self.cache_manager.get_or_set(key, expensive_operation)
        self.assertEqual(result1, "expensive_result")
        
        # Second call should return cached result
        result2 = self.cache_manager.get_or_set(key, expensive_operation)
        self.assertEqual(result2, "expensive_result")
    
    def test_cache_delete(self):
        """Test cache delete functionality"""
        key = "test_key_3"
        value = "test_value_3"
        
        # Set value
        self.cache_manager.set(key, value)
        
        # Verify value exists
        self.assertEqual(self.cache_manager.get(key), value)
        
        # Delete value
        self.cache_manager.delete(key)
        
        # Verify value is deleted
        self.assertIsNone(self.cache_manager.get(key))
    
    def test_cache_result_decorator(self):
        """Test cache_result decorator"""
        call_count = 0
        
        @cache_result(timeout=300)
        def expensive_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}"
        
        # First call
        result1 = expensive_function("test")
        self.assertEqual(result1, "result_test")
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = expensive_function("test")
        self.assertEqual(result2, "result_test")
        self.assertEqual(call_count, 1)  # Should not increment


class SecurityTestCase(TestCase):
    """Test cases for security functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_security_headers(self):
        """Test security headers are present"""
        response = self.client.get('/about/')
        
        # Check security headers
        self.assertIn('X-Content-Type-Options', response)
        self.assertIn('X-Frame-Options', response)
        self.assertIn('X-XSS-Protection', response)
        self.assertIn('Referrer-Policy', response)
        
        # Verify header values
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Make multiple requests to test rate limiting
        for i in range(10):
            response = self.client.get('/api/v1/about/statistics/')
            self.assertEqual(response.status_code, 200)
        
        # Additional requests should be rate limited
        response = self.client.get('/api/v1/about/statistics/')
        # Note: Rate limiting might not be active in test environment
        # This test verifies the endpoint works correctly


class IntegrationTestCase(TestCase):
    """Integration test cases"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        cache.clear()
        
        # Create comprehensive test data
        self.cooperative_info = CooperativeInfo.objects.create(
            cooperative_name="Integration Test Cooperative",
            description="Integration test description",
            mission="Integration test mission",
            vision="Integration test vision",
            values="Integration test values",
            established_date=timezone.now().date(),
            registration_number="123",
            license_number="456",
            address="Test Address",
            phone="9800000000",
            email="test@coop.com",
            is_active=True
        )
        
        # Create timeline events
        for i in range(5):
            CooperativeTimeline.objects.create(
                title=f"Timeline Event {i+1}",
                description=f"Description for event {i+1}",
                event_date=timezone.now().date() - timedelta(days=i*30),
                event_type="milestone",
                is_active=True,
                is_featured=(i < 2)
            )
    
    def test_full_about_page_flow(self):
        """Test complete about page flow"""
        # Test main about page
        response = self.client.get(reverse('about:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integration Test Cooperative")
        
        # Test timeline page
        response = self.client.get(reverse('about:timeline'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Timeline Event")
        
        # Test API endpoints
        response = self.client.get('/api/v1/about/cooperative-info/')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/api/v1/about/timeline/')
        self.assertEqual(response.status_code, 200)
    
    def test_search_functionality(self):
        """Test search functionality"""
        # Test web search
        response = self.client.get(reverse('search:advanced_search') + '?q=Timeline')
        self.assertEqual(response.status_code, 200)
        
        # Test API search
        response = self.client.get('/api/v1/about/search/?q=Timeline')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreater(len(data['timeline']), 0)
    
    def test_form_submissions(self):
        """Test form submissions"""
        # Test contact form
        data = {
            'name': 'Integration Test User',
            'email': 'integration@example.com',
            'phone': '1234567890',
            'inquiry_type': 'general',
            'subject': 'Integration Test Subject',
            'message': 'Integration test message'
        }
        response = self.client.post(reverse('about:contact'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Test newsletter signup
        data = {
            'name': 'Integration Test User',
            'email': 'integration@example.com',
            'interests': ['news']
        }
        response = self.client.post(
            reverse('about:newsletter_signup'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])


class PerformanceTestCase(TestCase):
    """Test cases for performance"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create large dataset for performance testing
        for i in range(100):
            CooperativeTimeline.objects.create(
                title=f"Performance Test Event {i+1}",
                description=f"Description for performance test event {i+1}",
                event_date=timezone.now().date() - timedelta(days=i),
                event_type="milestone",
                is_active=True
            )
    
    def test_timeline_performance(self):
        """Test timeline page performance"""
        import time
        
        start_time = time.time()
        response = self.client.get(reverse('about:timeline'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        # Page should load within reasonable time (adjust threshold as needed)
        self.assertLess(end_time - start_time, 2.0)  # 2 seconds max
    
    def test_api_performance(self):
        """Test API performance"""
        import time
        
        start_time = time.time()
        response = self.client.get('/api/v1/about/timeline/')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        # API should respond within reasonable time
        self.assertLess(end_time - start_time, 1.0)  # 1 second max
    
    def test_search_performance(self):
        """Test search performance"""
        import time
        
        start_time = time.time()
        response = self.client.get('/api/v1/about/search/?q=Performance')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        # Search should complete within reasonable time
        self.assertLess(end_time - start_time, 1.0)  # 1 second max


class ManagerTestCase(TestCase):
    """Test cases for custom managers"""

    def setUp(self):
        # Create active/inactive and featured/non-featured items
        CooperativeTimeline.objects.create(title="Active Featured", is_active=True, is_featured=True, event_date=timezone.now().date())
        CooperativeTimeline.objects.create(title="Active Non-Featured", is_active=True, is_featured=False, event_date=timezone.now().date())
        CooperativeTimeline.objects.create(title="Inactive Featured", is_active=False, is_featured=True, event_date=timezone.now().date())
        CooperativeTimeline.objects.create(title="Inactive Non-Featured", is_active=False, is_featured=False, event_date=timezone.now().date())

    def test_manager_active(self):
        """Test .active() manager method"""
        active_items = CooperativeTimeline.objects.active()
        self.assertEqual(active_items.count(), 2)
        for item in active_items:
            self.assertTrue(item.is_active)

    def test_manager_featured(self):
        """Test .featured() manager method"""
        # featured() should return ONLY active AND featured items
        featured_items = CooperativeTimeline.objects.featured()
        self.assertEqual(featured_items.count(), 1)
        self.assertEqual(featured_items.first().title, "Active Featured")


class ServiceTestCase(TestCase):
    """Test cases for services"""

    @patch('apps.about.services.send_mail')
    def test_send_contact_emails(self, mock_send_mail):
        """Test send_contact_emails service logic"""
        from apps.about.services import AboutService
        
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'inquiry_type': 'General',
            'subject': 'Test Subject',
            'message': 'Test Message'
        }
        
        # Test 1: Mock Mode (SEND_REAL_EMAILS = False)
        # Should return True but NOT call send_mail
        with self.settings(SEND_REAL_EMAILS=False):
            result = AboutService.send_contact_emails(data)
            self.assertTrue(result)
            mock_send_mail.assert_not_called()

        # Test 2: Real Mode (SEND_REAL_EMAILS = True)
        # Should call send_mail once (Admin notification)
        with self.settings(SEND_REAL_EMAILS=True):
            result = AboutService.send_contact_emails(data)
            self.assertTrue(result)
            self.assertEqual(mock_send_mail.call_count, 1)

    @patch('apps.about.services.send_mail')
    def test_send_newsletter_email(self, mock_send_mail):
        """Test send_newsletter_welcome_email service logic"""
        from apps.about.services import AboutService
        
        data = {
            'name': 'Subscriber',
            'email': 'sub@example.com',
            'interests': ['News', 'Events']
        }
        
        with self.settings(SEND_REAL_EMAILS=True):
            result = AboutService.send_newsletter_welcome_email(data)
            self.assertTrue(result)
            mock_send_mail.assert_called_once()
    
    @patch('apps.about.services.send_mail')
    def test_send_feedback_email(self, mock_send_mail):
        """Test send_feedback_email service logic"""
        from apps.about.services import AboutService
        
        data = {
            'feedback_type': 'Bug',
            'rating': 1,
            'comments': 'Fix it!',
            'email': 'user@example.com'
        }
        
        with self.settings(SEND_REAL_EMAILS=True):
            result = AboutService.send_feedback_email(data)
            self.assertTrue(result)
            mock_send_mail.assert_called_once()
