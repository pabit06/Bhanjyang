import logging
import zipfile
import tempfile
import os
import time
from typing import Any, Dict, List, Optional
from django.db.models import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views import View
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import activate

from apps.core.view_mixins import NepaliLanguageMixin
from .models import DownloadableFile, FileCategory, PriorityLevel
from .security import (
    rate_limit_downloads, rate_limit_bulk_downloads, require_download_permission,
    AccessControlManager, SecurityAuditLogger
)
from .performance import (
    DownloadsCache, DownloadsPerformanceMonitor, DownloadsQueryOptimizer,
    performance_monitor
)
from .services import FileDownloadService, BulkDownloadService
from .utils.error_codes import DownloadsErrorCodes, get_user_friendly_message, get_status_code_for_error
from .utils.performance import track_download_performance, track_bulk_download_performance

logger = logging.getLogger(__name__)


@method_decorator(performance_monitor, name='dispatch')
class DownloadCenterView(NepaliLanguageMixin, TemplateView):
    """
    Render the download center with files organized by category.
    Shows 6 files per category initially with "Show More" functionality.
    Only active, non-expired files are displayed.
    Enhanced with caching for better performance.
    """
    template_name = 'downloads/download.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Get context data for the view, utilizing caching and optimized queries.
        
        Returns:
            dict: Context dictionary for the template
        """
        # Call the mixin logic first
        # Note: NepaliLanguageMixin sets language in dispatch, but we can't assume context here unless mixed in properly
        # TemplateView calls get_context_data

        request = self.request
        category_code = request.GET.get('category')
        priority_code = request.GET.get('priority')
        featured_only = request.GET.get('featured') == 'true'
        query = request.GET.get('q', '').strip()
        show_all = request.GET.get('show_all') == 'true'

        # Generate cache key
        cache_key = DownloadsCache.get_file_list_cache_key(
            category=category_code,
            priority=priority_code,
            featured_only=featured_only,
            query=query
        )

        # Try to get cached data first
        cached_data = DownloadsPerformanceMonitor.get_cached_file_list(cache_key)
        
        # Initialize context with standard view data
        context = super().get_context_data(**kwargs)
        
        # Only use cached data if it's a dict
        if cached_data and isinstance(cached_data, dict) and not show_all:  
            logger.debug("Using cached file list data")
            context.update(cached_data)
            return context

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

        # Group files by category with "Show More" functionality
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

        # Get featured files for a separate section (use cache if available)
        featured_files_cache_key = DownloadsCache.get_file_list_cache_key(featured_only=True)
        cached_featured = DownloadsPerformanceMonitor.get_cached_file_list(featured_files_cache_key)
        
        # Ensure cached_featured is a list, not a dict (context)
        if cached_featured and isinstance(cached_featured, list):
            featured_files = cached_featured
        elif cached_featured and isinstance(cached_featured, dict):
            # If it's a dict, it's probably a full context, extract featured_files
            featured_files = cached_featured.get('featured_files', [])
        else:
            featured_files = list(DownloadsQueryOptimizer.get_optimized_file_queryset().filter(
                is_active=True,
                is_featured=True
            ).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
            ).order_by('-priority', '-uploaded_at')[:6])
            
            # Cache featured files as a list
            DownloadsPerformanceMonitor.cache_file_list(featured_files, featured_files_cache_key)

        # Prepare serializable data for caching
        cacheable_data = {
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
        
        # Cache the serializable data
        DownloadsPerformanceMonitor.cache_file_list(cacheable_data, cache_key)
        
        # Update context
        context.update(cacheable_data)
        
        return context


@method_decorator(rate_limit_downloads, name='dispatch')
class SecureFileServeView(View):
    """
    Securely serve files through Django view.
    This prevents direct URL access to media files and ensures all downloads
    go through access control and integrity checks.
    """
    
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request: HttpRequest, pk: int) -> Any:
        """
        Serve file securely with proper headers and access control.
        
        This view:
        - Verifies user has permission to download
        - Checks file expiration
        - Verifies file integrity
        - Serves file with appropriate headers
        - Prevents direct URL access
        """
        file_obj = get_object_or_404(DownloadableFile, pk=pk, is_active=True)
        
        # Check if file has expired
        if file_obj.is_expired:
            logger.warning(f"Attempted access to expired file ID {file_obj.pk}")
            return redirect('downloads:download_center')
        
        # Check access permissions
        can_download, reason = AccessControlManager.can_download_file(request.user, file_obj)
        if not can_download:
            SecurityAuditLogger.log_download_attempt(request, file_obj, False, reason)
            error_message = get_user_friendly_message(DownloadsErrorCodes.ACCESS_DENIED)
            return JsonResponse({
                'error': error_message,
                'error_code': DownloadsErrorCodes.ACCESS_DENIED
            }, status=get_status_code_for_error(DownloadsErrorCodes.ACCESS_DENIED))
        
        # Virus scan check (before serving file)
        from .security import VirusScanManager
        try:
            file_path = file_obj.file.path
            is_clean, scan_result = VirusScanManager.scan_file(file_path)
            
            if not is_clean:
                logger.error(
                    f"Virus detected in file ID {file_obj.pk} during serve: {scan_result}"
                )
                SecurityAuditLogger.log_download_attempt(
                    request, file_obj, False,
                    f"Virus detected: {scan_result}"
                )
                error_message = get_user_friendly_message(DownloadsErrorCodes.VIRUS_DETECTED)
                return JsonResponse({
                    'error': error_message,
                    'error_code': DownloadsErrorCodes.VIRUS_DETECTED
                }, status=get_status_code_for_error(DownloadsErrorCodes.VIRUS_DETECTED))
            else:
                logger.debug(f"Virus scan passed for file ID {file_obj.pk}: {scan_result}")
        except Exception as e:
            # If file path doesn't exist or scan fails, decide based on settings
            from django.conf import settings
            downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
            require_scan = downloads_settings.get('REQUIRE_VIRUS_SCAN', False)
            
            if require_scan:
                logger.error(
                    f"Virus scan required but failed for file ID {file_obj.pk}: {e}"
                )
                SecurityAuditLogger.log_download_attempt(
                    request, file_obj, False,
                    f"Virus scan failed: {str(e)}"
                )
                error_message = get_user_friendly_message(DownloadsErrorCodes.VIRUS_DETECTED)
                return JsonResponse({
                    'error': error_message,
                    'error_code': DownloadsErrorCodes.VIRUS_DETECTED
                }, status=get_status_code_for_error(DownloadsErrorCodes.VIRUS_DETECTED))
            else:
                logger.warning(
                    f"Could not scan file ID {file_obj.pk} for viruses: {e}. "
                    "Allowing serve (scan is optional)."
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
                        f"File integrity check failed for file ID {file_obj.pk} during serve. "
                        f"Expected hash: {file_obj.file_hash[:16]}..., "
                        f"Current hash: {current_hash[:16] if current_hash else 'N/A'}"
                    )
                    SecurityAuditLogger.log_download_attempt(
                        request, file_obj, False, 
                        f"File integrity check failed: {error_msg}"
                    )
                    error_message = get_user_friendly_message(DownloadsErrorCodes.FILE_INTEGRITY_FAILED)
                    return JsonResponse({
                        'error': error_message,
                        'error_code': DownloadsErrorCodes.FILE_INTEGRITY_FAILED
                    }, status=get_status_code_for_error(DownloadsErrorCodes.FILE_INTEGRITY_FAILED))
            except Exception as e:
                # If file path doesn't exist or other error, log but don't block
                logger.warning(
                    f"Could not verify file integrity for file ID {file_obj.pk} during serve: {e}. "
                    "Skipping integrity check."
                )
        
        # Get file path
        try:
            file_path = file_obj.file.path
            if not os.path.exists(file_path):
                logger.error(f"File not found on disk: {file_path}")
                error_message = get_user_friendly_message(DownloadsErrorCodes.FILE_NOT_FOUND)
                return JsonResponse({
                    'error': error_message,
                    'error_code': DownloadsErrorCodes.FILE_NOT_FOUND
                }, status=get_status_code_for_error(DownloadsErrorCodes.FILE_NOT_FOUND))
        except Exception as e:
            logger.error(f"Error accessing file path for file ID {file_obj.pk}: {e}", exc_info=True)
            error_message = get_user_friendly_message(DownloadsErrorCodes.DOWNLOAD_ERROR)
            return JsonResponse({
                'error': error_message,
                'error_code': DownloadsErrorCodes.DOWNLOAD_ERROR
            }, status=get_status_code_for_error(DownloadsErrorCodes.DOWNLOAD_ERROR))
        
        # Determine content type
        import mimetypes
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Set filename for download
        filename = os.path.basename(file_obj.file.name)
        # Sanitize filename for Content-Disposition header
        from .utils.helpers import sanitize_filename
        safe_filename = sanitize_filename(filename)
        
        # Use chunked streaming for large files (50MB+)
        # This prevents loading entire file into memory
        CHUNKED_DOWNLOAD_THRESHOLD = 50 * 1024 * 1024  # 50MB
        
        if file_size >= CHUNKED_DOWNLOAD_THRESHOLD:
            # Use StreamingHttpResponse for large files
            from django.http import StreamingHttpResponse
            
            def file_iterator(file_path, chunk_size=8192):
                """Generator function to read file in chunks"""
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            
            response = StreamingHttpResponse(
                file_iterator(file_path),
                content_type=content_type
            )
            response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
            response['Content-Length'] = file_size
            
            # Security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Log successful file serve
            SecurityAuditLogger.log_download_attempt(
                request, file_obj, True, 
                f"File served securely (chunked, size: {file_size} bytes)"
            )
            
            return response
        else:
            # For smaller files, read into memory (faster for small files)
            try:
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Create response with appropriate headers
                response = HttpResponse(file_content, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
                response['Content-Length'] = len(file_content)
                
                # Security headers
                response['X-Content-Type-Options'] = 'nosniff'
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                
                # Log successful file serve
                SecurityAuditLogger.log_download_attempt(request, file_obj, True, "File served securely")
                
                return response
            except Exception as e:
                logger.error(f"Error serving file ID {file_obj.pk}: {e}", exc_info=True)
                error_message = get_user_friendly_message(DownloadsErrorCodes.DOWNLOAD_ERROR)
                return JsonResponse({
                    'error': error_message,
                    'error_code': DownloadsErrorCodes.DOWNLOAD_ERROR
                }, status=get_status_code_for_error(DownloadsErrorCodes.DOWNLOAD_ERROR))


class DownloadFileView(View):
    """
    Increment the download count and redirect to the secure file serving view.
    Handles login requirements and expiration checks with enhanced security.
    """
    
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        activate('ne')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, pk: int) -> Any:
        """Handle file download request with performance tracking and error handling."""
        start_time = time.time()
        file_obj = get_object_or_404(DownloadableFile, pk=pk, is_active=True)

        # Process download using service layer
        success, file_url, error_code = FileDownloadService.process_file_download(request, file_obj)
        
        if not success:
            # Track failed download performance
            download_time = (time.time() - start_time) * 1000
            track_download_performance(
                download_time,
                0,
                request.META,
                request.user if request.user.is_authenticated else None,
                request.session.session_key if hasattr(request.session, 'session_key') else None,
                file_obj.pk
            )
            
            # Return appropriate error response
            if error_code == DownloadsErrorCodes.FILE_EXPIRED:
                return redirect('downloads:download_center')
            elif error_code == DownloadsErrorCodes.ACCESS_DENIED:
                error_message = get_user_friendly_message(error_code)
                return JsonResponse({
                    'error': error_message,
                    'error_code': error_code
                }, status=get_status_code_for_error(error_code))
            else:
                error_message = get_user_friendly_message(error_code or DownloadsErrorCodes.DOWNLOAD_ERROR)
                return JsonResponse({
                    'error': error_message,
                    'error_code': error_code or DownloadsErrorCodes.DOWNLOAD_ERROR
                }, status=get_status_code_for_error(error_code or DownloadsErrorCodes.DOWNLOAD_ERROR))

        # Track successful download performance
        download_time = (time.time() - start_time) * 1000
        file_size = file_obj.file.size if hasattr(file_obj.file, 'size') else 0
        track_download_performance(
            download_time,
            file_size,
            request.META,
            request.user if request.user.is_authenticated else None,
            request.session.session_key if hasattr(request.session, 'session_key') else None,
            file_obj.pk
        )

        # Redirect to secure file serving view
        return redirect(file_url)


class FileDetailView(NepaliLanguageMixin, DetailView):
    """
    Display detailed information about a file and increment view count.
    """
    model = DownloadableFile
    template_name = 'downloads/file_detail.html'
    context_object_name = 'file'
    
    def get_queryset(self) -> Any:
        return DownloadableFile.objects.filter(is_active=True)
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Handle file detail view request."""
        self.object = self.get_object()
        
        # Check if file has expired
        if self.object.is_expired:
            logger.warning(f"Attempted view of expired file ID {self.object.pk}")
            return redirect('downloads:download_center')

        # Increment view count using service
        FileDownloadService.process_file_view(request, self.object)
            
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


