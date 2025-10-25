from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import logging

logger = logging.getLogger('coop')

class APIKey(models.Model):
    """API Key model for authentication"""
    
    name = models.CharField(max_length=100, help_text="Descriptive name for this API key")
    key = models.CharField(max_length=64, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
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
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
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
