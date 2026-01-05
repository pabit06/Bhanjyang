"""
API Middleware for News Events App.

Adds API version headers and handles version negotiation.
"""
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class NewsEventsAPIVersionMiddleware(MiddlewareMixin):
    """
    Middleware to add API version information to response headers.
    
    Adds:
    - X-API-Version: Current API version
    - X-API-Version-Supported: Comma-separated list of supported versions
    - X-API-Version-Deprecated: Comma-separated list of deprecated versions (if any)
    """
    
    def process_response(self, request, response):
        """Add API version headers to response."""
        # Only add headers for API requests
        if request.path.startswith('/api/v1/news-events/'):
            response['X-API-Version'] = 'v1'
            response['X-API-Version-Supported'] = 'v1'
            response['X-API-Version-Deprecated'] = ''
            response['X-API-Version-Default'] = 'v1'
            
            # Add rate limit headers if available
            if hasattr(request, 'throttle_durations'):
                if request.throttle_durations:
                    response['X-RateLimit-Remaining'] = str(request.throttle_durations.get('remaining', 'unknown'))
                    response['X-RateLimit-Reset'] = str(request.throttle_durations.get('reset', 'unknown'))
        
        return response

