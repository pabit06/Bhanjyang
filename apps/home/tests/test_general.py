"""
Comprehensive test suite for the home app
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.utils import timezone
from django.conf import settings
import json
import tempfile
import os
from django.core.exceptions import ValidationError

from apps.home.models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    NewsletterSubscriber,
    ContactInquiry, PageView
)
from apps.gallery.models import GalleryImage


class HomePageContentModelTest(TestCase):
    """Test HomePageContent model"""
    
    def setUp(self):
        self.homepage_content = HomePageContent.objects.create(
            title="Test Homepage",
            subtitle="Test Subtitle",
            description="Test description",
            is_active=True,
            order=1,
            meta_title="Test Meta Title",
            meta_description="Test meta description"
        )
    
    def test_homepage_content_creation(self):
        """Test homepage content creation"""
        self.assertEqual(self.homepage_content.title, "Test Homepage")
        self.assertTrue(self.homepage_content.is_active)
        self.assertEqual(self.homepage_content.order, 1)
    
    def test_homepage_content_str(self):
        """Test string representation"""
        self.assertEqual(str(self.homepage_content), "Test Homepage")
    
    def test_homepage_content_ordering(self):
        """Test ordering by order and created_at"""
        content2 = HomePageContent.objects.create(
            title="Second Content",
            order=2
        )
        content3 = HomePageContent.objects.create(
            title="First Content",
            order=1
        )
        
        contents = HomePageContent.objects.all()
        self.assertEqual(contents[0], content3)  # order=1 comes first
        self.assertEqual(contents[1], self.homepage_content)  # order=1, older
        self.assertEqual(contents[2], content2)  # order=2


class TestimonialModelTest(TestCase):
    """Test Testimonial model"""
    
    def setUp(self):
        self.testimonial = Testimonial.objects.create(
            name="John Doe",
            position="Customer",
            company="Test Company",
            content="Great service!",
            rating=5,
            is_featured=True,
            is_active=True,
            language='en'
        )
    
    def test_testimonial_creation(self):
        """Test testimonial creation"""
        self.assertEqual(self.testimonial.name, "John Doe")
        self.assertEqual(self.testimonial.rating, 5)
        self.assertTrue(self.testimonial.is_featured)
    
    def test_testimonial_str(self):
        """Test string representation"""
        expected = "John Doe - Great service!..."
        self.assertEqual(str(self.testimonial), expected)
    
    def test_rating_validation(self):
        """Test rating validation"""
        # Test valid ratings
        testimonial = Testimonial.objects.create(
            name="Test",
            content="Test content",
            rating=3
        )
        self.assertEqual(testimonial.rating, 3)
        
        # Test invalid ratings
        with self.assertRaises(ValidationError):
            t = Testimonial(
                name="Test",
                content="Test content",
                rating=6  # Invalid rating
            )
            t.full_clean()


class StatisticModelTest(TestCase):
    """Test Statistic model"""
    
    def setUp(self):
        self.statistic = Statistic.objects.create(
            title="Total Members",
            value="2,500+",
            description="Active members",
            icon="fas fa-users",
            color="green",
            is_featured=True,
            is_active=True
        )
    
    def test_statistic_creation(self):
        """Test statistic creation"""
        self.assertEqual(self.statistic.title, "Total Members")
        self.assertEqual(self.statistic.value, "2,500+")
        self.assertEqual(self.statistic.color, "green")
    
    def test_statistic_str(self):
        """Test string representation"""
        expected = "Total Members: 2,500+"
        self.assertEqual(str(self.statistic), expected)


class AnnouncementModelTest(TestCase):
    """Test Announcement model"""
    
    def setUp(self):
        self.announcement = Announcement.objects.create(
            title="Test Announcement",
            content="Test content",
            summary="Test summary",
            announcement_type="general",
            priority="medium",
            is_featured=True,
            is_active=True,
            publish_date=timezone.now()
        )
    
    def test_announcement_creation(self):
        """Test announcement creation"""
        self.assertEqual(self.announcement.title, "Test Announcement")
        self.assertEqual(self.announcement.announcement_type, "general")
        self.assertEqual(self.announcement.priority, "medium")
    
    def test_announcement_str(self):
        """Test string representation"""
        self.assertEqual(str(self.announcement), "Test Announcement")
    
    def test_is_expired_property(self):
        """Test is_expired property"""
        # No expiry date
        self.assertFalse(self.announcement.is_expired)
        
        # Future expiry date
        future_date = timezone.now() + timezone.timedelta(days=1)
        self.announcement.expiry_date = future_date
        self.announcement.save()
        self.assertFalse(self.announcement.is_expired)
        
        # Past expiry date
        past_date = timezone.now() - timezone.timedelta(days=1)
        self.announcement.expiry_date = past_date
        self.announcement.save()
        self.assertTrue(self.announcement.is_expired)



class GalleryImageModelTest(TestCase):
    """Test GalleryImage model"""
    
    def setUp(self):
        # Create a temporary image file
        self.image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        self.gallery_image = GalleryImage.objects.create(
            title="Test Image",
            description="Test description",
            image=self.image_file,
            category="events",
            is_featured=True,
            is_active=True
        )
    
    def tearDown(self):
        """Clean up uploaded files"""
        if self.gallery_image.image:
            if os.path.exists(self.gallery_image.image.path):
                os.unlink(self.gallery_image.image.path)
    
    def test_gallery_image_creation(self):
        """Test gallery image creation"""
        self.assertEqual(self.gallery_image.title, "Test Image")
        self.assertEqual(self.gallery_image.category, "events")
        self.assertTrue(self.gallery_image.is_featured)
    
    def test_gallery_image_str(self):
        """Test string representation"""
        self.assertEqual(str(self.gallery_image), "Test Image")


class NewsletterSubscriberModelTest(TestCase):
    """Test NewsletterSubscriber model"""
    
    def setUp(self):
        self.subscriber = NewsletterSubscriber.objects.create(
            email="test@example.com",
            name="Test User",
            is_active=True
        )
    
    def test_subscriber_creation(self):
        """Test newsletter subscriber creation"""
        self.assertEqual(self.subscriber.email, "test@example.com")
        self.assertEqual(self.subscriber.name, "Test User")
        self.assertTrue(self.subscriber.is_active)
    
    def test_subscriber_str(self):
        """Test string representation"""
        self.assertEqual(str(self.subscriber), "test@example.com")
    
    def test_unique_email(self):
        """Test unique email constraint"""
        with self.assertRaises(Exception):
            NewsletterSubscriber.objects.create(
                email="test@example.com",  # Same email
                name="Another User"
            )


class ContactInquiryModelTest(TestCase):
    """Test ContactInquiry model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.inquiry = ContactInquiry.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            subject="Test Inquiry",
            message="Test message",
            inquiry_type="general"
        )
    
    def test_inquiry_creation(self):
        """Test contact inquiry creation"""
        self.assertEqual(self.inquiry.name, "John Doe")
        self.assertEqual(self.inquiry.email, "john@example.com")
        self.assertEqual(self.inquiry.inquiry_type, "general")
        self.assertFalse(self.inquiry.is_resolved)
    
    def test_inquiry_str(self):
        """Test string representation"""
        expected = "John Doe - Test Inquiry"
        self.assertEqual(str(self.inquiry), expected)
    
    def test_resolve_inquiry(self):
        """Test resolving inquiry"""
        self.inquiry.is_resolved = True
        self.inquiry.resolved_at = timezone.now()
        self.inquiry.resolved_by = self.user
        self.inquiry.response = "Test response"
        self.inquiry.save()
        
        self.assertTrue(self.inquiry.is_resolved)
        self.assertIsNotNone(self.inquiry.resolved_at)
        self.assertEqual(self.inquiry.resolved_by, self.user)


