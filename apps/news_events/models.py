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
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit, Transpose
from .managers import ArticleManager, EventManager

logger = logging.getLogger(__name__)

# Try to import unidecode for Nepali character transliteration
try:
    from unidecode import unidecode
    UNIDECODE_AVAILABLE = True
except ImportError:
    UNIDECODE_AVAILABLE = False
    logger.warning("unidecode not available. Nepali slug generation will use hash fallback.")

def slugify_nepali(text):
    """
    Generate a slug from text, handling Nepali and other Unicode characters.
    Falls back to hash-based slug if unidecode is not available.
    """
    if not text:
        return ""
    
    # Try to transliterate Nepali/Unicode to ASCII using unidecode
    if UNIDECODE_AVAILABLE:
        try:
            # Transliterate Unicode characters to ASCII
            ascii_text = unidecode(str(text))
            # Generate slug from transliterated text
            slug = slugify(ascii_text)
            # If slug is still empty after transliteration, use hash fallback
            if not slug:
                slug = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
            return slug
        except Exception as e:
            logger.warning(f"Error transliterating text for slug: {e}")
            # Fall through to hash-based approach
    
    # Fallback: Use hash-based slug for Nepali characters
    # This ensures we always have a valid slug even without unidecode
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
    # Try to get some readable part from the text if possible
    try:
        # Extract any ASCII characters that might exist
        ascii_part = ''.join(c for c in text if c.isalnum() and ord(c) < 128)
        if ascii_part:
            base_slug = slugify(ascii_part)
            if base_slug:
                return f"{base_slug}-{text_hash}"
    except Exception:
        pass
    
    # Final fallback: just use hash
    return text_hash

# Import constants for read time calculation
try:
    from .constants import AVERAGE_WORDS_PER_MINUTE, MIN_READ_TIME_MINUTES
except ImportError:
    # Fallback if constants not available
    AVERAGE_WORDS_PER_MINUTE = 200
    MIN_READ_TIME_MINUTES = 1

# Helper function to calculate read time
def calculate_read_time(content: str) -> int:
    """
    Calculate estimated reading time in minutes.
    
    Args:
        content: Article content text
        
    Returns:
        Estimated reading time in minutes (minimum 1)
    """
    if not content:
        return 0
    word_count = len(content.split())
    # Assumes an average reading speed (configurable via constants)
    read_time = (word_count + AVERAGE_WORDS_PER_MINUTE - 1) // AVERAGE_WORDS_PER_MINUTE
    return max(MIN_READ_TIME_MINUTES, read_time)

