"""
Tests for about app admin classes
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from django.utils import timezone
from datetime import date

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)
from apps.about.admin import (
    CooperativeInfoAdmin, CooperativeTimelineAdmin,
    CooperativeStatisticAdmin, CooperativeAffiliationAdmin, LeadershipMessageAdmin,
    PersonAdmin, CommitteeAdmin, MembershipAdmin, StaffAdmin,
    ActiveFilter, FeaturedFilter
)


class AboutAdminTestCase(TestCase):
    """Base test case for admin tests"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.request = self.factory.get('/admin/')
        self.request.user = self.admin_user


class CooperativeInfoAdminTest(AboutAdminTestCase):
    """Test CooperativeInfoAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = CooperativeInfoAdmin(CooperativeInfo, self.site)
        self.cooperative = CooperativeInfo.objects.create(
            cooperative_name="Test Cooperative",
            description="Test description",
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('cooperative_name', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)
        self.assertIn('created_at', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertTrue(any(isinstance(f, ActiveFilter) for f in self.admin.list_filter))
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('cooperative_name', self.admin.search_fields)
        self.assertIn('description', self.admin.search_fields)
    
    def test_actions_column(self):
        """Test actions column method"""
        result = self.admin.actions_column(self.cooperative)
        self.assertIsNotNone(result)
        self.assertIn('View on Site', result)
    
    def test_activate_selected_action(self):
        """Test activate selected action"""
        coop = CooperativeInfo.objects.create(
            cooperative_name="Inactive Coop",
            is_active=False
        )
        queryset = CooperativeInfo.objects.filter(id=coop.id)
        self.admin.activate_selected(self.request, queryset)
        coop.refresh_from_db()
        self.assertTrue(coop.is_active)
    
    def test_deactivate_selected_action(self):
        """Test deactivate selected action"""
        queryset = CooperativeInfo.objects.filter(id=self.cooperative.id)
        self.admin.deactivate_selected(self.request, queryset)
        self.cooperative.refresh_from_db()
        self.assertFalse(self.cooperative.is_active)
    
    def test_get_queryset(self):
        """Test queryset optimization"""
        queryset = self.admin.get_queryset(self.request)
        self.assertIsNotNone(queryset)


class CooperativeTimelineAdminTest(AboutAdminTestCase):
    """Test CooperativeTimelineAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = CooperativeTimelineAdmin(CooperativeTimeline, self.site)
        self.timeline = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test description",
            event_date=timezone.now().date(),
            is_active=True,
            is_featured=False
        )
    
    def test_list_display(self):
        """Test list display"""
        self.assertIn('title', self.admin.list_display)
        self.assertIn('event_date', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)
    
    def test_list_editable(self):
        """Test list editable fields"""
        self.assertIn('order', self.admin.list_editable)
        self.assertIn('is_featured', self.admin.list_editable)
    
    def test_feature_selected_action(self):
        """Test feature selected action"""
        queryset = CooperativeTimeline.objects.filter(id=self.timeline.id)
        self.admin.feature_selected(self.request, queryset)
        self.timeline.refresh_from_db()
        self.assertTrue(self.timeline.is_featured)
    
    def test_unfeature_selected_action(self):
        """Test unfeature selected action"""
        self.timeline.is_featured = True
        self.timeline.save()
        queryset = CooperativeTimeline.objects.filter(id=self.timeline.id)
        self.admin.unfeature_selected(self.request, queryset)
        self.timeline.refresh_from_db()
        self.assertFalse(self.timeline.is_featured)


class ActiveFilterTest(AboutAdminTestCase):
    """Test ActiveFilter"""
    
    def setUp(self):
        super().setUp()
        self.filter = ActiveFilter(
            request=self.request,
            params={},
            model=CooperativeInfo,
            model_admin=CooperativeInfoAdmin(CooperativeInfo, self.site)
        )
        CooperativeInfo.objects.create(
            cooperative_name="Active",
            is_active=True
        )
        CooperativeInfo.objects.create(
            cooperative_name="Inactive",
            is_active=False
        )
    
    def test_lookups(self):
        """Test filter lookups"""
        lookups = self.filter.lookups(self.request, CooperativeInfoAdmin(CooperativeInfo, self.site))
        self.assertEqual(len(lookups), 2)
        self.assertIn(('active', 'Active'), lookups)
        self.assertIn(('inactive', 'Inactive'), lookups)
    
    def test_queryset_active(self):
        """Test filtering active items"""
        self.filter.used_parameters = {'is_active': 'active'}
        queryset = self.filter.queryset(self.request, CooperativeInfo.objects.all())
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(queryset.first().is_active)
    
    def test_queryset_inactive(self):
        """Test filtering inactive items"""
        self.filter.used_parameters = {'is_active': 'inactive'}
        queryset = self.filter.queryset(self.request, CooperativeInfo.objects.all())
        self.assertEqual(queryset.count(), 1)
        self.assertFalse(queryset.first().is_active)


