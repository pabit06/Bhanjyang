from django.core.cache import cache
from django.conf import settings
from django.db.models import Avg, Count
from datetime import timedelta
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

class DashboardCache:
    """Cache manager for dashboard data"""
    
    CACHE_TIMEOUT = 300  # 5 minutes
    CACHE_PREFIX = 'dashboard'
    
    @staticmethod
    def get_cache_key(key, **kwargs):
        """Generate cache key"""
        key_parts = [DashboardCache.CACHE_PREFIX, key]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    @staticmethod
    def get_metrics_cache_key(days=7, device_type=None, browser=None):
        """Get cache key for metrics"""
        return DashboardCache.get_cache_key(
            'metrics',
            days=days,
            device=device_type or 'all',
            browser=browser or 'all'
        )
    
    @staticmethod
    def get_page_views_cache_key(days=7):
        """Get cache key for page views"""
        return DashboardCache.get_cache_key('page_views', days=days)
    
    @staticmethod
    def get_error_stats_cache_key(days=7):
        """Get cache key for error stats"""
        return DashboardCache.get_cache_key('error_stats', days=days)
    
    @staticmethod
    def get_slowest_pages_cache_key(days=7):
        """Get cache key for slowest pages"""
        return DashboardCache.get_cache_key('slowest_pages', days=days)
    
    @staticmethod
    def get_most_visited_cache_key(days=7):
        """Get cache key for most visited pages"""
        return DashboardCache.get_cache_key('most_visited', days=days)
    
    @staticmethod
    def get_device_stats_cache_key(days=7):
        """Get cache key for device stats"""
        return DashboardCache.get_cache_key('device_stats', days=days)
    
    @staticmethod
    def get_browser_stats_cache_key(days=7):
        """Get cache key for browser stats"""
        return DashboardCache.get_cache_key('browser_stats', days=days)
    
    @staticmethod
    def get_cached_data(key, default=None):
        """Get cached data"""
        try:
            return cache.get(key, default)
        except Exception as e:
            logger.error(f"Error getting cached data for key {key}: {e}")
            return default
    
    @staticmethod
    def set_cached_data(key, data, timeout=None):
        """Set cached data"""
        try:
            timeout = timeout or DashboardCache.CACHE_TIMEOUT
            cache.set(key, data, timeout)
        except Exception as e:
            logger.error(f"Error setting cached data for key {key}: {e}")
    
    @staticmethod
    def invalidate_cache_pattern(pattern):
        """Invalidate cache by pattern"""
        try:
            # This is a simplified version - in production you might want to use Redis
            # with pattern-based cache invalidation
            cache.delete(pattern)
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")
    
    @staticmethod
    def invalidate_dashboard_cache():
        """Invalidate all dashboard cache"""
        try:
            patterns = [
                DashboardCache.get_cache_key('metrics'),
                DashboardCache.get_cache_key('page_views'),
                DashboardCache.get_cache_key('error_stats'),
                DashboardCache.get_cache_key('slowest_pages'),
                DashboardCache.get_cache_key('most_visited'),
                DashboardCache.get_cache_key('device_stats'),
                DashboardCache.get_cache_key('browser_stats'),
            ]
            
            for pattern in patterns:
                DashboardCache.invalidate_cache_pattern(pattern)
                
        except Exception as e:
            logger.error(f"Error invalidating dashboard cache: {e}")

