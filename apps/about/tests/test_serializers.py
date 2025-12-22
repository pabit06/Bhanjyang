"""
Tests for about app serializers
"""
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)
from apps.about.serializers import (
    CooperativeInfoSerializer, CooperativeTimelineSerializer,
    CooperativeAchievementSerializer, CooperativeStatisticSerializer,
    CooperativeAffiliationSerializer, LeadershipMessageSerializer,
    PersonSerializer, CommitteeSerializer, MembershipSerializer,
    StaffSerializer, DetailedCooperativeInfoSerializer,
    DetailedPersonSerializer, DetailedCommitteeSerializer,
    SummaryCooperativeInfoSerializer, SummaryPersonSerializer,
    SummaryTimelineSerializer, SummaryAchievementSerializer
)


class SerializerTestCase(TestCase):
    """Base test case for serializers"""
    
    def setUp(self):
        self.cooperative = CooperativeInfo.objects.create(
            cooperative_name="Test Cooperative",
            description="Test description",
            mission="Test mission",
            vision="Test vision",
            values="Test values",
            established_date=timezone.now().date(),
            registration_number="123",
            is_active=True
        )
        self.timeline = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test description",
            event_date=timezone.now().date(),
            event_type="milestone",
            is_active=True
        )
        self.achievement = CooperativeAchievement.objects.create(
            title="Test Achievement",
            description="Test description",
            achievement_type="award",
            is_active=True
        )
        self.statistic = CooperativeStatistic.objects.create(
            title="Test Stat",
            value=100,
            unit="members",
            is_active=True
        )
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Affiliation",
            description="Test description",
            is_active=True
        )
        self.message = LeadershipMessage.objects.create(
            title="Test Message",
            content="Test content",
            author_name="Test Author",
            is_active=True
        )
        self.person = Person.objects.create(
            full_name="Test Person",
            bio="Test bio",
            email="test@example.com",
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


class CooperativeInfoSerializerTest(SerializerTestCase):
    """Test CooperativeInfoSerializer"""
    
    def test_serialize_cooperative_info(self):
        """Test serializing cooperative info"""
        serializer = CooperativeInfoSerializer(self.cooperative)
        data = serializer.data
        self.assertEqual(data['cooperative_name'], self.cooperative.cooperative_name)
        self.assertEqual(data['description'], self.cooperative.description)
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_deserialize_cooperative_info(self):
        """Test deserializing cooperative info"""
        data = {
            'cooperative_name': 'New Cooperative',
            'description': 'New description',
            'is_active': True
        }
        serializer = CooperativeInfoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.cooperative_name, 'New Cooperative')
    
    def test_readonly_fields(self):
        """Test readonly fields are not writable"""
        data = {
            'cooperative_name': 'New Cooperative',
            'id': 999,  # Should be ignored
            'created_at': '2020-01-01'  # Should be ignored
        }
        serializer = CooperativeInfoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertNotEqual(instance.id, 999)


class CooperativeTimelineSerializerTest(SerializerTestCase):
    """Test CooperativeTimelineSerializer"""
    
    def test_serialize_timeline(self):
        """Test serializing timeline"""
        serializer = CooperativeTimelineSerializer(self.timeline)
        data = serializer.data
        self.assertEqual(data['title'], self.timeline.title)
        self.assertEqual(data['event_type'], self.timeline.event_type)
        self.assertIn('is_featured', data)
        self.assertIn('order', data)


class CooperativeAchievementSerializerTest(SerializerTestCase):
    """Test CooperativeAchievementSerializer"""
    
    def test_serialize_achievement(self):
        """Test serializing achievement"""
        serializer = CooperativeAchievementSerializer(self.achievement)
        data = serializer.data
        self.assertEqual(data['title'], self.achievement.title)
        self.assertEqual(data['achievement_type'], self.achievement.achievement_type)


class CooperativeStatisticSerializerTest(SerializerTestCase):
    """Test CooperativeStatisticSerializer"""
    
    def test_serialize_statistic(self):
        """Test serializing statistic"""
        serializer = CooperativeStatisticSerializer(self.statistic)
        data = serializer.data
        self.assertEqual(data['title'], self.statistic.title)
        self.assertEqual(data['value'], self.statistic.value)
        self.assertEqual(data['unit'], self.statistic.unit)


class CooperativeAffiliationSerializerTest(SerializerTestCase):
    """Test CooperativeAffiliationSerializer"""
    
    def test_serialize_affiliation(self):
        """Test serializing affiliation"""
        serializer = CooperativeAffiliationSerializer(self.affiliation)
        data = serializer.data
        self.assertEqual(data['name'], self.affiliation.name)
        self.assertIn('affiliation_type', data)


