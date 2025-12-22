"""
Tests for about app API views
"""
from django.test import TestCase, APIClient
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)


class AboutAPITestCase(APITestCase):
    """Base test case for API views"""
    
    def setUp(self):
        self.client = APIClient()
        self.cooperative = CooperativeInfo.objects.create(
            cooperative_name="Test Cooperative",
            description="Test description",
            mission="Test mission",
            vision="Test vision",
            is_active=True,
            is_featured=True
        )
        self.timeline = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test description",
            event_date=timezone.now().date(),
            event_type="milestone",
            is_active=True,
            is_featured=True
        )
        self.achievement = CooperativeAchievement.objects.create(
            title="Test Achievement",
            description="Test description",
            achievement_type="award",
            is_active=True,
            is_featured=True
        )
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Affiliation",
            description="Test description",
            is_active=True,
            is_featured=True
        )
        self.message = LeadershipMessage.objects.create(
            title="Test Message",
            content="Test content",
            author_name="Test Author",
            is_active=True,
            is_featured=True
        )
        self.person = Person.objects.create(
            full_name="Test Person",
            bio="Test bio",
            is_active=True
        )
        self.committee = Committee.objects.create(
            name="Test Committee",
            is_active=True
        )
        self.membership = Membership.objects.create(
            person=self.person,
            committee=self.committee,
            position="Member",
            is_active=True
        )
        self.staff = Staff.objects.create(
            person=self.person,
            position="Manager",
            department="IT",
            is_active=True
        )


