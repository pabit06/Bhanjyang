from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class TimeStampedModel(models.Model):
    """Abstract base class with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class HomePageContent(TimeStampedModel):
    """Main content blocks for the home page"""
    title = models.CharField(max_length=200, help_text="Main title for the home page")
    subtitle = models.CharField(max_length=300, blank=True, help_text="Subtitle or tagline")
    description = models.TextField(help_text="Main description text")
    hero_image = models.ImageField(upload_to='home/hero/', blank=True, null=True)
    background_image = models.ImageField(upload_to='home/background/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Home Page Content"
        verbose_name_plural = "Home Page Contents"
    
    def __str__(self):
        return self.title


class Testimonial(TimeStampedModel):
    """Customer testimonials for the home page"""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True, help_text="Job title or role")
    company = models.CharField(max_length=100, blank=True, help_text="Company or organization")
    content = models.TextField(help_text="Testimonial text")
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    is_featured = models.BooleanField(default=False, help_text="Show on home page")
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
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
    
    def __str__(self):
        return f"{self.name} - {self.content[:50]}..."


class Statistic(TimeStampedModel):
    """Key statistics for the cooperative"""
    title = models.CharField(max_length=100, help_text="e.g., 'Total Members'")
    value = models.CharField(max_length=50, help_text="e.g., '2,500+' or 'Rs. 50M'")
    description = models.CharField(max_length=200, blank=True, help_text="Additional context")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    color = models.CharField(max_length=20, default='green', help_text="Color theme")
    is_featured = models.BooleanField(default=False, help_text="Show on home page")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Statistic"
        verbose_name_plural = "Statistics"
    
    def __str__(self):
        return f"{self.title}: {self.value}"


class Announcement(TimeStampedModel):
    """Important announcements and news"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.CharField(max_length=300, blank=True, help_text="Short summary for cards")
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    announcement_type = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General'),
            ('service', 'Service Update'),
            ('event', 'Event'),
            ('holiday', 'Holiday Notice'),
            ('maintenance', 'Maintenance'),
        ],
        default='general'
    )
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium'
    )
    is_featured = models.BooleanField(default=False, help_text="Show on home page")
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(blank=True, null=True, help_text="When to stop showing")
    
    class Meta:
        ordering = ['-priority', '-publish_date']
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False


class ServiceHighlight(TimeStampedModel):
    """Featured services on the home page"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    color = models.CharField(max_length=20, default='green', help_text="Color theme")
    interest_rate = models.CharField(max_length=20, blank=True, help_text="e.g., 'Up to 8%'")
    link_url = models.URLField(blank=True, help_text="Link to detailed service page")
    link_text = models.CharField(max_length=50, default="Learn More")
    is_featured = models.BooleanField(default=False, help_text="Show on home page")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Service Highlight"
        verbose_name_plural = "Service Highlights"
    
    def __str__(self):
        return self.title


class NewsletterSubscriber(TimeStampedModel):
    """Newsletter subscribers"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
    
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
            ('general', 'General Inquiry'),
            ('service', 'Service Information'),
            ('complaint', 'Complaint'),
            ('suggestion', 'Suggestion'),
            ('support', 'Technical Support'),
        ],
        default='general'
    )
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    response = models.TextField(blank=True, help_text="Response to the inquiry")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
    
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
        verbose_name = "Page View"
        verbose_name_plural = "Page Views"
    
    def __str__(self):
        return f"{self.page_url} - {self.created_at}"