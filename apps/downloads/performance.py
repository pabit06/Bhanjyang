"""
Downloads Performance Module
Caching and performance optimizations for downloads app
"""

import time
from django.core.cache import cache
from django.db.models import Count, Q, F, Avg
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'file_list': 300,      # 5 minutes
    'file_stats': 600,     # 10 minutes
    'category_stats': 900, # 15 minutes
    'user_downloads': 1800, # 30 minutes
    'popular_files': 3600, # 1 hour
}


class DownloadsCache:
    """Centralized caching for downloads app"""
    
    @staticmethod
    def get_file_list_cache_key(category=None, priority=None, featured_only=False, query=None):
        """Generate cache key for file list"""
        key_parts = ['downloads', 'file_list']
        
        if category:
            key_parts.append(f'cat_{category}')
        if priority:
            key_parts.append(f'pri_{priority}')
        if featured_only:
            key_parts.append('featured')
        if query:
            key_parts.append(f'q_{hash(query)}')
        
        return '_'.join(key_parts)
    
    @staticmethod
    def get_file_stats_cache_key():
        """Generate cache key for file statistics"""
        return 'downloads_file_stats'
    
    @staticmethod
    def get_category_stats_cache_key():
        """Generate cache key for category statistics"""
        return 'downloads_category_stats'
    
    @staticmethod
    def get_popular_files_cache_key():
        """Generate cache key for popular files"""
        return 'downloads_popular_files'
    
    @staticmethod
    def get_user_downloads_cache_key(user_id):
        """Generate cache key for user downloads"""
        return f'downloads_user_{user_id}_downloads'


class DownloadsPerformanceMonitor:
    """Monitor and optimize downloads performance"""
    
    @staticmethod
    def cache_file_list(files_data, cache_key, timeout=CACHE_TIMEOUTS['file_list']):
        """Cache file list data"""
        try:
            cache.set(cache_key, files_data, timeout)
            logger.debug(f"Cached file list with key: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to cache file list: {e}")
    
    @staticmethod
    def get_cached_file_list(cache_key):
        """Get cached file list data"""
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug(f"Retrieved cached file list with key: {cache_key}")
            return cached_data
        except Exception as e:
            logger.warning(f"Failed to retrieve cached file list: {e}")
            return None
    
    @staticmethod
    def cache_file_statistics(stats_data, timeout=CACHE_TIMEOUTS['file_stats']):
        """Cache file statistics"""
        cache_key = DownloadsCache.get_file_stats_cache_key()
        try:
            cache.set(cache_key, stats_data, timeout)
            logger.debug("Cached file statistics")
        except Exception as e:
            logger.warning(f"Failed to cache file statistics: {e}")
    
    @staticmethod
    def get_cached_file_statistics():
        """Get cached file statistics"""
        cache_key = DownloadsCache.get_file_stats_cache_key()
        try:
            cached_stats = cache.get(cache_key)
            if cached_stats:
                logger.debug("Retrieved cached file statistics")
            return cached_stats
        except Exception as e:
            logger.warning(f"Failed to retrieve cached file statistics: {e}")
            return None
    
    @staticmethod
    def cache_category_statistics(stats_data, timeout=CACHE_TIMEOUTS['category_stats']):
        """Cache category statistics"""
        cache_key = DownloadsCache.get_category_stats_cache_key()
        try:
            cache.set(cache_key, stats_data, timeout)
            logger.debug("Cached category statistics")
        except Exception as e:
            logger.warning(f"Failed to cache category statistics: {e}")
    
    @staticmethod
    def get_cached_category_statistics():
        """Get cached category statistics"""
        cache_key = DownloadsCache.get_category_stats_cache_key()
        try:
            cached_stats = cache.get(cache_key)
            if cached_stats:
                logger.debug("Retrieved cached category statistics")
            return cached_stats
        except Exception as e:
            logger.warning(f"Failed to retrieve cached category statistics: {e}")
            return None
    
    @staticmethod
    def cache_popular_files(files_data, timeout=CACHE_TIMEOUTS['popular_files']):
        """Cache popular files"""
        cache_key = DownloadsCache.get_popular_files_cache_key()
        try:
            cache.set(cache_key, files_data, timeout)
            logger.debug("Cached popular files")
        except Exception as e:
            logger.warning(f"Failed to cache popular files: {e}")
    
    @staticmethod
    def get_cached_popular_files():
        """Get cached popular files"""
        cache_key = DownloadsCache.get_popular_files_cache_key()
        try:
            cached_files = cache.get(cache_key)
            if cached_files:
                logger.debug("Retrieved cached popular files")
            return cached_files
        except Exception as e:
            logger.warning(f"Failed to retrieve cached popular files: {e}")
            return None


