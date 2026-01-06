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
        # Only apply to contact form POST requests
        if request.path == '/contact/' and request.method == 'POST':
            client_ip = get_client_ip(request)
            
            # Check if IP is blacklisted
            if IPBlacklistManager.is_blacklisted(client_ip):
                logger.warning(f"Blocked blacklisted IP: {client_ip}")
                
                # Return JSON for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': ['Your IP has been temporarily blocked. Please try again later.']}
                    }, status=429)
                
                # Return HTML for regular requests
                return HttpResponse(
                    '<h1>403 Forbidden</h1><p>Your IP has been temporarily blocked.</p>',
                    status=403
                )
            
            # Check rate limit (5 submissions per hour)
            allowed, count, reset_time = RateLimitManager.check_rate_limit(
                identifier=client_ip,
                action='contact_submission',
                max_requests=5,
                window=3600  # 1 hour
            )
            
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for IP {client_ip}: "
                    f"{count} requests, resets in {reset_time}s"
                )
                
                # Return JSON for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {
                            '__all__': [
                                f'Too many submissions. Please wait {reset_time // 60} minutes.'
                            ]
                        }
                    }, status=429)
                
                # Return HTML for regular requests
                return HttpResponse(
                    f'<h1>429 Too Many Requests</h1>'
                    f'<p>You have exceeded the submission limit.</p>'
                    f'<p>Please try again in {reset_time // 60} minutes.</p>',
                    status=429
                )
            
            # Log successful rate limit check
            remaining = 5 - count
            logger.info(
                f"Contact submission allowed for IP {client_ip}: "
                f"{remaining} remaining this hour"
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
