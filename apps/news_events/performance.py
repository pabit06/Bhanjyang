"""
News Events Performance Module
Caching and performance optimizations for news and events
"""

import time
from django.core.cache import cache
from django.db.models import Count, Q, F, Avg, Max, Min
from django.utils import timezone
from django.conf import settings
from django.core.paginator import Paginator
import logging

logger = logging.getLogger(__name__)

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'article_list': 300,      # 5 minutes
    'event_list': 300,        # 5 minutes
    'category_list': 600,     # 10 minutes
    'article_stats': 900,     # 15 minutes
    'event_stats': 900,       # 15 minutes
    'popular_content': 1800,  # 30 minutes
    'analytics': 3600,        # 1 hour
}

class NewsEventsCache:
    """Centralized caching for news events app"""
    
    @staticmethod
    def get_article_list_cache_key(category=None, status='published', featured_only=False, limit=None):
        """Generate cache key for article list"""
        key_parts = ['article_list', status]
        if category:
            key_parts.append(f"cat_{category}")
        if featured_only:
            key_parts.append('featured')
        if limit:
            key_parts.append(f"limit_{limit}")
        return '_'.join(key_parts)
    
    @staticmethod
    def get_event_list_cache_key(event_type=None, status='published', upcoming_only=True, limit=None):
        """Generate cache key for event list"""
        key_parts = ['event_list', status]
        if event_type:
            key_parts.append(f"type_{event_type}")
        if upcoming_only:
            key_parts.append('upcoming')
        if limit:
            key_parts.append(f"limit_{limit}")
        return '_'.join(key_parts)
    
    @staticmethod
    def get_category_stats_cache_key():
        """Generate cache key for category statistics"""
        return 'category_stats'
    
    @staticmethod
    def get_analytics_cache_key(content_type, date_range='30d'):
        """Generate cache key for analytics"""
        return f'analytics_{content_type}_{date_range}'
    
    @staticmethod
    def cache_article_list(articles_data, cache_key, timeout=CACHE_TIMEOUTS['article_list']):
        """Cache article list data"""
        try:
            cache.set(cache_key, articles_data, timeout)
            logger.debug(f"Cached article list: {cache_key}")
        except Exception as e:
            logger.error(f"Failed to cache article list: {e}")
    
    @staticmethod
    def get_cached_article_list(cache_key):
        """Get cached article list"""
        try:
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"Failed to get cached article list: {e}")
            return None
    
    @staticmethod
    def cache_event_list(events_data, cache_key, timeout=CACHE_TIMEOUTS['event_list']):
        """Cache event list data"""
        try:
            cache.set(cache_key, events_data, timeout)
            logger.debug(f"Cached event list: {cache_key}")
        except Exception as e:
            logger.error(f"Failed to cache event list: {e}")
    
    @staticmethod
    def get_cached_event_list(cache_key):
        """Get cached event list"""
        try:
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"Failed to get cached event list: {e}")
            return None

class NewsEventsPerformanceMonitor:
    """Performance monitoring for news events"""
    
    @staticmethod
    def cache_article_statistics(stats_data, timeout=CACHE_TIMEOUTS['article_stats']):
        """Cache article statistics"""
        try:
            cache.set('article_statistics', stats_data, timeout)
            logger.debug("Cached article statistics")
        except Exception as e:
            logger.error(f"Failed to cache article statistics: {e}")
    
    @staticmethod
    def get_cached_article_statistics():
        """Get cached article statistics"""
        try:
            return cache.get('article_statistics')
        except Exception as e:
            logger.error(f"Failed to get cached article statistics: {e}")
            return None
    
    @staticmethod
    def cache_event_statistics(stats_data, timeout=CACHE_TIMEOUTS['event_stats']):
        """Cache event statistics"""
        try:
            cache.set('event_statistics', stats_data, timeout)
            logger.debug("Cached event statistics")
        except Exception as e:
            logger.error(f"Failed to cache event statistics: {e}")
    
    @staticmethod
    def get_cached_event_statistics():
        """Get cached event statistics"""
        try:
            return cache.get('event_statistics')
        except Exception as e:
            logger.error(f"Failed to get cached event statistics: {e}")
            return None
    
    @staticmethod
    def cache_popular_content(content_data, timeout=CACHE_TIMEOUTS['popular_content']):
        """Cache popular content"""
        try:
            cache.set('popular_content', content_data, timeout)
            logger.debug("Cached popular content")
        except Exception as e:
            logger.error(f"Failed to cache popular content: {e}")
    
    @staticmethod
    def get_cached_popular_content():
        """Get cached popular content"""
        try:
            return cache.get('popular_content')
        except Exception as e:
            logger.error(f"Failed to get cached popular content: {e}")
            return None

