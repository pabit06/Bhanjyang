"""
Comprehensive tests for news_events app models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from apps.news_events.models import (
    Category, NewsArticle, Event, Subscriber, Comment,
    Newsletter, ContentAnalytics
)

User = get_user_model()


class CategoryModelTest(TestCase):
    """Test suite for Category model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description",
            color="#28A745",
            icon="fas fa-newspaper"
        )
    
    def test_category_creation(self):
        """Test basic category creation"""
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.color, "#28A745")
        self.assertTrue(self.category.is_active)
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from name"""
        self.assertIsNotNone(self.category.slug)
        self.assertEqual(self.category.slug, "test-category")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.category), "Test Category")
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.category.get_absolute_url()
        self.assertIn(self.category.slug, url)
    
    def test_article_count_property(self):
        """Test article_count property"""
        # Initially should be 0
        self.assertEqual(self.category.article_count, 0)
        
        # Create published article
        user = User.objects.create_user(username='testuser', password='testpass')
        article = NewsArticle.objects.create(
            title="Test Article",
            category=self.category,
            author=user,
            content="Test content",
            status=NewsArticle.Status.PUBLISHED
        )
        self.assertEqual(self.category.article_count, 1)
        
        # Draft article should not count
        NewsArticle.objects.create(
            title="Draft Article",
            category=self.category,
            author=user,
            content="Test content",
            status=NewsArticle.Status.DRAFT
        )
        self.assertEqual(self.category.article_count, 1)


class NewsArticleModelTest(TestCase):
    """Test suite for NewsArticle model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Test Category")
        self.article = NewsArticle.objects.create(
            title="Test Article",
            category=self.category,
            author=self.user,
            content="Test content for the article",
            status=NewsArticle.Status.PUBLISHED
        )
    
    def test_article_creation(self):
        """Test basic article creation"""
        self.assertEqual(self.article.title, "Test Article")
        self.assertEqual(self.article.category, self.category)
        self.assertEqual(self.article.author, self.user)
        self.assertEqual(self.article.status, NewsArticle.Status.PUBLISHED)
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from title"""
        self.assertIsNotNone(self.article.slug)
        self.assertEqual(self.article.slug, "test-article")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.article), "Test Article")
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.article.get_absolute_url()
        self.assertIn(self.article.slug, url)
    
    def test_read_time_calculation(self):
        """Test read time calculation"""
        # Article with content should have read_time calculated
        self.assertGreater(self.article.read_time, 0)
    
    def test_excerpt_auto_generation(self):
        """Test excerpt auto-generation"""
        # If excerpt not provided, should be auto-generated from content
        self.assertIsNotNone(self.article.excerpt)
    
    def test_meta_fields_auto_generation(self):
        """Test meta fields auto-generation"""
        # Meta fields should be auto-generated if not provided
        self.assertEqual(self.article.meta_title, "Test Article")
        self.assertIsNotNone(self.article.meta_description)
    
    def test_content_hash_generation(self):
        """Test content hash generation"""
        # Content hash should be generated for security
        self.assertIsNotNone(self.article.content_hash)
        self.assertEqual(len(self.article.content_hash), 64)  # SHA-256 produces 64 hex chars
    
    def test_increment_view_count(self):
        """Test increment_view_count method"""
        initial_count = self.article.view_count
        self.article.increment_view_count()
        self.article.refresh_from_db()
        self.assertEqual(self.article.view_count, initial_count + 1)
    
    def test_increment_share_count(self):
        """Test increment_share_count method"""
        initial_count = self.article.share_count
        self.article.increment_share_count()
        self.article.refresh_from_db()
        self.assertEqual(self.article.share_count, initial_count + 1)
    
    def test_is_published_property(self):
        """Test is_published property"""
        self.assertTrue(self.article.is_published)
        
        self.article.status = NewsArticle.Status.DRAFT
        self.article.save()
        self.assertFalse(self.article.is_published)
    
    def test_status_choices(self):
        """Test status choices"""
        statuses = [
            NewsArticle.Status.DRAFT,
            NewsArticle.Status.PUBLISHED,
            NewsArticle.Status.ARCHIVED,
            NewsArticle.Status.SCHEDULED
        ]
        for status in statuses:
            article = NewsArticle.objects.create(
                title=f"Test {status}",
                category=self.category,
                author=self.user,
                content="Test",
                status=status
            )
            self.assertEqual(article.status, status)
    
    def test_priority_choices(self):
        """Test priority choices"""
        priorities = [
            NewsArticle.Priority.LOW,
            NewsArticle.Priority.MEDIUM,
            NewsArticle.Priority.HIGH,
            NewsArticle.Priority.URGENT
        ]
        for priority in priorities:
            article = NewsArticle.objects.create(
                title=f"Test {priority}",
                category=self.category,
                author=self.user,
                content="Test",
                status=NewsArticle.Status.PUBLISHED,
                priority=priority
            )
            self.assertEqual(article.priority, priority)
    
    def test_ordering(self):
        """Test model ordering"""
        article2 = NewsArticle.objects.create(
            title="Second Article",
            category=self.category,
            author=self.user,
            content="Test",
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now() + timedelta(days=1)
        )
        articles = list(NewsArticle.objects.all())
        # Should be ordered by -published_date (newest first)
        self.assertEqual(articles[0], article2)
        self.assertEqual(articles[1], self.article)


class EventModelTest(TestCase):
    """Test suite for Event model"""
    
    def setUp(self):
        """Set up test data"""
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            event_type=Event.EventType.MEETING,
            location="Test Location",
            event_date=timezone.now() + timedelta(days=7)
        )
    
    def test_event_creation(self):
        """Test basic event creation"""
        self.assertEqual(self.event.title, "Test Event")
        self.assertEqual(self.event.event_type, Event.EventType.MEETING)
        self.assertEqual(self.event.status, Event.Status.DRAFT)
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from title"""
        self.assertIsNotNone(self.event.slug)
        self.assertEqual(self.event.slug, "test-event")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.event), "Test Event")
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.event.get_absolute_url()
        self.assertIn(self.event.slug, url)
    
    def test_increment_view_count(self):
        """Test increment_view_count method"""
        initial_count = self.event.view_count
        self.event.increment_view_count()
        self.event.refresh_from_db()
        self.assertEqual(self.event.view_count, initial_count + 1)
    
    def test_is_upcoming_property(self):
        """Test is_upcoming property"""
        # Future event with published status
        self.event.status = Event.Status.PUBLISHED
        self.event.event_date = timezone.now() + timedelta(days=7)
        self.event.save()
        self.assertTrue(self.event.is_upcoming)
        
        # Past event
        self.event.event_date = timezone.now() - timedelta(days=7)
        self.event.save()
        self.assertFalse(self.event.is_upcoming)
    
    def test_is_past_property(self):
        """Test is_past property"""
        # Past event
        self.event.event_date = timezone.now() - timedelta(days=7)
        self.event.save()
        self.assertTrue(self.event.is_past)
        
        # Future event
        self.event.event_date = timezone.now() + timedelta(days=7)
        self.event.save()
        self.assertFalse(self.event.is_past)
    
    def test_duration_hours_property(self):
        """Test duration_hours property"""
        # Event without end_date
        self.assertEqual(self.event.duration_hours, 0)
        
        # Event with end_date
        self.event.end_date = self.event.event_date + timedelta(hours=3)
        self.event.save()
        self.assertEqual(self.event.duration_hours, 3.0)
    
    def test_event_type_choices(self):
        """Test event type choices"""
        types = [
            Event.EventType.MEETING,
            Event.EventType.WORKSHOP,
            Event.EventType.CONFERENCE,
            Event.EventType.SEMINAR,
            Event.EventType.SOCIAL,
            Event.EventType.TRAINING,
            Event.EventType.OTHER
        ]
        for event_type in types:
            event = Event.objects.create(
                title=f"Test {event_type}",
                description="Test",
                event_type=event_type,
                event_date=timezone.now() + timedelta(days=7)
            )
            self.assertEqual(event.event_type, event_type)
    
    def test_status_choices(self):
        """Test status choices"""
        statuses = [
            Event.Status.DRAFT,
            Event.Status.PUBLISHED,
            Event.Status.CANCELLED,
            Event.Status.COMPLETED
        ]
        for status in statuses:
            event = Event.objects.create(
                title=f"Test {status}",
                description="Test",
                event_type=Event.EventType.OTHER,
                event_date=timezone.now() + timedelta(days=7),
                status=status
            )
            self.assertEqual(event.status, status)
    
    def test_ordering(self):
        """Test model ordering"""
        event2 = Event.objects.create(
            title="Earlier Event",
            description="Test",
            event_type=Event.EventType.OTHER,
            event_date=timezone.now() + timedelta(days=3)
        )
        events = list(Event.objects.all())
        # Should be ordered by event_date (earliest first)
        self.assertEqual(events[0], event2)
        self.assertEqual(events[1], self.event)