class DashboardDataProvider:
    """Data provider with caching for dashboard"""
    
    @staticmethod
    def get_page_views_data(days=7, use_cache=True):
        """Get page views data with caching"""
        cache_key = DashboardCache.get_page_views_cache_key(days)
        
        if use_cache:
            cached_data = DashboardCache.get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            from apps.dashboard.models import PageView
            
            start_date = timezone.now() - timedelta(days=days)
            
            data = PageView.objects.filter(
                timestamp__gte=start_date
            ).values('timestamp__date').annotate(
                avg_load_time=Avg('load_time'),
                count=Count('id')
            ).order_by('timestamp__date')
            
            result = {
                'labels': [item['timestamp__date'].strftime('%Y-%m-%d') for item in data],
                'data': [float(item['avg_load_time']) for item in data],
                'counts': [item['count'] for item in data]
            }
            
            if use_cache:
                DashboardCache.set_cached_data(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting page views data: {e}")
            return {'labels': [], 'data': [], 'counts': []}
    
    @staticmethod
    def get_error_data(days=7, use_cache=True):
        """Get error data with caching"""
        cache_key = DashboardCache.get_error_stats_cache_key(days)
        
        if use_cache:
            cached_data = DashboardCache.get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            from apps.dashboard.models import ErrorLog
            
            start_date = timezone.now() - timedelta(days=days)
            
            data = ErrorLog.objects.filter(
                timestamp__gte=start_date
            ).values('timestamp__date').annotate(
                count=Count('id')
            ).order_by('timestamp__date')
            
            result = {
                'labels': [item['timestamp__date'].strftime('%Y-%m-%d') for item in data],
                'data': [item['count'] for item in data]
            }
            
            if use_cache:
                DashboardCache.set_cached_data(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting error data: {e}")
            return {'labels': [], 'data': []}
    
    @staticmethod
    def get_slowest_pages(days=7, use_cache=True):
        """Get slowest pages with caching"""
        cache_key = DashboardCache.get_slowest_pages_cache_key(days)
        
        if use_cache:
            cached_data = DashboardCache.get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            from apps.dashboard.models import PageView
            
            start_date = timezone.now() - timedelta(days=days)
            
            data = list(PageView.objects.filter(
                timestamp__gte=start_date
            ).values('page_url', 'page_title').annotate(
                avg_load_time=Avg('load_time'),
                view_count=Count('id')
            ).order_by('-avg_load_time')[:10])
            
            if use_cache:
                DashboardCache.set_cached_data(cache_key, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting slowest pages: {e}")
            return []
    
    @staticmethod
    def get_most_visited_pages(days=7, use_cache=True):
        """Get most visited pages with caching"""
        cache_key = DashboardCache.get_most_visited_cache_key(days)
        
        if use_cache:
            cached_data = DashboardCache.get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            from apps.dashboard.models import PageView
            
            start_date = timezone.now() - timedelta(days=days)
            
            data = list(PageView.objects.filter(
                timestamp__gte=start_date
            ).values('page_url', 'page_title').annotate(
                view_count=Count('id'),
                avg_load_time=Avg('load_time')
            ).order_by('-view_count')[:10])
            
            if use_cache:
                DashboardCache.set_cached_data(cache_key, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting most visited pages: {e}")
            return []
    
    @staticmethod
    def get_device_stats(days=7, use_cache=True):
        """Get device statistics with caching"""
        cache_key = DashboardCache.get_device_stats_cache_key(days)
        
        if use_cache:
            cached_data = DashboardCache.get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            from apps.dashboard.models import PageView
            
            start_date = timezone.now() - timedelta(days=days)
            
            data = list(PageView.objects.filter(
                timestamp__gte=start_date
            ).values('is_mobile').annotate(
                count=Count('id'),
                avg_load_time=Avg('load_time')
            ))
            
            if use_cache:
                DashboardCache.set_cached_data(cache_key, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting device stats: {e}")
            return []
    
    @staticmethod
    def get_browser_stats(days=7, use_cache=True):
        """Get browser statistics with caching"""
        cache_key = DashboardCache.get_browser_stats_cache_key(days)
        
        if use_cache:
            cached_data = DashboardCache.get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            from apps.dashboard.models import PageView
            
            start_date = timezone.now() - timedelta(days=days)
            
            data = list(PageView.objects.filter(
                timestamp__gte=start_date
            ).values('browser').annotate(
                count=Count('id'),
                avg_load_time=Avg('load_time')
            ).order_by('-count')[:10])
            
            if use_cache:
                DashboardCache.set_cached_data(cache_key, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting browser stats: {e}")
            return []

class CacheInvalidationSignals:
    """Signal handlers for cache invalidation"""
    
    @staticmethod
    def invalidate_on_page_view(sender, instance, **kwargs):
        """Invalidate cache when new page view is created"""
        DashboardCache.invalidate_dashboard_cache()
    
    @staticmethod
    def invalidate_on_error_log(sender, instance, **kwargs):
        """Invalidate cache when new error is logged"""
        DashboardCache.invalidate_dashboard_cache()
    
    @staticmethod
    def invalidate_on_alert_log(sender, instance, **kwargs):
        """Invalidate cache when new alert is created"""
        DashboardCache.invalidate_dashboard_cache()