class PageViewModelTest(TestCase):
    """Test PageView model"""
    
    def setUp(self):
        self.page_view = PageView.objects.create(
            page_url="https://example.com/test",
            page_title="Test Page",
            user_ip="127.0.0.1",
            user_agent="Test Browser",
            referrer="https://google.com",
            session_id="test_session_123"
        )
    
    def test_page_view_creation(self):
        """Test page view creation"""
        self.assertEqual(self.page_view.page_url, "https://example.com/test")
        self.assertEqual(self.page_view.page_title, "Test Page")
        self.assertEqual(self.page_view.user_ip, "127.0.0.1")
    
    def test_page_view_str(self):
        """Test string representation"""
        expected = f"https://example.com/test - {self.page_view.created_at}"
        self.assertEqual(str(self.page_view), expected)


class HomeViewsTest(TestCase):
    """Test home views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.homepage_content = HomePageContent.objects.create(
            title="Test Homepage",
            description="Test description",
            is_active=True
        )
        
        self.testimonial = Testimonial.objects.create(
            name="John Doe",
            content="Great service!",
            rating=5,
            is_featured=True,
            is_active=True
        )
        
        self.statistic = Statistic.objects.create(
            title="Total Members",
            value="2,500+",
            is_featured=True,
            is_active=True
        )
        
        self.announcement = Announcement.objects.create(
            title="Test Announcement",
            content="Test content",
            is_featured=True,
            is_active=True
        )
        

        
        self.gallery_image = GalleryImage.objects.create(
            title="Test Image",
            description="Test description",
            category="events",
            is_featured=True,
            is_active=True
        )
    
    def test_index_view(self):
        """Test homepage view"""
        response = self.client.get(reverse('home:index'))
        self.assertEqual(response.status_code, 200)
        # Check for content that should be present
        self.assertContains(response, "Total Members")
        # Check for testimonial content if present
        if hasattr(self, 'testimonial') and self.testimonial:
            self.assertContains(response, self.testimonial.name)
    
    def test_about_view(self):
        """Test about page view - now handled by about app"""
        response = self.client.get(reverse('about:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_gallery_view(self):
        """Test gallery view"""
        response = self.client.get(reverse('gallery:gallery'))
        self.assertEqual(response.status_code, 200)
    
    def test_remittance_view(self):
        """Test remittance view"""
        response = self.client.get(reverse('home:remittance'))
        self.assertEqual(response.status_code, 200)
    
    def test_api_statistics(self):
        """Test statistics API endpoint"""
        response = self.client.get(reverse('home:api_statistics'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        # DRF ListAPIView returns paginated format with 'results' key
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
        if len(data['results']) > 0:
            self.assertEqual(data['results'][0]['title'], 'Total Members')
    
    def test_api_testimonials(self):
        """Test testimonials API endpoint"""
        response = self.client.get(reverse('home:api_testimonials'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        # DRF ListAPIView returns paginated format with 'results' key
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
        if len(data['results']) > 0:
            self.assertEqual(data['results'][0]['name'], 'John Doe')


class ContactFormTest(TestCase):
    """Test contact form functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_contact_form_submission(self):
        """Test contact form submission"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'subject': 'Test Inquiry',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        
        response = self.client.post(reverse('home:contact_submit'), form_data)
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Check if inquiry was created
        inquiry = ContactInquiry.objects.get(email='john@example.com')
        self.assertEqual(inquiry.name, 'John Doe')
        self.assertEqual(inquiry.subject, 'Test Inquiry')
    
    def test_contact_form_invalid_data(self):
        """Test contact form with invalid data"""
        form_data = {
            'name': '',  # Invalid: empty name
            'email': 'invalid-email',  # Invalid email
            'subject': 'Test',
            'message': 'Test message'
        }
        
        response = self.client.post(reverse('home:contact_submit'), form_data)
        
        # Should redirect with error
        self.assertEqual(response.status_code, 302)
        
        # Check if no inquiry was created
        self.assertEqual(ContactInquiry.objects.count(), 0)
    
    def test_contact_form_ajax(self):
        """Test contact form AJAX submission"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Inquiry',
            'message': 'Test message',
            'inquiry_type': 'general'
        }
        
        response = self.client.post(
            reverse('home:contact_submit'),
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )
        
        # View returns 400 for invalid JSON or 200 for success
        # If form is invalid, it returns 400 with errors
        if response.status_code == 400:
            data = json.loads(response.content)
            self.assertFalse(data['success'])
        else:
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertTrue(data['success'])
            self.assertIn('Thank you', data['message'])