class SubscriberModelTest(TestCase):
    """Test suite for Subscriber model"""
    
    def setUp(self):
        """Set up test data"""
        self.subscriber = Subscriber.objects.create(
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )
    
    def test_subscriber_creation(self):
        """Test basic subscriber creation"""
        self.assertEqual(self.subscriber.email, "test@example.com")
        self.assertEqual(self.subscriber.status, Subscriber.Status.ACTIVE)
        self.assertIsNotNone(self.subscriber.subscribed_at)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.subscriber), "test@example.com")
    
    def test_full_name_property(self):
        """Test full_name property"""
        self.assertEqual(self.subscriber.full_name, "John Doe")
        
        # Without last name
        subscriber2 = Subscriber.objects.create(
            email="test2@example.com",
            first_name="Jane"
        )
        self.assertEqual(subscriber2.full_name, "Jane")
        
        # Without first and last name
        subscriber3 = Subscriber.objects.create(email="test3@example.com")
        self.assertEqual(subscriber3.full_name, "test3@example.com")
    
    def test_generate_confirmation_token(self):
        """Test generate_confirmation_token method"""
        token = self.subscriber.generate_confirmation_token()
        self.assertIsNotNone(token)
        self.assertEqual(len(token), 43)  # token_urlsafe(32) produces 43 chars
        self.assertEqual(self.subscriber.confirmation_token, token)
    
    def test_unique_email(self):
        """Test that email must be unique"""
        with self.assertRaises(Exception):  # IntegrityError
            Subscriber.objects.create(email="test@example.com")
    
    def test_status_choices(self):
        """Test status choices"""
        statuses = [
            Subscriber.Status.ACTIVE,
            Subscriber.Status.UNSUBSCRIBED,
            Subscriber.Status.BOUNCED,
            Subscriber.Status.SPAM
        ]
        for status in statuses:
            subscriber = Subscriber.objects.create(
                email=f"test{status}@example.com",
                status=status
            )
            self.assertEqual(subscriber.status, status)
    
    def test_categories_many_to_many(self):
        """Test categories many-to-many relationship"""
        category1 = Category.objects.create(name="Category 1")
        category2 = Category.objects.create(name="Category 2")
        
        self.subscriber.categories.add(category1, category2)
        self.assertEqual(self.subscriber.categories.count(), 2)


