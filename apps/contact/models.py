"""
Models for the Contact app.

This module contains database models for contact form submissions.
"""
import os
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify

from .utils.constants import SECONDS_IN_24_HOURS


def contact_attachment_path(instance, filename):
    """
    Generate secure upload path for contact form attachments.
    
    Args:
        instance: ContactSubmission instance
        filename: Original filename
        
    Returns:
        str: Secure file path with timestamp and unique identifier
    """
    name, ext = os.path.splitext(filename)
    sanitized_name = slugify(name) or 'attachment'
    unique_filename = f"{sanitized_name}_{uuid.uuid4().hex[:8]}{ext.lower()}"
    timestamp = timezone.now().strftime('%Y/%m/%d')
    return f'contact_attachments/{timestamp}/{unique_filename}'


class ContactSubmission(models.Model):
    """
    Model to store contact form submissions for better record keeping and management.
    
    Tracks contact inquiries including sender details, message content,
    optional file attachments, and administrative status tracking.
    """
    
    STATUS_CHOICES = [
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('spam', _('Spam')),
    ]
    
    # Contact information
    name = models.CharField(
        max_length=100,
        help_text=_("Full name of the person submitting the form")
    )
    email = models.EmailField(help_text=_("Email address for response"))
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Optional phone number")
    )
    subject = models.CharField(
        max_length=200,
        help_text=_("Subject of the inquiry")
    )
    message = models.TextField(help_text=_("Detailed message content"))
    attachment = models.FileField(
        upload_to=contact_attachment_path,
        blank=True,
        null=True,
        help_text=_("Optional file attachment")
    )
    
    # Technical tracking fields
    ip_address = models.GenericIPAddressField(
        help_text=_("IP address of the submitter")
    )
    user_agent = models.TextField(
        blank=True,
        help_text=_("Browser user agent string")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the submission was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When the submission was last updated")
    )
    
    # Management fields
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        help_text=_("Current status of the submission")
    )
    admin_notes = models.TextField(
        blank=True,
        help_text=_("Internal notes for admin use")
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the submission was resolved")
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Contact Submission')
        verbose_name_plural = _('Contact Submissions')
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['status']),
            models.Index(fields=['resolved_at']),
            models.Index(fields=['name']),
            models.Index(fields=['phone']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['subject']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def get_status_display_color(self):
        """Return CSS color class for status display."""
        colors = {
            'new': 'text-blue-600',
            'in_progress': 'text-yellow-600',
            'resolved': 'text-green-600',
            'spam': 'text-red-600',
        }
        return colors.get(self.status, 'text-gray-600')
    
    def is_recent(self):
        """Check if submission is from the last 24 hours."""
        return (timezone.now() - self.created_at).total_seconds() < SECONDS_IN_24_HOURS
    
    def mark_as_resolved(self):
        """Mark submission as resolved with timestamp."""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at', 'updated_at'])
    
    def mark_as_spam(self):
        """Mark submission as spam."""
        self.status = 'spam'
        self.save(update_fields=['status', 'updated_at'])
    
    def has_attachment(self):
        """Check if submission has an attachment."""
        return bool(self.attachment and self.attachment.name)
    
    def get_attachment_filename(self):
        """Get the filename of the attachment."""
        if self.has_attachment():
            return os.path.basename(self.attachment.name)
        return None
    
    def get_attachment_size(self):
        """Get the size of the attachment in bytes."""
        if self.has_attachment():
            try:
                return self.attachment.size
            except (OSError, ValueError):
                return 0
        return 0
    
    def get_attachment_size_display(self):
        """Get human-readable attachment size."""
        size = self.get_attachment_size()
        if size == 0:
            return "No attachment"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class OfficeLocation(models.Model):
    """
    Model to store cooperative office and branch locations.
    
    Used for displaying office locations on maps and contact pages.
    Supports multiple location types: main office, branch office, service center, ATM center.
    """
    
    LOCATION_TYPES = [
        ('main_office', _('Main Office')),
        ('branch_office', _('Branch Office')),
        ('service_center', _('Service Center')),
        ('atm_center', _('ATM Center')),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text=_("Name of the location (e.g., 'Main Office', 'Polyang Branch')")
    )
    address = models.CharField(
        max_length=255,
        help_text=_("Full address of the location")
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text=_("Latitude coordinate for map display")
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text=_("Longitude coordinate for map display")
    )
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPES,
        default='branch_office',
        help_text=_("Type of location")
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Contact phone number for this location")
    )
    email = models.EmailField(
        blank=True,
        help_text=_("Contact email for this location")
    )
    hours = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Operating hours (e.g., '9:00 AM - 5:00 PM', '24/7')")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description of the location and services offered")
    )
    image = models.ImageField(
        upload_to='contact/locations/',
        blank=True,
        null=True,
        help_text=_("Image of the location")
    )
    services = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of services offered at this location (e.g., ['Savings', 'Loans'])")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this location is currently active")
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text=_("Display order (lower numbers appear first)")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Office Location')
        verbose_name_plural = _('Office Locations')
        indexes = [
            models.Index(fields=['location_type', 'is_active']),
            models.Index(fields=['is_active', 'order']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_location_type_display()}"


class PrivacyPolicy(models.Model):
    """
    Model to manage Privacy Policy content.
    """
    title = models.CharField(max_length=200, default='Privacy Policy')
    content = models.TextField(help_text=_("HTML content of the privacy policy"))
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)
    last_updated = models.DateField(auto_now=True)
    
    class Meta:
        verbose_name = _('Privacy Policy')
        verbose_name_plural = _('Privacy Policies')
    
    def __str__(self):
        return f"{self.title} (v{self.version})"


class FAQ(models.Model):
    """
    Model for Frequently Asked Questions.
    
    Allows dynamic management of FAQs on the contact page.
    """
    question = models.CharField(max_length=255, verbose_name=_("Question"))
    answer = models.TextField(verbose_name=_("Answer"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"), help_text=_("Order to display the FAQ (lowest first)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
    
    def __str__(self):
        return self.question
