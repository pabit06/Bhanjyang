"""
Throttling classes for News Events API.

Provides rate limiting for API endpoints to prevent abuse.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, SimpleRateThrottle
import logging

logger = logging.getLogger(__name__)


class NewsEventsAnonRateThrottle(AnonRateThrottle):
    """
    Throttle for anonymous users accessing News Events API.
    
    Rate: 100 requests per hour for anonymous users
    """
    rate = '100/hour'
    scope = 'news_events_anon'


class NewsEventsUserRateThrottle(UserRateThrottle):
    """
    Throttle for authenticated users accessing News Events API.
    
    Rate: 1000 requests per hour for authenticated users
    """
    rate = '1000/hour'
    scope = 'news_events_user'


class NewsEventsSearchThrottle(SimpleRateThrottle):
    """
    Throttle for search endpoints (more restrictive).
    
    Rate: 60 requests per hour for anonymous, 300 per hour for authenticated
    """
    scope = 'news_events_search'
    rate = '60/hour'  # Default rate
    
    def get_cache_key(self, request, view):
        """
        Get cache key based on user authentication status.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
            # Use different scope for authenticated users
            self.scope = 'news_events_search_user'
            # Set rate for authenticated users
            self.rate = '300/hour'
        else:
            ident = self.get_ident(request)
            self.scope = 'news_events_search_anon'
            self.rate = '60/hour'
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class NewsEventsWriteThrottle(SimpleRateThrottle):
    """
    Throttle for write operations (POST, PUT, PATCH, DELETE).
    
    Rate: 30 requests per hour for anonymous, 200 per hour for authenticated
    """
    scope = 'news_events_write'
    rate = '30/hour'  # Default rate
    
    def get_cache_key(self, request, view):
        """
        Get cache key based on user authentication status.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
            self.scope = 'news_events_write_user'
            self.rate = '200/hour'
        else:
            ident = self.get_ident(request)
            self.scope = 'news_events_write_anon'
            self.rate = '30/hour'
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def allow_request(self, request, view):
        """
        Only throttle write operations.
        """
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return super().allow_request(request, view)


class NewsEventsBurstThrottle(SimpleRateThrottle):
    """
    Burst throttle for short-term rate limiting.
    
    Rate: 20 requests per minute for all users
    """
    scope = 'news_events_burst'
    rate = '20/minute'
    
    def get_cache_key(self, request, view):
        """
        Get cache key for burst throttling.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
