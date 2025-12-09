from django.db import models
from django.utils import timezone
import os


def contact_attachment_path(instance, filename):
    """Generate secure upload path for contact form attachments"""
    import uuid
    import os
    from django.utils.text import slugify
    
    # Sanitize filename
    name, ext = os.path.splitext(filename)
    sanitized_name = slugify(name)
    unique_filename = f"{sanitized_name}_{uuid.uuid4().hex[:8]}{ext}"
    
    timestamp = timezone.now().strftime('%Y/%m/%d')
    return f'contact_attachments/{timestamp}/{unique_filename}'


class ContactSubmission(models.Model):
    """
    Model to store contact form submissions for better record keeping and management.
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('spam', 'Spam'),
    ]
    
    name = models.CharField(max_length=100, help_text="Full name of the person submitting the form")
    email = models.EmailField(help_text="Email address for response")
    phone = models.CharField(max_length=20, blank=True, help_text="Optional phone number")
    subject = models.CharField(max_length=200, help_text="Subject of the inquiry")
    message = models.TextField(help_text="Detailed message content")
    attachment = models.FileField(
        upload_to=contact_attachment_path,
        blank=True,
        null=True,
        help_text="Optional file attachment"
    )
    
    # Technical tracking fields
    ip_address = models.GenericIPAddressField(help_text="IP address of the submitter")
    user_agent = models.TextField(blank=True, help_text="Browser user agent string")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the submission was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the submission was last updated")
    
    # Management fields
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        help_text="Current status of the submission"
    )
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admin use")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="When the submission was resolved")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['status']),
            models.Index(fields=['resolved_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def get_status_display_color(self):
        """Return CSS color class for status display"""
        colors = {
            'new': 'text-blue-600',
            'in_progress': 'text-yellow-600',
            'resolved': 'text-green-600',
            'spam': 'text-red-600',
        }
        return colors.get(self.status, 'text-gray-600')
    
    def is_recent(self):
        """Check if submission is from the last 24 hours"""
        return (timezone.now() - self.created_at).total_seconds() < 86400
    
    def mark_as_resolved(self):
        """Mark submission as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
    
    def mark_as_spam(self):
        """Mark submission as spam"""
        self.status = 'spam'
        self.save()
    
    def has_attachment(self):
        """Check if submission has an attachment"""
        return bool(self.attachment and self.attachment.name)
    
    def get_attachment_filename(self):
        """Get the filename of the attachment"""
        if self.has_attachment():
            return os.path.basename(self.attachment.name)
        return None
    
    def get_attachment_size(self):
        """Get the size of the attachment in bytes"""
        if self.has_attachment():
            try:
                return self.attachment.size
            except (OSError, ValueError):
                return 0
        return 0
    
    def get_attachment_size_display(self):
        """Get human-readable attachment size"""
        size = self.get_attachment_size()
        if size == 0:
            return "No attachment"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


def kym_document_path(instance, filename):
    """Generate secure upload path for KYM form documents"""
    import uuid
    from django.utils.text import slugify
    
    # Sanitize filename
    name, ext = os.path.splitext(filename)
    sanitized_name = slugify(name)
    unique_filename = f"{sanitized_name}_{uuid.uuid4().hex[:8]}{ext}"
    
    timestamp = timezone.now().strftime('%Y/%m/%d')
    return f'kym_documents/{timestamp}/{unique_filename}'


class KYMSubmission(models.Model):
    """
    Model to store Know Your Member (KYM) form submissions.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Personal Details
    full_name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    marital_status = models.CharField(max_length=20, choices=[
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ])
    nationality = models.CharField(max_length=50, default='Nepali')
    
    # Contact Information
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    permanent_address = models.CharField(max_length=255)
    district = models.CharField(max_length=100, default='Kaski')
    province = models.CharField(max_length=100, default='Gandaki Province')
    
    # Family Details
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    spouse_name = models.CharField(max_length=100, blank=True)
    grand_father_name = models.CharField(max_length=100)
    nominee_name = models.CharField(max_length=100, blank=True)
    
    # Occupation & Income
    occupation = models.CharField(max_length=100)
    income_source = models.CharField(max_length=100)
    estimated_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Documents
    citizenship_front = models.FileField(upload_to=kym_document_path)
    citizenship_back = models.FileField(upload_to=kym_document_path)
    passport_photo = models.FileField(upload_to=kym_document_path)
    address_proof = models.FileField(upload_to=kym_document_path)
    income_proof = models.FileField(upload_to=kym_document_path, blank=True, null=True)
    
    # Technical tracking
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Management fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kym_reviews'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'KYM Submission'
        verbose_name_plural = 'KYM Submissions'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.email} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def get_status_display_color(self):
        """Return CSS color class for status display"""
        colors = {
            'pending': 'text-blue-600',
            'under_review': 'text-yellow-600',
            'approved': 'text-green-600',
            'rejected': 'text-red-600',
        }
        return colors.get(self.status, 'text-gray-600')
    
    def is_recent(self):
        """Check if submission is from the last 24 hours"""
        return (timezone.now() - self.created_at).total_seconds() < 86400