class NewsEventsQueryOptimizer:
    """Query optimization for news events"""
    
    @staticmethod
    def get_optimized_article_queryset():
        """Get optimized article queryset with select_related and prefetch_related"""
        from .models import NewsArticle
        
        return NewsArticle.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'comments'
        ).only(
            'id', 'title', 'slug', 'excerpt', 'image', 'image_alt',
            'status', 'is_featured', 'published_date', 'created_at',
            'view_count', 'read_time', 'author__username', 'author__first_name',
            'author__last_name', 'category__name', 'category__slug', 'category__color'
        )
    
    @staticmethod
    def get_optimized_event_queryset():
        """Get optimized event queryset with select_related and prefetch_related"""
        from .models import Event
        
        return Event.objects.only(
            'id', 'title', 'slug', 'description', 'image', 'image_alt',
            'status', 'is_featured', 'event_date', 'end_date', 'location',
            'created_at', 'view_count', 'registration_required'
        )
    
    @staticmethod
    def get_optimized_article_queryset_with_comments():
        """Get optimized article queryset with comments"""
        from .models import NewsArticle
        
        return NewsArticle.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'comments'
        ).only(
            'id', 'title', 'slug', 'content', 'excerpt', 'image', 'image_alt',
            'status', 'is_featured', 'published_date', 'created_at',
            'view_count', 'read_time', 'allow_comments', 'require_login',
            'author__username', 'author__first_name', 'author__last_name',
            'category__name', 'category__slug', 'category__color'
        )
    
    @staticmethod
    def get_article_statistics():
        """Get article statistics with optimized queries"""
        from .models import NewsArticle
        
        stats = NewsEventsQueryOptimizer.get_optimized_article_queryset().aggregate(
            total_articles=Count('id'),
            published_articles=Count('id', filter=Q(status=NewsArticle.Status.PUBLISHED)),
            draft_articles=Count('id', filter=Q(status=NewsArticle.Status.DRAFT)),
            featured_articles=Count('id', filter=Q(is_featured=True)),
            total_views=Count('view_count'),
            total_shares=Count('share_count'),
            avg_read_time=Avg('read_time'),
            recent_articles=Count('id', filter=Q(created_at__gte=timezone.now() - timezone.timedelta(days=7)))
        )
        
        return stats
    
    @staticmethod
    def get_event_statistics():
        """Get event statistics with optimized queries"""
        from .models import Event
        
        now = timezone.now()
        stats = NewsEventsQueryOptimizer.get_optimized_event_queryset().aggregate(
            total_events=Count('id'),
            upcoming_events=Count('id', filter=Q(event_date__gt=now, status=Event.Status.PUBLISHED)),
            past_events=Count('id', filter=Q(event_date__lt=now)),
            featured_events=Count('id', filter=Q(is_featured=True)),
            total_views=Count('view_count')
        )
        
        # Calculate average duration manually for SQLite compatibility
        events_with_end_date = Event.objects.filter(end_date__isnull=False)
        total_duration = 0
        count = 0
        for event in events_with_end_date:
            duration = (event.end_date - event.event_date).total_seconds() / 3600  # hours
            total_duration += duration
            count += 1
        
        stats['avg_duration'] = total_duration / count if count > 0 else 0
        
        return stats
    
    @staticmethod
    def get_category_statistics():
        """Get category statistics"""
        from .models import Category, NewsArticle
        
        categories = Category.objects.filter(is_active=True).annotate(
            article_count=Count('articles', filter=Q(articles__status=NewsArticle.Status.PUBLISHED)),
            total_views=Count('articles__view_count'),
            avg_read_time=Avg('articles__read_time')
        ).order_by('-article_count')
        
        return list(categories)
    
    @staticmethod
    def get_popular_articles(limit=5):
        """Get popular articles based on views and shares"""
        from .models import NewsArticle
        
        popular_articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
            status=NewsArticle.Status.PUBLISHED
        ).annotate(
            popularity_score=F('view_count') + F('share_count') * 2
        ).order_by('-popularity_score', '-published_date')[:limit]
        
        return list(popular_articles)
    
    @staticmethod
    def get_upcoming_events(limit=5):
        """Get upcoming events"""
        from .models import Event
        
        upcoming_events = NewsEventsQueryOptimizer.get_optimized_event_queryset().filter(
            event_date__gt=timezone.now(),
            status=Event.Status.PUBLISHED
        ).order_by('event_date')[:limit]
        
        return list(upcoming_events)
    
    @staticmethod
    def get_recent_articles(limit=5):
        """Get recent articles"""
        from .models import NewsArticle
        
        recent_articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
            status=NewsArticle.Status.PUBLISHED
        ).order_by('-published_date')[:limit]
        
        return list(recent_articles)
    
    @staticmethod
    def get_featured_content(limit=3):
        """Get featured articles and events"""
        from .models import NewsArticle, Event
        
        featured_articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
            is_featured=True,
            status=NewsArticle.Status.PUBLISHED
        ).order_by('-published_date')[:limit]
        
        featured_events = NewsEventsQueryOptimizer.get_optimized_event_queryset().filter(
            is_featured=True,
            status=Event.Status.PUBLISHED,
            event_date__gt=timezone.now()
        ).order_by('event_date')[:limit]
        
        return {
            'articles': list(featured_articles),
            'events': list(featured_events)
        }
    
    @staticmethod
    def get_content_trends(days=30):
        """Get content trends over time"""
        from .models import NewsArticle, Event
        
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=days)
        
        # Article trends
        article_trends = NewsArticle.objects.filter(
            published_date__gte=start_date,
            published_date__lte=end_date,
            status=NewsArticle.Status.PUBLISHED
        ).extra(
            select={'day': 'date(published_date)'}
        ).values('day').annotate(
            articles=Count('id'),
            views=Count('view_count'),
            shares=Count('share_count')
        ).order_by('day')
        
        # Event trends
        event_trends = Event.objects.filter(
            event_date__gte=start_date,
            event_date__lte=end_date,
            status=Event.Status.PUBLISHED
        ).extra(
            select={'day': 'date(event_date)'}
        ).values('day').annotate(
            events=Count('id'),
            views=Count('view_count')
        ).order_by('day')
        
        return {
            'articles': list(article_trends),
            'events': list(event_trends)
        }
    
    @staticmethod
    def get_user_engagement_patterns():
        """Get user engagement patterns"""
        from .models import NewsArticle, Event
        
        # Most viewed content
        popular_articles = NewsArticle.objects.filter(
            status=NewsArticle.Status.PUBLISHED
        ).order_by('-view_count')[:10]
        
        popular_events = Event.objects.filter(
            status=Event.Status.PUBLISHED
        ).order_by('-view_count')[:10]
        
        # Content performance by category
        category_performance = NewsArticle.objects.filter(
            status=NewsArticle.Status.PUBLISHED
        ).values('category__name').annotate(
            avg_views=Avg('view_count'),
            avg_shares=Avg('share_count'),
            avg_read_time=Avg('read_time'),
            article_count=Count('id')
        ).order_by('-avg_views')
        
        return {
            'popular_articles': list(popular_articles),
            'popular_events': list(popular_events),
            'category_performance': list(category_performance)
        }