class CooperativeInfoViewSetTest(AboutAPITestCase):
    """Test CooperativeInfoViewSet"""
    
    def test_list_cooperative_info(self):
        """Test listing cooperative info"""
        url = reverse('about_api:cooperative-info-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_retrieve_cooperative_info(self):
        """Test retrieving single cooperative info"""
        url = reverse('about_api:cooperative-info-detail', args=[self.cooperative.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cooperative_name'], self.cooperative.cooperative_name)
    
    def test_featured_endpoint(self):
        """Test featured endpoint"""
        url = reverse('about_api:cooperative-info-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('cooperative_name', response.data)
    
    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        CooperativeStatistic.objects.create(
            title="Test Stat",
            value=100,
            is_active=True
        )
        url = reverse('about_api:cooperative-info-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_search_functionality(self):
        """Test search functionality"""
        url = reverse('about_api:cooperative-info-list')
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_ordering(self):
        """Test ordering"""
        url = reverse('about_api:cooperative-info-list')
        response = self.client.get(url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_pagination(self):
        """Test pagination"""
        # Create multiple items
        for i in range(25):
            CooperativeInfo.objects.create(
                cooperative_name=f"Coop {i}",
                is_active=True
            )
        url = reverse('about_api:cooperative-info-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)


class CooperativeTimelineViewSetTest(AboutAPITestCase):
    """Test CooperativeTimelineViewSet"""
    
    def test_list_timeline(self):
        """Test listing timeline events"""
        url = reverse('about_api:timeline-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_retrieve_timeline(self):
        """Test retrieving single timeline event"""
        url = reverse('about_api:timeline-detail', args=[self.timeline.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.timeline.title)
    
    def test_featured_endpoint(self):
        """Test featured endpoint"""
        url = reverse('about_api:timeline-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_recent_endpoint(self):
        """Test recent endpoint"""
        url = reverse('about_api:timeline-recent')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_filter_by_event_type(self):
        """Test filtering by event type"""
        url = reverse('about_api:timeline-list')
        response = self.client.get(url, {'event_type': 'milestone'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)


class CooperativeAchievementViewSetTest(AboutAPITestCase):
    """Test CooperativeAchievementViewSet"""
    
    def test_list_achievements(self):
        """Test listing achievements"""
        url = reverse('about_api:achievements-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_retrieve_achievement(self):
        """Test retrieving single achievement"""
        url = reverse('about_api:achievements-detail', args=[self.achievement.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.achievement.title)
    
    def test_featured_endpoint(self):
        """Test featured endpoint"""
        url = reverse('about_api:achievements-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_by_type_endpoint(self):
        """Test by type endpoint"""
        url = reverse('about_api:achievements-by-type')
        response = self.client.get(url, {'type': 'award'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_by_type_endpoint_missing_param(self):
        """Test by type endpoint without parameter"""
        url = reverse('about_api:achievements-by-type')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CooperativeAffiliationViewSetTest(AboutAPITestCase):
    """Test CooperativeAffiliationViewSet"""
    
    def test_list_affiliations(self):
        """Test listing affiliations"""
        url = reverse('about_api:affiliations-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_featured_endpoint(self):
        """Test featured endpoint"""
        url = reverse('about_api:affiliations-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class LeadershipMessageViewSetTest(AboutAPITestCase):
    """Test LeadershipMessageViewSet"""
    
    def test_list_messages(self):
        """Test listing leadership messages"""
        url = reverse('about_api:leadership-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_featured_endpoint(self):
        """Test featured endpoint"""
        url = reverse('about_api:leadership-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class PersonViewSetTest(AboutAPITestCase):
    """Test PersonViewSet"""
    
    def test_list_persons(self):
        """Test listing persons"""
        url = reverse('about_api:team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_current_team_endpoint(self):
        """Test current team endpoint"""
        url = reverse('about_api:team-current-team')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_past_team_endpoint(self):
        """Test past team endpoint"""
        url = reverse('about_api:team-past-team')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_by_position_endpoint(self):
        """Test by position endpoint"""
        url = reverse('about_api:team-by-position')
        response = self.client.get(url, {'position': 'Manager'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_by_position_endpoint_missing_param(self):
        """Test by position endpoint without parameter"""
        url = reverse('about_api:team-by-position')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommitteeViewSetTest(AboutAPITestCase):
    """Test CommitteeViewSet"""
    
    def test_list_committees(self):
        """Test listing committees"""
        url = reverse('about_api:committees-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_members_endpoint(self):
        """Test members endpoint"""
        url = reverse('about_api:committees-members', args=[self.committee.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class StaffViewSetTest(AboutAPITestCase):
    """Test StaffViewSet"""
    
    def test_list_staff(self):
        """Test listing staff"""
        url = reverse('about_api:staff-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_by_department_endpoint(self):
        """Test by department endpoint"""
        url = reverse('about_api:staff-by-department')
        response = self.client.get(url, {'department': 'IT'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_by_department_endpoint_missing_param(self):
        """Test by department endpoint without parameter"""
        url = reverse('about_api:staff-by-department')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SearchAPIViewTest(AboutAPITestCase):
    """Test SearchAPIView"""
    
    def test_search_all_content(self):
        """Test searching all content"""
        url = reverse('about_api:search')
        response = self.client.get(url, {'q': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
        self.assertIn('cooperative_info', response.data)
        self.assertIn('timeline', response.data)
        self.assertIn('achievements', response.data)
    
    def test_search_missing_query(self):
        """Test search without query parameter"""
        url = reverse('about_api:search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_empty_query(self):
        """Test search with empty query"""
        url = reverse('about_api:search')
        response = self.client.get(url, {'q': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_caching(self):
        """Test search result caching"""
        url = reverse('about_api:search')
        # First request
        response1 = self.client.get(url, {'q': 'Test'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Second request should use cache
        response2 = self.client.get(url, {'q': 'Test'})
        self.assertEqual(response2.status_code, status.HTTP_200_OK)


class StatisticsAPIViewTest(AboutAPITestCase):
    """Test StatisticsAPIView"""
    
    def test_get_statistics(self):
        """Test getting site statistics"""
        url = reverse('about_api:statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('cooperative_info_count', response.data)
        self.assertIn('timeline_events_count', response.data)
        self.assertIn('achievements_count', response.data)
        self.assertIn('last_updated', response.data)
    
    def test_statistics_caching(self):
        """Test statistics caching"""
        url = reverse('about_api:statistics')
        # First request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Second request should use cache
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)


class ContactAPIViewTest(AboutAPITestCase):
    """Test ContactAPIView"""
    
    def test_post_contact_form(self):
        """Test posting contact form"""
        url = reverse('about_api:contact')
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('submission_id', response.data)
    
    def test_post_contact_form_error(self):
        """Test contact form with error"""
        url = reverse('about_api:contact')
        # Missing required fields to trigger error
        with self.settings(DEBUG=False):
            response = self.client.post(url, {}, format='json')
            # Should handle error gracefully
            self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])


class NewsletterAPIViewTest(AboutAPITestCase):
    """Test NewsletterAPIView"""
    
    def test_post_newsletter_subscription(self):
        """Test posting newsletter subscription"""
        url = reverse('about_api:newsletter')
        data = {
            'email': 'test@example.com',
            'name': 'Test User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('subscriber_id', response.data)
    
    def test_post_newsletter_missing_email(self):
        """Test newsletter subscription without email"""
        url = reverse('about_api:newsletter')
        data = {'name': 'Test User'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

