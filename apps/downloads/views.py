import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.translation import activate
from .models import DownloadableFile, FileCategory, PriorityLevel
from .security import (
    rate_limit_downloads, rate_limit_bulk_downloads, require_download_permission,
    AccessControlManager, SecurityAuditLogger
)
from .performance import (
    DownloadsCache, DownloadsPerformanceMonitor, DownloadsQueryOptimizer,
    DownloadsCDNManager, performance_monitor
)

logger = logging.getLogger(__name__)


@performance_monitor
def download_center_view(request):
    """
    Render the download center with files organized by category.
    Shows 6 files per category initially with "Show More" functionality.
    Only active, non-expired files are displayed.
    Enhanced with caching for better performance.
    """
    activate('ne')
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
    # Only use cached data if it's a dict (full context), not a list (just featured_files)
    if cached_data and isinstance(cached_data, dict) and not show_all:  # Don't use cache if showing all files
        logger.debug("Using cached file list data")
        return render(request, 'downloads/download.html', cached_data)

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
    
    return render(request, 'downloads/download.html', context)


@rate_limit_downloads
@require_download_permission
def download_file_view(request, pk):
    """
    Increment the download count and redirect to the actual file URL.
    Handles login requirements and expiration checks with enhanced security.
    """
    activate('ne')
    file_obj = get_object_or_404(DownloadableFile, pk=pk, is_active=True)

    # Check if file has expired
    if file_obj.is_expired:
        logger.warning(f"Attempted download of expired file ID {file_obj.pk}")
        SecurityAuditLogger.log_download_attempt(request, file_obj, False, "File expired")
        return redirect('downloads:download_center')

    # Check access permissions
    can_download, reason = AccessControlManager.can_download_file(request.user, file_obj)
    if not can_download:
        SecurityAuditLogger.log_download_attempt(request, file_obj, False, reason)
        return JsonResponse({'error': reason}, status=403)

    try:
        # Use the new increment method
        file_obj.increment_download_count()
        SecurityAuditLogger.log_download_attempt(request, file_obj, True)
    except Exception as exc:
        logger.warning(
            "Failed to increment download count for file ID %s: %s",
            file_obj.pk, exc
        )

    return redirect(file_obj.file.url)


def file_detail_view(request, pk):
    """
    Display detailed information about a file and increment view count.
    """
    activate('ne')
    file_obj = get_object_or_404(DownloadableFile, pk=pk, is_active=True)

    # Check if file has expired
    if file_obj.is_expired:
        logger.warning(f"Attempted view of expired file ID {file_obj.pk}")
        return redirect('downloads:download_center')

    # Increment view count
    try:
        file_obj.increment_view_count()
    except Exception as exc:
        logger.warning(
            "Failed to increment view count for file ID %s: %s",
            file_obj.pk, exc
        )

    context = {
        'file': file_obj,
    }
    return render(request, 'downloads/file_detail.html', context)


@rate_limit_bulk_downloads
@login_required
@require_http_methods(["POST"])
def bulk_download_view(request):
    """
    Create a ZIP file containing multiple downloadable files.
    """
    activate('ne')
    try:
        import zipfile
        import tempfile
        import os
        from django.http import HttpResponse
        
        file_ids = request.POST.getlist('file_ids')
        if not file_ids:
            return JsonResponse({'error': 'No files selected'}, status=400)
        
        # Get files that user can download
        downloadable_files = []
        for file_id in file_ids:
            try:
                file_obj = DownloadableFile.objects.get(pk=file_id, is_active=True)
                can_download, reason = AccessControlManager.can_download_file(request.user, file_obj)
                if can_download and not file_obj.is_expired:
                    downloadable_files.append(file_obj)
            except DownloadableFile.DoesNotExist:
                continue
        
        if not downloadable_files:
            return JsonResponse({'error': 'No accessible files found'}, status=403)
        
        # Create ZIP file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_obj in downloadable_files:
                try:
                    # Add file to ZIP
                    zip_file.write(file_obj.file.path, file_obj.file.name)
                    
                    # Increment download count
                    file_obj.increment_download_count()
                    
                    # Log download
                    SecurityAuditLogger.log_download_attempt(request, file_obj, True, "Bulk download")
                    
                except Exception as e:
                    logger.warning(f"Failed to add file {file_obj.id} to ZIP: {e}")
                    continue
        
        # Prepare response
        with open(temp_file.name, 'rb') as zip_content:
            response = HttpResponse(zip_content.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="downloads_{timezone.now().strftime("%Y%m%d_%H%M%S")}.zip"'
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        return response
        
    except Exception as e:
        logger.error(f"Bulk download failed: {e}")
        return JsonResponse({'error': 'Bulk download failed'}, status=500)


@login_required
def download_history_view(request):
    """
    Show user's download history.
    """
    activate('ne')
    # This would typically query a download history table
    # For now, we'll show recent downloads from the user's session
    context = {
        'downloads': [],  # Would be populated from download history model
        'user': request.user,
    }
    return render(request, 'downloads/download_history.html', context)


def file_preview_view(request, pk):
    """
    Preview file content (for supported file types).
    """
    activate('ne')
    file_obj = get_object_or_404(DownloadableFile, pk=pk, is_active=True)
    
    # Check access permissions
    can_download, reason = AccessControlManager.can_download_file(request.user, file_obj)
    if not can_download:
        return JsonResponse({'error': reason}, status=403)
    
    # Only allow preview for certain file types
    previewable_types = ['pdf', 'jpg', 'jpeg', 'png', 'gif']
    if file_obj.file_type not in previewable_types:
        return JsonResponse({'error': 'File type not supported for preview'}, status=400)
    
    # Increment view count
    file_obj.increment_view_count()
    
    context = {
        'file': file_obj,
        'preview_url': file_obj.file.url,
    }
    return render(request, 'downloads/file_preview.html', context)
