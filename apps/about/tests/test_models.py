"""
Comprehensive tests for about app models
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import date, timedelta
from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeStatistic,
    CooperativeAffiliation, LeadershipMessage, Person, Committee,
    Membership, Staff, ContentManager
)


class ContentManagerTest(TestCase):
    """Test suite for ContentManager custom manager"""
    
    def setUp(self):
        """Set up test data"""
        self.cooperative = CooperativeInfo.objects.create(
            cooperative_name="Test Cooperative",
            cooperative_name_nepali="परीक्षण सहकारी",
            established_date=date(2020, 1, 1),
            registration_number="REG123",
            license_number="LIC123",
            address="Test Address",
            phone="1234567890",
            email="test@example.com",
            mission="Test Mission",
            vision="Test Vision",
            values="Test Values",
            description="Test Description",
            is_active=True
        )
    
    def test_active_manager(self):
        """Test active() manager method"""
        active_coop = CooperativeInfo.objects.create(
            cooperative_name="Active Coop",
            cooperative_name_nepali="सक्रिय",
            established_date=date(2020, 1, 1),
            registration_number="REG124",
            license_number="LIC124",
            address="Test",
            phone="123",
            email="active@example.com",
            mission="M",
            vision="V",
            values="V",
            description="D",
            is_active=True
        )
        inactive_coop = CooperativeInfo.objects.create(
            cooperative_name="Inactive Coop",
            cooperative_name_nepali="निष्क्रिय",
            established_date=date(2020, 1, 1),
            registration_number="REG125",
            license_number="LIC125",
            address="Test",
            phone="123",
            email="inactive@example.com",
            mission="M",
            vision="V",
            values="V",
            description="D",
            is_active=False
        )
        
        active_queryset = CooperativeInfo.objects.active()
        self.assertIn(active_coop, active_queryset)
        self.assertIn(self.cooperative, active_queryset)
        self.assertNotIn(inactive_coop, active_queryset)
    
    def test_featured_manager(self):
        """Test featured() manager method"""
        featured_coop = CooperativeInfo.objects.create(
            cooperative_name="Featured Coop",
            cooperative_name_nepali="विशेष",
            established_date=date(2020, 1, 1),
            registration_number="REG126",
            license_number="LIC126",
            address="Test",
            phone="123",
            email="featured@example.com",
            mission="M",
            vision="V",
            values="V",
            description="D",
            is_active=True,
            is_featured=True
        )
        
        featured_queryset = CooperativeInfo.objects.featured()
        self.assertIn(featured_coop, featured_queryset)
        self.assertNotIn(self.cooperative, featured_queryset)


class CooperativeInfoModelTest(TestCase):
    """Test suite for CooperativeInfo model"""
    
    def setUp(self):
        """Set up test data"""
        self.cooperative = CooperativeInfo.objects.create(
            cooperative_name="Test Cooperative",
            cooperative_name_nepali="परीक्षण सहकारी",
            established_date=date(2020, 1, 1),
            registration_number="REG123",
            license_number="LIC123",
            address="Test Address",
            phone="1234567890",
            email="test@example.com",
            mission="Test Mission",
            vision="Test Vision",
            values="Test Values",
            description="Test Description"
        )
    
    def test_cooperative_creation(self):
        """Test basic cooperative creation"""
        self.assertEqual(self.cooperative.cooperative_name, "Test Cooperative")
        self.assertEqual(self.cooperative.cooperative_name_nepali, "परीक्षण सहकारी")
        self.assertTrue(self.cooperative.is_active)
        self.assertIsNotNone(self.cooperative.created_at)
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from cooperative_name"""
        self.assertIsNotNone(self.cooperative.slug)
        self.assertEqual(self.cooperative.slug, "test-cooperative")
    
    def test_slug_manual_setting(self):
        """Test manual slug setting"""
        coop = CooperativeInfo.objects.create(
            cooperative_name="Manual Slug Coop",
            cooperative_name_nepali="म्यानुअल",
            established_date=date(2020, 1, 1),
            registration_number="REG127",
            license_number="LIC127",
            address="Test",
            phone="123",
            email="manual@example.com",
            mission="M",
            vision="V",
            values="V",
            description="D",
            slug="custom-slug"
        )
        self.assertEqual(coop.slug, "custom-slug")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.cooperative), "Test Cooperative")
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.cooperative.get_absolute_url()
        self.assertIn(self.cooperative.slug, url)
        self.assertIn('cooperative', url)
    
    def test_ordering(self):
        """Test model ordering"""
        coop2 = CooperativeInfo.objects.create(
            cooperative_name="Second Coop",
            cooperative_name_nepali="दोस्रो",
            established_date=date(2020, 1, 1),
            registration_number="REG128",
            license_number="LIC128",
            address="Test",
            phone="123",
            email="second@example.com",
            mission="M",
            vision="V",
            values="V",
            description="D"
        )
        coops = list(CooperativeInfo.objects.all())
        # Should be ordered by -created_at (newest first)
        self.assertEqual(coops[0], coop2)
        self.assertEqual(coops[1], self.cooperative)


