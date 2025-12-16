# downloads/models.py

import os
from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings

# Define choices for categories using a TextChoices class for cleaner code.
class FileCategory(models.TextChoices):
    FORM = 'FRM', 'Application Form'
    REPORT = 'RPT', 'Financial Report'
    POLICY = 'PCY', 'Policy & Bylaw'
    PUBLICATION = 'PUB', 'Publication'
    MANUAL = 'MAN', 'User Manual'
    CERTIFICATE = 'CERT', 'Certificate'
    BROCHURE = 'BRO', 'Brochure'
    OTHER = 'OTH', 'Other Document'

class PriorityLevel(models.TextChoices):
    LOW = 'LOW', 'Low Priority'
    MEDIUM = 'MED', 'Medium Priority'
    HIGH = 'HIGH', 'High Priority'
    URGENT = 'URG', 'Urgent'

class DownloadableFile(models.Model):
    """
    Stores a file available for download, with categorization and tracking.
    """
    category = models.CharField(
        max_length=4,
        choices=FileCategory.choices,
        default=FileCategory.OTHER,
        help_text="फाइलको श्रेणी (जस्तै: फारम, रिपोर्ट)।"
    )
    title = models.CharField(max_length=200, help_text="फाइलको शीर्षक।")
    description = models.TextField(blank=True, help_text="फाइलको संक्षिप्त विवरण।")
    file = models.FileField(
        upload_to='downloads/', 
        help_text="अपलोड गर्ने फाइल।",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png'])]
    )

    is_active = models.BooleanField(
        default=True,
        help_text="यो फाइल वेबसाइटमा देखाउने कि नदेखाउने?"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="यो फाइल फिचर्ड सूचीमा देखाउने?"
    )
    priority = models.CharField(
        max_length=4,
        choices=PriorityLevel.choices,
        default=PriorityLevel.MEDIUM,
        help_text="फाइलको प्राथमिकता स्तर।"
    )
    requires_login = models.BooleanField(
        default=False,
        help_text="यो फाइल डाउनलोड गर्न लगइन आवश्यक छ?"
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="फाइलको समाप्ति मिति (वैकल्पिक)।"
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="फाइलका ट्यागहरू (कमा द्वारा अलग)।"
    )
    thumbnail = models.ImageField(
        upload_to='downloads/thumbnails/',
        blank=True,
        null=True,
        help_text="फाइलको थम्बनेल छवि (वैकल्पिक)।"
    )

    download_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="यो फाइल कति पटक डाउनलोड भयो।"
    )
    view_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="यो फाइल कति पटक हेरियो।"
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
        help_text="User who uploaded this file."
    )
    last_accessed = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time this file was accessed."
    )
    access_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="Total number of times this file has been accessed."
    )
    file_type = models.CharField(
        max_length=10,
        blank=True,
        editable=False,
        help_text="फाइलको प्रकार (स्वचालित रूपमा पत्ता लगाइन्छ)।"
    )

    class Meta:
        ordering = ['-priority', '-uploaded_at']
        verbose_name = "डाउनलोड फाइल"
        verbose_name_plural = "डाउनलोड फाइलहरू"
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
        """
        if self.file:
            _name, extension = os.path.splitext(self.file.name)
            self.file_type = extension.replace('.', '').lower()
            
            # Generate file hash for security
            try:
                from .security import FileSecurityValidator
                security_data = FileSecurityValidator.validate_file_security(self.file)
                self.file_hash = security_data.get('file_hash', '')
            except Exception as e:
                # Log error but don't fail the save
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to generate file hash: {e}")
        
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
