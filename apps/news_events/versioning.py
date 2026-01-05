"""
API Versioning for News Events App.

Provides API version negotiation and management.
"""
from rest_framework.versioning import URLPathVersioning, AcceptHeaderVersioning, NamespaceVersioning
from rest_framework.versioning import QueryParameterVersioning
from rest_framework import versioning
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class NewsEventsAPIVersioning(URLPathVersioning):
    """
    Custom API versioning for News Events app.
    
    Supports multiple versioning schemes:
    1. URL path versioning (primary): /api/v1/news-events/...
    2. Query parameter versioning: ?version=1
    3. Accept header versioning: Accept: application/json; version=1
    
    Default version: v1
    Allowed versions: v1
    """
    default_version = 'v1'
    allowed_versions = ['v1']
    version_param = 'version'
    
    def determine_version(self, request, *args, **kwargs):
        """
        Determine API version from request.
        
        Priority:
        1. URL path (e.g., /api/v1/news-events/)
        2. Query parameter (e.g., ?version=1)
        3. Accept header (e.g., Accept: application/json; version=1)
        4. Default version
        """
        # Try URL path first
        version = super().determine_version(request, *args, **kwargs)
        if version:
            return version
        
        # Try query parameter
        version = request.query_params.get(self.version_param)
        if version:
            # Normalize version (v1, 1, etc.)
            if version.startswith('v'):
                version = version[1:]
            version = f'v{version}'
            if version in self.allowed_versions:
                return version
        
        # Try Accept header
        accept_header = request.META.get('HTTP_ACCEPT', '')
        if 'version=' in accept_header:
            try:
                version_part = accept_header.split('version=')[1].split(';')[0].split(',')[0].strip()
                if version_part.startswith('v'):
                    version = version_part
                else:
                    version = f'v{version_part}'
                if version in self.allowed_versions:
                    return version
            except Exception as e:
                logger.debug(f"Error parsing Accept header version: {e}")
        
        # Return default version
        return self.default_version
    
    def reverse(self, viewname, args=None, kwargs=None, request=None, format=None, **extra):
        """
        Reverse URL with version included.
        """
        if request is not None:
            version = self.determine_version(request)
            kwargs = kwargs or {}
            kwargs[self.version_param] = version
        
        return super().reverse(viewname, args, kwargs, request, format, **extra)


class APIVersionMiddleware:
    """
    Middleware to add API version information to response headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add API version header if this is an API request
        if request.path.startswith('/api/'):
            version = 'v1'  # Current API version
            response['X-API-Version'] = version
            response['X-API-Version-Supported'] = ','.join(['v1'])
            response['X-API-Version-Deprecated'] = ''  # No deprecated versions yet
        
        return response

