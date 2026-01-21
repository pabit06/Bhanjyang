"""
Business logic services for the Downloads app.

This module contains service classes that handle business logic
separate from views, making the code more maintainable and testable.
"""
import logging
from typing import Dict, Any, List, Tuple, Optional, Union
from django.db.models import Q, QuerySet
from django.utils import timezone
from django.http import HttpRequest

from .models import DownloadableFile, FileCategory, PriorityLevel
from .performance import (
    DownloadsCache, DownloadsPerformanceMonitor, DownloadsQueryOptimizer
)
from .security import AccessControlManager, SecurityAuditLogger
from .utils.performance import track_performance
from .utils.error_codes import DownloadsErrorCodes

logger = logging.getLogger(__name__)


class DownloadsService:
    """Service class for handling download center operations."""
    
    @staticmethod
    @track_performance('download_center', '/downloads/')
    def get_download_center_context(
        request_params: Dict[str, Any], 
        show_all: bool = False
    ) -> Dict[str, Any]:
        """
        Get context data for the download center page.
        
        Args:
            request_params: Dictionary with query parameters (category, priority, featured, q)
            show_all: Boolean indicating whether to show all files
            
        Returns:
            dict: Context dictionary for the template
        """
        category_code = request_params.get('category')
        priority_code = request_params.get('priority')
        featured_only = request_params.get('featured') == 'true'
        query = request_params.get('q', '').strip()
        
        # Generate cache key
        cache_key = DownloadsCache.get_file_list_cache_key(
            category=category_code,
            priority=priority_code,
            featured_only=featured_only,
            query=query
        )
        
        # Try to get cached data first
        cached_data = DownloadsPerformanceMonitor.get_cached_file_list(cache_key)
        if cached_data and not show_all:
            logger.debug("Using cached file list data")
            return cached_data
        
        # Get filtered files
        downloads_list = DownloadsService._get_filtered_files(
            category_code, priority_code, featured_only, query
        )
        
        # Group files by category
        files_by_category = DownloadsService._group_files_by_category(
            downloads_list, show_all
        )
        
        # Get featured files
        featured_files = DownloadsService._get_featured_files()
        
        context = {
            'files_by_category': files_by_category,
            'featured_files': featured_files,
            'active_category': category_code or '',
            'active_priority': priority_code or '',
            'featured_only': featured_only,
            'categories': FileCategory.choices,
            'priorities': PriorityLevel.choices,
            'q': query,
            'show_all': show_all,
            'total_files': downloads_list.count(),
        }
        
        # Cache the context data
        DownloadsPerformanceMonitor.cache_file_list(context, cache_key)
        
        return context
    
    @staticmethod
    def _get_filtered_files(
        category_code: Optional[str],
        priority_code: Optional[str],
        featured_only: bool,
        query: str
    ) -> QuerySet[DownloadableFile]:
        """
        Get filtered list of downloadable files.
        
        Args:
            category_code: Category filter code
            priority_code: Priority filter code
            featured_only: Boolean to filter only featured files
            query: Search query string
            
        Returns:
            QuerySet: Filtered DownloadableFile queryset
        """
        # Start with the optimized queryset
        downloads_list = DownloadsQueryOptimizer.get_optimized_file_queryset().filter(
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        ).order_by('-priority', '-uploaded_at')
        
        # Apply filters if they exist
        valid_category_codes = {code for code, _ in FileCategory.choices}
        if category_code in valid_category_codes:
            downloads_list = downloads_list.filter(category=category_code)
        
        valid_priority_codes = {code for code, _ in PriorityLevel.choices}
        if priority_code in valid_priority_codes:
            downloads_list = downloads_list.filter(priority=priority_code)
        
        if featured_only:
            downloads_list = downloads_list.filter(is_featured=True)
        
        if query:
            downloads_list = downloads_list.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) | 
                Q(tags__icontains=query)
            )
        
        return downloads_list
    
    @staticmethod
    def _group_files_by_category(
        downloads_list: QuerySet[DownloadableFile],
        show_all: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        Group files by category with "Show More" functionality.
        
        Args:
            downloads_list: QuerySet of DownloadableFile objects
            show_all: Boolean indicating whether to show all files
            
        Returns:
            dict: Dictionary with category codes as keys
        """
        files_by_category = {}
        files_per_category = 6  # Show 6 files initially
        
        for category_code_key, category_label in FileCategory.choices:
            category_files = downloads_list.filter(category=category_code_key)
            total_count = category_files.count()
            
            if total_count > 0:
                # Show all files if show_all is True, otherwise limit to files_per_category
                files_to_show = category_files if show_all else category_files[:files_per_category]
                
                files_by_category[category_code_key] = {
                    'files': list(files_to_show),
                    'total_count': total_count,
                    'has_more': total_count > files_per_category and not show_all,
                    'remaining_count': max(0, total_count - files_per_category) if not show_all else 0,
                    'label': category_label
                }
        
        return files_by_category
    
    @staticmethod
    def _get_featured_files() -> List[DownloadableFile]:
        """
        Get featured files for display.
        
        Returns:
            list: List of featured DownloadableFile objects
        """
        featured_files_cache_key = DownloadsCache.get_file_list_cache_key(featured_only=True)
        featured_files = DownloadsPerformanceMonitor.get_cached_file_list(featured_files_cache_key)
        
        if not featured_files:
            featured_files = list(DownloadsQueryOptimizer.get_optimized_file_queryset().filter(
                is_active=True,
                is_featured=True
            ).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
            ).order_by('-priority', '-uploaded_at')[:6])
            
            # Cache featured files
            DownloadsPerformanceMonitor.cache_file_list(featured_files, featured_files_cache_key)
        
        return featured_files


class FileDownloadService:
    """Service class for handling file download operations."""
    
    @staticmethod
    @track_performance('file_download')
    def process_file_download(
        request: HttpRequest,
        file_obj: DownloadableFile
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process a file download request.
        
        Args:
            request: HTTP request object
            file_obj: DownloadableFile instance
            
        Returns:
            tuple: (success: bool, file_url_or_none: Optional[str], error_code_or_none: Optional[str])
        """
        # Check if file has expired
        if file_obj.is_expired:
            logger.warning(f"Attempted download of expired file ID {file_obj.pk}")
            SecurityAuditLogger.log_download_attempt(request, file_obj, False, "File expired")
            return False, None, DownloadsErrorCodes.FILE_EXPIRED
        
        # Check access permissions
        can_download, reason = AccessControlManager.can_download_file(request.user, file_obj)
        if not can_download:
            SecurityAuditLogger.log_download_attempt(request, file_obj, False, reason)
            error_code = DownloadsErrorCodes.ACCESS_DENIED
            return False, None, error_code
        
        # Virus scan check (before allowing download)
        from .security import VirusScanManager
        try:
            file_path = file_obj.file.path
            is_clean, scan_result = VirusScanManager.scan_file(file_path)
            
            if not is_clean:
                logger.error(
                    f"Virus detected in file ID {file_obj.pk}: {scan_result}"
                )
                SecurityAuditLogger.log_download_attempt(
                    request, file_obj, False,
                    f"Virus detected: {scan_result}"
                )
                return False, None, DownloadsErrorCodes.VIRUS_DETECTED
            else:
                logger.debug(f"Virus scan passed for file ID {file_obj.pk}: {scan_result}")
        except Exception as e:
            # If file path doesn't exist or scan fails, log but decide based on settings
            from django.conf import settings
            downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
            require_scan = downloads_settings.get('REQUIRE_VIRUS_SCAN', False)
            
            if require_scan:
                # If scan is required but failed, block download
                logger.error(
                    f"Virus scan required but failed for file ID {file_obj.pk}: {e}"
                )
                SecurityAuditLogger.log_download_attempt(
                    request, file_obj, False,
                    f"Virus scan failed: {str(e)}"
                )
                return False, None, DownloadsErrorCodes.VIRUS_DETECTED
            else:
                # If scan is optional and fails, allow but log warning
                logger.warning(
                    f"Could not scan file ID {file_obj.pk} for viruses: {e}. "
                    "Allowing download (scan is optional)."
                )
        
        # Verify file integrity (hash check)
        if file_obj.file_hash:
            from .security import FileSecurityValidator
            try:
                file_path = file_obj.file.path
                is_valid, current_hash, error_msg = FileSecurityValidator.verify_file_hash(
                    file_path,
                    file_obj.file_hash
                )
                
                if not is_valid:
                    logger.error(
                        f"File integrity check failed for file ID {file_obj.pk}. "
                        f"Expected hash: {file_obj.file_hash[:16]}..., "
                        f"Current hash: {current_hash[:16] if current_hash else 'N/A'}"
                    )
                    SecurityAuditLogger.log_download_attempt(
                        request, file_obj, False, 
                        f"File integrity check failed: {error_msg}"
                    )
                    return False, None, DownloadsErrorCodes.FILE_INTEGRITY_FAILED
            except Exception as e:
                # If file path doesn't exist or other error, log but don't block
                # (file might be on remote storage)
                logger.warning(
                    f"Could not verify file integrity for file ID {file_obj.pk}: {e}. "
                    "Skipping integrity check."
                )
        
        try:
            # Increment download count
            file_obj.increment_download_count()
            SecurityAuditLogger.log_download_attempt(request, file_obj, True)
            # Return secure URL instead of direct media URL
            # This ensures files are served through Django view with access control
            from django.urls import reverse
            secure_url = reverse('downloads:serve_file', kwargs={'pk': file_obj.pk})
            return True, secure_url, None
        except Exception as exc:
            logger.error(
                "Failed to increment download count for file ID %s: %s",
                file_obj.pk, exc,
                exc_info=True
            )
            return False, None, DownloadsErrorCodes.DATABASE_ERROR
    
    @staticmethod
    def process_file_view(
        request: HttpRequest,
        file_obj: DownloadableFile
    ) -> bool:
        """
        Process a file view request (increment view count).
        
        Args:
            request: HTTP request object
            file_obj: DownloadableFile instance
            
        Returns:
            bool: Success status
        """
        if file_obj.is_expired:
            logger.warning(f"Attempted view of expired file ID {file_obj.pk}")
            return False
        
        try:
            file_obj.increment_view_count()
            return True
        except Exception as exc:
            logger.error(
                "Failed to increment view count for file ID %s: %s",
                file_obj.pk, exc,
                exc_info=True
            )
            return False


class BulkDownloadService:
    """Service class for handling bulk download operations."""
    
    @staticmethod
    def get_accessible_files(
        user: Optional[Any],
        file_ids: List[Union[int, str]]
    ) -> List[DownloadableFile]:
        """
        Get list of files that user can download.
        
        Args:
            user: User instance (optional)
            file_ids: List of file IDs to check
            
        Returns:
            list: List of DownloadableFile objects user can access
        """
        accessible_files = []
        
        for file_id in file_ids:
            try:
                file_obj = DownloadableFile.objects.get(pk=file_id, is_active=True)
                can_download, reason = AccessControlManager.can_download_file(user, file_obj)
                if can_download and not file_obj.is_expired:
                    accessible_files.append(file_obj)
            except DownloadableFile.DoesNotExist:
                continue
        
        return accessible_files
    
    @staticmethod
    @track_performance('bulk_download')
    def create_zip_file(
        file_objects: List[DownloadableFile]
    ) -> Tuple[str, int, List[int]]:
        """
        Create a ZIP file containing multiple files.
        
        Args:
            file_objects: List of DownloadableFile objects
            
        Returns:
            tuple: (temp_file_path: str, success_count: int, failed_files: List[int])
        """
        import zipfile
        import tempfile
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        success_count = 0
        failed_files = []
        
        with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_obj in file_objects:
                try:
                    # Add file to ZIP
                    zip_file.write(file_obj.file.path, file_obj.file.name)
                    success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to add file {file_obj.id} to ZIP: {e}")
                    failed_files.append(file_obj.id)
                    continue
        
        return temp_file.name, success_count, failed_files


class DownloadsAnalyticsService:
    """Service class for download analytics and statistics."""
    
    @staticmethod
    @track_performance('download_stats')
    def get_download_stats() -> Dict[str, Any]:
        """
        Get statistics about downloads.
        
        Returns:
            dict: Dictionary with various statistics
        """
        total_files = DownloadableFile.objects.filter(is_active=True).count()
        featured_files = DownloadableFile.objects.filter(is_active=True, is_featured=True).count()
        total_downloads = sum(
            DownloadableFile.objects.filter(is_active=True).values_list('download_count', flat=True)
        )
        total_views = sum(
            DownloadableFile.objects.filter(is_active=True).values_list('view_count', flat=True)
        )
        
        # Files by category
        files_by_category = {}
        for category_code, category_label in FileCategory.choices:
            count = DownloadableFile.objects.filter(
                is_active=True, category=category_code
            ).count()
            if count > 0:
                files_by_category[category_code] = {
                    'label': category_label,
                    'count': count
                }
        
        return {
            'total_files': total_files,
            'featured_files': featured_files,
            'total_downloads': total_downloads,
            'total_views': total_views,
            'files_by_category': files_by_category,
        }