class CooperativeTimelineModelTest(TestCase):
    """Test suite for CooperativeTimeline model"""
    
    def setUp(self):
        """Set up test data"""
        self.timeline = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test Description",
            event_date=date(2020, 1, 1),
            event_type="milestone"
        )
    
    def test_timeline_creation(self):
        """Test basic timeline creation"""
        self.assertEqual(self.timeline.title, "Test Event")
        self.assertEqual(self.timeline.event_type, "milestone")
        self.assertTrue(self.timeline.is_active)
    
    def test_str_representation(self):
        """Test string representation"""
        expected = f"Test Event - {date(2020, 1, 1)}"
        self.assertEqual(str(self.timeline), expected)
    
    def test_event_type_choices(self):
        """Test event type choices"""
        event_types = ['milestone', 'achievement', 'expansion', 'award', 'partnership', 'other']
        for event_type in event_types:
            timeline = CooperativeTimeline.objects.create(
                title=f"Event {event_type}",
                description="Test",
                event_date=date(2020, 1, 1),
                event_type=event_type
            )
            self.assertEqual(timeline.event_type, event_type)
    
    def test_ordering(self):
        """Test model ordering"""
        timeline2 = CooperativeTimeline.objects.create(
            title="Earlier Event",
            description="Test",
            event_date=date(2019, 1, 1),
            event_type="milestone"
        )
        timelines = list(CooperativeTimeline.objects.all())
        # Should be ordered by -event_date, order
        self.assertEqual(timelines[0], self.timeline)  # 2020 > 2019
        self.assertEqual(timelines[1], timeline2)


class CooperativeStatisticModelTest(TestCase):
    """Test suite for CooperativeStatistic model"""
    
    def setUp(self):
        """Set up test data"""
        self.statistic = CooperativeStatistic.objects.create(
            title="Total Members",
            value="1000",
            unit="members",
            statistic_type="members"
        )
    
    def test_statistic_creation(self):
        """Test basic statistic creation"""
        self.assertEqual(self.statistic.title, "Total Members")
        self.assertEqual(self.statistic.value, "1000")
        self.assertEqual(self.statistic.statistic_type, "members")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.statistic), "Total Members: 1000 members")
    
    def test_statistic_type_choices(self):
        """Test statistic type choices"""
        types = ['members', 'deposits', 'loans', 'branches', 'employees', 'assets', 'other']
        for stat_type in types:
            stat = CooperativeStatistic.objects.create(
                title=f"Test {stat_type}",
                value="100",
                statistic_type=stat_type
            )
            self.assertEqual(stat.statistic_type, stat_type)
    
    def test_default_color(self):
        """Test default color theme"""
        self.assertEqual(self.statistic.color, "deuraligreen")


class CooperativeAffiliationModelTest(TestCase):
    """Test suite for CooperativeAffiliation model"""
    
    def setUp(self):
        """Set up test data"""
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Organization",
            description="Test Description",
            affiliation_type="association"
        )
    
    def test_affiliation_creation(self):
        """Test basic affiliation creation"""
        self.assertEqual(self.affiliation.name, "Test Organization")
        self.assertEqual(self.affiliation.affiliation_type, "association")
        self.assertTrue(self.affiliation.is_active)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.affiliation), "Test Organization")
    
    def test_affiliation_type_choices(self):
        """Test affiliation type choices"""
        types = ['regulatory', 'association', 'partnership', 'certification', 
                 'umbrella', 'cooperative_bank', 'other']
        for aff_type in types:
            aff = CooperativeAffiliation.objects.create(
                name=f"Test {aff_type}",
                description="Test",
                affiliation_type=aff_type
            )
            self.assertEqual(aff.affiliation_type, aff_type)


class LeadershipMessageModelTest(TestCase):
    """Test suite for LeadershipMessage model"""
    
    def setUp(self):
        """Set up test data"""
        self.message = LeadershipMessage.objects.create(
            title="Chairman's Message",
            message_type="chairman",
            content="Test content",
            author_name="John Doe",
            author_position="Chairman"
        )
    
    def test_message_creation(self):
        """Test basic message creation"""
        self.assertEqual(self.message.title, "Chairman's Message")
        self.assertEqual(self.message.message_type, "chairman")
        self.assertEqual(self.message.author_name, "John Doe")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.message), "Chairman's Message - John Doe")
    
    def test_message_type_choices(self):
        """Test message type choices"""
        types = ['chairman', 'manager', 'director', 'other']
        for msg_type in types:
            msg = LeadershipMessage.objects.create(
                title=f"{msg_type} Message",
                message_type=msg_type,
                content="Test",
                author_name="Test Author",
                author_position="Test Position"
            )
            self.assertEqual(msg.message_type, msg_type)