class CommentModelTest(TestCase):
    """Test suite for Comment model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Test Category")
        self.article = NewsArticle.objects.create(
            title="Test Article",
            category=self.category,
            author=self.user,
            content="Test content",
            status=NewsArticle.Status.PUBLISHED
        )
        self.comment = Comment.objects.create(
            article=self.article,
            author_name="John Doe",
            author_email="john@example.com",
            content="Test comment"
        )
    
    def test_comment_creation(self):
        """Test basic comment creation"""
        self.assertEqual(self.comment.article, self.article)
        self.assertEqual(self.comment.author_name, "John Doe")
        self.assertEqual(self.comment.status, Comment.Status.PENDING)
    
    def test_str_representation(self):
        """Test string representation"""
        expected = f"Comment by John Doe on {self.article.title}"
        self.assertEqual(str(self.comment), expected)
    
    def test_status_choices(self):
        """Test status choices"""
        statuses = [
            Comment.Status.PENDING,
            Comment.Status.APPROVED,
            Comment.Status.REJECTED,
            Comment.Status.SPAM
        ]
        for status in statuses:
            comment = Comment.objects.create(
                article=self.article,
                author_name=f"Test {status}",
                author_email=f"test{status}@example.com",
                content="Test",
                status=status
            )
            self.assertEqual(comment.status, status)
    
    def test_ordering(self):
        """Test model ordering"""
        comment2 = Comment.objects.create(
            article=self.article,
            author_name="Second Commenter",
            author_email="second@example.com",
            content="Second comment"
        )
        comments = list(Comment.objects.all())
        # Should be ordered by -created_at (newest first)
        self.assertEqual(comments[0], comment2)
        self.assertEqual(comments[1], self.comment)


class NewsletterModelTest(TestCase):
    """Test suite for Newsletter model"""
    
    def setUp(self):
        """Set up test data"""
        self.newsletter = Newsletter.objects.create(
            title="Test Newsletter",
            subject="Test Subject",
            content="Test content"
        )
    
    def test_newsletter_creation(self):
        """Test basic newsletter creation"""
        self.assertEqual(self.newsletter.title, "Test Newsletter")
        self.assertEqual(self.newsletter.status, Newsletter.Status.DRAFT)
        self.assertTrue(self.newsletter.send_to_all)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.newsletter), "Test Newsletter")
    
    def test_status_choices(self):
        """Test status choices"""
        statuses = [
            Newsletter.Status.DRAFT,
            Newsletter.Status.SCHEDULED,
            Newsletter.Status.SENDING,
            Newsletter.Status.SENT,
            Newsletter.Status.FAILED
        ]
        for status in statuses:
            newsletter = Newsletter.objects.create(
                title=f"Test {status}",
                subject="Test",
                content="Test",
                status=status
            )
            self.assertEqual(newsletter.status, status)
    
    def test_categories_many_to_many(self):
        """Test categories many-to-many relationship"""
        category1 = Category.objects.create(name="Category 1")
        category2 = Category.objects.create(name="Category 2")
        
        self.newsletter.categories.add(category1, category2)
        self.assertEqual(self.newsletter.categories.count(), 2)


class ContentAnalyticsModelTest(TestCase):
    """Test suite for ContentAnalytics model"""
    
    def setUp(self):
        """Set up test data"""
        self.analytics = ContentAnalytics.objects.create(
            content_type="article",
            content_id=1,
            date=date.today(),
            views=100,
            unique_views=80,
            shares=10,
            comments=5
        )
    
    def test_analytics_creation(self):
        """Test basic analytics creation"""
        self.assertEqual(self.analytics.content_type, "article")
        self.assertEqual(self.analytics.content_id, 1)
        self.assertEqual(self.analytics.views, 100)
    
    def test_str_representation(self):
        """Test string representation"""
        expected = f"article 1 - {date.today()}"
        self.assertEqual(str(self.analytics), expected)
    
    def test_unique_together(self):
        """Test unique_together constraint"""
        # Same content_type, content_id, and date should fail
        with self.assertRaises(Exception):  # IntegrityError
            ContentAnalytics.objects.create(
                content_type="article",
                content_id=1,
                date=date.today(),
                views=200
            )

