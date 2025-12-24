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
from apps.about.forms import ContactForm, NewsletterSignupForm, FeedbackForm

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
            description="Test Description"
        )
        
        # Create timeline event
        self.timeline = CooperativeTimeline.objects.create(
            title="Test Event",
            description="Test Description",
            event_date=date(2020, 1, 1),
            event_type="milestone"
        )
        
        # Create affiliation
        self.affiliation = CooperativeAffiliation.objects.create(
            name="Test Organization",
            description="Test Description",
            affiliation_type="association"
        )
        
        # Create leadership message
        self.leadership = LeadershipMessage.objects.create(
            title="Chairman's Message",
            message_type="chairman",
            content="Test content",
            author_name="John Doe",
            author_position="Chairman"
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
        """Test AboutHomeView GET request"""
        response = self.client.get(reverse('about:home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/about.html')
        # Check context contains expected data
        self.assertIn('cooperative', response.context)
    
    def test_about_home_view_with_staff(self):
        """Test AboutHomeView with staff user"""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('about:home'))
        self.assertEqual(response.status_code, 200)
    
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
    
    def test_leadership_view(self):
        """Test LeadershipView GET request"""
        response = self.client.get(reverse('about:leadership'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/leadership.html')
        self.assertIn('leadership_messages', response.context)
        self.assertIn('breadcrumbs', response.context)
    
    def test_team_view(self):
        """Test TeamView GET request"""
        response = self.client.get(reverse('about:team'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/team.html')
        self.assertIn('committees', response.context)
        self.assertIn('management_team', response.context)
        self.assertIn('breadcrumbs', response.context)
    
    def test_past_team_view(self):
        """Test PastTeamView GET request"""
        # Create inactive committee
        past_committee = Committee.objects.create(
            name="Past Committee",
            tenure_bs="2079-2082",
            is_active=False
        )
        
        response = self.client.get(reverse('about:past_team'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/past_team.html')
        self.assertIn('committees', response.context)
        self.assertIn('breadcrumbs', response.context)
    
    def test_cooperative_detail_view(self):
        """Test CooperativeDetailView GET request"""
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
    
    def test_contact_view_get(self):
        """Test ContactView GET request"""
        response = self.client.get(reverse('about:contact'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/contact.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ContactForm)
    
    def test_contact_view_post_valid(self):
        """Test ContactView POST with valid data"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        
        response = self.client.post(reverse('about:contact'), form_data)
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('about:contact_success'))
    
    def test_contact_view_post_invalid(self):
        """Test ContactView POST with invalid data"""
        form_data = {
            'name': '',  # Invalid
            'email': 'invalid-email',  # Invalid
            'subject': '',
            'message': ''
        }
        
        response = self.client.post(reverse('about:contact'), form_data)
        
        # Should render form with errors
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
    
    def test_contact_success_view(self):
        """Test ContactSuccessView GET request"""
        response = self.client.get(reverse('about:contact_success'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/contact_success.html')
    
    def test_newsletter_signup_view_post_valid(self):
        """Test NewsletterSignupView POST with valid data"""
        form_data = {
            'email': 'new@example.com',
            'name': 'New Subscriber'
        }
        
        response = self.client.post(
            reverse('about:newsletter_signup'),
            json.dumps(form_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success', False))
    
    def test_newsletter_signup_view_post_invalid(self):
        """Test NewsletterSignupView POST with invalid data"""
        form_data = {
            'email': 'invalid-email',  # Invalid
            'name': ''
        }
        
        response = self.client.post(
            reverse('about:newsletter_signup'),
            json.dumps(form_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data.get('success', False))
    
    def test_feedback_view_post_valid(self):
        """Test FeedbackView POST with valid data"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'feedback_type': 'general',
            'message': 'Test feedback message'
        }
        
        response = self.client.post(
            reverse('about:feedback'),
            json.dumps(form_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success', False))
    
    def test_feedback_view_post_invalid(self):
        """Test FeedbackView POST with invalid data"""
        form_data = {
            'email': 'invalid-email',  # Invalid
            'message': ''  # Invalid
        }
        
        response = self.client.post(
            reverse('about:feedback'),
            json.dumps(form_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data.get('success', False))
    
    def test_gallery_view(self):
        """Test GalleryView GET request"""
        response = self.client.get(reverse('about:gallery'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/gallery.html')
        self.assertIn('breadcrumbs', response.context)