class LeadershipMessageSerializerTest(SerializerTestCase):
    """Test LeadershipMessageSerializer"""
    
    def test_serialize_message(self):
        """Test serializing leadership message"""
        serializer = LeadershipMessageSerializer(self.message)
        data = serializer.data
        self.assertEqual(data['title'], self.message.title)
        self.assertEqual(data['author_name'], self.message.author_name)
        self.assertIn('content', data)


class PersonSerializerTest(SerializerTestCase):
    """Test PersonSerializer"""
    
    def test_serialize_person(self):
        """Test serializing person"""
        serializer = PersonSerializer(self.person)
        data = serializer.data
        self.assertEqual(data['full_name'], self.person.full_name)
        self.assertEqual(data['email'], self.person.email)
        self.assertIn('bio', data)


class CommitteeSerializerTest(SerializerTestCase):
    """Test CommitteeSerializer"""
    
    def test_serialize_committee(self):
        """Test serializing committee"""
        serializer = CommitteeSerializer(self.committee)
        data = serializer.data
        self.assertEqual(data['name'], self.committee.name)
        self.assertIn('is_active', data)


class MembershipSerializerTest(SerializerTestCase):
    """Test MembershipSerializer"""
    
    def test_serialize_membership(self):
        """Test serializing membership"""
        serializer = MembershipSerializer(self.membership)
        data = serializer.data
        self.assertEqual(data['position'], self.membership.position)
        self.assertIn('person_name', data)
        self.assertIn('committee_name', data)
        self.assertEqual(data['person_name'], self.person.full_name)
        self.assertEqual(data['committee_name'], self.committee.name)


class StaffSerializerTest(SerializerTestCase):
    """Test StaffSerializer"""
    
    def test_serialize_staff(self):
        """Test serializing staff"""
        serializer = StaffSerializer(self.staff)
        data = serializer.data
        self.assertEqual(data['position'], self.staff.position)
        self.assertEqual(data['department'], self.staff.department)
        self.assertIn('person_name', data)
        self.assertEqual(data['person_name'], self.person.full_name)


class DetailedCooperativeInfoSerializerTest(SerializerTestCase):
    """Test DetailedCooperativeInfoSerializer"""
    
    def test_serialize_with_related_data(self):
        """Test serializing with related data"""
        serializer = DetailedCooperativeInfoSerializer(self.cooperative)
        data = serializer.data
        self.assertIn('statistics', data)
        self.assertIn('timeline_events', data)
        self.assertIn('achievements', data)
        self.assertIn('affiliations', data)
        self.assertIn('leadership_messages', data)


class DetailedPersonSerializerTest(SerializerTestCase):
    """Test DetailedPersonSerializer"""
    
    def test_serialize_with_memberships(self):
        """Test serializing with memberships"""
        serializer = DetailedPersonSerializer(self.person)
        data = serializer.data
        self.assertIn('memberships', data)
        self.assertIn('staff_positions', data)


class DetailedCommitteeSerializerTest(SerializerTestCase):
    """Test DetailedCommitteeSerializer"""
    
    def test_serialize_with_members(self):
        """Test serializing with members"""
        serializer = DetailedCommitteeSerializer(self.committee)
        data = serializer.data
        self.assertIn('memberships', data)
        self.assertEqual(len(data['memberships']), 1)


class SummarySerializersTest(SerializerTestCase):
    """Test summary serializers"""
    
    def test_summary_cooperative_info(self):
        """Test SummaryCooperativeInfoSerializer"""
        serializer = SummaryCooperativeInfoSerializer(self.cooperative)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('cooperative_name', data)
        self.assertIn('description', data)
        self.assertIn('logo', data)
        # Should not have all fields
        self.assertNotIn('mission', data)
        self.assertNotIn('vision', data)
    
    def test_summary_person(self):
        """Test SummaryPersonSerializer"""
        serializer = SummaryPersonSerializer(self.person)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('full_name', data)
        self.assertIn('photo', data)
        self.assertIn('position_general', data)
    
    def test_summary_timeline(self):
        """Test SummaryTimelineSerializer"""
        serializer = SummaryTimelineSerializer(self.timeline)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('title', data)
        self.assertIn('event_date', data)
        self.assertIn('is_featured', data)
    
    def test_summary_achievement(self):
        """Test SummaryAchievementSerializer"""
        serializer = SummaryAchievementSerializer(self.achievement)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('title', data)
        self.assertIn('achievement_type', data)
        self.assertIn('is_featured', data)

