"""
Contact App Security Middleware

Implements rate limiting and security features for contact submissions.

Author: Bhanjyang Tech Team
Created: 2026-01-06
"""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
from apps.downloads.security_enhanced import RateLimitManager, IPBlacklistManager
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ContactRateLimitMiddleware:
    """
    Rate limiting middleware for contact form submissions.
    
    Limits:
    - 5 submissions per hour per IP address
    - Integration with IP blacklist system
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Define protected paths and their specific limits
        # Path: (limit_count, limit_window_seconds)
        protected_paths = {
            '/contact/': (5, 3600),          # 5/hour
            '/contact/kym-form/': (3, 3600), # 3/hour
        }
        
        if request.method == 'POST' and request.path in protected_paths:
            limit_count, limit_window = protected_paths[request.path]
            client_ip = get_client_ip(request)
            
            # Check if IP is blacklisted
            if IPBlacklistManager.is_blacklisted(client_ip):
                logger.warning(f"Blocked blacklisted IP: {client_ip}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': ['Your IP has been temporarily blocked. Please try again later.']}
                    }, status=429)
                
                return HttpResponse(
                    '<h1>403 Forbidden</h1><p>Your IP has been temporarily blocked.</p>',
                    status=403
                )
            
            # Check rate limit
            allowed, count, reset_time = RateLimitManager.check_rate_limit(
                identifier=client_ip,
                action=f'submission_{request.path.strip("/")}',
                max_requests=limit_count,
                window=limit_window
            )
            
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for IP {client_ip}: "
                    f"{count} requests, resets in {reset_time}s"
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {
                            '__all__': [
                                f'Too many submissions. Please wait {reset_time // 60} minutes.'
                            ]
                        }
                    }, status=429)
                
                return HttpResponse(
                    f'<h1>429 Too Many Requests</h1>'
                    f'<p>You have exceeded the submission limit.</p>'
                    f'<p>Please try again in {reset_time // 60} minutes.</p>',
                    status=429
                )
            
            # Log successful rate limit check
            remaining = limit_count - count
            logger.info(
                f"Submission allowed for IP {client_ip} on {request.path}: "
                f"{remaining} remaining this window"
            )
        
        response = self.get_response(request)
        return response


class ContactSecurityHeadersMiddleware:
    """
    Add security headers specifically for contact page.
    """
    
    HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Apply headers only to contact routes
        if request.path.startswith('/contact/'):
            for header, value in self.HEADERS.items():
                if header not in response:
                    response[header] = value
        
        return response
