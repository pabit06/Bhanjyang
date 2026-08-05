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
from apps.shared_security import (
    get_client_ip as resolve_client_ip,
    get_client_ip_from_meta as resolve_client_ip_from_meta,
)

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP from request."""
    return resolve_client_ip(request)


class ContactRateLimitMiddleware:
    """
    Rate limiting middleware for contact form submissions.
    
    Limits:
    - 5 submissions per hour per IP address (contact form)
    - Contact form: 5 per hour per IP
    - 3 submissions per hour per email address (both forms)
    - Integration with IP blacklist system
    """
    
    # Email rate limit: 3 submissions per hour per email
    EMAIL_RATE_LIMIT_COUNT = 3
    EMAIL_RATE_LIMIT_WINDOW = 3600  # 1 hour
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Define protected paths and their specific limits
        # Path: (ip_limit_count, limit_window_seconds)
        protected_paths = {
            '/contact/': (5, 3600),          # 5/hour per IP
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
            
            # Check IP-based rate limit
            ip_allowed, ip_count, ip_reset_time = RateLimitManager.check_rate_limit(
                identifier=client_ip,
                action=f'submission_{request.path.strip("/")}',
                max_requests=limit_count,
                window=limit_window
            )
            
            if not ip_allowed:
                logger.warning(
                    f"IP rate limit exceeded for IP {client_ip}: "
                    f"{ip_count} requests, resets in {ip_reset_time}s"
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {
                            '__all__': [
                                f'Too many submissions from this IP. Please wait {ip_reset_time // 60} minutes.'
                            ]
                        }
                    }, status=429)
                
                return HttpResponse(
                    f'<h1>429 Too Many Requests</h1>'
                    f'<p>You have exceeded the submission limit for this IP address.</p>'
                    f'<p>Please try again in {ip_reset_time // 60} minutes.</p>',
                    status=429
                )
            
            # Check email-based rate limit (if email is provided)
            email = request.POST.get('email', '').strip().lower()
            email_count = None  # Initialize to avoid UnboundLocalError
            email_remaining = None  # Track email remaining count for logging
            
            if email:
                email_allowed, email_count, email_reset_time = RateLimitManager.check_rate_limit(
                    identifier=email,
                    action=f'email_submission_{request.path.strip("/")}',
                    max_requests=self.EMAIL_RATE_LIMIT_COUNT,
                    window=self.EMAIL_RATE_LIMIT_WINDOW
                )
                
                if not email_allowed:
                    logger.warning(
                        f"Email rate limit exceeded for email {email}: "
                        f"{email_count} requests, resets in {email_reset_time}s"
                    )
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': {
                                '__all__': [
                                    f'Too many submissions from this email address. Please wait {email_reset_time // 60} minutes.'
                                ]
                            }
                        }, status=429)
                    
                    return HttpResponse(
                        f'<h1>429 Too Many Requests</h1>'
                        f'<p>You have exceeded the submission limit for this email address.</p>'
                        f'<p>Please try again in {email_reset_time // 60} minutes.</p>',
                        status=429
                    )
                
                # Calculate email remaining count only if email was provided and rate limit check passed
                if email_count is not None:
                    email_remaining = self.EMAIL_RATE_LIMIT_COUNT - email_count
            
            # Log successful rate limit check
            ip_remaining = limit_count - ip_count
            log_message = (
                f"Submission allowed for IP {client_ip} on {request.path}: "
                f"{ip_remaining} IP requests remaining"
            )
            if email_remaining is not None:
                log_message += f", {email_remaining} email requests remaining"
            logger.info(log_message)
        
        response = self.get_response(request)
        return response


class ContactSecurityHeadersMiddleware:
    """
    Add security headers specifically for contact page.

    Content-Security-Policy is deliberately NOT set here. django-csp
    (csp.middleware.CSPMiddleware) builds the site-wide policy from the CSP_*
    settings, including the per-request script nonce. This middleware runs
    earlier in the response phase, so setting the header here would win -
    django-csp does not overwrite an existing header - and contact pages would
    silently fall back to a policy with no nonce and 'unsafe-inline'.
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
            # Add standard security headers
            for header, value in self.HEADERS.items():
                if header not in response:
                    response[header] = value

        return response