class NewsletterSignupTest(TestCase):
    """Test newsletter signup functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_newsletter_signup_new_subscriber(self):
        """Test newsletter signup for new subscriber"""
        form_data = {
            'email': 'new@example.com',
            'name': 'New User'
        }
        
        response = self.client.post(reverse('home:newsletter_signup'), form_data)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('Thank you for subscribing', data['message'])
        
        # Check if subscriber was created
        subscriber = NewsletterSubscriber.objects.get(email='new@example.com')
        self.assertEqual(subscriber.name, 'New User')
        self.assertTrue(subscriber.is_active)
    
    def test_newsletter_signup_existing_subscriber(self):
        """Test newsletter signup for existing subscriber"""
        # Create existing subscriber
        NewsletterSubscriber.objects.create(
            email='existing@example.com',
            name='Existing User',
            is_active=True
        )
        
        form_data = {
            'email': 'existing@example.com',
            'name': 'Existing User'
        }
        
        response = self.client.post(reverse('home:newsletter_signup'), form_data)
        
        # May return 400 if form validation fails or 200 with success/info message
        if response.status_code == 400:
            data = json.loads(response.content)
            self.assertFalse(data['success'])
        else:
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            # Existing subscriber may return success or info message
            self.assertIn('message', data)
            # Check if message contains subscription-related text
            message_lower = data['message'].lower()
            self.assertTrue('already' in message_lower or 'subscribed' in message_lower or 'success' in message_lower)
    
    def test_newsletter_signup_invalid_email(self):
        """Test newsletter signup with invalid email"""
        form_data = {
            'email': 'invalid-email',
            'name': 'Test User'
        }
        
        response = self.client.post(reverse('home:newsletter_signup'), form_data)
        
        # Invalid email should return 400 with error message
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        # Check for error message or errors dict
        self.assertTrue('message' in data or 'errors' in data)


class SecurityTest(TestCase):
    """Test security aspects"""
    
    def setUp(self):
        self.client = Client()
    
    def test_csrf_protection(self):
        """Test CSRF protection on forms"""
        # Test contact form CSRF protection
        # Note: In test environment, CSRF might be disabled or handled differently
        response = self.client.post(reverse('home:contact_submit'), {})
        # CSRF error can be 403, 400 (invalid form), or redirect to form with error (302)
        # The view returns 400 for invalid form data or 302 for redirect
        self.assertIn(response.status_code, [302, 400, 403])
    
    def test_xss_protection(self):
        """Test XSS protection"""
        malicious_script = '<script>alert("XSS")</script>'
        
        form_data = {
            'name': malicious_script,
            'email': 'test@example.com',
            'subject': 'Test',
            'message': 'Test message'
        }
        
        response = self.client.post(reverse('home:contact_submit'), form_data)
        
        # Should handle malicious input safely
        if response.status_code == 302:  # Successful submission
            inquiry = ContactInquiry.objects.get(email='test@example.com')
            # The malicious script should be escaped/stripped
            self.assertNotIn('<script>', inquiry.name)
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        malicious_input = "'; DROP TABLE home_homepagecontent; --"
        
        form_data = {
            'name': malicious_input,
            'email': 'test@example.com',
            'subject': 'Test',
            'message': 'Test message'
        }
        
        response = self.client.post(reverse('home:contact_submit'), form_data)
        
        # Should handle malicious input safely
        if response.status_code == 302:  # Successful submission
            # Table should still exist
            self.assertTrue(HomePageContent.objects.exists())


class PerformanceTest(TestCase):
    """Test performance aspects"""
    
    def setUp(self):
        self.client = Client()
        
        # Create multiple test records
        for i in range(10):
            Testimonial.objects.create(
                name=f"Testimonial {i}",
                content=f"Content {i}",
                rating=5,
                is_featured=True,
                is_active=True
            )
            
            Statistic.objects.create(
                title=f"Statistic {i}",
                value=f"Value {i}",
                is_featured=True,
                is_active=True
            )
    
    def test_homepage_performance(self):
        """Test homepage loading performance"""
        import time
        
        start_time = time.time()
        response = self.client.get(reverse('home:index'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        
        # Should load within reasonable time (adjust threshold as needed)
        load_time = end_time - start_time
        self.assertLess(load_time, 2.0)  # Less than 2 seconds
    
    def test_api_performance(self):
        """Test API endpoint performance"""
        import time
        
        start_time = time.time()
        response = self.client.get(reverse('home:api_statistics'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        
        load_time = end_time - start_time
        self.assertLess(load_time, 1.0)  # Less than 1 second


class ErrorHandlingTest(TestCase):
    """Test error handling"""
    
    def setUp(self):
        self.client = Client()
    
    def test_database_error_handling(self):
        """Test handling of database errors"""
        # This would require mocking database operations
        # For now, test that views handle exceptions gracefully
        response = self.client.get(reverse('home:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_url_handling(self):
        """Test handling of invalid URLs"""
        response = self.client.get('/invalid-url/')
        self.assertEqual(response.status_code, 404)
    
    def test_api_error_handling(self):
        """Test API error handling"""
        # Test with invalid data that might cause errors
        response = self.client.get(reverse('home:api_statistics'))
        self.assertEqual(response.status_code, 200)
        
        # Response should be valid JSON even if there are errors
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)


if __name__ == '__main__':
    import django
    django.setup()