class DownloadsQueryOptimizer:
    """Optimize database queries for downloads"""
    
    @staticmethod
    def get_optimized_file_queryset():
        """Get optimized queryset for files with select_related and prefetch_related"""
        from .models import DownloadableFile
        
        return DownloadableFile.objects.select_related('uploaded_by').only(
            'id', 'title', 'description', 'category', 'priority', 'is_active',
            'is_featured', 'requires_login', 'expires_at', 'tags', 'thumbnail',
            'download_count', 'view_count', 'uploaded_at', 'file_type',
            'file_hash', 'last_accessed', 'access_count', 'uploaded_by__username'
        )
    
    @staticmethod
    def get_file_statistics():
        """Get optimized file statistics"""
        from .models import DownloadableFile
        
        # Check cache first
        cached_stats = DownloadsPerformanceMonitor.get_cached_file_statistics()
        if cached_stats:
            return cached_stats
        
        # Generate statistics
        stats = DownloadableFile.objects.aggregate(
            total_files=Count('id'),
            active_files=Count('id', filter=Q(is_active=True)),
            featured_files=Count('id', filter=Q(is_featured=True)),
            expired_files=Count('id', filter=Q(expires_at__lt=timezone.now())),
            total_downloads=Count('download_count'),
            total_views=Count('view_count'),
            avg_downloads=Avg('download_count'),
            avg_views=Avg('view_count')
        )
        
        # Cache the results
        DownloadsPerformanceMonitor.cache_file_statistics(stats)
        
        return stats
    
    @staticmethod
    def get_category_statistics():
        """Get optimized category statistics"""
        from .models import DownloadableFile
        
        # Check cache first
        cached_stats = DownloadsPerformanceMonitor.get_cached_category_statistics()
        if cached_stats:
            return cached_stats
        
        # Generate statistics
        stats = list(DownloadableFile.objects.values('category').annotate(
            count=Count('id'),
            total_downloads=Count('download_count'),
            total_views=Count('view_count')
        ).order_by('-count'))
        
        # Cache the results
        DownloadsPerformanceMonitor.cache_category_statistics(stats)
        
        return stats
    
    @staticmethod
    def get_popular_files(limit=10):
        """Get most popular files"""
        from .models import DownloadableFile
        
        # Check cache first
        cached_files = DownloadsPerformanceMonitor.get_cached_popular_files()
        if cached_files:
            return cached_files
        
        # Generate popular files list
        files = list(DownloadsQueryOptimizer.get_optimized_file_queryset().filter(
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        ).order_by('-download_count', '-view_count')[:limit])
        
        # Cache the results
        DownloadsPerformanceMonitor.cache_popular_files(files)
        
        return files
    
    @staticmethod
    def get_download_trends(days=30):
        """Get download trends with optimized queries"""
        from .models import DownloadableFile
        
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=days)
        
        # Use extra for efficient daily aggregation
        trends = list(DownloadableFile.objects.filter(
            uploaded_at__gte=start_date,
            uploaded_at__lte=end_date
        ).extra(
            select={'day': 'date(uploaded_at)'}
        ).values('day').annotate(
            uploads=Count('id'),
            downloads=Count('download_count'),
            views=Count('view_count')
        ).order_by('day'))
        
        return trends
    
    @staticmethod
    def get_user_download_patterns():
        """Get user download patterns"""
        from .models import DownloadableFile
        
        # This would typically query a download history table
        # For now, we'll return basic patterns from the file model
        patterns = DownloadableFile.objects.values('category').annotate(
            avg_downloads=Avg('download_count'),
            avg_views=Avg('view_count'),
            file_count=Count('id')
        ).order_by('-avg_downloads')
        
        return list(patterns)


class DownloadsCDNManager:
    """CDN integration for file delivery"""
    
    @staticmethod
    def get_cdn_url(file_path):
        """Get CDN URL for file if CDN is configured"""
        if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
            return f"{settings.CDN_URL.rstrip('/')}/{file_path.lstrip('/')}"
        return None
    
    @staticmethod
    def get_file_url(file_obj):
        """Get optimized file URL (CDN or local)"""
        cdn_url = DownloadsCDNManager.get_cdn_url(file_obj.file.name)
        if cdn_url:
            return cdn_url
        return file_obj.file.url


class DownloadsCompressionManager:
    """File compression for better performance"""
    
    @staticmethod
    def compress_file_if_needed(file_obj):
        """Compress file if it's large and compressible"""
        try:
            # Only compress files larger than 1MB
            if file_obj.file.size > 1024 * 1024:
                # This would typically integrate with a compression service
                # For now, we'll just log the intention
                logger.info(f"File {file_obj.id} could be compressed for better performance")
        except Exception as e:
            logger.warning(f"Failed to check compression for file {file_obj.id}: {e}")


def performance_monitor(func):
    """Decorator to monitor function performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log slow operations
            if execution_time > 1.0:  # More than 1 second
                logger.warning(f"Slow operation detected: {func.__name__} took {execution_time:.2f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Operation failed: {func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper


class DownloadsAnalyticsOptimizer:
    """Optimize analytics queries"""
    
    @staticmethod
    def get_download_trends(days=30):
        """Get download trends with optimized queries"""
        from .models import DownloadableFile
        from django.db.models import TruncDate
        
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=days)
        
        # Use TruncDate for efficient daily aggregation
        trends = list(DownloadableFile.objects.filter(
            uploaded_at__gte=start_date,
            uploaded_at__lte=end_date
        ).extra(
            select={'day': 'date(uploaded_at)'}
        ).values('day').annotate(
            uploads=Count('id'),
            downloads=Count('download_count'),
            views=Count('view_count')
        ).order_by('day'))
        
        return trends
    
    @staticmethod
    def get_user_download_patterns():
        """Get user download patterns"""
        from .models import DownloadableFile
        
        # This would typically query a download history table
        # For now, we'll return basic patterns from the file model
        patterns = DownloadableFile.objects.values('category').annotate(
            avg_downloads=Avg('download_count'),
            avg_views=Avg('view_count'),
            file_count=Count('id')
        ).order_by('-avg_downloads')
        
        return list(patterns)
