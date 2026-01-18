"""
Comprehensive tests for about app views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date
import json

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeStatistic,
    CooperativeAffiliation, LeadershipMessage, Person, Committee,
    Membership, Staff
)
# ContactForm removed - legacy tests updated


User = get_user_model()


class AboutViewsTest(TestCase):
    """Test cases for about views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test cooperative
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
            status=CooperativeInfo.Status.PUBLISHED
        )
        
        # Create timeline event
        self.timeline = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test Description",
            event_date=date(2020, 1, 1),
            event_type="milestone",
            status=CooperativeTimeline.Status.PUBLISHED
        )
        
        # Create affiliation
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Organization",
            description="Test Description",
            affiliation_type="association",
            status=CooperativeAffiliation.Status.PUBLISHED
        )
        
        # Create leadership message
        self.leadership = LeadershipMessage.objects.create(
            title="Chairman's Message",
            message_type="chairman",
            content="Test content",
            author_name="John Doe",
            author_position="Chairman",
            status=LeadershipMessage.Status.PUBLISHED
        )
        
        # Create team data
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
        self.staff = Staff.objects.create(
            person=Person.objects.create(full_name="Jane Doe"),
            position="Manager"
        )
    
    def test_about_home_view(self):
        """Test AboutHomeView GET request - should redirect to introduction"""
        response = self.client.get(reverse('about:home'))
        
        # Should redirect to introduction page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('about:introduction'))
    
    def test_about_home_view_with_staff(self):
        """Test AboutHomeView with staff user - should still redirect"""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('about:home'))
        # Should redirect to introduction page even for staff
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('about:introduction'))
    
    def test_timeline_view(self):
        """Test TimelineView GET request"""
        response = self.client.get(reverse('about:timeline'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/timeline.html')
        self.assertIn('breadcrumbs', response.context)
        # Check pagination context
        self.assertIn('page_obj', response.context)
    
    def test_affiliations_view(self):
        """Test AffiliationsView GET request"""
        response = self.client.get(reverse('about:affiliations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/affiliations.html')
        self.assertIn('affiliations', response.context)
        self.assertIn('breadcrumbs', response.context)
    
    def test_chairperson_message_view(self):
        """Test ChairpersonMessageView GET request"""
        response = self.client.get(reverse('about:chairperson_message'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/chairperson_message.html')
        self.assertIn('message', response.context)
        self.assertIn('breadcrumbs', response.context)
        
    def test_manager_commitment_view(self):
        """Test ManagerCommitmentView GET request"""
        response = self.client.get(reverse('about:manager_commitment'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/manager_commitment.html')
        self.assertIn('message', response.context)
        self.assertIn('breadcrumbs', response.context)

    def test_board_of_directors_view(self):
        """Test BoardOfDirectorsView GET request"""
        response = self.client.get(reverse('about:board_of_directors'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/board_of_directors.html')
        self.assertIn('committees', response.context)
        self.assertIn('breadcrumbs', response.context)
        
    def test_management_view(self):
        """Test ManagementView GET request"""
        response = self.client.get(reverse('about:management'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/management.html')
        self.assertIn('management_team', response.context)
        self.assertIn('breadcrumbs', response.context)
    
    def test_cooperative_detail_view(self):
        """Test CooperativeDetailView GET request"""
        # Create a second cooperative to prevent redirect to introduction
        CooperativeInfo.objects.create(
            cooperative_name="Second Cooperative",
            cooperative_name_nepali="दोस्रो सहकारी",
            established_date=date(2021, 1, 1),
            registration_number="REG456",
            license_number="LIC456",
            address="Test Address 2",
            phone="0987654321",
            email="test2@example.com",
            mission="Test Mission 2",
            vision="Test Vision 2",
            values="Test Values 2",
            description="Test Description 2",
            status=CooperativeInfo.Status.PUBLISHED
        )

        response = self.client.get(reverse(
            'about:cooperative_detail',
            kwargs={'slug': self.cooperative.slug}
        ))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/cooperative_detail.html')
        self.assertIn('cooperative', response.context)
        self.assertEqual(response.context['cooperative'], self.cooperative)
        self.assertIn('breadcrumbs', response.context)
    
    def test_cooperative_detail_view_invalid_slug(self):
        """Test CooperativeDetailView with invalid slug"""
        response = self.client.get(reverse(
            'about:cooperative_detail',
            kwargs={'slug': 'non-existent-slug'}
        ))
        
        self.assertEqual(response.status_code, 404)
    
    def test_contact_view(self):
        """Test ContactView redirects to main contact app"""
        response = self.client.get(reverse('about:contact'))
        self.assertEqual(response.status_code, 302)

    def test_staff_logic_in_views(self):
        """Test staff vs non-staff branching in various views"""
        # Create draft versions of content
        draft_coop = CooperativeInfo.objects.create(
            cooperative_name="Draft Coop", established_date=date(2020, 1, 1),
            registration_number="REG_DRAFT", license_number="LIC_DRAFT",
            address="Test", phone="123", email="d@e.com",
            mission="M", vision="V", values="V", description="D",
            status=CooperativeInfo.Status.DRAFT
        )
        
        # 1. IntroductionView
        # Non-staff should not see draft coops (not applicable here as introduction uses first())
        # But should see published timeline events
        
        # 2. MemberTestimonialsView logic check
        # (Assuming Testimonial model is available and has status)
        from apps.home.models import Testimonial
        published_t = Testimonial.objects.create(name="Pub", content="C", status='PB')
        draft_t = Testimonial.objects.create(name="Draft", content="C", status='DF')
        
        # Non-staff
        response = self.client.get(reverse('about:member_testimonials'), follow=True)
        # Check if we landed on the right page
        self.assertEqual(response.status_code, 200)
        self.assertIn(published_t, response.context['testimonials'])
        self.assertNotIn(draft_t, response.context['testimonials'])
        
        # Staff
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('about:member_testimonials'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(published_t, response.context['testimonials'])
        self.assertIn(draft_t, response.context['testimonials'])

    def test_single_cooperative_redirect(self):
        """Test redirect to introduction when only one cooperative exists"""
        # Delete the second cooperative created in setup or by other tests
        CooperativeInfo.objects.exclude(pk=self.cooperative.pk).delete()
        
        # Accessing detail view of the ONLY coop should redirect to introduction
        response = self.client.get(reverse(
            'about:cooperative_detail',
            kwargs={'slug': self.cooperative.slug}
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('about:introduction'))

    def test_preview_view_access(self):
        """Test PreviewContentView access control"""
        url = reverse('about:preview_content', kwargs={
            'model_name': 'cooperativeinfo',
            'pk': self.cooperative.pk
        })
        
        # Anonymous/Non-staff should get 404
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='testpass123')
        
        # Add title attribute to avoid VariableDoesNotExist during template rendering
        self.cooperative.title = self.cooperative.cooperative_name
        
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_preview_view_with_token(self):
        """Test PreviewContentView with signing tokens"""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='testpass123')
        
        from django.core.signing import TimestampSigner
        signer = TimestampSigner()
        token = signer.sign(str(self.cooperative.pk))
        
        # Valid token
        url = reverse('about:preview_content_token', kwargs={
            'model_name': 'cooperativeinfo',
            'pk': self.cooperative.pk,
            'token': token
        })
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Invalid token
        url_invalid = reverse('about:preview_content_token', kwargs={
            'model_name': 'cooperativeinfo',
            'pk': self.cooperative.pk,
            'token': 'invalid-token'
        })
        response = self.client.get(url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    
    # test_gallery_view removed - gallery functionality moved to main gallery app
    # Use gallery app tests instead

