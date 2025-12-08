from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator, validate_image_file_extension
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone
from PIL import Image
from typing import Optional, Tuple
import io
import os
import logging

from .constants import (
    MAX_IMAGE_SIZE_BYTES, MAX_IMAGE_DIMENSION, MIN_IMAGE_DIMENSION,
    WARN_IMAGE_DIMENSION, THUMBNAIL_SIZE, MOBILE_IMAGE_SIZE,
    MOBILE_IMAGE_QUALITY, THUMBNAIL_QUALITY, MAX_IMAGE_SIZE_MB
)

logger = logging.getLogger(__name__)


class GalleryAlbum(models.Model):
    """Albums for organizing gallery images"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(
        upload_to='gallery/albums/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
        ],
        help_text="Album cover image (JPG, PNG, WEBP only)"
    )
    parent_album = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='sub_albums',
        help_text="Leave blank for root album"
    )
    is_featured = models.BooleanField(default=False, help_text="Show on home page")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Gallery Album"
        verbose_name_plural = "Gallery Albums"
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['parent_album', 'is_active']),
            models.Index(fields=['order', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.get_path()
    
    def get_path(self) -> str:
        """Get full path of album including parent albums"""
        if self.parent_album:
            return f"{self.parent_album.get_path()} / {self.name}"
        return self.name
    
    def get_image_count(self) -> int:
        """Get the number of images in this album"""
        return self.images.filter(is_active=True).count()
    
    def get_sub_album_count(self) -> int:
        """Get the number of sub-albums"""
        return self.sub_albums.filter(is_active=True).count()
    
    def delete(self, *args, **kwargs) -> None:
        """Delete cover image file when album is deleted"""
        if self.cover_image:
            try:
                if default_storage.exists(self.cover_image.name):
                    default_storage.delete(self.cover_image.name)
            except Exception as e:
                logger.error(f"Error deleting cover image for album {self.id}: {e}", exc_info=True)
        super().delete(*args, **kwargs)


def validate_image_size(value):
    """Validate that image size doesn't exceed MAX_IMAGE_SIZE_MB"""
    if value.size > MAX_IMAGE_SIZE_BYTES:
        size_mb = value.size / (1024 * 1024)
        raise ValidationError(
            f'Image size cannot exceed {MAX_IMAGE_SIZE_MB}MB. Current size: {size_mb:.2f}MB'
        )

def validate_image_dimensions(value):
    """Validate that image dimensions are reasonable"""
    try:
        from PIL import Image as PILImage
        img = PILImage.open(value)
        width, height = img.size
        if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
            raise ValidationError(
                f'Image dimensions are too large: {width}x{height}. '
                f'Maximum: {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}'
            )
        if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
            raise ValidationError(
                f'Image dimensions are too small: {width}x{height}. '
                f'Minimum: {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION}'
            )
    except Exception:
        pass  # Let other validators handle invalid images

