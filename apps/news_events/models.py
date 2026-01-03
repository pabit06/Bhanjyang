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
    name = models.CharField(max_length=100, unique=True, verbose_name=_("नाम"), help_text=_("श्रेणीको नाम"))
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name=_("स्लग"), help_text=_("URL-अनुकूल संस्करण"))
    description = models.TextField(blank=True, verbose_name=_("विवरण"), help_text=_("श्रेणीको विवरण"))
    color = models.CharField(max_length=7, default="#28A745", verbose_name=_("रङ"), help_text=_("श्रेणीको हेक्स रङ कोड"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("आइकन"), help_text=_("FontAwesome आइकन क्लास"))
    is_active = models.BooleanField(default=True, verbose_name=_("सक्रिय"), help_text=_("यो श्रेणी सक्रिय छ कि छैन"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("क्रम"), help_text=_("प्रदर्शनको लागि क्रम"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("सिर्जना मिति"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("अपडेट मिति"))

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = _("श्रेणी")
        verbose_name_plural = _("श्रेणीहरू")
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
        DRAFT = 'DF', _('मस्यौदा')
        PUBLISHED = 'PB', _('प्रकाशित')
        ARCHIVED = 'AR', _('संग्रह')
        SCHEDULED = 'SC', _('तालिकाबद्ध')

    class Priority(models.TextChoices):
        LOW = 'LOW', _('न्यून प्राथमिकता')
        MEDIUM = 'MED', _('मध्यम प्राथमिकता')
        HIGH = 'HIGH', _('उच्च प्राथमिकता')
        URGENT = 'URG', _('तत्काल')

    # Basic fields
    title = models.CharField(max_length=200, verbose_name=_("शीर्षक"), help_text=_("लेखको शीर्षक"))
    slug = models.SlugField(unique=True, blank=True, max_length=250, verbose_name=_("स्लग"), help_text=_("URL-अनुकूल शीर्षक"))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='articles', verbose_name=_("श्रेणी"), help_text=_("लेखको श्रेणी"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_events_articles', verbose_name=_("लेखक"), help_text=_("लेखको लेखक"))
    
    # Content fields
    content = models.TextField(verbose_name=_("सामग्री"), help_text=_("लेखको सामग्री"))
    excerpt = models.TextField(blank=True, max_length=500, verbose_name=_("सारांश"), help_text=_("छोटो लेख सारांश"))
    image = models.ImageField(upload_to='news_events/images/', blank=True, null=True, verbose_name=_("छवि"), help_text=_("मुख्य छवि"))
    image_alt = models.CharField(max_length=200, blank=True, verbose_name=_("छवि Alt पाठ"), help_text=_("छविको Alt पाठ"))
    
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
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name=_("स्थिति"), help_text=_("प्रकाशन स्थिति"))
    priority = models.CharField(max_length=4, choices=Priority.choices, default=Priority.MEDIUM, verbose_name=_("प्राथमिकता"), help_text=_("सामग्री प्राथमिकता"))
    published_date = models.DateTimeField(default=timezone.now, verbose_name=_("प्रकाशन मिति"), help_text=_("प्रकाशन मिति"))
    scheduled_date = models.DateTimeField(blank=True, null=True, verbose_name=_("तालिकाबद्ध मिति"), help_text=_("तालिकाबद्ध प्रकाशन मिति"))
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_("SEO शीर्षक"), help_text=_("SEO शीर्षक"))
    meta_description = models.TextField(blank=True, max_length=300, verbose_name=_("SEO विवरण"), help_text=_("SEO विवरण"))
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name=_("SEO कीवर्ड"), help_text=_("SEO कीवर्ड"))
    
    # Analytics fields
    read_time = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("पढ्ने समय"), help_text=_("अनुमानित पढ्ने समय (मिनेटमा)"))
    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("हेराइ संख्या"), help_text=_("हेराइको संख्या"))
    share_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("साझेदारी संख्या"), help_text=_("साझेदारीको संख्या"))
    comment_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("टिप्पणी संख्या"), help_text=_("टिप्पणीको संख्या"))
    
    # Security fields
    content_hash = models.CharField(max_length=64, blank=True, editable=False, verbose_name=_("सामग्री ह्यास"), help_text=_("सामग्रीको SHA-256 ह्यास"))
    is_featured = models.BooleanField(default=False, verbose_name=_("मुख्य"), help_text=_("मुख्य लेख"))
    allow_comments = models.BooleanField(default=True, verbose_name=_("टिप्पणी अनुमति"), help_text=_("टिप्पणी अनुमति दिनुहोस्"))
    require_login = models.BooleanField(default=False, verbose_name=_("लगइन आवश्यक"), help_text=_("हेर्नको लागि लगइन आवश्यक"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("सिर्जना मिति"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("अपडेट मिति"))
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name=_("अन्तिम पहुँच मिति"), help_text=_("अन्तिम पहुँच समय"))

    objects = ArticleManager()

    class Meta:
        ordering = ['-published_date']
        verbose_name = _("समाचार लेख")
        verbose_name_plural = _("समाचार लेखहरू")
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
    
    @property
    def optimized_image_url(self):
        """
        Get optimized image URL (WebP format, automatically resized).
        Falls back to original image if optimization not available.
        Includes CDN URL support if configured.
        """
        if self.image:
            try:
                # Try to get WebP version first (best compression)
                if hasattr(self, 'image_webp') and self.image_webp:
                    url = self.image_webp.url
                else:
                    # Fallback to original
                    url = self.image.url
                
                # Apply CDN URL if configured
                if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
                    from .performance import NewsEventsCDNManager
                    return NewsEventsCDNManager.get_cdn_url(url)
                
                return url
            except Exception as e:
                logger.warning(f"Error getting optimized image for article {self.id}: {e}")
                if self.image:
                    url = self.image.url
                    # Apply CDN URL if configured
                    if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
                        from .performance import NewsEventsCDNManager
                        return NewsEventsCDNManager.get_cdn_url(url)
                    return url
                return None
        return None

class Event(models.Model):
    """Events with enhanced features"""
    class EventType(models.TextChoices):
        MEETING = 'MEET', _('बैठक')
        WORKSHOP = 'WORK', _('कार्यशाला')
        CONFERENCE = 'CONF', _('सम्मेलन')
        SEMINAR = 'SEMI', _('सेमिनार')
        SOCIAL = 'SOC', _('सामाजिक कार्यक्रम')
        TRAINING = 'TRAIN', _('प्रशिक्षण')
        OTHER = 'OTH', _('अन्य')

    class Status(models.TextChoices):
        DRAFT = 'DF', _('मस्यौदा')
        PUBLISHED = 'PB', _('प्रकाशित')
        CANCELLED = 'CAN', _('रद्द')
        COMPLETED = 'COM', _('पूर्ण')

    # Basic fields
    title = models.CharField(max_length=200, verbose_name=_("शीर्षक"), help_text=_("कार्यक्रमको शीर्षक"))
    slug = models.SlugField(unique=True, blank=True, max_length=250, verbose_name=_("स्लग"), help_text=_("URL-अनुकूल शीर्षक"))
    description = models.TextField(verbose_name=_("विवरण"), help_text=_("कार्यक्रमको विवरण"))
    short_description = models.TextField(blank=True, max_length=300, verbose_name=_("छोटो विवरण"), help_text=_("छोटो कार्यक्रम विवरण"))
    
    # Event details
    event_type = models.CharField(max_length=5, choices=EventType.choices, default=EventType.OTHER, verbose_name=_("कार्यक्रम प्रकार"), help_text=_("कार्यक्रमको प्रकार"))
    location = models.CharField(max_length=150, default="Cooperative Office", verbose_name=_("स्थान"), help_text=_("कार्यक्रम स्थान"))
    address = models.TextField(blank=True, verbose_name=_("ठेगाना"), help_text=_("पूर्ण कार्यक्रम ठेगाना"))
    event_date = models.DateTimeField(verbose_name=_("कार्यक्रम मिति"), help_text=_("कार्यक्रम मिति र समय"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("अन्त्य मिति"), help_text=_("कार्यक्रम अन्त्य मिति र समय"))
    
    # Registration
    max_attendees = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("अधिकतम सहभागी"), help_text=_("अधिकतम सहभागी संख्या"))
    registration_required = models.BooleanField(default=False, verbose_name=_("दर्ता आवश्यक"), help_text=_("दर्ता आवश्यक"))
    registration_deadline = models.DateTimeField(blank=True, null=True, verbose_name=_("दर्ता अन्तिम मिति"), help_text=_("दर्ता अन्तिम मिति"))
    registration_url = models.URLField(blank=True, verbose_name=_("दर्ता URL"), help_text=_("दर्ता URL"))
    
    # Media
    image = models.ImageField(upload_to='news_events/events/', blank=True, null=True, verbose_name=_("छवि"), help_text=_("कार्यक्रम छवि"))
    image_alt = models.CharField(max_length=200, blank=True, verbose_name=_("छवि Alt पाठ"), help_text=_("छविको Alt पाठ"))
    
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
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.DRAFT, verbose_name=_("स्थिति"), help_text=_("कार्यक्रम स्थिति"))
    is_featured = models.BooleanField(default=False, verbose_name=_("मुख्य"), help_text=_("मुख्य कार्यक्रम"))
    is_recurring = models.BooleanField(default=False, verbose_name=_("पुनरावृत्ति"), help_text=_("पुनरावृत्ति हुने कार्यक्रम"))
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("हेराइ संख्या"), help_text=_("हेराइको संख्या"))
    registration_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("दर्ता संख्या"), help_text=_("दर्ताको संख्या"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("सिर्जना मिति"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("अपडेट मिति"))
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name=_("अन्तिम पहुँच मिति"), help_text=_("अन्तिम पहुँच समय"))

    objects = EventManager()

    class Meta:
        ordering = ['event_date']
        verbose_name = _("कार्यक्रम")
        verbose_name_plural = _("कार्यक्रमहरू")
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
    
    @property
    def optimized_image_url(self):
        """
        Get optimized image URL (WebP format, automatically resized).
        Falls back to original image if optimization not available.
        Includes CDN URL support if configured.
        """
        if self.image:
            try:
                # Try to get WebP version first (best compression)
                if hasattr(self, 'image_webp') and self.image_webp:
                    url = self.image_webp.url
                else:
                    # Fallback to original
                    url = self.image.url
                
                # Apply CDN URL if configured
                if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
                    from .performance import NewsEventsCDNManager
                    return NewsEventsCDNManager.get_cdn_url(url)
                
                return url
            except Exception as e:
                logger.warning(f"Error getting optimized image for event {self.id}: {e}")
                if self.image:
                    url = self.image.url
                    # Apply CDN URL if configured
                    if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
                        from .performance import NewsEventsCDNManager
                        return NewsEventsCDNManager.get_cdn_url(url)
                    return url
                return None
        return None

