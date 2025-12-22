from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import json
import hashlib
from functools import wraps
import time
from typing import Any, Callable, Optional, Union


class CacheManager:
    """Advanced caching manager with Redis support"""
    
    def __init__(self):
        self.default_timeout = getattr(settings, 'CACHE_DEFAULT_TIMEOUT', 300)
        self.version = getattr(settings, 'CACHE_VERSION', 1)
    
    def get_cache_key(self, key: str, version: Optional[int] = None) -> str:
        """Generate cache key with version"""
        version = version or self.version
        return f"v{version}:{key}"
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None, version: Optional[int] = None) -> bool:
        """Set cache value with timeout"""
        cache_key = self.get_cache_key(key, version)
        timeout = timeout or self.default_timeout
        return cache.set(cache_key, value, timeout)
    
    def get(self, key: str, default: Any = None, version: Optional[int] = None) -> Any:
        """Get cache value"""
        cache_key = self.get_cache_key(key, version)
        return cache.get(cache_key, default)
    
    def delete(self, key: str, version: Optional[int] = None) -> bool:
        """Delete cache value"""
        cache_key = self.get_cache_key(key, version)
        return cache.delete(cache_key)
    
    def get_or_set(self, key: str, callable_func: Callable, timeout: Optional[int] = None, version: Optional[int] = None) -> Any:
        """Get cache value or set it using callable"""
        cache_key = self.get_cache_key(key, version)
        timeout = timeout or self.default_timeout
        
        value = cache.get(cache_key)
        if value is None:
            value = callable_func()
            cache.set(cache_key, value, timeout)
        
        return value
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if hasattr(cache, 'delete_pattern'):
            return cache.delete_pattern(pattern)
        
        # Fallback for non-Redis backends
        return 0
    
    def invalidate_model_cache(self, model_class, instance_id: Optional[int] = None):
        """Invalidate all cache keys related to a model"""
        model_name = model_class.__name__.lower()
        
        # Delete model-specific keys
        patterns = [
            f"v{self.version}:*{model_name}*",
            f"v{self.version}:*{model_name}_list*",
            f"v{self.version}:*{model_name}_detail*",
        ]
        
        if instance_id:
            patterns.extend([
                f"v{self.version}:*{model_name}_{instance_id}*",
                f"v{self.version}:*{model_name}_detail_{instance_id}*",
            ])
        
        deleted_count = 0
        for pattern in patterns:
            deleted_count += self.delete_pattern(pattern)
        
        return deleted_count


# Global cache manager instance
cache_manager = CacheManager()


def cache_result(timeout: int = 300, key_prefix: str = "", version: Optional[int] = None):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [func.__name__, key_prefix]
            
            # Add args to key
            for arg in args:
                if hasattr(arg, 'pk'):
                    key_parts.append(str(arg.pk))
                else:
                    key_parts.append(str(arg))
            
            # Add kwargs to key
            for k, v in sorted(kwargs.items()):
                if hasattr(v, 'pk'):
                    key_parts.append(f"{k}_{v.pk}")
                else:
                    key_parts.append(f"{k}_{v}")
            
            cache_key = "_".join(key_parts)
            
            # Try to get from cache
            result = cache_manager.get(cache_key, version=version)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout, version)
            
            return result
        
        return wrapper
    return decorator


def cache_page(timeout: int = 300, key_prefix: str = ""):
    """Decorator to cache entire page responses"""
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key from request
            path = request.get_full_path()
            user_id = getattr(request.user, 'id', 'anonymous')
            cache_key = f"page_{key_prefix}_{path}_{user_id}"
            
            # Try to get from cache
            response = cache_manager.get(cache_key)
            if response is not None:
                return response
            
            # Execute view and cache response
            response = view_func(request, *args, **kwargs)
            cache_manager.set(cache_key, response, timeout)
            
            return response
        
        return wrapper
    return decorator


class ModelCacheMixin:
    """Mixin to add caching capabilities to models"""
    
    @classmethod
    def get_cached(cls, pk: int, timeout: int = 300):
        """Get model instance from cache"""
        cache_key = f"{cls.__name__.lower()}_detail_{pk}"
        return cache_manager.get(cache_key)
    
    @classmethod
    def set_cached(cls, instance, timeout: int = 300):
        """Cache model instance"""
        cache_key = f"{cls.__name__.lower()}_detail_{instance.pk}"
        cache_manager.set(cache_key, instance, timeout)
    
    @classmethod
    def get_cached_list(cls, filters: dict = None, timeout: int = 300):
        """Get model list from cache"""
        filters_str = json.dumps(filters or {}, sort_keys=True)
        cache_key = f"{cls.__name__.lower()}_list_{hashlib.md5(filters_str.encode()).hexdigest()}"
        return cache_manager.get(cache_key)
    
    @classmethod
    def set_cached_list(cls, queryset, filters: dict = None, timeout: int = 300):
        """Cache model list"""
        filters_str = json.dumps(filters or {}, sort_keys=True)
        cache_key = f"{cls.__name__.lower()}_list_{hashlib.md5(filters_str.encode()).hexdigest()}"
        cache_manager.set(cache_key, list(queryset), timeout)
    
    def invalidate_cache(self):
        """Invalidate cache for this instance"""
        cache_manager.invalidate_model_cache(self.__class__, self.pk)


