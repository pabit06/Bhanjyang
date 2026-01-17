from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Abstract base class with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class HomePageContent(TimeStampedModel):
    """Main content blocks for the home page"""
    title = models.CharField(max_length=200, help_text=_("Main title for the home page"))
    subtitle = models.CharField(max_length=300, blank=True, help_text=_("Subtitle or tagline"))
    description = models.TextField(help_text=_("Main description text"))
    hero_image = models.ImageField(upload_to='home/hero/', blank=True, null=True, help_text=_("Hero background image for slider"))
    background_image = models.ImageField(upload_to='home/background/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
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
    
    def __str__(self):
        return self.title


class Testimonial(TimeStampedModel):
    """Customer testimonials for the home page"""
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
    is_active = models.BooleanField(default=True)
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
    
    def __str__(self):
        return f"{self.name} - {self.content[:50]}..."


class Statistic(TimeStampedModel):
    """Key statistics for the cooperative"""
    title = models.CharField(max_length=100, help_text=_("e.g., 'Total Members'"))
    value = models.CharField(max_length=50, help_text=_("e.g., '2,500+' or 'Rs. 50M'"))
    description = models.CharField(max_length=200, blank=True, help_text=_("Additional context"))
    icon = models.CharField(max_length=50, blank=True, help_text=_("FontAwesome icon class"))
    color = models.CharField(max_length=20, default='green', help_text=_("Color theme"))
    is_featured = models.BooleanField(default=False, help_text=_("Show on home page"))
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _("Statistic")
        verbose_name_plural = _("Statistics")
    
    def __str__(self):
        return f"{self.title}: {self.value}"


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
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(blank=True, null=True, help_text=_("When to stop showing"))
    
    class Meta:
        ordering = ['-priority', '-publish_date']
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False



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