class FeaturedFilterTest(AboutAdminTestCase):
    """Test FeaturedFilter"""
    
    def setUp(self):
        super().setUp()
        self.filter = FeaturedFilter(
            request=self.request,
            params={},
            model=CooperativeTimeline,
            model_admin=CooperativeTimelineAdmin(CooperativeTimeline, self.site)
        )
        CooperativeTimeline.objects.create(
            title="Featured",
            is_featured=True
        )
        CooperativeTimeline.objects.create(
            title="Not Featured",
            is_featured=False
        )
    
    def test_lookups(self):
        """Test filter lookups"""
        lookups = self.filter.lookups(self.request, CooperativeTimelineAdmin(CooperativeTimeline, self.site))
        self.assertEqual(len(lookups), 2)
    
    def test_queryset_featured(self):
        """Test filtering featured items"""
        self.filter.used_parameters = {'is_featured': 'featured'}
        queryset = self.filter.queryset(self.request, CooperativeTimeline.objects.all())
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(queryset.first().is_featured)


class PersonAdminTest(AboutAdminTestCase):
    """Test PersonAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = PersonAdmin(Person, self.site)
        self.person = Person.objects.create(
            full_name="Test Person",
            email="test@example.com",
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display"""
        self.assertIn('full_name', self.admin.list_display)
        self.assertIn('email', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)


class CommitteeAdminTest(AboutAdminTestCase):
    """Test CommitteeAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = CommitteeAdmin(Committee, self.site)
        self.person = Person.objects.create(full_name="Test Person")
        self.committee = Committee.objects.create(
            name="Test Committee",
            is_active=True
        )
        self.membership = Membership.objects.create(
            person=self.person,
            committee=self.committee,
            position="Member"
        )
    
    def test_member_count(self):
        """Test member count method"""
        count = self.admin.member_count(self.committee)
        self.assertEqual(count, 1)
    
    def test_list_display(self):
        """Test list display"""
        self.assertIn('member_count', self.admin.list_display)


class LeadershipMessageAdminTest(AboutAdminTestCase):
    """Test LeadershipMessageAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = LeadershipMessageAdmin(LeadershipMessage, self.site)
        self.message = LeadershipMessage.objects.create(
            title="Test Message",
            content="Test content",
            author_name="Test Author",
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display"""
        self.assertIn('title', self.admin.list_display)
        self.assertIn('author_name', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)


# Removed: CooperativeAchievementAdminTest - achievements admin no longer exists


class CooperativeStatisticAdminTest(AboutAdminTestCase):
    """Test CooperativeStatisticAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = CooperativeStatisticAdmin(CooperativeStatistic, self.site)
        self.statistic = CooperativeStatistic.objects.create(
            title="Test Stat",
            value=100,
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display"""
        self.assertIn('title', self.admin.list_display)
        self.assertIn('value', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)


class CooperativeAffiliationAdminTest(AboutAdminTestCase):
    """Test CooperativeAffiliationAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = CooperativeAffiliationAdmin(CooperativeAffiliation, self.site)
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Affiliation",
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('affiliation_type', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)


class StaffAdminTest(AboutAdminTestCase):
    """Test StaffAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = StaffAdmin(Staff, self.site)
        self.person = Person.objects.create(full_name="Test Person")
        self.staff = Staff.objects.create(
            person=self.person,
            position="Manager",
            department="IT",
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display"""
        self.assertIn('person', self.admin.list_display)
        self.assertIn('position', self.admin.list_display)
        self.assertIn('department', self.admin.list_display)


class MembershipAdminTest(AboutAdminTestCase):
    """Test MembershipAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = MembershipAdmin(Membership, self.site)
        self.person = Person.objects.create(full_name="Test Person")
        self.committee = Committee.objects.create(name="Test Committee")
        self.membership = Membership.objects.create(
            person=self.person,
            committee=self.committee,
            position="Member",
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display"""
        self.assertIn('person', self.admin.list_display)
        self.assertIn('committee', self.admin.list_display)
        self.assertIn('position', self.admin.list_display)

