from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib import messages
from apps.about.admin import (
    ActiveFilter, FeaturedFilter, CooperativeInfoAdmin, 
    MembershipInlineForm, CooperativeTimelineAdmin
)
from apps.about.models import (
    CooperativeInfo, Person, Committee, Membership, CooperativeTimeline
)
from datetime import date
from unittest.mock import MagicMock

User = get_user_model()

class AdminComprehensiveTest(TestCase):
    """Comprehensive tests for about app admin interfaces"""

    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(username='admin', email='a@b.com', password='p')
        self.cooperative = CooperativeInfo.objects.create(
            cooperative_name="Admin Test Coop", 
            established_date=date(2020, 1, 1),
            registration_number="R1", license_number="L1", 
            address="A", phone="P", email="E@E.com",
            mission="M", vision="V", values="V", description="D",
            status=CooperativeInfo.Status.PUBLISHED
        )

    def test_active_filter_queryset(self):
        """Test ActiveFilter queryset logic"""
        from apps.about.admin import ActiveFilter
        # Create an inactive item
        inactive_event = CooperativeTimeline.objects.create(
            title="Inactive", event_date=date(2020, 1, 1), status='DF'
        )
        # Note: CooperativeTimeline save() sets is_active based on status
        self.assertFalse(inactive_event.is_active)
        
        request = self.factory.get('/')
        f = ActiveFilter(request, {'is_active': 'active'}, CooperativeTimeline, CooperativeTimelineAdmin)
        qs = f.queryset(request, CooperativeTimeline.objects.all())
        self.assertNotIn(inactive_event, qs)
        
        f_inactive = ActiveFilter(request, {'is_active': 'inactive'}, CooperativeTimeline, CooperativeTimelineAdmin)
        qs_inactive = f_inactive.queryset(request, CooperativeTimeline.objects.all())
        self.assertIn(inactive_event, qs_inactive)

    def test_featured_filter_queryset(self):
        """Test FeaturedFilter queryset logic"""
        from apps.about.admin import FeaturedFilter
        featured = CooperativeTimeline.objects.create(title="F", event_date=date(2020, 1, 1), status='PB', is_featured=True)
        not_featured = CooperativeTimeline.objects.create(title="NF", event_date=date(2020, 1, 1), status='PB', is_featured=False)
        
        request = self.factory.get('/')
        f = FeaturedFilter(request, {'is_featured': 'featured'}, CooperativeTimeline, CooperativeTimelineAdmin)
        qs = f.queryset(request, CooperativeTimeline.objects.all())
        self.assertIn(featured, qs)
        self.assertNotIn(not_featured, qs)

    def test_cooperative_info_admin_actions(self):
        """Test bulk actions in CooperativeInfoAdmin"""
        admin = CooperativeInfoAdmin(CooperativeInfo, self.site)
        request = self.factory.get('/')
        request.user = self.user
        # Mock message_user to avoid dealing with cookie storage in tests
        admin.message_user = MagicMock()
        
        queryset = CooperativeInfo.objects.filter(pk=self.cooperative.pk)
        
        # Test draft_selected
        admin.draft_selected(request, queryset)
        self.cooperative.refresh_from_db()
        self.assertEqual(self.cooperative.status, CooperativeInfo.Status.DRAFT)
        
        # Test publish_selected
        admin.publish_selected(request, queryset)
        self.cooperative.refresh_from_db()
        self.assertEqual(self.cooperative.status, CooperativeInfo.Status.PUBLISHED)
        self.assertTrue(self.cooperative.is_active)

    def test_cooperative_info_singleton(self):
        """Test singleton restriction (has_add_permission)"""
        admin = CooperativeInfoAdmin(CooperativeInfo, self.site)
        request = self.factory.get('/')
        request.user = self.user
        
        # Should be False if one already exists
        self.assertFalse(admin.has_add_permission(request))
        
        # Should be True if none exist
        CooperativeInfo.objects.all().delete()
        self.assertTrue(admin.has_add_permission(request))

    def test_membership_inline_form_create_person(self):
        """Test creating a person via the MembershipInlineForm"""
        data = {
            'person_name': 'New Person From Admin',
            'position': 'member',
            'order': 10
        }
        committee = Committee.objects.create(name="C", tenure_bs="2080-81")
        form = MembershipInlineForm(data=data)
        form.committee = committee
        
        self.assertTrue(form.is_valid())
        membership = form.save(commit=False)
        # Manually set committee since it's usually handled by Inline
        membership.committee = committee
        membership.save()
        
        self.assertEqual(membership.person.full_name, 'New Person From Admin')
        self.assertTrue(Person.objects.filter(full_name='New Person From Admin').exists())

    def test_membership_inline_form_validation(self):
        """Test validation logic in MembershipInlineForm"""
        # 1. Missing both person and name
        form = MembershipInlineForm(data={'position': 'member', 'order': 1})
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        
        # 2. Position 'other' without custom name
        form = MembershipInlineForm(data={
            'person_name': 'Tester',
            'position': 'other',
            'order': 1
        })
        self.assertFalse(form.is_valid())
        self.assertIn('position_custom', form.errors)

    def test_admin_previews(self):
        """Test preview links and columns in admin"""
        admin = CooperativeInfoAdmin(CooperativeInfo, self.site)
        
        # Test preview_link
        link = admin.preview_link(self.cooperative)
        self.assertIn('href=', link)
        self.assertIn('preview', link)
        
        # Test actions_column
        col = admin.actions_column(self.cooperative)
        self.assertIn('View on Site', col)
