"""
Comprehensive tests for home app models
"""
from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.home.models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    ServiceHighlight, NewsletterSubscriber, ContactInquiry, PageView
)

User = get_user_model()


class HomePageContentModelTest(TestCase):
    """Test suite for HomePageContent model"""
    
    def setUp(self):
        """Set up test data"""
        self.content = HomePageContent.objects.create(
            title="Test Homepage",
            subtitle="Test Subtitle",
            description="Test Description",
            is_active=True,
            order=0
        )
    
    def test_content_creation(self):
        """Test basic content creation"""
        self.assertEqual(self.content.title, "Test Homepage")
        self.assertEqual(self.content.subtitle, "Test Subtitle")
        self.assertTrue(self.content.is_active)
        self.assertIsNotNone(self.content.created_at)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.content), "Test Homepage")
    
    def test_ordering(self):
        """Test model ordering"""
        content2 = HomePageContent.objects.create(
            title="Second Homepage",
            description="Test",
            order=1
        )
        contents = list(HomePageContent.objects.all())
        # Should be ordered by order, -created_at
        self.assertEqual(contents[0], self.content)  # order=0
        self.assertEqual(contents[1], content2)  # order=1


class TestimonialModelTest(TestCase):
    """Test suite for Testimonial model"""
    
    def setUp(self):
        """Set up test data"""
        self.testimonial = Testimonial.objects.create(
            name="John Doe",
            position="Manager",
            company="Test Company",
            content="Great service!",
            rating=5,
            is_featured=True,
            is_active=True
        )
    
    def test_testimonial_creation(self):
        """Test basic testimonial creation"""
        self.assertEqual(self.testimonial.name, "John Doe")
        self.assertEqual(self.testimonial.rating, 5)
        self.assertTrue(self.testimonial.is_featured)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn("John Doe", str(self.testimonial))
        self.assertIn("Great service!", str(self.testimonial))
    
    def test_rating_validation(self):
        """Test rating validation"""
        # Rating should be between 1 and 5
        testimonial = Testimonial(
            name="Test",
            content="Test",
            rating=6  # Invalid
        )
        with self.assertRaises(ValidationError):
            testimonial.full_clean()
    
    def test_language_choices(self):
        """Test language choices"""
        languages = ['en', 'ne']
        for lang in languages:
            testimonial = Testimonial.objects.create(
                name=f"Test {lang}",
                content="Test",
                language=lang
            )
            self.assertEqual(testimonial.language, lang)
    
    def test_ordering(self):
        """Test model ordering"""
        testimonial2 = Testimonial.objects.create(
            name="Jane Doe",
            content="Test",
            order=1
        )
        testimonials = list(Testimonial.objects.all())
        # Should be ordered by order, -created_at
        self.assertEqual(testimonials[0], self.testimonial)  # order=0
        self.assertEqual(testimonials[1], testimonial2)  # order=1


class StatisticModelTest(TestCase):
    """Test suite for Statistic model"""
    
    def setUp(self):
        """Set up test data"""
        self.statistic = Statistic.objects.create(
            title="Total Members",
            value="2,500+",
            description="Active members",
            icon="fas fa-users",
            color="green",
            is_featured=True
        )
    
    def test_statistic_creation(self):
        """Test basic statistic creation"""
        self.assertEqual(self.statistic.title, "Total Members")
        self.assertEqual(self.statistic.value, "2,500+")
        self.assertEqual(self.statistic.color, "green")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.statistic), "Total Members: 2,500+")
    
    def test_default_color(self):
        """Test default color"""
        statistic = Statistic.objects.create(
            title="Test",
            value="100"
        )
        self.assertEqual(statistic.color, "green")
    
    def test_ordering(self):
        """Test model ordering"""
        statistic2 = Statistic.objects.create(
            title="Test 2",
            value="200",
            order=1
        )
        statistics = list(Statistic.objects.all())
        # Should be ordered by order, -created_at
        self.assertEqual(statistics[0], self.statistic)  # order=0
        self.assertEqual(statistics[1], statistic2)  # order=1


class AnnouncementModelTest(TestCase):
    """Test suite for Announcement model"""
    
    def setUp(self):
        """Set up test data"""
        self.announcement = Announcement.objects.create(
            title="Test Announcement",
            content="Test content",
            announcement_type="general",
            priority="high"
        )
    
    def test_announcement_creation(self):
        """Test basic announcement creation"""
        self.assertEqual(self.announcement.title, "Test Announcement")
        self.assertEqual(self.announcement.announcement_type, "general")
        self.assertEqual(self.announcement.priority, "high")
        self.assertIsNotNone(self.announcement.publish_date)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.announcement), "Test Announcement")
    
    def test_is_expired_property(self):
        """Test is_expired property"""
        # No expiry date
        self.assertFalse(self.announcement.is_expired)
        
        # Future expiry date
        self.announcement.expiry_date = timezone.now() + timedelta(days=7)
        self.announcement.save()
        self.assertFalse(self.announcement.is_expired)
        
        # Past expiry date
        self.announcement.expiry_date = timezone.now() - timedelta(days=7)
        self.announcement.save()
        self.assertTrue(self.announcement.is_expired)
    
    def test_announcement_type_choices(self):
        """Test announcement type choices"""
        types = ['general', 'service', 'event', 'holiday', 'maintenance']
        for ann_type in types:
            announcement = Announcement.objects.create(
                title=f"Test {ann_type}",
                content="Test",
                announcement_type=ann_type
            )
            self.assertEqual(announcement.announcement_type, ann_type)
    
    def test_priority_choices(self):
        """Test priority choices"""
        priorities = ['low', 'medium', 'high', 'urgent']
        for priority in priorities:
            announcement = Announcement.objects.create(
                title=f"Test {priority}",
                content="Test",
                priority=priority
            )
            self.assertEqual(announcement.priority, priority)
    
    def test_ordering(self):
        """Test model ordering"""
        announcement2 = Announcement.objects.create(
            title="Low Priority",
            content="Test",
            priority="low"
        )
        announcements = list(Announcement.objects.all())
        # Should be ordered by -priority, -publish_date
        # 'high' comes before 'low' in default ordering
        self.assertEqual(announcements[0], self.announcement)
        self.assertEqual(announcements[1], announcement2)


