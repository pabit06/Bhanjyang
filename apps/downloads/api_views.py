"""
REST API Views for Downloads App
=================================

Provides RESTful API endpoints for downloading files using
Django REST Framework ViewSets.

Author: Prem Bhandari
Date: January 6, 2026
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
    AllowAny
)
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging

from .models import DownloadableFile, FileCategory, PriorityLevel
from .serializers import (
    DownloadableFileSerializer,
    DownloadableFileListSerializer,
    DownloadableFileCreateUpdateSerializer,
    FileCategorySerializer,
    FilePrioritySerializer,
    FileStatsSerializer,
)
from .security import AccessControlManager
from .services import (
    FileDownloadService,
   DownloadsAnalyticsService
)
from .security_enhanced import (
    SecurityAuditEnhancedLogger,
    RequestValidator
)

logger = logging.getLogger(__name__)


class DownloadableFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DownloadableFile model.
    
    Endpoints:
    - GET /api/downloads/files/ - List all files
    - GET /api/downloads/files/{id}/ - Get file details
    - POST /api/downloads/files/ - Create file (admin only)
    - PUT/PATCH /api/downloads/files/{id}/ - Update file (admin only)
    - DELETE /api/downloads/files/{id}/ - Delete file (admin only)
    - POST /api/downloads/files/{id}/download/ - Download file
    - POST /api/downloads/files/{id}/increment_view/ - Increment view count
    - GET /api/downloads/files/featured/ - Get featured files
    - GET /api/downloads/files/categories/ - Get categories
    - GET /api/downloads/files/priorities/ - Get priorities
    - GET /api/downloads/files/stats/ - Get statistics (admin only)
    """
    
    queryset = DownloadableFile.objects.filter(
        is_active=True
    ).select_related('uploaded_by').order_by('-priority', '-uploaded_at')
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    
    filterset_fields = {
        'category': ['exact'],
        'priority': ['exact'],
        'is_featured': ['exact'],
        'requires_login': ['exact'],
        'uploaded_at': ['gte', 'lte'],
    }
    
    search_fields = ['title', 'description', 'tags']
    
    ordering_fields = [
        'uploaded_at',
        'download_count',
        'view_count',
        'priority',
        'title'
    ]
    
    ordering = ['-priority', '-uploaded_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return DownloadableFileListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DownloadableFileCreateUpdateSerializer
        return DownloadableFileSerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action == 'stats':
            return [IsAdminUser()]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions.
        """
        queryset = super().get_queryset()
        
        # Exclude expired files
        queryset = queryset.filter(
            models.Q(expires_at__isnull=True) |
            models.Q(expires_at__gt=timezone.now())
        )
        
        return AccessControlManager.filter_accessible_queryset(
            self.request.user,
            queryset,
        )
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """
        Download a file and increment download count.
        
        POST /api/downloads/files/{id}/download/
        
        Returns:
            200: Success with file URL
            403: Forbidden (login required, expired, etc.)
            404: Not found
        """
        file_obj = self.get_object()
        from .utils.helpers import get_client_ip
        client_ip = get_client_ip(request)
        
        # Process download through service
        success, response, error = FileDownloadService.process_file_download(
            request,
            file_obj
        )
        
        if not success:
            # Log failed access
            SecurityAuditEnhancedLogger.log_failed_access(
                request.user,
                file_obj,
                client_ip,
                error
            )
            
            return Response(
                {
                    'error': error,
                    'file_id': file_obj.id,
                    'file_title': file_obj.title
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Log successful download
        SecurityAuditEnhancedLogger.log_download(
            request.user,
            file_obj,
            client_ip
        )
        
        return Response({
            'message': 'Download started',
            'file_id': file_obj.id,
            'file_title': file_obj.title,
            'file_url': request.build_absolute_uri(response),
            'file_size': file_obj.file_size,
            'download_count': file_obj.download_count + 1
        })
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """
        Increment view count for a file.
        
        POST /api/downloads/files/{id}/increment_view/
        
        Returns:
            200: Success
            404: Not found
        """
        file_obj = self.get_object()
        
        # Process view through service
        FileDownloadService.process_file_view(request, file_obj)
        
        return Response({
            'message': 'View count incremented',
            'file_id': file_obj.id,
            'view_count': file_obj.view_count + 1
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured files.
        
        GET /api/downloads/files/featured/
        
        Returns:
            200: List of featured files
        """
        queryset = self.get_queryset().filter(is_featured=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DownloadableFileListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = DownloadableFileListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def categories(self, request):
        """
        Get all file categories.
        
        GET /api/downloads/files/categories/
        
        Returns:
            200: List of categories
        """
        categories = FileCategorySerializer.get_categories()
        return Response(categories)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def priorities(self, request):
        """
        Get all priority levels.
        
        GET /api/downloads/files/priorities/
        
        Returns:
            200: List of priorities
        """
        priorities = FilePrioritySerializer.get_priorities()
        return Response(priorities)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """
        Get download statistics.
        
        GET /api/downloads/files/stats/
        
        Admin only.
        
        Returns:
            200: Statistics data
        """
        stats = DownloadsAnalyticsService.get_download_stats()
        serializer = FileStatsSerializer(stats, context={'request': request})
        return Response(serializer.data)


# Add missing import
from django.db import models


# Export ViewSet
__all__ = ['DownloadableFileViewSet']
