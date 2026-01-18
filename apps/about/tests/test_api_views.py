"""
Tests for about app API views
"""
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline,
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
            established_date='2020-01-01',
            registration_number='123',
            license_number='456',
            address='Kathmandu',
            phone='9800000000',
            email='info@example.com',
            status='PB'
        )
        self.timeline = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test description",
            event_date=timezone.now().date(),
            event_type="milestone",
            is_active=True,
            is_featured=True,
            status='PB'
        )
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Affiliation",
            description="Test description",
            is_active=True,
            is_featured=True,
            status='PB'
        )
        self.message = LeadershipMessage.objects.create(
            title="Test Message",
            content="Test content",
            author_name="Test Author",
            is_active=True,
            is_featured=True,
            status='PB'
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
    
    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        CooperativeStatistic.objects.create(
            title="Test Stat",
            value=100,
            is_active=True,
            status='PB'
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
                is_active=True,
                established_date='2020-01-01',
                registration_number=f'REG{i}',
                license_number=f'LIC{i}',
                address='Kathmandu',
                phone='9800000000',
                email='info@example.com',
                status='PB'
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


# ContactAPIViewTest removed - ContactAPIView has been removed, use contact app's API instead

# NewsletterAPIViewTest removed - NewsletterAPIView no longer needed


# ============================================================================
# Edge Case Tests
# ============================================================================

class EdgeCaseTests(AboutAPITestCase):
    """Test edge cases and error scenarios for API views"""
    
    def test_cooperative_info_not_found(self):
        """Test retrieving non-existent cooperative info"""
        url = reverse('about_api:cooperative-info-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_timeline_not_found(self):
        """Test retrieving non-existent timeline event"""
        url = reverse('about_api:timeline-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_affiliation_not_found(self):
        """Test retrieving non-existent affiliation"""
        url = reverse('about_api:affiliations-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_leadership_message_not_found(self):
        """Test retrieving non-existent leadership message"""
        url = reverse('about_api:leadership-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_person_not_found(self):
        """Test retrieving non-existent person"""
        url = reverse('about_api:team-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_committee_not_found(self):
        """Test retrieving non-existent committee"""
        url = reverse('about_api:committees-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_staff_not_found(self):
        """Test retrieving non-existent staff"""
        url = reverse('about_api:staff-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_committee_members_empty_committee(self):
        """Test getting members of committee with no members"""
        empty_committee = Committee.objects.create(
            name="Empty Committee",
            is_active=True
        )
        url = reverse('about_api:committees-members', args=[empty_committee.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_featured_timeline_empty(self):
        """Test featured timeline endpoint with no featured events"""
        # Deactivate the featured timeline
        self.timeline.is_featured = False
        self.timeline.save()
        url = reverse('about_api:timeline-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_featured_affiliations_empty(self):
        """Test featured affiliations endpoint with no featured affiliations"""
        # Deactivate the featured affiliation
        self.affiliation.is_featured = False
        self.affiliation.save()
        url = reverse('about_api:affiliations-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_featured_leadership_empty(self):
        """Test featured leadership endpoint with no featured messages"""
        # Deactivate the featured message
        self.message.is_featured = False
        self.message.save()
        url = reverse('about_api:leadership-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_current_team_empty(self):
        """Test current team endpoint with no current members"""
        # Make membership inactive or add end date
        self.membership.end_date = timezone.now().date()
        self.membership.save()
        url = reverse('about_api:team-current-team')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty or not include this member
        self.assertIsInstance(response.data, list)
    
    def test_past_team_empty(self):
        """Test past team endpoint with no past members"""
        # Ensure membership has no end date
        self.membership.end_date = None
        self.membership.save()
        url = reverse('about_api:team-past-team')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_by_position_no_results(self):
        """Test by_position endpoint with no matching results"""
        url = reverse('about_api:team-by-position')
        response = self.client.get(url, {'position': 'NonExistentPosition'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_by_department_no_results(self):
        """Test by_department endpoint with no matching results"""
        url = reverse('about_api:staff-by-department')
        response = self.client.get(url, {'department': 'NonExistentDept'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_search_no_results(self):
        """Test search with query that matches nothing"""
        url = reverse('about_api:search')
        response = self.client.get(url, {'q': 'NonExistentSearchTermXYZ123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
        # All result lists should be empty
        self.assertEqual(len(response.data.get('cooperative_info', [])), 0)
        self.assertEqual(len(response.data.get('timeline', [])), 0)
    
    def test_search_special_characters(self):
        """Test search with special characters"""
        url = reverse('about_api:search')
        response = self.client.get(url, {'q': '!@#$%^&*()'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
    
    def test_search_very_long_query(self):
        """Test search with very long query string"""
        url = reverse('about_api:search')
        long_query = 'A' * 1000
        response = self.client.get(url, {'q': long_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
    
    def test_pagination_last_page(self):
        """Test pagination on last page"""
        # Create exactly 20 items (one page)
        for i in range(20):
            CooperativeInfo.objects.create(
                cooperative_name=f"Coop {i}",
                is_active=True,
                established_date='2020-01-01',
                registration_number=f'REG{i}',
                license_number=f'LIC{i}',
                address='Kathmandu',
                phone='9800000000',
                email='info@example.com',
                status='PB'
            )
        url = reverse('about_api:cooperative-info-list')
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_pagination_out_of_range(self):
        """Test pagination with page number out of range"""
        url = reverse('about_api:cooperative-info-list')
        response = self.client.get(url, {'page': 99999})
        # Should return 404 or empty results
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
    
    def test_ordering_invalid_field(self):
        """Test ordering with invalid field name"""
        url = reverse('about_api:cooperative-info-list')
        response = self.client.get(url, {'ordering': 'invalid_field'})
        # Should still return 200, just ignore invalid ordering
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_inactive_items(self):
        """Test that inactive items are not returned"""
        # Create inactive cooperative
        inactive_coop = CooperativeInfo.objects.create(
            cooperative_name="Inactive Coop",
            is_active=False,
            established_date='2020-01-01',
            registration_number='INACTIVE',
            license_number='LIC',
            address='Kathmandu',
            phone='9800000000',
            email='info@example.com',
            status='DF'
        )
        url = reverse('about_api:cooperative-info-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Inactive item should not be in results
        coop_ids = [item['id'] for item in response.data['results']]
        self.assertNotIn(inactive_coop.id, coop_ids)
    
    def test_statistics_with_no_data(self):
        """Test statistics endpoint with no data in database"""
        # Clear all data
        CooperativeInfo.objects.all().delete()
        CooperativeTimeline.objects.all().delete()
        CooperativeAffiliation.objects.all().delete()
        LeadershipMessage.objects.all().delete()
        Person.objects.all().delete()
        Committee.objects.all().delete()
        Staff.objects.all().delete()
        
        from django.core.cache import cache
        cache.clear()
        
        url = reverse('about_api:statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cooperative_info_count'], 0)
        self.assertEqual(response.data['timeline_events_count'], 0)
        self.assertIn('last_updated', response.data)
    
    def test_by_position_empty_string(self):
        """Test by_position with empty string parameter"""
        url = reverse('about_api:team-by-position')
        response = self.client.get(url, {'position': ''})
        # Empty string should be treated as missing parameter
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_by_department_empty_string(self):
        """Test by_department with empty string parameter"""
        url = reverse('about_api:staff-by-department')
        response = self.client.get(url, {'department': ''})
        # Empty string should be treated as missing parameter
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_whitespace_only(self):
        """Test search with whitespace-only query"""
        url = reverse('about_api:search')
        response = self.client.get(url, {'q': '   '})
        # Whitespace-only should be treated as empty
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_recent_timeline_ordering(self):
        """Test that recent timeline events are properly ordered"""
        # Create multiple timeline events with different dates
        from datetime import timedelta
        for i in range(5):
            CooperativeTimeline.objects.create(
                title=f"Event {i}",
                description=f"Description {i}",
                event_date=(timezone.now() - timedelta(days=i)).date(),
                event_type="milestone",
                is_active=True,
                status='PB'
            )
        url = reverse('about_api:timeline-recent')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return at most 10 events
        self.assertLessEqual(len(response.data), 10)
        # Events should be ordered by date (newest first)
        if len(response.data) > 1:
            dates = [item['event_date'] for item in response.data]
            self.assertEqual(dates, sorted(dates, reverse=True))

