from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import SET_NULL


class TimeStampedModel(models.Model):
    """Abstract base class with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


import reversion


@reversion.register()
class HomePageContent(TimeStampedModel):
    """Main content blocks for the home page"""
    class Status(models.TextChoices):
        DRAFT = 'DF', _('Draft')
        PUBLISHED = 'PB', _('Published')
        SCHEDULED = 'SC', _('Scheduled')
        ARCHIVED = 'AR', _('Archived')
    
    title = models.CharField(max_length=200, help_text=_("Main title for the home page"))
    subtitle = models.CharField(max_length=300, blank=True, help_text=_("Subtitle or tagline"))
    description = models.TextField(help_text=_("Main description text"))
    hero_image = models.ImageField(upload_to='home/hero/', blank=True, null=True, help_text=_("Hero background image for slider"))
    background_image = models.ImageField(upload_to='home/background/', blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Kept for backward compatibility
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Status"), help_text=_("Publication status"))
    scheduled_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Scheduled Date"), help_text=_("Schedule this content to be published at a specific date/time"))
    published_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Published Date"), help_text=_("Date when this content was published"))
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, blank=True, null=True, related_name='published_homepage_contents', verbose_name=_("Published By"), help_text=_("User who published this content"))
    order = models.PositiveIntegerField(default=0, help_text=_("Display order"))
    
    # Button fields for hero slides
    primary_button_text = models.CharField(max_length=100, blank=True, help_text=_("Primary button text (e.g., 'Explore Services')"))
    primary_button_url = models.CharField(max_length=200, blank=True, help_text=_("Primary button URL (e.g., '/services/')"))
    secondary_button_text = models.CharField(max_length=100, blank=True, help_text=_("Secondary button text (e.g., 'Contact Us')"))
    secondary_button_url = models.CharField(max_length=200, blank=True, help_text=_("Secondary button URL (e.g., '/contact/')"))
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _("Home Page Content")
        verbose_name_plural = _("Home Page Contents")
        indexes = [
            models.Index(fields=['status', 'order'], name='home_status_order_idx'),
            models.Index(fields=['status', 'scheduled_date'], name='home_status_sched_idx'),
            models.Index(fields=['status', 'published_date'], name='home_status_pub_idx'),
        ]
    
    def __str__(self):
        return self.title


@reversion.register()
class Testimonial(TimeStampedModel):
    """Customer testimonials for the home page"""
    class Status(models.TextChoices):
        DRAFT = 'DF', _('Draft')
        PUBLISHED = 'PB', _('Published')
        SCHEDULED = 'SC', _('Scheduled')
        ARCHIVED = 'AR', _('Archived')
    
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True, help_text=_("Job title or role"))
    company = models.CharField(max_length=100, blank=True, help_text=_("Company or organization"))
    content = models.TextField(help_text=_("Testimonial text"))
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Rating from 1 to 5 stars")
    )
    is_featured = models.BooleanField(default=False, help_text=_("Show on home page"))
    is_active = models.BooleanField(default=True)  # Kept for backward compatibility
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Status"), help_text=_("Publication status"))
    scheduled_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Scheduled Date"), help_text=_("Schedule this testimonial to be published at a specific date/time"))
    published_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Published Date"), help_text=_("Date when this testimonial was published"))
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, blank=True, null=True, related_name='published_testimonials', verbose_name=_("Published By"), help_text=_("User who published this testimonial"))
    order = models.PositiveIntegerField(default=0)
    
    # Language support
    language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('ne', 'Nepali')],
        default='en'
    )
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        indexes = [
            models.Index(fields=['status', 'is_featured', 'order'], name='test_status_feat_idx'),
            models.Index(fields=['status', 'scheduled_date'], name='test_status_sched_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        """Sync is_active with status for backward compatibility"""
        self.is_active = (self.status == self.Status.PUBLISHED)
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        """Check if testimonial is published"""
        return self.status == self.Status.PUBLISHED
    
    @property
    def is_draft(self):
        """Check if testimonial is draft"""
        return self.status == self.Status.DRAFT
    
    @property
    def is_scheduled(self):
        """Check if testimonial is scheduled for future publication"""
        return self.status == self.Status.SCHEDULED and self.scheduled_date and self.scheduled_date > timezone.now()
    
    def get_preview_url(self):
        """Get preview URL for this testimonial with token for security"""
        from django.urls import reverse
        from django.core.signing import TimestampSigner
        signer = TimestampSigner()
        token = signer.sign(str(self.pk))
        return reverse('home:preview_content', kwargs={
            'model_name': 'testimonial',
            'pk': self.pk,
            'token': token
        })


@reversion.register()
class Statistic(TimeStampedModel):
    """Key statistics for the cooperative"""
    class Status(models.TextChoices):
        DRAFT = 'DF', _('Draft')
        PUBLISHED = 'PB', _('Published')
        SCHEDULED = 'SC', _('Scheduled')
        ARCHIVED = 'AR', _('Archived')
    
    title = models.CharField(max_length=100, help_text=_("e.g., 'Total Members'"))
    value = models.CharField(max_length=50, help_text=_("e.g., '2,500+' or 'Rs. 50M'"))
    description = models.CharField(max_length=200, blank=True, help_text=_("Additional context"))
    icon = models.CharField(max_length=50, blank=True, help_text=_("FontAwesome icon class"))
    color = models.CharField(max_length=20, default='green', help_text=_("Color theme"))
    is_featured = models.BooleanField(default=False, help_text=_("Show on home page"))
    is_active = models.BooleanField(default=True)  # Kept for backward compatibility
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Status"), help_text=_("Publication status"))
    scheduled_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Scheduled Date"), help_text=_("Schedule this statistic to be published at a specific date/time"))
    published_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Published Date"), help_text=_("Date when this statistic was published"))
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, blank=True, null=True, related_name='published_statistics', verbose_name=_("Published By"), help_text=_("User who published this statistic"))
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _("Statistic")
        verbose_name_plural = _("Statistics")
        indexes = [
            models.Index(fields=['status', 'is_featured', 'order'], name='stat_status_feat_idx'),
            models.Index(fields=['status', 'scheduled_date'], name='stat_status_sched_idx'),
        ]
    
    def __str__(self):
        return f"{self.title}: {self.value}"
    
    def save(self, *args, **kwargs):
        """Sync is_active with status for backward compatibility"""
        self.is_active = (self.status == self.Status.PUBLISHED)
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        """Check if statistic is published"""
        return self.status == self.Status.PUBLISHED
    
    @property
    def is_draft(self):
        """Check if statistic is draft"""
        return self.status == self.Status.DRAFT
    
    @property
    def is_scheduled(self):
        """Check if statistic is scheduled for future publication"""
        return self.status == self.Status.SCHEDULED and self.scheduled_date and self.scheduled_date > timezone.now()
    
    def get_preview_url(self):
        """Get preview URL for this statistic with token for security"""
        from django.urls import reverse
        from django.core.signing import TimestampSigner
        signer = TimestampSigner()
        token = signer.sign(str(self.pk))
        return reverse('home:preview_content', kwargs={
            'model_name': 'statistic',
            'pk': self.pk,
            'token': token
        })


@reversion.register()
class Announcement(TimeStampedModel):
    """Important announcements and news"""
    class AnnouncementType(models.TextChoices):
        GENERAL = 'general', _('General')
        SERVICE = 'service', _('Service Update')
        EVENT = 'event', _('Event')
        HOLIDAY = 'holiday', _('Holiday Notice')
        MAINTENANCE = 'maintenance', _('Maintenance')

    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        URGENT = 'urgent', _('Urgent')
    
    class Status(models.TextChoices):
        DRAFT = 'DF', _('Draft')
        PUBLISHED = 'PB', _('Published')
        SCHEDULED = 'SC', _('Scheduled')
        ARCHIVED = 'AR', _('Archived')

    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.CharField(max_length=300, blank=True, help_text=_("Short summary for cards"))
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    announcement_type = models.CharField(
        max_length=20,
        choices=AnnouncementType.choices,
        default=AnnouncementType.GENERAL
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    is_featured = models.BooleanField(default=False, help_text=_("Show on home page"))
    is_active = models.BooleanField(default=True)  # Kept for backward compatibility
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Status"), help_text=_("Publication status"))
    publish_date = models.DateTimeField(default=timezone.now, verbose_name=_("Publish Date"), help_text=_("Original publish date"))
    scheduled_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Scheduled Date"), help_text=_("Schedule this announcement to be published at a specific date/time"))
    published_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Published Date"), help_text=_("Date when this announcement was actually published"))
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, blank=True, null=True, related_name='published_announcements', verbose_name=_("Published By"), help_text=_("User who published this announcement"))
    expiry_date = models.DateTimeField(blank=True, null=True, help_text=_("When to stop showing"))
    auto_expire = models.BooleanField(default=False, verbose_name=_("Auto Expire"), help_text=_("Automatically archive this announcement when expiry_date is reached"))
    
    class Meta:
        ordering = ['-priority', '-publish_date']
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")
        indexes = [
            models.Index(fields=['status', 'is_featured', '-priority'], name='ann_status_feat_idx'),
            models.Index(fields=['status', 'scheduled_date'], name='ann_status_sched_idx'),
            models.Index(fields=['status', 'expiry_date'], name='ann_status_expiry_idx'),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    @property
    def is_published(self):
        """Check if announcement is published"""
        return self.status == self.Status.PUBLISHED
    
    @property
    def is_draft(self):
        """Check if announcement is draft"""
        return self.status == self.Status.DRAFT
    
    @property
    def is_scheduled(self):
        """Check if announcement is scheduled for future publication"""
        return self.status == self.Status.SCHEDULED and self.scheduled_date and self.scheduled_date > timezone.now()
    
    def save(self, *args, **kwargs):
        """Sync is_active with status for backward compatibility"""
        self.is_active = (self.status == self.Status.PUBLISHED)
        super().save(*args, **kwargs)
    
    def get_preview_url(self):
        """Get preview URL for this announcement with token for security"""
        from django.urls import reverse
        from django.core.signing import TimestampSigner
        signer = TimestampSigner()
        token = signer.sign(str(self.pk))
        return reverse('home:preview_content', kwargs={
            'model_name': 'announcement',
            'pk': self.pk,
            'token': token
        })



class NewsletterSubscriber(TimeStampedModel):
    """Newsletter subscribers"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = _("Newsletter Subscriber")
        verbose_name_plural = _("Newsletter Subscribers")
    
    def __str__(self):
        return self.email