class PersonModelTest(TestCase):
    """Test suite for Person model"""
    
    def setUp(self):
        """Set up test data"""
        self.person = Person.objects.create(
            full_name="John Doe"
        )
    
    def test_person_creation(self):
        """Test basic person creation"""
        self.assertEqual(self.person.full_name, "John Doe")
        self.assertTrue(self.person.is_active)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.person), "John Doe")
    
    def test_unique_full_name(self):
        """Test that full_name must be unique"""
        with self.assertRaises(IntegrityError):
            Person.objects.create(full_name="John Doe")


class CommitteeModelTest(TestCase):
    """Test suite for Committee model"""
    
    def setUp(self):
        """Set up test data"""
        self.committee = Committee.objects.create(
            name="सञ्चालक समिति",
            tenure_bs="२०८०-२०८३"
        )
    
    def test_committee_creation(self):
        """Test basic committee creation"""
        self.assertEqual(self.committee.name, "सञ्चालक समिति")
        self.assertEqual(self.committee.tenure_bs, "२०८०-२०८३")
        self.assertTrue(self.committee.is_active)
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated"""
        self.assertIsNotNone(self.committee.slug)
        self.assertIn("2080", self.committee.slug)
    
    def test_str_representation(self):
        """Test string representation"""
        expected = "सञ्चालक समिति (२०८०-२०८३)"
        self.assertEqual(str(self.committee), expected)
    
    def test_ordering(self):
        """Test model ordering"""
        inactive_committee = Committee.objects.create(
            name="Inactive Committee",
            tenure_bs="2079-2082",
            is_active=False
        )
        committees = list(Committee.objects.all())
        # Should be ordered by -is_active, order (active first)
        self.assertEqual(committees[0], self.committee)
        self.assertEqual(committees[1], inactive_committee)


class MembershipModelTest(TestCase):
    """Test suite for Membership model"""
    
    def setUp(self):
        """Set up test data"""
        self.person = Person.objects.create(full_name="John Doe")
        self.committee = Committee.objects.create(
            name="Test Committee",
            tenure_bs="2080-2083"
        )
        self.membership = Membership.objects.create(
            person=self.person,
            committee=self.committee,
            position="chairman",
            order=1
        )
    
    def test_membership_creation(self):
        """Test basic membership creation"""
        self.assertEqual(self.membership.person, self.person)
        self.assertEqual(self.membership.committee, self.committee)
        self.assertEqual(self.membership.position, "chairman")
    
    def test_str_representation(self):
        """Test string representation"""
        expected = f"John Doe - Chairman of {self.committee}"
        self.assertEqual(str(self.membership), expected)
    
    def test_position_display_property(self):
        """Test position_display property"""
        self.assertEqual(self.membership.position_display, "Chairman")
        
        # Test custom position - use different person/committee to avoid unique constraint
        person2 = Person.objects.create(full_name="Jane Doe")
        committee2 = Committee.objects.create(
            name="Test Committee 2",
            tenure_bs="2081-2084"
        )
        membership2 = Membership.objects.create(
            person=person2,
            committee=committee2,
            position="other",
            position_custom="अध्यक्ष",
            order=2
        )
        self.assertEqual(membership2.position_display, "अध्यक्ष")
    
    def test_unique_together(self):
        """Test that person and committee combination must be unique"""
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.person,
                committee=self.committee,
                position="member"
            )


class StaffModelTest(TestCase):
    """Test suite for Staff model"""
    
    def setUp(self):
        """Set up test data"""
        self.person = Person.objects.create(full_name="Jane Doe")
        self.staff = Staff.objects.create(
            person=self.person,
            position="Manager"
        )
    
    def test_staff_creation(self):
        """Test basic staff creation"""
        self.assertEqual(self.staff.person, self.person)
        self.assertEqual(self.staff.position, "Manager")
        self.assertTrue(self.staff.is_active)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.staff), "Jane Doe - Manager")
    
    def test_one_to_one_relationship(self):
        """Test that one person can only have one staff profile"""
        person2 = Person.objects.create(full_name="Another Person")
        staff2 = Staff.objects.create(person=person2, position="Accountant")
        
        # Should be able to create different staff for different persons
        self.assertNotEqual(self.staff, staff2)
        
        # But same person cannot have multiple staff profiles
        with self.assertRaises(IntegrityError):
            Staff.objects.create(person=self.person, position="Another Position")