class Category(models.Model):
    """News and events categories"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"), help_text=_("Name of the category"))
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name=_("Slug"), help_text=_("URL-friendly version"))
    description = models.TextField(blank=True, verbose_name=_("Description"), help_text=_("Category description"))
    color = models.CharField(max_length=7, default="#28A745", verbose_name=_("Color"), help_text=_("Hex color code for the category"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon"), help_text=_("FontAwesome icon class"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"), help_text=_("Whether this category is active"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort Order"), help_text=_("Order for display"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

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
            self.slug = slugify_nepali(self.name)
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
    title = models.CharField(max_length=200, verbose_name=_("Title"), help_text=_("Title of the article"))
    slug = models.SlugField(unique=True, blank=True, max_length=250, verbose_name=_("Slug"), help_text=_("URL-friendly title"))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='articles', verbose_name=_("Category"), help_text=_("Category of the article"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_events_articles', verbose_name=_("Author"), help_text=_("Author of the article"))
    
    # Content fields
    content = models.TextField(verbose_name=_("Content"), help_text=_("Content of the article"))
    excerpt = models.TextField(blank=True, max_length=500, verbose_name=_("Excerpt"), help_text=_("Short article summary"))
    image = models.ImageField(upload_to='news_events/images/', blank=True, null=True, verbose_name=_("Image"), help_text=_("Main image"))
    image_alt = models.CharField(max_length=200, blank=True, verbose_name=_("Image Alt Text"), help_text=_("Alt text for the image"))
    
    # Optimized image variants (automatically generated on save)
    # Thumbnail for list views (300x200, WebP format)
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[
            Transpose(),  # Auto-rotate based on EXIF
            ResizeToFill(300, 200),
        ],
        format='WEBP',
        options={'quality': 85}
    )
    
    # Medium size for detail pages (800x600, WebP format)
    image_medium = ImageSpecField(
        source='image',
        processors=[
            Transpose(),
            ResizeToFit(800, 600),
        ],
        format='WEBP',
        options={'quality': 90}
    )
    
    # Large size for featured content (1200x800, WebP format)
    image_large = ImageSpecField(
        source='image',
        processors=[
            Transpose(),
            ResizeToFit(1200, 800),
        ],
        format='WEBP',
        options={'quality': 92}
    )
    
    # WebP version of original (for maximum compatibility)
    image_webp = ImageSpecField(
        source='image',
        processors=[
            Transpose(),
        ],
        format='WEBP',
        options={'quality': 95}
    )
    
    # Metadata
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Status"), help_text=_("Publication status"))
    priority = models.CharField(max_length=4, choices=Priority.choices, default=Priority.MEDIUM, verbose_name=_("Priority"), help_text=_("Content priority"))
    published_date = models.DateTimeField(default=timezone.now, verbose_name=_("Published Date"), help_text=_("Publication date"))
    scheduled_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Scheduled Date"), help_text=_("Scheduled publication date"))
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_("SEO Title"), help_text=_("SEO title"))
    meta_description = models.TextField(blank=True, max_length=300, verbose_name=_("SEO Description"), help_text=_("SEO description"))
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name=_("SEO Keywords"), help_text=_("SEO keywords"))
    
    # Analytics fields
    read_time = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("Read Time"), help_text=_("Estimated reading time (in minutes)"))
    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("View Count"), help_text=_("Number of views"))
    share_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("Share Count"), help_text=_("Number of shares"))
    comment_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("Comment Count"), help_text=_("Number of comments"))
    
    # Security fields
    content_hash = models.CharField(max_length=64, blank=True, editable=False, verbose_name=_("Content Hash"), help_text=_("SHA-256 hash of the content"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Is Featured"), help_text=_("Featured article"))
    allow_comments = models.BooleanField(default=True, verbose_name=_("Allow Comments"), help_text=_("Allow comments for this article"))
    require_login = models.BooleanField(default=False, verbose_name=_("Require Login"), help_text=_("Login required to view"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Accessed"), help_text=_("Last accessed time"))

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
            self.slug = slugify_nepali(self.title)
        
        # Ensure slug is unique by appending hash if needed
        if self.slug:
            original_slug = self.slug
            counter = 1
            while NewsArticle.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                # Append counter to make it unique
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                # Safety check to prevent infinite loop
                if counter > 1000:
                    # Use hash as last resort
                    self.slug = f"{original_slug}-{hashlib.md5(self.title.encode('utf-8')).hexdigest()[:8]}"
                    break
        
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
    
    @property
    def optimized_image_url(self):
        """
        Get optimized image URL (WebP format, automatically resized).
        Falls back to original image if optimization not available.
        Includes CDN URL support if configured.
        """
        if not self.image:
            return None
            
        try:
            # Try to get WebP version first (best compression)
            # Check if image_webp exists and has a file
            # Always use original image URL for now
            # WebP conversion will happen automatically when imagekit processes it
            # Accessing image_webp.url might trigger generation which can cause issues
            url = self.image.url
            
            # Apply CDN URL if configured
            if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
                from .performance import NewsEventsCDNManager
                return NewsEventsCDNManager.get_cdn_url(url)
            
            return url
        except Exception as e:
            logger.warning(f"Error getting optimized image for article {self.id}: {e}")
            # Final fallback to original image
            try:
                url = self.image.url
                if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
                    from .performance import NewsEventsCDNManager
                    return NewsEventsCDNManager.get_cdn_url(url)
                return url
            except Exception:
                return None

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
    title = models.CharField(max_length=200, verbose_name=_("Title"), help_text=_("Title of the event"))
    slug = models.SlugField(unique=True, blank=True, max_length=250, verbose_name=_("Slug"), help_text=_("URL-friendly title"))
    description = models.TextField(verbose_name=_("Description"), help_text=_("Description of the event"))
    short_description = models.TextField(blank=True, max_length=300, verbose_name=_("Short Description"), help_text=_("Brief event description"))
    
    # Event details
    event_type = models.CharField(max_length=5, choices=EventType.choices, default=EventType.OTHER, verbose_name=_("Event Type"), help_text=_("Type of the event"))
    location = models.CharField(max_length=150, default=_("Cooperative Office"), verbose_name=_("Location"), help_text=_("Event location"))
    address = models.TextField(blank=True, verbose_name=_("Address"), help_text=_("Full event address"))
    event_date = models.DateTimeField(verbose_name=_("Event Date"), help_text=_("Event date and time"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End Date"), help_text=_("Event end date and time"))
    
    # Registration
    max_attendees = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Max Attendees"), help_text=_("Maximum number of attendees"))
    registration_required = models.BooleanField(default=False, verbose_name=_("Registration Required"), help_text=_("Is registration required"))
    registration_deadline = models.DateTimeField(blank=True, null=True, verbose_name=_("Registration Deadline"), help_text=_("Registration deadline"))
    registration_url = models.URLField(blank=True, verbose_name=_("Registration URL"), help_text=_("Registration URL"))
    
    # Media
    image = models.ImageField(upload_to='news_events/events/', blank=True, null=True, verbose_name=_("Image"), help_text=_("Event image"))
    image_alt = models.CharField(max_length=200, blank=True, verbose_name=_("Image Alt Text"), help_text=_("Alt text for the image"))
    
    # Optimized image variants (automatically generated on save)
    # Thumbnail for list views (300x200, WebP format)
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[
            Transpose(),
            ResizeToFill(300, 200),
        ],
        format='WEBP',
        options={'quality': 85}
    )
    
    # Medium size for detail pages (800x600, WebP format)
    image_medium = ImageSpecField(
        source='image',
        processors=[
            Transpose(),
            ResizeToFit(800, 600),
        ],
        format='WEBP',
        options={'quality': 90}
    )
    
    # Large size for featured content (1200x800, WebP format)
    image_large = ImageSpecField(
        source='image',
        processors=[
            Transpose(),
            ResizeToFit(1200, 800),
        ],
        format='WEBP',
        options={'quality': 92}
    )
    
    # WebP version of original
    image_webp = ImageSpecField(
        source='image',
        processors=[
            Transpose(),
        ],
        format='WEBP',
        options={'quality': 95}
    )
    
    # Status and visibility
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Status"), help_text=_("Event status"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Is Featured"), help_text=_("Featured event"))
    is_recurring = models.BooleanField(default=False, verbose_name=_("Is Recurring"), help_text=_("Recurring event"))
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("View Count"), help_text=_("Number of views"))
    registration_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("Registration Count"), help_text=_("Number of registrations"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Accessed"), help_text=_("Last accessed time"))

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
            self.slug = slugify_nepali(self.title)
        
        # Ensure slug is unique by appending hash if needed
        if self.slug:
            original_slug = self.slug
            counter = 1
            while Event.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                # Append counter to make it unique
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                # Safety check to prevent infinite loop
                if counter > 1000:
                    # Use hash as last resort
                    self.slug = f"{original_slug}-{hashlib.md5(self.title.encode('utf-8')).hexdigest()[:8]}"
                    break
        
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
    
    @property
    def optimized_image_url(self):
        """
        Get optimized image URL (WebP format, automatically resized).
        Falls back to original image if optimization not available.
        Includes CDN URL support if configured.
        """
        if not self.image:
            return None
            
        try:
            # Try to get WebP version first (best compression)
            # Check if image_webp exists and has a file
            # Always use original image URL for now
            # WebP conversion will happen automatically when imagekit processes it
            # Accessing image_webp.url might trigger generation which can cause issues
            url = self.image.url
            
            # Apply CDN URL if configured
            if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
                from .performance import NewsEventsCDNManager
                return NewsEventsCDNManager.get_cdn_url(url)
            
            return url
        except Exception as e:
            logger.warning(f"Error getting optimized image for event {self.id}: {e}")
            # Final fallback to original image
            try:
                url = self.image.url
                if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
                    from .performance import NewsEventsCDNManager
                    return NewsEventsCDNManager.get_cdn_url(url)
                return url
            except Exception:
                return None

class Subscriber(models.Model):
    """Newsletter subscribers with enhanced features"""
    class Status(models.TextChoices):
        ACTIVE = 'ACT', _('Active')
        UNSUBSCRIBED = 'UNS', _('Unsubscribed')
        BOUNCED = 'BOU', _('Bounced')
        SPAM = 'SPA', _('Spam')

    email = models.EmailField(unique=True, verbose_name=_("Email"), help_text=_("Subscriber email address"))
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_("First Name"), help_text=_("First name"))
    last_name = models.CharField(max_length=100, blank=True, verbose_name=_("Last Name"), help_text=_("Last name"))
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.ACTIVE, verbose_name=_("Status"), help_text=_("Subscription status"))
    
    # Preferences
    categories = models.ManyToManyField(Category, blank=True, verbose_name=_("Preferred Categories"), help_text=_("Preferred categories"))
    frequency = models.CharField(max_length=20, default=_('weekly'), verbose_name=_("Frequency"), help_text=_("Email frequency preference"))
    
    # Analytics
    open_count = models.PositiveIntegerField(default=0, verbose_name=_("Open Count"), help_text=_("Number of emails opened"))
    click_count = models.PositiveIntegerField(default=0, verbose_name=_("Click Count"), help_text=_("Number of links clicked"))
    
    # Security
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP Address"), help_text=_("IP address during subscription"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"), help_text=_("User agent during subscription"))
    confirmation_token = models.CharField(max_length=64, blank=True, verbose_name=_("Confirmation Token"), help_text=_("Email confirmation token"))
    is_confirmed = models.BooleanField(default=False, verbose_name=_("Is Confirmed"), help_text=_("Whether email is confirmed"))
    
    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Subscribed At"))
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Confirmed At"), help_text=_("Email confirmation date"))
    last_activity = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Activity Date"), help_text=_("Last activity date"))

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

    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments', verbose_name=_("Article"), help_text=_("Related article"))
    author_name = models.CharField(max_length=100, verbose_name=_("Author Name"), help_text=_("Comment author's name"))
    author_email = models.EmailField(verbose_name=_("Author Email"), help_text=_("Comment author's email"))
    content = models.TextField(verbose_name=_("Content"), help_text=_("Comment content"))
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.PENDING, verbose_name=_("Status"), help_text=_("Comment status"))
    
    # Moderation
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved"), help_text=_("Whether comment is approved"))
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Moderated By"), help_text=_("User who moderated"))
    moderation_notes = models.TextField(blank=True, verbose_name=_("Moderation Notes"), help_text=_("Moderation notes"))
    
    # Analytics
    like_count = models.PositiveIntegerField(default=0, verbose_name=_("Like Count"), help_text=_("Number of likes"))
    
    # Security
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP Address"), help_text=_("IP address"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"), help_text=_("User agent"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

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

    title = models.CharField(max_length=200, verbose_name=_("Title"), help_text=_("Newsletter title"))
    subject = models.CharField(max_length=200, verbose_name=_("Subject"), help_text=_("Email subject"))
    content = models.TextField(verbose_name=_("Content"), help_text=_("Newsletter content"))
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Status"), help_text=_("Newsletter status"))
    
    # Targeting
    categories = models.ManyToManyField(Category, blank=True, verbose_name=_("Target Categories"), help_text=_("Target categories"))
    send_to_all = models.BooleanField(default=True, verbose_name=_("Send to All"), help_text=_("Send to all subscribers"))
    
    # Scheduling
    scheduled_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Scheduled Date"), help_text=_("Scheduled send date"))
    sent_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Sent Date"), help_text=_("Actual send date"))
    
    # Analytics
    total_sent = models.PositiveIntegerField(default=0, verbose_name=_("Total Sent"), help_text=_("Total emails sent"))
    total_opened = models.PositiveIntegerField(default=0, verbose_name=_("Total Opened"), help_text=_("Total emails opened"))
    total_clicked = models.PositiveIntegerField(default=0, verbose_name=_("Total Clicked"), help_text=_("Total links clicked"))
    failed_recipients = models.TextField(blank=True, verbose_name=_("Failed Recipients"), help_text=_("List of recipients who failed to receive email (JSON format)"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

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
    content_type = models.CharField(max_length=20, verbose_name=_("Content Type"), help_text=_("Content type (article, event)"))
    content_id = models.PositiveIntegerField(verbose_name=_("Content ID"), help_text=_("Content identifier"))
    date = models.DateField(verbose_name=_("Date"), help_text=_("Analytics date"))
    
    # Metrics
    views = models.PositiveIntegerField(default=0, verbose_name=_("Views"), help_text=_("Number of views"))
    unique_views = models.PositiveIntegerField(default=0, verbose_name=_("Unique Views"), help_text=_("Number of unique views"))
    shares = models.PositiveIntegerField(default=0, verbose_name=_("Shares"), help_text=_("Number of shares"))
    comments = models.PositiveIntegerField(default=0, verbose_name=_("Comments"), help_text=_("Number of comments"))
    time_on_page = models.FloatField(default=0, verbose_name=_("Time on Page"), help_text=_("Average time on page (in seconds)"))
    
    # Traffic sources
    organic_search = models.PositiveIntegerField(default=0, verbose_name=_("Organic Search"), help_text=_("Organic search views"))
    social_media = models.PositiveIntegerField(default=0, verbose_name=_("Social Media"), help_text=_("Social media views"))
    direct_traffic = models.PositiveIntegerField(default=0, verbose_name=_("Direct Traffic"), help_text=_("Direct traffic views"))
    referral_traffic = models.PositiveIntegerField(default=0, verbose_name=_("Referral Traffic"), help_text=_("Referral traffic views"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

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


class Notice(models.Model):
    """Notices (Soochana) for general public information"""
    class Type(models.TextChoices):
        GENERAL = 'GEN', _('General Notice')
        URGENT = 'URG', _('Urgent Notice')
        AGM = 'AGM', _('Annual General Meeting')
        TENDER = 'TEN', _('Tender Notice')
        OTHER = 'OTH', _('Other')

    title = models.CharField(max_length=200, verbose_name=_("Title"), help_text=_("Notice title"))
    slug = models.SlugField(unique=True, blank=True, max_length=250, verbose_name=_("Slug"), help_text=_("URL-friendly title"))
    content = models.TextField(verbose_name=_("Description"), help_text=_("Detailed description of the notice"))
    
    # Optional file attachment (e.g., scanned PDF)
    file = models.FileField(upload_to='news_events/notices/', blank=True, null=True, verbose_name=_("File"), help_text=_("Notice file (PDF/Image)"))
    
    notice_type = models.CharField(max_length=3, choices=Type.choices, default=Type.GENERAL, verbose_name=_("Type"), help_text=_("Notice type"))
    published_date = models.DateTimeField(default=timezone.now, verbose_name=_("Published Date"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"), help_text=_("Whether notice is active"))
    is_pinned = models.BooleanField(default=False, verbose_name=_("Pinned"), help_text=_("Pin to top"))
    show_as_popup = models.BooleanField(default=False, verbose_name=_("Show as Popup"), help_text=_("Check if this notice should be shown in a popup modal on the home page"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    @property
    def is_currently_active(self):
        """Check if notice should be displayed (for popup compatibility)"""
        return self.is_active

    class Meta:
        ordering = ['-is_pinned', '-published_date']
        verbose_name = _("Notice")
        verbose_name_plural = _("Notices")
        indexes = [
            models.Index(fields=['is_active', 'published_date']),
            models.Index(fields=['is_pinned']),
            models.Index(fields=['show_as_popup', 'is_active']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_events:notice-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_nepali(self.title)
        
        # Ensure slug is unique
        if self.slug:
            original_slug = self.slug
            counter = 1
            while Notice.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)


class PopupNotice(models.Model):
    """Popup notice model for home page modal notices (e.g., AGM notices)"""
    
    class NoticeType(models.TextChoices):
        AGM = 'agm', _('Annual General Meeting (AGM)')
        EGM = 'egm', _('Extraordinary General Meeting (EGM)')
        GENERAL = 'general', _('General Notice')
        IMPORTANT = 'important', _('Important Notice')
        EVENT = 'event', _('Event')
        OTHER = 'other', _('Other')
    
    # Basic Information
    title = models.CharField(
        max_length=200, 
        verbose_name=_("Title"),
        help_text=_("Popup notice title (e.g., '14th Annual General Meeting Notice')")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Short description of the notice (optional)")
    )
    notice_type = models.CharField(
        max_length=20,
        choices=NoticeType.choices,
        default=NoticeType.GENERAL,
        verbose_name=_("Notice Type"),
        help_text=_("Select the type of notice")
    )
    
    # Image
    image = models.ImageField(
        upload_to='news_events/popup_notices/',
        verbose_name=_("Notice Image"),
        help_text=_("Image to display in the popup (JPG, PNG format)")
    )
    image_alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Image Alt Text"),
        help_text=_("Alt text for the image (for accessibility)")
    )
    
    # Link (optional)
    link_url = models.URLField(
        blank=True,
        verbose_name=_("Link URL"),
        help_text=_("URL if the image should link to another page (optional)")
    )
    link_text = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Link Text"),
        help_text=_("Text for the link button (optional)")
    )
    open_in_new_tab = models.BooleanField(
        default=False,
        verbose_name=_("Open in New Tab"),
        help_text=_("Check if the link should open in a new tab")
    )
    
    # Display Settings
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Priority"),
        help_text=_("Higher priority notices appear first. If multiple active notices exist, highest priority shows.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Check this to show the popup on home page. Uncheck to hide without deleting.")
    )
    
    # Date Settings
    start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Start Date"),
        help_text=_("When to start showing (default: now)")
    )
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("End Date"),
        help_text=_("When to stop showing (blank = show indefinitely)")
    )
    
    # Auto-close Duration (in seconds)
    auto_close_duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Auto-Close Duration (Seconds)"),
        help_text=_("Seconds before popup auto-closes (blank = manual close only)")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Popup Notice")
        verbose_name_plural = _("Popup Notices")
        ordering = ['-priority', '-start_date']
        indexes = [
            models.Index(fields=['is_active', 'start_date', 'end_date']),
            models.Index(fields=['priority', 'is_active']),
            models.Index(fields=['notice_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_notice_type_display()})"
    
    @property
    def is_currently_active(self):
        """Check if notice should be displayed now"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        if now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def clean(self):
        """Validate model data"""
        from django.core.exceptions import ValidationError
        
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError({
                'end_date': _('End date must be after start date.')
            })


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
    from .performance import NewsEventsCache
    
    _cache_delete_pattern('article_list_*')
    _cache_delete_pattern('featured_content_*')
    _cache_delete_pattern('recent_articles_*')
    _cache_delete_pattern('category_articles_*')
    _cache_delete_pattern('search_results_*')
    
    # Clear invalid slug cache for this article's slug
    # This ensures newly created articles work even if slug was previously cached as invalid
    if instance.slug:
        cache_key = NewsEventsCache.get_invalid_slug_cache_key('article', instance.slug)
        cache.delete(cache_key)

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
    from .performance import NewsEventsCache
    
    _cache_delete_pattern('event_list_*')
    _cache_delete_pattern('featured_content_*')
    _cache_delete_pattern('upcoming_events_*')
    _cache_delete_pattern('category_events_*')
    _cache_delete_pattern('search_results_*')
    
    # Clear invalid slug cache for this event's slug
    # This ensures newly created events work even if slug was previously cached as invalid
    if instance.slug:
        cache_key = NewsEventsCache.get_invalid_slug_cache_key('event', instance.slug)
        cache.delete(cache_key)

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


