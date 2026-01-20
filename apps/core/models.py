from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import secrets
import logging

logger = logging.getLogger('bhanjyang')

class APIKey(models.Model):
    """API Key model for authentication"""
    
    name = models.CharField(max_length=100, help_text="Descriptive name for this API key")
    key = models.CharField(max_length=64, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_keys')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Leave empty for no expiration")
    
    # Rate limiting
    requests_per_hour = models.PositiveIntegerField(default=1000)
    requests_per_day = models.PositiveIntegerField(default=10000)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)
    
    def generate_key(self):
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)
    
    def is_valid(self):
        """Check if API key is valid"""
        if not self.is_active:
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        return True
    
    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])

class SecurityLog(models.Model):
    """Security event logging"""
    
    EVENT_TYPES = [
        ('login_success', 'Successful Login'),
        ('login_failed', 'Failed Login'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('suspicious_input', 'Suspicious Input'),
        ('brute_force_blocked', 'Brute Force Blocked'),
        ('api_key_used', 'API Key Used'),
        ('api_key_invalid', 'Invalid API Key'),
        ('security_header_violation', 'Security Header Violation'),
    ]
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.ip_address}"


class PageSEO(models.Model):
    """
    Model for page-specific SEO settings for pages that don't have their own models.
    Examples: Contact page, About introduction page, etc.
    """
    PAGE_CHOICES = [
        ('contact', _('Contact Page')),
        ('about_intro', _('About Introduction')),
        ('about_cooperative', _('About Cooperative')),
        ('about_board', _('About Board')),
        ('about_management', _('About Management')),
        ('about_timeline', _('About Timeline')),
        ('services_overview', _('Services Overview')),
        ('downloads', _('Downloads')),
        ('gallery', _('Gallery')),
    ]
    
    page = models.CharField(
        max_length=50,
        choices=PAGE_CHOICES,
        unique=True,
        verbose_name=_("Page"),
        help_text=_("Select the page for SEO settings")
    )
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Meta Title"),
        help_text=_("Page-specific SEO title. If empty, falls back to site_info.meta_title or default.")
    )
    meta_description = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_("Meta Description"),
        help_text=_("Page-specific SEO description. If empty, falls back to site_info.meta_description or default.")
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Meta Keywords"),
        help_text=_("Comma-separated keywords for SEO. If empty, falls back to site_info.meta_keywords or default.")
    )
    og_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Open Graph Title"),
        help_text=_("Title for social media sharing. If empty, uses meta_title.")
    )
    og_description = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_("Open Graph Description"),
        help_text=_("Description for social media sharing. If empty, uses meta_description.")
    )
    og_image = models.ImageField(
        upload_to='seo/page_og_images/',
        blank=True,
        null=True,
        verbose_name=_("Open Graph Image"),
        help_text=_("Image for social media sharing (1200x630px recommended). If empty, uses site_info.og_image.")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Only active SEO settings are used.")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Page SEO")
        verbose_name_plural = _("Page SEO Settings")
        ordering = ['page']
    
    def __str__(self):
        return f"SEO: {self.get_page_display()}"