class QuerySetCacheMixin:
    """Mixin to add caching capabilities to QuerySets"""
    
    def cache_result(self, timeout: int = 300, key_suffix: str = ""):
        """Cache QuerySet result"""
        cache_key = f"queryset_{self.model.__name__.lower()}_{key_suffix}_{hash(str(self.query))}"
        
        result = cache_manager.get(cache_key)
        if result is None:
            result = list(self)
            cache_manager.set(cache_key, result, timeout)
        
        return result


class CacheInvalidationSignals:
    """Handle cache invalidation on model changes"""
    
    @staticmethod
    @receiver(post_save)
    def invalidate_on_save(sender, instance, **kwargs):
        """Invalidate cache when model is saved"""
        if hasattr(instance, 'invalidate_cache'):
            instance.invalidate_cache()
        else:
            cache_manager.invalidate_model_cache(sender, instance.pk)
    
    @staticmethod
    @receiver(post_delete)
    def invalidate_on_delete(sender, instance, **kwargs):
        """Invalidate cache when model is deleted"""
        if hasattr(instance, 'invalidate_cache'):
            instance.invalidate_cache()
        else:
            cache_manager.invalidate_model_cache(sender, instance.pk)


class CacheStats:
    """Cache statistics and monitoring"""
    
    @staticmethod
    def get_cache_stats():
        """Get cache statistics"""
        stats = {
            'backend': cache.__class__.__name__,
            'default_timeout': cache_manager.default_timeout,
            'version': cache_manager.version,
        }
        
        # Try to get Redis-specific stats
        if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_client'):
            try:
                client = cache._cache.get_client()
                info = client.info()
                stats.update({
                    'redis_version': info.get('redis_version'),
                    'used_memory': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients'),
                    'total_commands_processed': info.get('total_commands_processed'),
                    'keyspace_hits': info.get('keyspace_hits'),
                    'keyspace_misses': info.get('keyspace_misses'),
                })
                
                # Calculate hit ratio
                hits = info.get('keyspace_hits', 0)
                misses = info.get('keyspace_misses', 0)
                if hits + misses > 0:
                    stats['hit_ratio'] = round((hits / (hits + misses)) * 100, 2)
                
            except Exception as e:
                stats['redis_error'] = str(e)
        
        return stats
    
    @staticmethod
    def clear_all_cache():
        """Clear all cache"""
        cache.clear()
        return True
    
    @staticmethod
    def get_cache_keys(pattern: str = "*"):
        """Get all cache keys matching pattern"""
        if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_client'):
            try:
                client = cache._cache.get_client()
                return client.keys(pattern)
            except Exception:
                pass
        return []


class CacheWarming:
    """Cache warming utilities"""
    
    @staticmethod
    def warm_model_cache(model_class, timeout: int = 300):
        """Warm cache for all instances of a model"""
        instances = model_class.objects.all()
        for instance in instances:
            model_class.set_cached(instance, timeout)
        
        return len(instances)
    
    @staticmethod
    def warm_queryset_cache(queryset, timeout: int = 300, key_suffix: str = ""):
        """Warm cache for a queryset"""
        cache_key = f"queryset_{queryset.model.__name__.lower()}_{key_suffix}_{hash(str(queryset.query))}"
        result = list(queryset)
        cache_manager.set(cache_key, result, timeout)
        return len(result)
    
    @staticmethod
    def warm_api_endpoints():
        """Warm cache for common API endpoints"""
        from apps.about.models import (
            CooperativeInfo, CooperativeTimeline,
            CooperativeAffiliation, LeadershipMessage, Person
        )
        
        warmed_count = 0
        
        # Warm cooperative info
        if CooperativeInfo.objects.exists():
            CacheWarming.warm_model_cache(CooperativeInfo)
            warmed_count += 1
        
        # Warm timeline events
        if CooperativeTimeline.objects.exists():
            CacheWarming.warm_model_cache(CooperativeTimeline)
            warmed_count += 1
        
        # Warm achievements
        # Removed: CooperativeAchievement cache warming - model no longer exists
            warmed_count += 1
        
        # Warm affiliations
        if CooperativeAffiliation.objects.exists():
            CacheWarming.warm_model_cache(CooperativeAffiliation)
            warmed_count += 1
        
        # Warm leadership messages
        if LeadershipMessage.objects.exists():
            CacheWarming.warm_model_cache(LeadershipMessage)
            warmed_count += 1
        
        # Warm team members
        if Person.objects.exists():
            CacheWarming.warm_model_cache(Person)
            warmed_count += 1
        
        return warmed_count


# Cache configuration for different environments
CACHE_CONFIGS = {
    'development': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    },
    'production': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 300,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    },
    'testing': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


def get_cache_config(environment: str = 'development') -> dict:
    """Get cache configuration for environment"""
    return CACHE_CONFIGS.get(environment, CACHE_CONFIGS['development'])