@receiver(post_save, sender=PopupNotice)
@receiver(post_delete, sender=PopupNotice)
def invalidate_popup_notice_cache(sender, instance, **kwargs):
    """Invalidate homepage cache when popup notice is saved or deleted"""
    # Clear homepage cache to ensure popup notice updates immediately
    try:
        # Clear both staff and non-staff cache
        cache.delete('homepage_data_True')
        cache.delete('homepage_data_False')
        # Also use pattern deletion if available
        _cache_delete_pattern('homepage_data_*')
        logger.info(f"Homepage cache cleared due to PopupNotice change: {instance.title if hasattr(instance, 'title') else 'deleted'}")
    except Exception as e:
        logger.warning(f"Failed to clear homepage cache: {e}")

@receiver(post_save, sender=Notice)
def invalidate_notice_cache(sender, instance, **kwargs):
    """Invalidate cache when notices are saved"""
    _cache_delete_pattern('notice_list_*')
    _cache_delete_pattern('notice_detail_*')
    # Clear invalid slug cache for this notice's slug
    if instance.slug:
        try:
            from .performance import NewsEventsCache
            cache_key = NewsEventsCache.get_invalid_slug_cache_key('notice', instance.slug)
            cache.delete(cache_key)
        except Exception:
            pass

@receiver(post_delete, sender=Notice)
def invalidate_notice_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when notices are deleted"""
    _cache_delete_pattern('notice_list_*')
    _cache_delete_pattern('notice_detail_*')