class Subscriber(models.Model):
    """Newsletter subscribers with enhanced features"""
    class Status(models.TextChoices):
        ACTIVE = 'ACT', _('सक्रिय')
        UNSUBSCRIBED = 'UNS', _('सदस्यता रद्द')
        BOUNCED = 'BOU', _('बाउन्स')
        SPAM = 'SPA', _('स्प्याम')

    email = models.EmailField(unique=True, verbose_name=_("इमेल"), help_text=_("सदस्यको इमेल"))
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_("पहिलो नाम"), help_text=_("पहिलो नाम"))
    last_name = models.CharField(max_length=100, blank=True, verbose_name=_("अन्तिम नाम"), help_text=_("अन्तिम नाम"))
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.ACTIVE, verbose_name=_("स्थिति"), help_text=_("सदस्यता स्थिति"))
    
    # Preferences
    categories = models.ManyToManyField(Category, blank=True, verbose_name=_("प्राथमिकता श्रेणी"), help_text=_("प्राथमिकता श्रेणीहरू"))
    frequency = models.CharField(max_length=20, default='weekly', verbose_name=_("आवृत्ति"), help_text=_("इमेल आवृत्ति प्राथमिकता"))
    
    # Analytics
    open_count = models.PositiveIntegerField(default=0, verbose_name=_("खोलिएको संख्या"), help_text=_("खोलिएको इमेल संख्या"))
    click_count = models.PositiveIntegerField(default=0, verbose_name=_("क्लिक संख्या"), help_text=_("क्लिक गरिएको लिङ्क संख्या"))
    
    # Security
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP ठेगाना"), help_text=_("सदस्यता लिँदा IP ठेगाना"))
    user_agent = models.TextField(blank=True, verbose_name=_("प्रयोगकर्ता एजेन्ट"), help_text=_("सदस्यता लिँदा प्रयोगकर्ता एजेन्ट"))
    confirmation_token = models.CharField(max_length=64, blank=True, verbose_name=_("पुष्टिकरण टोकन"), help_text=_("इमेल पुष्टिकरण टोकन"))
    is_confirmed = models.BooleanField(default=False, verbose_name=_("पुष्टि भएको"), help_text=_("इमेल पुष्टि भएको"))
    
    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("सदस्यता मिति"))
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name=_("पुष्टि मिति"), help_text=_("इमेल पुष्टि मिति"))
    last_activity = models.DateTimeField(blank=True, null=True, verbose_name=_("अन्तिम गतिविधि मिति"), help_text=_("अन्तिम गतिविधि मिति"))

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = _("सदस्य")
        verbose_name_plural = _("सदस्यहरू")
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
        PENDING = 'PEN', _('अनुमोदन पछि')
        APPROVED = 'APP', _('अनुमोदित')
        REJECTED = 'REJ', _('अस्वीकृत')
        SPAM = 'SPA', _('स्प्याम')

    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments', verbose_name=_("लेख"), help_text=_("सम्बन्धित लेख"))
    author_name = models.CharField(max_length=100, verbose_name=_("लेखकको नाम"), help_text=_("टिप्पणी लेखकको नाम"))
    author_email = models.EmailField(verbose_name=_("लेखकको इमेल"), help_text=_("टिप्पणी लेखकको इमेल"))
    content = models.TextField(verbose_name=_("सामग्री"), help_text=_("टिप्पणी सामग्री"))
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.PENDING, verbose_name=_("स्थिति"), help_text=_("टिप्पणी स्थिति"))
    
    # Moderation
    is_approved = models.BooleanField(default=False, verbose_name=_("अनुमोदित"), help_text=_("टिप्पणी अनुमोदित"))
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("निरीक्षण गरेको"), help_text=_("निरीक्षण गरेको"))
    moderation_notes = models.TextField(blank=True, verbose_name=_("निरीक्षण नोट"), help_text=_("निरीक्षण नोट"))
    
    # Analytics
    like_count = models.PositiveIntegerField(default=0, verbose_name=_("मन पराइएको संख्या"), help_text=_("मन पराइएको संख्या"))
    
    # Security
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP ठेगाना"), help_text=_("IP ठेगाना"))
    user_agent = models.TextField(blank=True, verbose_name=_("प्रयोगकर्ता एजेन्ट"), help_text=_("प्रयोगकर्ता एजेन्ट"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("सिर्जना मिति"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("अपडेट मिति"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("टिप्पणी")
        verbose_name_plural = _("टिप्पणीहरू")
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
        DRAFT = 'DF', _('मस्यौदा')
        SCHEDULED = 'SC', _('तालिकाबद्ध')
        SENDING = 'SE', _('पठाइरहेको')
        SENT = 'SN', _('पठाइएको')
        FAILED = 'FA', _('असफल')

    title = models.CharField(max_length=200, verbose_name=_("शीर्षक"), help_text=_("न्युजलेटर शीर्षक"))
    subject = models.CharField(max_length=200, verbose_name=_("विषय"), help_text=_("इमेल विषय"))
    content = models.TextField(verbose_name=_("सामग्री"), help_text=_("न्युजलेटर सामग्री"))
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name=_("स्थिति"), help_text=_("न्युजलेटर स्थिति"))
    
    # Targeting
    categories = models.ManyToManyField(Category, blank=True, verbose_name=_("लक्ष्य श्रेणी"), help_text=_("लक्ष्य श्रेणीहरू"))
    send_to_all = models.BooleanField(default=True, verbose_name=_("सबैलाई पठाउनुहोस्"), help_text=_("सबै सदस्यहरूलाई पठाउनुहोस्"))
    
    # Scheduling
    scheduled_date = models.DateTimeField(blank=True, null=True, verbose_name=_("तालिकाबद्ध मिति"), help_text=_("तालिकाबद्ध पठाउने मिति"))
    sent_date = models.DateTimeField(blank=True, null=True, verbose_name=_("पठाइएको मिति"), help_text=_("वास्तविक पठाउने मिति"))
    
    # Analytics
    total_sent = models.PositiveIntegerField(default=0, verbose_name=_("कुल पठाइएको"), help_text=_("कुल पठाइएको इमेल"))
    total_opened = models.PositiveIntegerField(default=0, verbose_name=_("कुल खोलिएको"), help_text=_("कुल खोलिएको इमेल"))
    total_clicked = models.PositiveIntegerField(default=0, verbose_name=_("कुल क्लिक गरिएको"), help_text=_("कुल क्लिक गरिएको लिङ्क"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("सिर्जना मिति"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("अपडेट मिति"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("न्युजलेटर")
        verbose_name_plural = _("न्युजलेटरहरू")
        indexes = [
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['sent_date']),
        ]

    def __str__(self):
        return self.title

class ContentAnalytics(models.Model):
    """Content analytics and performance tracking"""
    content_type = models.CharField(max_length=20, verbose_name=_("सामग्री प्रकार"), help_text=_("सामग्री प्रकार (लेख, कार्यक्रम)"))
    content_id = models.PositiveIntegerField(verbose_name=_("सामग्री ID"), help_text=_("सामग्री ID"))
    date = models.DateField(verbose_name=_("मिति"), help_text=_("विश्लेषण मिति"))
    
    # Metrics
    views = models.PositiveIntegerField(default=0, verbose_name=_("हेराइ"), help_text=_("हेराइको संख्या"))
    unique_views = models.PositiveIntegerField(default=0, verbose_name=_("अद्वितीय हेराइ"), help_text=_("अद्वितीय हेराइको संख्या"))
    shares = models.PositiveIntegerField(default=0, verbose_name=_("साझेदारी"), help_text=_("साझेदारीको संख्या"))
    comments = models.PositiveIntegerField(default=0, verbose_name=_("टिप्पणी"), help_text=_("टिप्पणीको संख्या"))
    time_on_page = models.FloatField(default=0, verbose_name=_("पृष्ठमा समय"), help_text=_("पृष्ठमा औसत समय (सेकेन्डमा)"))
    
    # Traffic sources
    organic_search = models.PositiveIntegerField(default=0, verbose_name=_("जैविक खोज"), help_text=_("जैविक खोज हेराइ"))
    social_media = models.PositiveIntegerField(default=0, verbose_name=_("सामाजिक मिडिया"), help_text=_("सामाजिक मिडिया हेराइ"))
    direct_traffic = models.PositiveIntegerField(default=0, verbose_name=_("प्रत्यक्ष ट्राफिक"), help_text=_("प्रत्यक्ष ट्राफिक हेराइ"))
    referral_traffic = models.PositiveIntegerField(default=0, verbose_name=_("रेफरल ट्राफिक"), help_text=_("रेफरल ट्राफिक हेराइ"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("सिर्जना मिति"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("अपडेट मिति"))

    class Meta:
        unique_together = ['content_type', 'content_id', 'date']
        ordering = ['-date']
        verbose_name = _("सामग्री विश्लेषण")
        verbose_name_plural = _("सामग्री विश्लेषणहरू")
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