class NewsEventsCDNManager:
    """CDN management for media files"""
    
    @staticmethod
    def get_cdn_url(file_path):
        """Get CDN URL for file"""
        if hasattr(settings, 'CDN_URL') and settings.CDN_URL:
            return f"{settings.CDN_URL.rstrip('/')}/{file_path.lstrip('/')}"
        return file_path
    
    @staticmethod
    def optimize_image_url(image_field):
        """Optimize image URL for CDN"""
        if image_field and hasattr(image_field, 'url'):
            return NewsEventsCDNManager.get_cdn_url(image_field.url)
        return None
    
    @staticmethod
    def get_optimized_image_urls(articles):
        """Get optimized image URLs for multiple articles"""
        optimized_articles = []
        for article in articles:
            if hasattr(article, 'image') and article.image:
                article.optimized_image_url = NewsEventsCDNManager.get_cdn_url(article.image.url)
            else:
                article.optimized_image_url = None
            optimized_articles.append(article)
        return optimized_articles

# Performance monitoring decorator
def performance_monitor(func):
    """Decorator to monitor function performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log performance if execution time is significant
            if execution_time > 0.5:  # More than 500ms
                logger.warning(f"Slow execution detected: {func.__name__} took {execution_time:.3f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    return wrapper

class NewsEventsAnalyticsOptimizer:
    """Analytics optimization for news events"""
    
    @staticmethod
    def get_content_analytics(content_type, content_id, days=30):
        """Get analytics for specific content"""
        from .models import ContentAnalytics
        
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=days)
        
        analytics = ContentAnalytics.objects.filter(
            content_type=content_type,
            content_id=content_id,
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(
            total_views=Count('views'),
            total_unique_views=Count('unique_views'),
            total_shares=Count('shares'),
            total_comments=Count('comments'),
            avg_time_on_page=Avg('time_on_page'),
            total_organic=Count('organic_search'),
            total_social=Count('social_media'),
            total_direct=Count('direct_traffic'),
            total_referral=Count('referral_traffic')
        )
        
        return analytics
    
    @staticmethod
    def get_overall_analytics(days=30):
        """Get overall analytics for the site"""
        from .models import ContentAnalytics
        
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=days)
        
        analytics = ContentAnalytics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(
            total_views=Count('views'),
            total_unique_views=Count('unique_views'),
            total_shares=Count('shares'),
            total_comments=Count('comments'),
            avg_time_on_page=Avg('time_on_page'),
            total_organic=Count('organic_search'),
            total_social=Count('social_media'),
            total_direct=Count('direct_traffic'),
            total_referral=Count('referral_traffic')
        )
        
        return analytics