@method_decorator(rate_limit_bulk_downloads, name='dispatch')
class BulkDownloadView(LoginRequiredMixin, View):
    """
    Create a ZIP file containing multiple downloadable files.
    """
    
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        activate('ne')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest) -> Any:
        """Handle bulk download request with performance tracking and error handling."""
        start_time = time.time()
        
        try:
            file_ids = request.POST.getlist('file_ids')
            if not file_ids:
                error_message = get_user_friendly_message(DownloadsErrorCodes.BULK_DOWNLOAD_EMPTY)
                return JsonResponse({
                    'error': error_message,
                    'error_code': DownloadsErrorCodes.BULK_DOWNLOAD_EMPTY
                }, status=get_status_code_for_error(DownloadsErrorCodes.BULK_DOWNLOAD_EMPTY))
            
            # Check bulk download limit
            from .utils.constants import DEFAULT_PAGE_SIZE
            if len(file_ids) > DEFAULT_PAGE_SIZE:
                error_message = get_user_friendly_message(DownloadsErrorCodes.BULK_DOWNLOAD_LIMIT_EXCEEDED)
                return JsonResponse({
                    'error': error_message,
                    'error_code': DownloadsErrorCodes.BULK_DOWNLOAD_LIMIT_EXCEEDED
                }, status=get_status_code_for_error(DownloadsErrorCodes.BULK_DOWNLOAD_LIMIT_EXCEEDED))
            
            # Get files that user can download using service
            downloadable_files = BulkDownloadService.get_accessible_files(
                request.user if request.user.is_authenticated else None,
                file_ids
            )
            
            if not downloadable_files:
                error_message = get_user_friendly_message(DownloadsErrorCodes.ACCESS_DENIED)
                return JsonResponse({
                    'error': error_message,
                    'error_code': DownloadsErrorCodes.ACCESS_DENIED
                }, status=get_status_code_for_error(DownloadsErrorCodes.ACCESS_DENIED))
            
            # Check if async bulk download is enabled and file count exceeds threshold
            from django.conf import settings
            downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
            async_threshold = downloads_settings.get('ASYNC_BULK_DOWNLOAD_THRESHOLD', 10)
            use_async = downloads_settings.get('ENABLE_ASYNC_BULK_DOWNLOAD', True)
            
            if use_async and len(downloadable_files) >= async_threshold:
                # Use Celery task for large bulk downloads
                try:
                    from .tasks import create_bulk_download_zip_task
                    
                    # Get user email for notification
                    user_email = None
                    if request.user.is_authenticated and hasattr(request.user, 'email'):
                        user_email = request.user.email
                    
                    # Start async task
                    task = create_bulk_download_zip_task.delay(
                        file_ids=[f.id for f in downloadable_files],
                        user_id=request.user.id if request.user.is_authenticated else None,
                        notification_email=user_email
                    )
                    
                    logger.info(
                        f"Bulk download task started: {task.id} "
                        f"({len(downloadable_files)} files, user: {request.user.id if request.user.is_authenticated else 'anonymous'})"
                    )
                    
                    # Return task ID for client to poll status
                    return JsonResponse({
                        'status': 'processing',
                        'message': 'Your bulk download is being prepared. You will be notified when ready.',
                        'task_id': task.id,
                        'file_count': len(downloadable_files)
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to start async bulk download task: {e}", exc_info=True)
                    # Fall back to synchronous processing
                    logger.info("Falling back to synchronous bulk download")
            
            # Synchronous processing for small bulk downloads
            # Create ZIP file using service
            temp_file_path, success_count, failed_files = BulkDownloadService.create_zip_file(
                downloadable_files
            )
            
            if success_count == 0:
                error_message = get_user_friendly_message(DownloadsErrorCodes.BULK_DOWNLOAD_ERROR)
                return JsonResponse({
                    'error': error_message,
                    'error_code': DownloadsErrorCodes.BULK_DOWNLOAD_ERROR
                }, status=get_status_code_for_error(DownloadsErrorCodes.BULK_DOWNLOAD_ERROR))
            
            # Use chunked streaming for large ZIP files
            zip_size = os.path.getsize(temp_file_path)
            CHUNKED_DOWNLOAD_THRESHOLD = 50 * 1024 * 1024  # 50MB
            
            if zip_size >= CHUNKED_DOWNLOAD_THRESHOLD:
                # Use StreamingHttpResponse for large ZIP files
                from django.http import StreamingHttpResponse
                
                def zip_iterator(file_path, chunk_size=8192):
                    """Generator function to read ZIP file in chunks"""
                    with open(file_path, 'rb') as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            yield chunk
                
                response = StreamingHttpResponse(
                    zip_iterator(temp_file_path),
                    content_type='application/zip'
                )
                response['Content-Disposition'] = f'attachment; filename="downloads_{timezone.now().strftime("%Y%m%d_%H%M%S")}.zip"'
                response['Content-Length'] = zip_size
            else:
                # For smaller ZIP files, read into memory
                with open(temp_file_path, 'rb') as zip_content:
                    response = HttpResponse(zip_content.read(), content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename="downloads_{timezone.now().strftime("%Y%m%d_%H%M%S")}.zip"'
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            # Track bulk download performance
            total_time = (time.time() - start_time) * 1000
            total_size = sum(f.file.size if hasattr(f.file, 'size') else 0 for f in downloadable_files)
            track_bulk_download_performance(
                total_time,
                success_count,
                total_size,
                request.META,
                request.user if request.user.is_authenticated else None,
                request.session.session_key if hasattr(request.session, 'session_key') else None
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Bulk download failed: {e}", exc_info=True)
            error_message = get_user_friendly_message(DownloadsErrorCodes.BULK_DOWNLOAD_ERROR)
            return JsonResponse({
                'error': error_message,
                'error_code': DownloadsErrorCodes.BULK_DOWNLOAD_ERROR
            }, status=get_status_code_for_error(DownloadsErrorCodes.BULK_DOWNLOAD_ERROR))


class DownloadHistoryView(NepaliLanguageMixin, LoginRequiredMixin, ListView):
    """
    Show user's download history.
    
    Note: Currently shows recently accessed files that the user can download.
    A proper download history model would be needed for per-user tracking.
    """
    template_name = 'downloads/download_history.html'
    context_object_name = 'downloads'
    
    def get_queryset(self) -> QuerySet[DownloadableFile]:
        """
        Get queryset for download history.
        
        Returns recently accessed files that are active and accessible to the user.
        For a complete history, a DownloadHistory model would need to be created.
        """
        user = self.request.user
        queryset = DownloadableFile.objects.filter(
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
        
        # Filter by login requirement
        if not user.is_authenticated:
            queryset = queryset.filter(requires_login=False)
        
        # Order by last accessed (most recent first)
        # Files with last_accessed are prioritized
        queryset = queryset.order_by(
            '-last_accessed',
            '-uploaded_at'
        )[:50]  # Limit to 50 most recent
        
        return queryset
        
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Get context data for download history view."""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['total_files'] = self.get_queryset().count()
        context['has_history'] = context['total_files'] > 0
        return context


class BulkDownloadStatusView(LoginRequiredMixin, View):
    """
    Check status of async bulk download task.
    """
    
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request: HttpRequest, task_id: str) -> Any:
        """Get status of bulk download task"""
        try:
            from celery.result import AsyncResult
            from .tasks import create_bulk_download_zip_task
            
            task = AsyncResult(task_id, app=create_bulk_download_zip_task.app)
            
            if task.ready():
                if task.successful():
                    result = task.result
                    return JsonResponse({
                        'status': 'success',
                        'download_url': result.get('download_url'),
                        'file_path': result.get('file_path'),
                        'success_count': result.get('success_count', 0),
                        'failed_files': result.get('failed_files', []),
                        'created_at': result.get('created_at')
                    })
                else:
                    # Task failed
                    return JsonResponse({
                        'status': 'error',
                        'message': str(task.result.get('message', 'Task failed'))
                    }, status=500)
            else:
                # Task still processing
                return JsonResponse({
                    'status': 'processing',
                    'message': 'Your bulk download is still being prepared...'
                })
                
        except Exception as e:
            logger.error(f"Error checking bulk download status: {e}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': 'Error checking task status'
            }, status=500)


class FilePreviewView(View):
    """
    Preview file content (for supported file types).
    """
    
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        activate('ne')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, pk: int) -> Any:
        """Handle file preview request."""
        file_obj = get_object_or_404(DownloadableFile, pk=pk, is_active=True)
        
        # Check access permissions
        can_download, reason = AccessControlManager.can_download_file(request.user, file_obj)
        if not can_download:
            error_message = get_user_friendly_message(DownloadsErrorCodes.ACCESS_DENIED)
            return JsonResponse({
                'error': error_message,
                'error_code': DownloadsErrorCodes.ACCESS_DENIED
            }, status=get_status_code_for_error(DownloadsErrorCodes.ACCESS_DENIED))
        
        # Only allow preview for certain file types
        previewable_types = ['pdf', 'jpg', 'jpeg', 'png', 'gif']
        if file_obj.file_type not in previewable_types:
            error_message = get_user_friendly_message(DownloadsErrorCodes.INVALID_FILE_TYPE)
            return JsonResponse({
                'error': error_message,
                'error_code': DownloadsErrorCodes.INVALID_FILE_TYPE
            }, status=get_status_code_for_error(DownloadsErrorCodes.INVALID_FILE_TYPE))
        
        # Increment view count using service
        FileDownloadService.process_file_view(request, file_obj)
        
        context: Dict[str, Any] = {
            'file': file_obj,
            'preview_url': file_obj.file.url,
        }
        return render(request, 'downloads/file_preview.html', context)
