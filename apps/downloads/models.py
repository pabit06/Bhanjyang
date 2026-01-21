# downloads/models.py

import os
from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Define choices for categories using a TextChoices class for cleaner code.
class FileCategory(models.TextChoices):
    FORM = 'FRM', _('Application Form')
    REPORT = 'RPT', _('Financial Report')
    POLICY = 'PCY', _('Policy & Bylaw')
    PUBLICATION = 'PUB', _('Publication')
    MANUAL = 'MAN', _('User Manual')
    CERTIFICATE = 'CERT', _('Certificate')
    BROCHURE = 'BRO', _('Brochure')
    OTHER = 'OTH', _('Other Document')

class PriorityLevel(models.TextChoices):
    LOW = 'LOW', _('Low Priority')
    MEDIUM = 'MED', _('Medium Priority')
    HIGH = 'HIGH', _('High Priority')
    URGENT = 'URG', _('Urgent')

class DownloadableFile(models.Model):
    """
    Stores a file available for download, with categorization and tracking.
    """
    category = models.CharField(
        max_length=4,
        choices=FileCategory.choices,
        default=FileCategory.OTHER,
        help_text=_("Category of the file (e.g., Form, Report).")
    )
    title = models.CharField(max_length=200, help_text=_("Title of the file."))
    description = models.TextField(blank=True, help_text=_("Short description of the file."))
    file = models.FileField(
        upload_to='downloads/', 
        help_text=_("The file to upload."),
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png'])]
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether to show this file on the website.")
    )
    is_featured = models.BooleanField(
        default=False,
        help_text=_("Show this file in the featured list?")
    )
    priority = models.CharField(
        max_length=4,
        choices=PriorityLevel.choices,
        default=PriorityLevel.MEDIUM,
        help_text=_("Priority level of the file.")
    )
    requires_login = models.BooleanField(
        default=False,
        help_text=_("Is login required to download this file?")
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Expiration date of the file (optional).")
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Tags for the file (separated by commas).")
    )
    thumbnail = models.ImageField(
        upload_to='downloads/thumbnails/',
        blank=True,
        null=True,
        help_text=_("Thumbnail image for the file (optional).")
    )

    download_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text=_("How many times this file has been downloaded.")
    )
    view_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text=_("How many times this file has been viewed.")
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    file_hash = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
        help_text="SHA-256 hash of file content for security tracking."
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("User who uploaded this file.")
    )
    last_accessed = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Last time this file was accessed.")
    )
    access_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text=_("Total number of times this file has been accessed.")
    )
    file_type = models.CharField(
        max_length=10,
        blank=True,
        editable=False,
        help_text=_("Type of the file (detected automatically).")
    )

    class Meta:
        ordering = ['-priority', '-uploaded_at']
        verbose_name = _("Downloadable File")
        verbose_name_plural = _("Downloadable Files")
        get_latest_by = 'uploaded_at'
        indexes = [
            models.Index(fields=['category', 'is_active'], name='downloads_d_categor_0ca7e6_idx'),
            models.Index(fields=['priority', 'is_featured'], name='downloads_d_priorit_4e95c0_idx'),
            models.Index(fields=['uploaded_at'], name='downloads_d_uploade_f68532_idx'),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically set the file_type
        based on the file's extension and generate security hash.
        
        Hash is calculated using SHA-256 for file integrity verification.
        """
        import hashlib
        import logging
        
        logger = logging.getLogger(__name__)
        
        if self.file:
            _name, extension = os.path.splitext(self.file.name)
            self.file_type = extension.replace('.', '').lower()
            
            # Generate file hash for security and integrity checking
            # Always recalculate hash if file is new or has changed
            try:
                # Check if file is being uploaded (has read method)
                if hasattr(self.file, 'read'):
                    # New file upload - generate hash from file content
                    from .security import FileSecurityValidator
                    file_hash = FileSecurityValidator.generate_file_hash(self.file)
                    if file_hash:
                        self.file_hash = file_hash
                # If file already exists on disk, calculate hash from disk
                elif hasattr(self.file, 'path') and os.path.exists(self.file.path):
                    with open(self.file.path, 'rb') as f:
                        self.file_hash = hashlib.sha256(f.read()).hexdigest()
            except Exception as e:
                # Log error but don't fail the save
                logger.warning(
                    f"Failed to generate file hash for file '{self.file.name}': {e}",
                    exc_info=True
                )
                # If hash generation fails, we still save the file
                # but log the warning for admin attention
        
        super().save(*args, **kwargs)

    @property
    def file_size(self):
        """
        Returns the file size in a human-readable format (B, KB, MB, GB).
        Handles potential FileNotFoundError if the file is missing from storage.
        """
        try:
            if self.file and hasattr(self.file, 'size'):
                size = self.file.size
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 ** 2:
                    return f"{size / 1024:.1f} KB"
                elif size < 1024 ** 3:
                    return f"{size / (1024 ** 2):.1f} MB"
                else:
                    return f"{size / (1024 ** 3):.1f} GB"
        except FileNotFoundError:
            return "File not found"
        return "N/A"

    @property
    def is_expired(self):
        """Check if the file has expired."""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False

    @property
    def tag_list(self):
        """Return tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def increment_view_count(self):
        """Increment the view count atomically."""
        from django.db.models import F
        from django.utils import timezone
        DownloadableFile.objects.filter(pk=self.pk).update(
            view_count=F('view_count') + 1,
            last_accessed=timezone.now(),
            access_count=F('access_count') + 1
        )
    
    def increment_download_count(self):
        """Increment the download count atomically."""
        from django.db.models import F
        from django.utils import timezone
        DownloadableFile.objects.filter(pk=self.pk).update(
            download_count=F('download_count') + 1,
            last_accessed=timezone.now(),
            access_count=F('access_count') + 1
        )
