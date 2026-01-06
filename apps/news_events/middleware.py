"""
Security Middleware for News Events App

Applies enhanced security measures to all requests:
- IP blacklist checking
- Security headers
- Session security
- Request size limits
- Security event logging
"""

import logging
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin
from .security_enhanced import (
    IPBlacklistManager,
    SecurityHeadersManager,
    SessionSecurityManager,
    log_security_event,
    MAX_REQUEST_SIZE
)

logger = logging.getLogger(__name__)


class NewsEventsSecurityMiddleware(MiddlewareMixin):
    """
    Comprehensive security middleware for news events app
    
    Applies security checks and headers to requests/responses
    """
    
    def process_request(self, request):
        """
        Process incoming requests for security
        
        Args:
            request: HTTP request object
            
        Returns:
            None if request is allowed, HttpResponse if blocked
        """
        # Skip security checks for certain paths
        exempt_paths = [
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(path) for path in exempt_paths):
            return None
        
        # Get client IP
        ip_address = self.get_client_ip(request)
        
        # Check IP blacklist
        is_blacklisted, reason = IPBlacklistManager.is_blacklisted(ip_address)
        if is_blacklisted:
            log_security_event(
                'blocked_blacklisted_ip',
                {'ip': ip_address, 'reason': reason, 'path': request.path},
                request
            )
            return HttpResponseForbidden(
                "<h1>Access Denied</h1><p>Your IP address has been temporarily blocked.</p>"
            )
        
        # Check request size
        try:
            content_length = int(request.META.get('CONTENT_LENGTH', 0))
            if content_length > MAX_REQUEST_SIZE:
                violation_count = IPBlacklistManager.record_violation(ip_address, 'oversized_request')
                log_security_event(
                    'oversized_request',
                    {'ip': ip_address, 'size': content_length, 'violations': violation_count},
                    request
                )
                return JsonResponse({
                    'error': 'Request too large',
                    'max_size': MAX_REQUEST_SIZE
                }, status=413)
        except (ValueError, TypeError):
            pass
        
        # Check session security for authenticated users
        if request.user.is_authenticated:
            if not SessionSecurityManager.validate_session_integrity(request):
                log_security_event(
                    'session_integrity_failure',
                    {'user_id': request.user.id},
                    request
                )
                # Log out user
                from django.contrib.auth import logout
                logout(request)
                return JsonResponse({
                    'error': 'Session validation failed',
                    'message': 'Please log in again'
                }, status=401)
            
            # Check session timeout
            if not SessionSecurityManager.check_session_timeout(request):
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
        """
        Add security headers to responses
        
        Args:
            request: HTTP request object
            response: HTTP response object
            
        Returns:
            Response with security headers added
        """
        # Apply security headers
        response = SecurityHeadersManager.apply_security_headers(response)
        
        return response
    
    def process_exception(self, request, exception):
        """
        Handle security-related exceptions
        
        Args:
            request: HTTP request object
            exception: Exception that was raised
            
        Returns:
            HttpResponse or None
        """
        if isinstance(exception, PermissionDenied):
            ip_address = self.get_client_ip(request)
            log_security_event(
                'permission_denied',
                {'ip': ip_address, 'exception': str(exception)},
                request
            )
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address from request
        
        Handles proxies and load balancers
        
        Args:
            request: HTTP request object
            
        Returns:
            Client IP address string
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """
    Advanced rate limiting middleware
    
    Complements DRF throttling for web views
    """
    
    # Rate limits per path pattern (requests per minute)
    RATE_LIMITS = {
        '/news-events/subscribe/': 3,  # 3 subscriptions per minute
        '/news-events/article/.*/comment/': 5,  # 5 comments per minute
        '/news-events/search/': 10,  # 10 searches per minute
    }
    
    def process_request(self, request):
        """
        Check rate limits for request
        
        Args:
            request: HTTP request object
            
        Returns:
            None if allowed, HttpResponse if rate limited
        """
        # Only apply to POST requests
        if request.method != 'POST':
            return None
        
        # Check if path matches any rate limit patterns
        from django.core.cache import cache
        import re
        
        ip_address = NewsEventsSecurityMiddleware.get_client_ip(request)
        
        for pattern, limit in self.RATE_LIMITS.items():
            if re.match(pattern, request.path):
                cache_key = f"rate_limit_{pattern}_{ip_address}"
                request_count = cache.get(cache_key, 0)
                
                if request_count >= limit:
                    violation_count = IPBlacklistManager.record_violation(ip_address, 'rate_limit_exceeded')
                    log_security_event(
                        'rate_limit_exceeded',
                        {'ip': ip_address, 'path': request.path, 'limit': limit, 'violations': violation_count},
                        request
                    )
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'Too many requests. Please try again later.',
                        'limit': limit,
                        'retry_after': 60
                    }, status=429)
                
                # Increment counter
                cache.set(cache_key, request_count + 1, 60)  # 1 minute window
        
        return None
