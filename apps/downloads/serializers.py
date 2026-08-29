"""
DRF Serializers for Downloads API
==================================

Provides serialization/deserialization for DownloadableFile model
and related data for REST API endpoints.

Author: Prem Bhandari
Date: January 6, 2026
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import DownloadableFile, FileCategory, PriorityLevel
from .utils.cdn import CDNManager

User = get_user_model()


class DownloadableFileSerializer(serializers.ModelSerializer):
    """
    Full serializer for DownloadableFile model.
    
    Includes all fields and computed properties.
    """
    # Read-only computed fields
    file_size = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    tag_list = serializers.ReadOnlyField()
    
    # Display fields (human-readable)
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    
    # File URL (absolute)
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    # Uploader info
    uploaded_by_username = serializers.CharField(
        source='uploaded_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = DownloadableFile
        fields = [
            # Identifiers
            'id',
            
            # Basic Info
            'category',
            'category_display',
            'title',
            'description',
            
            # File
            'file',
            'file_url',
            'file_size',
            'file_type',
            'file_hash',
            
            # Thumbnail
            'thumbnail',
            'thumbnail_url',
            
            # Status
            'is_active',
            'is_featured',
            'priority',
            'priority_display',
            
            # Access Control
            'requires_login',
            'expires_at',
            'is_expired',
            
            # Organization
            'tags',
            'tag_list',
            
            # Statistics
            'download_count',
            'view_count',
            'access_count',
            'last_accessed',
            
            # Metadata
            'uploaded_at',
            'updated_at',
            'uploaded_by',
            'uploaded_by_username',
        ]
        read_only_fields = [
            'file_type',
            'file_hash',
            'download_count',
            'view_count',
            'access_count',
            'last_accessed',
            'uploaded_at',
            'updated_at',
        ]
    
    def get_file_url(self, obj):
        """Get absolute secure download URL (served through access-controlled view)."""
        request = self.context.get('request')
        if obj.file and request:
            return CDNManager.get_secure_download_url(obj, request)
        return None
    
    def get_thumbnail_url(self, obj):
        """Get absolute thumbnail URL."""
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class DownloadableFileListSerializer(serializers.ModelSerializer):
    """
    Lighter serializer for list views.
    
    Excludes heavy fields for better performance.
    """
    file_size = serializers.ReadOnlyField()
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DownloadableFile
        fields = [
            'id',
            'category',
            'category_display',
            'title',
            'file_size',
            'file_type',
            'file_url',
            'is_featured',
            'priority',
            'priority_display',
            'download_count',
            'view_count',
            'uploaded_at',
        ]
    
    def get_file_url(self, obj):
        """Get absolute secure download URL (served through access-controlled view)."""
        request = self.context.get('request')
        if obj.file and request:
            return CDNManager.get_secure_download_url(obj, request)
        return None


class DownloadableFileCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating files.
    
    Validates input and handles file uploads.
    """
    class Meta:
        model = DownloadableFile
        fields = [
            'category',
            'title',
            'description',
            'file',
            'is_active',
            'is_featured',
            'priority',
            'requires_login',
            'expires_at',
            'tags',
            'thumbnail',
        ]
    
    def validate_file(self, value):
        """
        Validate uploaded file.
        
        Checks:
        - File size
        - Extension
        - MIME type
        """
        from django.conf import settings
        
        # Get max file size from settings
        max_size = getattr(
            settings,
            'FILE_UPLOAD_MAX_MEMORY_SIZE',
            5 * 1024 * 1024  # 5MB default
        )
        
        if value.size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise serializers.ValidationError(
                f'File size exceeds maximum allowed size of {max_mb}MB.'
            )
        
        # Get allowed extensions
        allowed_extensions = [
            'pdf', 'doc', 'docx', 'xls', 'xlsx',
            'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png'
        ]
        
        # Check extension
        import os
        ext = os.path.splitext(value.name)[1].lower().replace('.', '')
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f'File type "{ext}" is not allowed. '
                f'Allowed types: {", ".join(allowed_extensions)}'
            )
        
        return value
    
    def create(self, validated_data):
        """Create file with current user as uploader."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class FileCategorySerializer(serializers.Serializer):
    """
    Serializer for file category choices.
    """
    code = serializers.CharField()
    label = serializers.CharField()
    
    @staticmethod
    def get_categories():
        """Get all file categories."""
        return [
            {'code': choice[0], 'label': choice[1]}
            for choice in FileCategory.choices
        ]


class FilePrioritySerializer(serializers.Serializer):
    """
    Serializer for file priority choices.
    """
    code = serializers.CharField()
    label = serializers.CharField()
    
    @staticmethod
    def get_priorities():
        """Get all priority levels."""
        return [
            {'code': choice[0], 'label': choice[1]}
            for choice in PriorityLevel.choices
        ]


class FileStatsSerializer(serializers.Serializer):
    """
    Serializer for file download statistics.
    """
    total_files = serializers.IntegerField()
    active_files = serializers.IntegerField()
    total_downloads = serializers.IntegerField()
    total_views = serializers.IntegerField()
    featured_files = serializers.IntegerField()
    expired_files = serializers.IntegerField()
    
    # Category breakdown
    files_by_category = serializers.DictField()
    downloads_by_category = serializers.DictField()
    
    # Most popular
    most_downloaded = DownloadableFileListSerializer(many=True)
    most_viewed = DownloadableFileListSerializer(many=True)
    
    # Recent
    recent_uploads = DownloadableFileListSerializer(many=True)


# Export all serializers
__all__ = [
    'DownloadableFileSerializer',
    'DownloadableFileListSerializer',
    'DownloadableFileCreateUpdateSerializer',
    'FileCategorySerializer',
    'FilePrioritySerializer',
    'FileStatsSerializer',
]
