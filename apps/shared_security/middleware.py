"""
Shared Security Middleware for Bhanjyang Project

Apply security features across all apps
"""

import logging
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from . import (
    IPBlacklistManager,
    SecurityHeadersManager,
    SessionSecurityManager,
    log_security_event,
    get_client_ip
)

logger = logging.getLogger(__name__)

# Get settings with defaults
MAX_REQUEST_SIZE = getattr(settings, 'MAX_REQUEST_SIZE', 10 * 1024 * 1024)
EXEMPT_PATHS = getattr(settings, 'SECURITY_EXEMPT_PATHS', [
    '/admin/',
    '/static/',
    '/media/',
])


class BhanjyangSecurityMiddleware(MiddlewareMixin):
    """
    Global security middleware for all Bhanjyang apps
    
    Features:
    - IP blacklist enforcement
    - Security headers
    - Session security
    - Request size limiting
    """
    
    def process_request(self, request):
        """Process incoming requests"""
        # Skip exempt paths
        if any(request.path.startswith(path) for path in EXEMPT_PATHS):
            return None
        
        # Get client IP
        ip_address = get_client_ip(request)
        
        # Check IP blacklist
        is_blacklisted, reason = IPBlacklistManager.is_blacklisted(ip_address)
        if is_blacklisted:
            log_security_event(
                'blocked_blacklisted_ip',
                {'ip': ip_address, 'reason': reason, 'path': request.path},
                request
            )
            return HttpResponseForbidden(
                "<h1>Access Denied</h1>"
                "<p>Your IP address has been temporarily blocked due to security violations.</p>"
            )
        
        # Check request size
        try:
            content_length = int(request.META.get('CONTENT_LENGTH', 0))
            if content_length > MAX_REQUEST_SIZE:
                violation_count = IPBlacklistManager.record_violation(
                    ip_address, 'oversized_request'
                )
                log_security_event(
                    'oversized_request',
                    {
                        'ip': ip_address,
                        'size': content_length,
                        'violations': violation_count
                    },
                    request
                )
                return JsonResponse({
                    'error': 'Request too large',
                    'max_size': MAX_REQUEST_SIZE
                }, status=413)
        except (ValueError, TypeError):
            pass
        
        # Check session security for authenticated users (requires AuthenticationMiddleware)
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            if not SessionSecurityManager.validate_session_integrity(request):
                log_security_event(
                    'session_integrity_failure',
                    {'user_id': request.user.id},
                    request
                )
                from django.contrib.auth import logout
                logout(request)
                return JsonResponse({
                    'error': 'Session validation failed',
                    'message': 'Please log in again for security reasons'
                }, status=401)
            
            # Check session timeout
            timeout_minutes = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 30)
            if not SessionSecurityManager.check_session_timeout(request, timeout_minutes):
                log_security_event(
                    'session_timeout',
                    {'user_id': request.user.id},
                    request
                )
                from django.contrib.auth import logout
                logout(request)
                return JsonResponse({
                    'error': 'Session expired',
                    'message': 'Your session has expired. Please log in again'
                }, status=401)
        
        return None
    
    def process_response(self, request, response):
        """Add security headers to responses"""
        response = SecurityHeadersManager.apply_security_headers(response)
        return response
    
    def process_exception(self, request, exception):
        """Handle security exceptions"""
        if isinstance(exception, PermissionDenied):
            ip_address = get_client_ip(request)
            log_security_event(
                'permission_denied',
                {'ip': ip_address, 'exception': str(exception)},
                request
            )
        return None


class GlobalRateLimitMiddleware(MiddlewareMixin):
    """
    Global rate limiting middleware
    
    Can be customized per app by setting rate limits in settings.py
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        # Get rate limits from settings
        self.rate_limits = getattr(settings, 'GLOBAL_RATE_LIMITS', {})
    
    def process_request(self, request):
        """Check rate limits"""
        if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return None
        
        from django.core.cache import cache
        import re
        
        ip_address = get_client_ip(request)
        
        # Check each rate limit pattern
        for pattern, limit in self.rate_limits.items():
            if re.match(pattern, request.path):
                cache_key = f"rate_limit_{pattern}_{ip_address}"
                request_count = cache.get(cache_key, 0)
                
                if request_count >= limit:
                    violation_count = IPBlacklistManager.record_violation(
                        ip_address, 'rate_limit_exceeded'
                    )
                    log_security_event(
                        'rate_limit_exceeded',
                        {
                            'ip': ip_address,
                            'path': request.path,
                            'limit': limit,
                            'violations': violation_count
                        },
                        request
                    )
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': 'Too many requests. Please try again later.',
                        'limit': limit,
                        'retry_after': 60
                    }, status=429)
                
                # Increment counter. cache.add() seeds the key with a fresh 60s
                # TTL only when the window is new; incr() then leaves that TTL
                # alone, so the window actually closes. Re-setting the TTL on
                # every request would keep extending it under sustained traffic.
                if cache.add(cache_key, 1, 60):
                    continue
                try:
                    cache.incr(cache_key)
                except ValueError:
                    # Key expired between add() and incr(); the next request
                    # starts a new window.
                    pass
        
        return None