class ServiceHighlightModelTest(TestCase):
    """Test suite for ServiceHighlight model"""
    
    def setUp(self):
        """Set up test data"""
        self.highlight = ServiceHighlight.objects.create(
            title="Savings Account",
            description="High interest savings",
            icon="fas fa-piggy-bank",
            color="green",
            interest_rate="Up to 8%",
            link_url="https://example.com/savings",
            is_featured=True
        )
    
    def test_highlight_creation(self):
        """Test basic service highlight creation"""
        self.assertEqual(self.highlight.title, "Savings Account")
        self.assertEqual(self.highlight.icon, "fas fa-piggy-bank")
        self.assertEqual(self.highlight.interest_rate, "Up to 8%")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.highlight), "Savings Account")
    
    def test_default_link_text(self):
        """Test default link text"""
        self.assertEqual(self.highlight.link_text, "Learn More")
    
    def test_ordering(self):
        """Test model ordering"""
        highlight2 = ServiceHighlight.objects.create(
            title="Loan Service",
            description="Test",
            icon="fas fa-money",
            order=1
        )
        highlights = list(ServiceHighlight.objects.all())
        # Should be ordered by order, -created_at
        self.assertEqual(highlights[0], self.highlight)  # order=0
        self.assertEqual(highlights[1], highlight2)  # order=1


class NewsletterSubscriberModelTest(TestCase):
    """Test suite for NewsletterSubscriber model"""
    
    def setUp(self):
        """Set up test data"""
        self.subscriber = NewsletterSubscriber.objects.create(
            email="test@example.com",
            name="John Doe"
        )
    
    def test_subscriber_creation(self):
        """Test basic subscriber creation"""
        self.assertEqual(self.subscriber.email, "test@example.com")
        self.assertTrue(self.subscriber.is_active)
        self.assertIsNotNone(self.subscriber.subscribed_at)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.subscriber), "test@example.com")
    
    def test_unique_email(self):
        """Test that email must be unique"""
        with self.assertRaises(IntegrityError):
            NewsletterSubscriber.objects.create(email="test@example.com")
    
    def test_ordering(self):
        """Test model ordering"""
        subscriber2 = NewsletterSubscriber.objects.create(
            email="test2@example.com"
        )
        subscribers = list(NewsletterSubscriber.objects.all())
        # Should be ordered by -subscribed_at (newest first)
        self.assertEqual(subscribers[0], subscriber2)
        self.assertEqual(subscribers[1], self.subscriber)


class ContactInquiryModelTest(TestCase):
    """Test suite for ContactInquiry model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.inquiry = ContactInquiry.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            subject="Test Subject",
            message="Test message",
            inquiry_type="general"
        )
    
    def test_inquiry_creation(self):
        """Test basic inquiry creation"""
        self.assertEqual(self.inquiry.name, "John Doe")
        self.assertEqual(self.inquiry.inquiry_type, "general")
        self.assertFalse(self.inquiry.is_resolved)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.inquiry), "John Doe - Test Subject")
    
    def test_inquiry_type_choices(self):
        """Test inquiry type choices"""
        types = ['general', 'service', 'complaint', 'suggestion', 'support']
        for inq_type in types:
            inquiry = ContactInquiry.objects.create(
                name="Test",
                email=f"test{inq_type}@example.com",
                subject="Test",
                message="Test",
                inquiry_type=inq_type
            )
            self.assertEqual(inquiry.inquiry_type, inq_type)
    
    def test_ordering(self):
        """Test model ordering"""
        inquiry2 = ContactInquiry.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            subject="Second Subject",
            message="Test"
        )
        inquiries = list(ContactInquiry.objects.all())
        # Should be ordered by -created_at (newest first)
        self.assertEqual(inquiries[0], inquiry2)
        self.assertEqual(inquiries[1], self.inquiry)


class PageViewModelTest(TestCase):
    """Test suite for PageView model"""
    
    def setUp(self):
        """Set up test data"""
        self.page_view = PageView.objects.create(
            page_url="https://example.com/test",
            page_title="Test Page",
            user_ip="192.168.1.1",
            user_agent="Test Agent"
        )
    
    def test_page_view_creation(self):
        """Test basic page view creation"""
        self.assertEqual(self.page_view.page_url, "https://example.com/test")
        self.assertEqual(self.page_view.user_ip, "192.168.1.1")
        self.assertIsNotNone(self.page_view.created_at)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn("https://example.com/test", str(self.page_view))
        self.assertIn(str(self.page_view.created_at.date()), str(self.page_view))
    
    def test_ordering(self):
        """Test model ordering"""
        page_view2 = PageView.objects.create(
            page_url="https://example.com/test2",
            user_ip="192.168.1.2"
        )
        page_views = list(PageView.objects.all())
        # Should be ordered by -created_at (newest first)
        self.assertEqual(page_views[0], page_view2)
        self.assertEqual(page_views[1], self.page_view)

