"""
Query Result Caching for News Events App

Provides caching for frequently accessed query results to improve performance.
"""

from django.core.cache import cache
from django.db.models import QuerySet
from typing import Any, Optional, Callable
from functools import wraps
import hashlib
import json
from apps.news_events.constants import CACHE_TIMEOUT_ARTICLE_LIST, CACHE_TIMEOUT_EVENT_LIST
import logging

logger = logging.getLogger(__name__)


class QueryResultCache:
    """
    Cache query results for improved performance.
    """
    
    @staticmethod
    def get_cache_key(prefix: str, **kwargs) -> str:
        """
        Generate cache key from prefix and parameters.
        
        Args:
            prefix: Cache key prefix
            **kwargs: Parameters to include in key
            
        Returns:
            Cache key string
        """
        # Sort kwargs for consistent keys
        sorted_kwargs = sorted(kwargs.items())
        params_str = json.dumps(sorted_kwargs, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
        return f"{prefix}_{params_hash}"
    
    @staticmethod
    def cache_queryset(
        queryset: QuerySet,
        cache_key: str,
        timeout: int = CACHE_TIMEOUT_ARTICLE_LIST
    ) -> None:
        """
        Cache queryset results.
        
        Args:
            queryset: Django QuerySet to cache
            cache_key: Cache key
            timeout: Cache timeout in seconds
        """
        try:
            # Convert queryset to list for caching
            results = list(queryset)
            cache.set(cache_key, results, timeout)
            logger.debug(f"Cached queryset with key: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to cache queryset: {e}")
    
    @staticmethod
    def get_cached_queryset(cache_key: str) -> Optional[list]:
        """
        Get cached queryset results.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached results or None
        """
        try:
            cached = cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for key: {cache_key}")
            return cached
        except Exception as e:
            logger.warning(f"Failed to get cached queryset: {e}")
            return None
    
    @staticmethod
    def invalidate_cache(prefix: str) -> None:
        """
        Invalidate all cache entries with given prefix.
        
        Args:
            prefix: Cache key prefix
        """
        # Note: Django cache doesn't support pattern deletion directly
        # This would require Redis with pattern matching or manual key tracking
        logger.info(f"Cache invalidation requested for prefix: {prefix}")


def cache_query_result(
    timeout: int = CACHE_TIMEOUT_ARTICLE_LIST,
    key_prefix: str = 'query_cache'
):
    """
    Decorator to cache query results.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Cache key prefix
        
    Usage:
        @cache_query_result(timeout=300, key_prefix='articles')
        def get_articles():
            return NewsArticle.objects.all()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = QueryResultCache.get_cache_key(
                key_prefix,
                func_name=func.__name__,
                args=str(args),
                kwargs=kwargs
            )
            
            # Try to get from cache
            cached_result = QueryResultCache.get_cached_queryset(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            # Cache if it's a QuerySet
            if isinstance(result, QuerySet):
                QueryResultCache.cache_queryset(result, cache_key, timeout)
            else:
                # Cache other results
                try:
                    cache.set(cache_key, result, timeout)
                except Exception as e:
                    logger.warning(f"Failed to cache result: {e}")
            
            return result
        
        return wrapper
    return decorator