class GalleryImage(models.Model):
    """Images for the gallery section"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='gallery/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size,
        ],
        help_text="Upload images (JPG, PNG, WEBP only, max 10MB)"
    )
    album = models.ForeignKey(
        GalleryAlbum, 
        on_delete=models.CASCADE, 
        related_name='images',
        blank=True, 
        null=True,
        help_text="Album this image belongs to"
    )
    category = models.CharField(
        max_length=20,
        choices=[
            ('events', 'Events'),
            ('team', 'Team'),
            ('office', 'Office'),
            ('community', 'Community'),
            ('awards', 'Awards'),
        ],
        default='events'
    )
    is_featured = models.BooleanField(default=False, help_text="Show on home page")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # AI-powered features
    ai_tags = models.JSONField(default=list, blank=True, help_text="AI-generated tags")
    ai_description = models.TextField(blank=True, help_text="AI-generated description")
    ai_color_palette = models.JSONField(default=list, blank=True, help_text="AI-detected color palette")
    ai_objects = models.JSONField(default=list, blank=True, help_text="AI-detected objects")
    ai_scene_type = models.CharField(max_length=100, blank=True, help_text="AI-detected scene type")
    ai_sentiment = models.CharField(max_length=50, blank=True, help_text="AI-detected sentiment")
    ai_quality_score = models.FloatField(default=0.0, help_text="AI quality score (0-1)")
    
    # Social features
    likes_count = models.PositiveIntegerField(default=0, help_text="Number of likes")
    shares_count = models.PositiveIntegerField(default=0, help_text="Number of shares")
    views_count = models.PositiveIntegerField(default=0, help_text="Number of views")
    comments_count = models.PositiveIntegerField(default=0, help_text="Number of comments")
    is_public = models.BooleanField(default=True, help_text="Publicly visible")
    allow_comments = models.BooleanField(default=True, help_text="Allow comments")
    allow_downloads = models.BooleanField(default=False, help_text="Allow downloads")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['album', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_public', 'is_active']),
        ]
    
    def clean(self):
        """Additional model-level validation"""
        super().clean()
        if self.image:
            # Validate image dimensions during upload
            try:
                from PIL import Image as PILImage
                img = PILImage.open(self.image)
                width, height = img.size
                
                # Warn about very large images
                if width > WARN_IMAGE_DIMENSION or height > WARN_IMAGE_DIMENSION:
                    logger.warning(f"Large image uploaded: {width}x{height}")
                    
                if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                    raise ValidationError(
                        f'Image dimensions are too large: {width}x{height}. '
                        f'Maximum: {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}'
                    )
                    
            except Exception as e:
                # If we can't open the image, it's likely invalid
                raise ValidationError(f'Invalid image file: {str(e)}')
    
    def __str__(self):
        return self.title
    
    def get_album_path(self):
        """Get the album path for this image"""
        if self.album:
            return self.album.get_path()
        return "No Album"
    
    def optimize_image_for_mobile(
        self, 
        size: Tuple[int, int] = MOBILE_IMAGE_SIZE, 
        quality: int = MOBILE_IMAGE_QUALITY
    ) -> Optional[str]:
        """Create mobile-optimized version of the image"""
        try:
            if not self.image:
                return None
                
            # Open the original image
            with default_storage.open(self.image.name, 'rb') as f:
                image_data = f.read()
                
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
                
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize while maintaining aspect ratio
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            # Generate filename for mobile version
            original_name = os.path.basename(self.image.name)
            name, ext = os.path.splitext(original_name)
            mobile_filename = f"{name}_mobile{ext}"
            mobile_path = os.path.join(os.path.dirname(self.image.name), mobile_filename)
            
            # Save to storage
            mobile_file = ContentFile(output.getvalue())
            mobile_path = default_storage.save(mobile_path, mobile_file)
            
            return mobile_path
            
        except Exception as e:
            logger.error(f"Error optimizing image for mobile: {e}", exc_info=True)
            return None
    
    def get_mobile_image_url(self):
        """Get mobile-optimized image URL"""
        try:
            mobile_path = self.optimize_image_for_mobile()
            if mobile_path and default_storage.exists(mobile_path):
                return default_storage.url(mobile_path)
            return self.image.url
        except Exception:
            return self.image.url
    
    def get_thumbnail_url(self, size: Tuple[int, int] = THUMBNAIL_SIZE) -> Optional[str]:
        """Get thumbnail URL"""
        try:
            if not self.image:
                return None
                
            # Open the original image
            with default_storage.open(self.image.name, 'rb') as f:
                image_data = f.read()
                
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
                
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Create thumbnail
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=THUMBNAIL_QUALITY, optimize=True)
            output.seek(0)
            
            # Generate filename for thumbnail
            original_name = os.path.basename(self.image.name)
            name, ext = os.path.splitext(original_name)
            thumbnail_filename = f"{name}_thumb{ext}"
            thumbnail_path = os.path.join(os.path.dirname(self.image.name), thumbnail_filename)
            
            # Save to storage
            thumbnail_file = ContentFile(output.getvalue())
            thumbnail_path = default_storage.save(thumbnail_path, thumbnail_file)
            
            return default_storage.url(thumbnail_path)
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}", exc_info=True)
            return self.image.url if self.image else None
    
    def get_image_dimensions(self) -> Tuple[int, int]:
        """Get image dimensions"""
        try:
            if not self.image:
                return (0, 0)
                
            with default_storage.open(self.image.name, 'rb') as f:
                image = Image.open(f)
                return image.size
        except Exception as e:
            logger.error(f"Error getting image dimensions: {e}", exc_info=True)
            return (0, 0)
    
    def get_file_size(self) -> int:
        """Get file size in bytes"""
        try:
            if not self.image:
                return 0
            return default_storage.size(self.image.name)
        except Exception as e:
            logger.error(f"Error getting file size: {e}", exc_info=True)
            return 0
    
    def get_file_size_mb(self) -> float:
        """Get file size in MB"""
        return round(self.get_file_size() / (1024 * 1024), 2)


class GalleryImageLike(models.Model):
    """User likes for gallery images"""
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='gallery_likes')
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['image', 'session_id']  # Prevent duplicate session likes
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['image', 'created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Like on {self.image.title} by {self.user or self.session_id}"


class GalleryImageComment(models.Model):
    """Comments on gallery images"""
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='gallery_comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['image', 'is_approved']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Comment on {self.image.title} by {self.user or self.name}"


class GalleryImageShare(models.Model):
    """Social shares of gallery images"""
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_shares')
    platform = models.CharField(max_length=50, choices=[
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('copy_link', 'Copy Link'),
    ])
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['image', 'platform']),
            models.Index(fields=['created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Share of {self.image.title} on {self.platform}"


class GalleryImageDownload(models.Model):
    """Downloads of gallery images"""
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='downloads')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_downloads')
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True, db_index=True)
    download_type = models.CharField(max_length=20, choices=[
        ('original', 'Original'),
        ('thumbnail', 'Thumbnail'),
        ('medium', 'Medium'),
    ], default='original')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['image', 'created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Download of {self.image.title} by {self.user or self.session_id}"


class SmartCollection(models.Model):
    """AI-powered smart collections that automatically categorize images"""
    name = models.CharField(max_length=200, help_text="Collection name")
    description = models.TextField(blank=True, help_text="Collection description")
    
    # AI Criteria
    ai_tags = models.JSONField(default=list, blank=True, help_text="Required AI tags")
    ai_objects = models.JSONField(default=list, blank=True, help_text="Required detected objects")
    ai_scene_type = models.CharField(max_length=100, blank=True, help_text="Required scene type")
    ai_sentiment = models.CharField(max_length=50, blank=True, help_text="Required sentiment")
    ai_color_palette = models.JSONField(default=list, blank=True, help_text="Required color palette")
    min_quality_score = models.FloatField(default=0.0, help_text="Minimum AI quality score")
    
    # Collection Settings
    is_active = models.BooleanField(default=True, help_text="Active collection")
    is_featured = models.BooleanField(default=False, help_text="Featured collection")
    auto_update = models.BooleanField(default=True, help_text="Automatically update with new images")
    max_images = models.PositiveIntegerField(default=50, help_text="Maximum images in collection")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(null=True, blank=True, help_text="Last auto-update")
    
    class Meta:
        ordering = ['-is_featured', 'name']
        verbose_name = "Smart Collection"
        verbose_name_plural = "Smart Collections"
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['auto_update', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_image_count(self):
        """Get number of images in this collection"""
        return self.collection_images.filter(is_active=True).count()
    
    def get_images(self):
        """Get images in this collection"""
        return self.collection_images.filter(is_active=True).order_by('-created_at')[:self.max_images]
    
    def update_collection(self):
        """Update collection with matching images"""
        from django.db.models import Q
        
        # Build query based on AI criteria
        query = Q(is_active=True)
        
        if self.ai_tags:
            for tag in self.ai_tags:
                query &= Q(ai_tags__icontains=tag)
        
        if self.ai_objects:
            for obj in self.ai_objects:
                query &= Q(ai_objects__icontains=obj)
        
        if self.ai_scene_type:
            query &= Q(ai_scene_type__icontains=self.ai_scene_type)
        
        if self.ai_sentiment:
            query &= Q(ai_sentiment__icontains=self.ai_sentiment)
        
        if self.min_quality_score > 0:
            query &= Q(ai_quality_score__gte=self.min_quality_score)
        
        # Get matching images
        matching_images = GalleryImage.objects.filter(query).order_by('-ai_quality_score')[:self.max_images]
        
        # Clear existing collection images
        self.collection_images.all().delete()
        
        # Add new images to collection
        for i, image in enumerate(matching_images):
            SmartCollectionImage.objects.create(
                collection=self,
                image=image,
                match_score=self.calculate_match_score(image),
                order=i
            )
        
        # Update last updated timestamp
        from django.utils import timezone
        self.last_updated = timezone.now()
        self.save()
        
        return len(matching_images)
    
    def calculate_match_score(self, image):
        """Calculate how well an image matches this collection"""
        score = 0.0
        
        # Tag matching
        if self.ai_tags and image.ai_tags:
            matching_tags = set(self.ai_tags) & set(image.ai_tags)
            score += len(matching_tags) / len(self.ai_tags) * 0.3
        
        # Object matching
        if self.ai_objects and image.ai_objects:
            matching_objects = set(self.ai_objects) & set(image.ai_objects)
            score += len(matching_objects) / len(self.ai_objects) * 0.25
        
        # Scene type matching
        if self.ai_scene_type and image.ai_scene_type:
            if self.ai_scene_type.lower() in image.ai_scene_type.lower():
                score += 0.2
        
        # Sentiment matching
        if self.ai_sentiment and image.ai_sentiment:
            if self.ai_sentiment.lower() == image.ai_sentiment.lower():
                score += 0.15
        
        # Quality score
        if self.min_quality_score > 0:
            score += min(image.ai_quality_score / self.min_quality_score, 1.0) * 0.1
        
        return min(score, 1.0)


class SmartCollectionImage(models.Model):
    """Images in smart collections with match scores"""
    collection = models.ForeignKey(SmartCollection, on_delete=models.CASCADE, related_name='collection_images')
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='smart_collections')
    match_score = models.FloatField(default=0.0, help_text="How well this image matches the collection")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-match_score', 'order']
        unique_together = ['collection', 'image']
        indexes = [
            models.Index(fields=['collection', 'match_score']),
            models.Index(fields=['image', 'collection']),
        ]
    
    def __str__(self):
        return f"{self.collection.name} - {self.image.title}"


class AutoCategorizationRule(models.Model):
    """Rules for automatic image categorization"""
    name = models.CharField(max_length=200, help_text="Rule name")
    description = models.TextField(blank=True, help_text="Rule description")
    
    # Conditions
    ai_tags = models.JSONField(default=list, blank=True, help_text="Required AI tags")
    ai_objects = models.JSONField(default=list, blank=True, help_text="Required detected objects")
    ai_scene_type = models.CharField(max_length=100, blank=True, help_text="Required scene type")
    ai_sentiment = models.CharField(max_length=50, blank=True, help_text="Required sentiment")
    min_quality_score = models.FloatField(default=0.0, help_text="Minimum AI quality score")
    
    # Actions
    target_category = models.CharField(max_length=50, choices=[
        ('events', 'Events'),
        ('team', 'Team'),
        ('office', 'Office'),
        ('community', 'Community'),
        ('awards', 'Awards'),
    ], help_text="Category to assign")
    
    target_album = models.ForeignKey(GalleryAlbum, on_delete=models.SET_NULL, null=True, blank=True, help_text="Album to assign")
    mark_featured = models.BooleanField(default=False, help_text="Mark as featured")
    
    # Rule Settings
    is_active = models.BooleanField(default=True, help_text="Active rule")
    priority = models.PositiveIntegerField(default=0, help_text="Rule priority (higher = more important)")
    auto_apply = models.BooleanField(default=True, help_text="Automatically apply to new images")
    
    # Statistics
    times_applied = models.PositiveIntegerField(default=0, help_text="Number of times this rule was applied")
    last_applied = models.DateTimeField(null=True, blank=True, help_text="Last time this rule was applied")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = "Auto Categorization Rule"
        verbose_name_plural = "Auto Categorization Rules"
        indexes = [
            models.Index(fields=['is_active', 'auto_apply', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.name} → {self.target_category}"
    
    def apply_to_image(self, image):
        """Apply this rule to an image"""
        if not self.matches_image(image):
            return False
        
        # Apply the rule
        image.category = self.target_category
        if self.target_album:
            image.album = self.target_album
        if self.mark_featured:
            image.is_featured = True
        
        image.save()
        
        # Update statistics
        self.times_applied += 1
        from django.utils import timezone
        self.last_applied = timezone.now()
        self.save()
        
        return True
    
    def matches_image(self, image):
        """Check if an image matches this rule"""
        # Tag matching
        if self.ai_tags and image.ai_tags:
            if not any(tag in image.ai_tags for tag in self.ai_tags):
                return False
        
        # Object matching
        if self.ai_objects and image.ai_objects:
            if not any(obj in image.ai_objects for obj in self.ai_objects):
                return False
        
        # Scene type matching
        if self.ai_scene_type and image.ai_scene_type:
            if self.ai_scene_type.lower() not in image.ai_scene_type.lower():
                return False
        
        # Sentiment matching
        if self.ai_sentiment and image.ai_sentiment:
            if self.ai_sentiment.lower() != image.ai_sentiment.lower():
                return False
        
        # Quality score
        if self.min_quality_score > 0:
            if image.ai_quality_score < self.min_quality_score:
                return False
        
        return True


class ImageAnalysisJob(models.Model):
    """Background jobs for AI image analysis"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='analysis_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, help_text="Error message if failed")
    
    # Analysis Results
    analysis_data = models.JSONField(default=dict, blank=True, help_text="Raw analysis data")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Image Analysis Job"
        verbose_name_plural = "Image Analysis Jobs"
    
    def __str__(self):
        return f"Analysis for {self.image.title} - {self.status}"