# news_events/models.py

import os
import hashlib
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import logging
from .managers import ArticleManager, EventManager

logger = logging.getLogger(__name__)

# Helper function to calculate read time
def calculate_read_time(content):
    """Calculate estimated reading time in minutes"""
    if not content:
        return 0
    word_count = len(content.split())
    # Assumes an average reading speed of 200 words per minute
    read_time = (word_count + 199) // 200
    return max(1, read_time)

class Category(models.Model):
    """News and events categories"""
    name = models.CharField(max_length=100, unique=True, help_text=_("Category name"))
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text=_("URL-friendly version of name"))
    description = models.TextField(blank=True, help_text=_("Category description"))
    color = models.CharField(max_length=7, default="#28A745", help_text=_("Hex color code for category"))
    icon = models.CharField(max_length=50, blank=True, help_text=_("FontAwesome icon class"))
    is_active = models.BooleanField(default=True, help_text=_("Whether this category is active"))
    sort_order = models.PositiveIntegerField(default=0, help_text=_("Sort order for display"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        indexes = [
            models.Index(fields=['is_active', 'sort_order']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news_events:article-by-category', args=[self.slug])

    @property
    def article_count(self):
        """Get count of published articles in this category"""
        return self.articles.filter(status=NewsArticle.Status.PUBLISHED).count()

class NewsArticle(models.Model):
    """News articles with enterprise features"""
    class Status(models.TextChoices):
        DRAFT = 'DF', _('Draft')
        PUBLISHED = 'PB', _('Published')
        ARCHIVED = 'AR', _('Archived')
        SCHEDULED = 'SC', _('Scheduled')

    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low Priority')
        MEDIUM = 'MED', _('Medium Priority')
        HIGH = 'HIGH', _('High Priority')
        URGENT = 'URG', _('Urgent')

    # Basic fields
    title = models.CharField(max_length=200, help_text=_("Article title"))
    slug = models.SlugField(unique=True, blank=True, max_length=250, help_text=_("URL-friendly version of title"))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='articles', help_text=_("Article category"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_events_articles', help_text=_("Article author"))
    
    # Content fields
    content = models.TextField(help_text=_("Article content"))
    excerpt = models.TextField(blank=True, max_length=500, help_text=_("Short article summary"))
    image = models.ImageField(upload_to='news_events/images/', blank=True, null=True, help_text=_("Featured image"))
    image_alt = models.CharField(max_length=200, blank=True, help_text=_("Alt text for image"))
    
    # Metadata
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, help_text=_("Publication status"))
    priority = models.CharField(max_length=4, choices=Priority.choices, default=Priority.MEDIUM, help_text=_("Content priority"))
    published_date = models.DateTimeField(default=timezone.now, help_text=_("Publication date"))
    scheduled_date = models.DateTimeField(blank=True, null=True, help_text=_("Scheduled publication date"))
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True, help_text=_("SEO title"))
    meta_description = models.TextField(blank=True, max_length=300, help_text=_("SEO description"))
    meta_keywords = models.CharField(max_length=500, blank=True, help_text=_("SEO keywords"))
    
    # Analytics fields
    read_time = models.PositiveIntegerField(default=0, editable=False, help_text=_("Estimated read time in minutes"))
    view_count = models.PositiveIntegerField(default=0, editable=False, help_text=_("Number of views"))
    share_count = models.PositiveIntegerField(default=0, editable=False, help_text=_("Number of shares"))
    comment_count = models.PositiveIntegerField(default=0, editable=False, help_text=_("Number of comments"))
    
    # Security fields
    content_hash = models.CharField(max_length=64, blank=True, editable=False, help_text=_("SHA-256 hash of content"))
    is_featured = models.BooleanField(default=False, help_text=_("Featured article"))
    allow_comments = models.BooleanField(default=True, help_text=_("Allow comments"))
    require_login = models.BooleanField(default=False, help_text=_("Require login to view"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(blank=True, null=True, help_text=_("Last access time"))

    objects = ArticleManager()

    class Meta:
        ordering = ['-published_date']
        verbose_name = _("News Article")
        verbose_name_plural = _("News Articles")
        indexes = [
            models.Index(fields=['status', 'published_date']),
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['status', 'published_date', 'is_featured']),
            models.Index(fields=['category', 'status', 'published_date']),
            models.Index(fields=['view_count']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_events:article-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Calculate read time
        if self.content:
            self.read_time = calculate_read_time(self.content)
        
        # Generate content hash for security
        if self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()
        
        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            self.excerpt = self.content[:500] + "..." if len(self.content) > 500 else self.content
        
        # Auto-generate meta fields if not provided
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.excerpt
        
        super().save(*args, **kwargs)

    def increment_view_count(self):
        """Increment view count atomically"""
        from django.db.models import F
        NewsArticle.objects.filter(pk=self.pk).update(
            view_count=F('view_count') + 1,
            last_accessed=timezone.now()
        )

    def increment_share_count(self):
        """Increment share count atomically"""
        from django.db.models import F
        NewsArticle.objects.filter(pk=self.pk).update(
            share_count=F('share_count') + 1
        )

    @property
    def is_published(self):
        """Check if article is published"""
        return self.status == self.Status.PUBLISHED

    @property
    def is_scheduled(self):
        """Check if article is scheduled for future publication"""
        return self.status == self.Status.SCHEDULED and self.scheduled_date and self.scheduled_date > timezone.now()

    @property
    def can_view(self):
        """Check if article can be viewed"""
        return self.is_published or self.is_scheduled

class Event(models.Model):
    """Events with enhanced features"""
    class EventType(models.TextChoices):
        MEETING = 'MEET', _('Meeting')
        WORKSHOP = 'WORK', _('Workshop')
        CONFERENCE = 'CONF', _('Conference')
        SEMINAR = 'SEMI', _('Seminar')
        SOCIAL = 'SOC', _('Social Event')
        TRAINING = 'TRAIN', _('Training')
        OTHER = 'OTH', _('Other')

    class Status(models.TextChoices):
        DRAFT = 'DF', _('Draft')
        PUBLISHED = 'PB', _('Published')
        CANCELLED = 'CAN', _('Cancelled')
        COMPLETED = 'COM', _('Completed')

    # Basic fields
    title = models.CharField(max_length=200, help_text=_("Event title"))
    slug = models.SlugField(unique=True, blank=True, max_length=250, help_text=_("URL-friendly version of title"))
    description = models.TextField(help_text=_("Event description"))
    short_description = models.TextField(blank=True, max_length=300, help_text=_("Short event description"))
    
    # Event details
    event_type = models.CharField(max_length=5, choices=EventType.choices, default=EventType.OTHER, help_text=_("Type of event"))
    location = models.CharField(max_length=150, default="Cooperative Office", help_text=_("Event location"))
    address = models.TextField(blank=True, help_text=_("Full event address"))
    event_date = models.DateTimeField(help_text=_("Event date and time"))
    end_date = models.DateTimeField(blank=True, null=True, help_text=_("Event end date and time"))
    
    # Registration
    max_attendees = models.PositiveIntegerField(blank=True, null=True, help_text=_("Maximum number of attendees"))
    registration_required = models.BooleanField(default=False, help_text=_("Registration required"))
    registration_deadline = models.DateTimeField(blank=True, null=True, help_text=_("Registration deadline"))
    registration_url = models.URLField(blank=True, help_text=_("Registration URL"))
    
    # Media
    image = models.ImageField(upload_to='news_events/events/', blank=True, null=True, help_text=_("Event image"))
    image_alt = models.CharField(max_length=200, blank=True, help_text=_("Alt text for image"))
    
    # Status and visibility
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.DRAFT, help_text=_("Event status"))
    is_featured = models.BooleanField(default=False, help_text=_("Featured event"))
    is_recurring = models.BooleanField(default=False, help_text=_("Recurring event"))
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0, editable=False, help_text=_("Number of views"))
    registration_count = models.PositiveIntegerField(default=0, editable=False, help_text=_("Number of registrations"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(blank=True, null=True, help_text=_("Last access time"))

    objects = EventManager()

    class Meta:
        ordering = ['event_date']
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        indexes = [
            models.Index(fields=['event_date']),
            models.Index(fields=['status', 'event_date']),
            models.Index(fields=['event_type', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['slug']),
            models.Index(fields=['view_count']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['end_date']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_events:event-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def increment_view_count(self):
        """Increment view count atomically"""
        from django.db.models import F
        Event.objects.filter(pk=self.pk).update(
            view_count=F('view_count') + 1,
            last_accessed=timezone.now()
        )

    @property
    def is_upcoming(self):
        """Check if event is upcoming"""
        return self.event_date > timezone.now() and self.status == self.Status.PUBLISHED

    @property
    def is_past(self):
        """Check if event is past"""
        return self.event_date < timezone.now()

    @property
    def duration_hours(self):
        """Calculate event duration in hours"""
        if self.end_date:
            duration = self.end_date - self.event_date
            return duration.total_seconds() / 3600
        return 0

class Subscriber(models.Model):
    """Newsletter subscribers with enhanced features"""
    class Status(models.TextChoices):
        ACTIVE = 'ACT', _('Active')
        UNSUBSCRIBED = 'UNS', _('Unsubscribed')
        BOUNCED = 'BOU', _('Bounced')
        SPAM = 'SPA', _('Spam')

    email = models.EmailField(unique=True, help_text=_("Subscriber email"))
    first_name = models.CharField(max_length=100, blank=True, help_text=_("First name"))
    last_name = models.CharField(max_length=100, blank=True, help_text=_("Last name"))
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.ACTIVE, help_text=_("Subscription status"))
    
    # Preferences
    categories = models.ManyToManyField(Category, blank=True, help_text=_("Preferred categories"))
    frequency = models.CharField(max_length=20, default='weekly', help_text=_("Email frequency preference"))
    
    # Analytics
    open_count = models.PositiveIntegerField(default=0, help_text=_("Number of emails opened"))
    click_count = models.PositiveIntegerField(default=0, help_text=_("Number of links clicked"))
    
    # Security
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text=_("IP address when subscribed"))
    user_agent = models.TextField(blank=True, help_text=_("User agent when subscribed"))
    confirmation_token = models.CharField(max_length=64, blank=True, help_text=_("Email confirmation token"))
    is_confirmed = models.BooleanField(default=False, help_text=_("Email confirmed"))
    
    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True, help_text=_("Email confirmation date"))
    last_activity = models.DateTimeField(blank=True, null=True, help_text=_("Last activity date"))

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")
        indexes = [
            models.Index(fields=['status', 'subscribed_at']),
            models.Index(fields=['email']),
            models.Index(fields=['is_confirmed', 'status']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def generate_confirmation_token(self):
        """Generate email confirmation token"""
        import secrets
        self.confirmation_token = secrets.token_urlsafe(32)
        return self.confirmation_token

class Comment(models.Model):
    """Comments on news articles"""
    class Status(models.TextChoices):
        PENDING = 'PEN', _('Pending Approval')
        APPROVED = 'APP', _('Approved')
        REJECTED = 'REJ', _('Rejected')
        SPAM = 'SPA', _('Spam')

    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments', help_text=_("Related article"))
    author_name = models.CharField(max_length=100, help_text=_("Comment author name"))
    author_email = models.EmailField(help_text=_("Comment author email"))
    content = models.TextField(help_text=_("Comment content"))
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.PENDING, help_text=_("Comment status"))
    
    # Moderation
    is_approved = models.BooleanField(default=False, help_text=_("Comment approved"))
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, help_text=_("Moderated by"))
    moderation_notes = models.TextField(blank=True, help_text=_("Moderation notes"))
    
    # Analytics
    like_count = models.PositiveIntegerField(default=0, help_text=_("Number of likes"))
    
    # Security
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text=_("IP address"))
    user_agent = models.TextField(blank=True, help_text=_("User agent"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        indexes = [
            models.Index(fields=['article', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['is_approved', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author_name} on {self.article.title}"

class Newsletter(models.Model):
    """Newsletter campaigns"""
    class Status(models.TextChoices):
        DRAFT = 'DF', _('Draft')
        SCHEDULED = 'SC', _('Scheduled')
        SENDING = 'SE', _('Sending')
        SENT = 'SN', _('Sent')
        FAILED = 'FA', _('Failed')

    title = models.CharField(max_length=200, help_text=_("Newsletter title"))
    subject = models.CharField(max_length=200, help_text=_("Email subject"))
    content = models.TextField(help_text=_("Newsletter content"))
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, help_text=_("Newsletter status"))
    
    # Targeting
    categories = models.ManyToManyField(Category, blank=True, help_text=_("Target categories"))
    send_to_all = models.BooleanField(default=True, help_text=_("Send to all subscribers"))
    
    # Scheduling
    scheduled_date = models.DateTimeField(blank=True, null=True, help_text=_("Scheduled send date"))
    sent_date = models.DateTimeField(blank=True, null=True, help_text=_("Actual send date"))
    
    # Analytics
    total_sent = models.PositiveIntegerField(default=0, help_text=_("Total emails sent"))
    total_opened = models.PositiveIntegerField(default=0, help_text=_("Total emails opened"))
    total_clicked = models.PositiveIntegerField(default=0, help_text=_("Total links clicked"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Newsletter")
        verbose_name_plural = _("Newsletters")
        indexes = [
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['sent_date']),
        ]

    def __str__(self):
        return self.title

class ContentAnalytics(models.Model):
    """Content analytics and performance tracking"""
    content_type = models.CharField(max_length=20, help_text=_("Type of content (article, event)"))
    content_id = models.PositiveIntegerField(help_text=_("Content ID"))
    date = models.DateField(help_text=_("Analytics date"))
    
    # Metrics
    views = models.PositiveIntegerField(default=0, help_text=_("Number of views"))
    unique_views = models.PositiveIntegerField(default=0, help_text=_("Number of unique views"))
    shares = models.PositiveIntegerField(default=0, help_text=_("Number of shares"))
    comments = models.PositiveIntegerField(default=0, help_text=_("Number of comments"))
    time_on_page = models.FloatField(default=0, help_text=_("Average time on page (seconds)"))
    
    # Traffic sources
    organic_search = models.PositiveIntegerField(default=0, help_text=_("Organic search views"))
    social_media = models.PositiveIntegerField(default=0, help_text=_("Social media views"))
    direct_traffic = models.PositiveIntegerField(default=0, help_text=_("Direct traffic views"))
    referral_traffic = models.PositiveIntegerField(default=0, help_text=_("Referral traffic views"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['content_type', 'content_id', 'date']
        ordering = ['-date']
        verbose_name = _("Content Analytics")
        verbose_name_plural = _("Content Analytics")
        indexes = [
            models.Index(fields=['content_type', 'content_id', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.content_type} {self.content_id} - {self.date}"


# Cache invalidation signals
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

def _cache_delete_pattern(pattern: str) -> None:
    """Best-effort cache invalidation supporting backends without delete_pattern.
    Falls back to cache.clear() in development LocMemCache.
    """
    try:
        delete_pattern_fn = getattr(cache, 'delete_pattern', None)
        if callable(delete_pattern_fn):
            delete_pattern_fn(pattern)
        else:
            # Backends like LocMemCache don't support delete_pattern
            cache.clear()
    except Exception:
        # Never fail app flow due to cache invalidation
        pass

@receiver(post_save, sender=NewsArticle)
def invalidate_article_cache(sender, instance, **kwargs):
    """Invalidate cache when articles are saved"""
    _cache_delete_pattern('article_list_*')
    _cache_delete_pattern('featured_content_*')
    _cache_delete_pattern('recent_articles_*')
    _cache_delete_pattern('category_articles_*')
    _cache_delete_pattern('search_results_*')

@receiver(post_delete, sender=NewsArticle)
def invalidate_article_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when articles are deleted"""
    _cache_delete_pattern('article_list_*')
    _cache_delete_pattern('featured_content_*')
    _cache_delete_pattern('recent_articles_*')
    _cache_delete_pattern('category_articles_*')
    _cache_delete_pattern('search_results_*')

@receiver(post_save, sender=Event)
def invalidate_event_cache(sender, instance, **kwargs):
    """Invalidate cache when events are saved"""
    _cache_delete_pattern('event_list_*')
    _cache_delete_pattern('featured_content_*')
    _cache_delete_pattern('upcoming_events_*')
    _cache_delete_pattern('category_events_*')
    _cache_delete_pattern('search_results_*')

@receiver(post_delete, sender=Event)
def invalidate_event_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when events are deleted"""
    _cache_delete_pattern('event_list_*')
    _cache_delete_pattern('featured_content_*')
    _cache_delete_pattern('upcoming_events_*')
    _cache_delete_pattern('category_events_*')
    _cache_delete_pattern('search_results_*')

@receiver(post_save, sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    """Invalidate cache when categories are saved"""
    _cache_delete_pattern('category_list_*')
    _cache_delete_pattern('category_articles_*')
    _cache_delete_pattern('category_events_*')

@receiver(post_delete, sender=Category)
def invalidate_category_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when categories are deleted"""
    _cache_delete_pattern('category_list_*')
    _cache_delete_pattern('category_articles_*')
    _cache_delete_pattern('category_events_*')

@receiver(post_save, sender=Comment)
def invalidate_comment_cache(sender, instance, **kwargs):
    """Invalidate cache when comments are saved"""
    _cache_delete_pattern(f'article_comments_{instance.article.id}_*')
    _cache_delete_pattern('comment_stats_*')

@receiver(post_delete, sender=Comment)
def invalidate_comment_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when comments are deleted"""
    _cache_delete_pattern(f'article_comments_{instance.article.id}_*')
    _cache_delete_pattern('comment_stats_*')