class ContactInquiry(TimeStampedModel):
    """Contact form submissions"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    inquiry_type = models.CharField(
        max_length=20,
        choices=[
            ('general', _('General Inquiry')),
            ('service', _('Service Information')),
            ('complaint', _('Complaint')),
            ('suggestion', _('Suggestion')),
            ('support', _('Technical Support')),
        ],
        default='general'
    )
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    response = models.TextField(blank=True, help_text=_("Response to the inquiry"))
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Contact Inquiry")
        verbose_name_plural = _("Contact Inquiries")
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class PageView(TimeStampedModel):
    """Track page views for analytics"""
    page_url = models.URLField()
    page_title = models.CharField(max_length=200, blank=True)
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Page View")
        verbose_name_plural = _("Page Views")
    
    def __str__(self):
        return f"{self.page_url} - {self.created_at}"


# A/B Testing Model
class ContentVariant(TimeStampedModel):
    """A/B testing variants for content"""
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.contenttypes.fields import GenericForeignKey
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_("Content Type"))
    object_id = models.PositiveIntegerField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey('content_type', 'object_id')
    
    variant_name = models.CharField(max_length=100, verbose_name=_("Variant Name"), help_text=_("e.g., 'Variant A', 'Variant B'"))
    variant_data = models.JSONField(default=dict, verbose_name=_("Variant Data"), help_text=_("Store variant-specific data (title, description, etc.)"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Active"), help_text=_("Is this variant currently active?"))
    views = models.PositiveIntegerField(default=0, verbose_name=_("Views"), help_text=_("Number of times this variant was viewed"))
    conversions = models.PositiveIntegerField(default=0, verbose_name=_("Conversions"), help_text=_("Number of conversions (clicks, signups, etc.)"))
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Content Variant")
        verbose_name_plural = _("Content Variants")
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.variant_name} - {self.content_object}"
    
    @property
    def conversion_rate(self):
        """Calculate conversion rate"""
        if self.views == 0:
            return 0.0
        return (self.conversions / self.views) * 100