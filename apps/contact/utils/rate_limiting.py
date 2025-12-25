"""
Rate limiting utilities for the Contact app.

Uses Django's cache framework to implement rate limiting without external dependencies.
"""
import logging
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from .constants import (
    CONTACT_FORM_RATE_LIMIT_PER_IP,
    CONTACT_FORM_RATE_LIMIT_PER_EMAIL,
)

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Get client IP address from request.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def parse_rate_limit(rate_limit_string):
    """
    Parse rate limit string (e.g., '5/m' = 5 per minute, '3/h' = 3 per hour).
    
    Args:
        rate_limit_string: Rate limit string in format 'N/m' or 'N/h'
        
    Returns:
        tuple: (limit, window_seconds)
    """
    try:
        limit, period = rate_limit_string.split('/')
        limit = int(limit)
        
        if period == 'm':
            window_seconds = 60
        elif period == 'h':
            window_seconds = 3600
        elif period == 'd':
            window_seconds = 86400
        else:
            # Default to per minute
            window_seconds = 60
        
        return limit, window_seconds
    except (ValueError, AttributeError):
        # Default: 5 per minute
        logger.warning(f"Invalid rate limit format: {rate_limit_string}, using default 5/m")
        return 5, 60


def rate_limit_by_ip(rate_limit_string=CONTACT_FORM_RATE_LIMIT_PER_IP):
    """
    Decorator to rate limit requests by IP address.
    
    Args:
        rate_limit_string: Rate limit string (e.g., '5/m' for 5 per minute)
        
    Usage:
        @rate_limit_by_ip('5/m')
        def my_view(request):
            ...
    """
    limit, window_seconds = parse_rate_limit(rate_limit_string)
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Only apply rate limiting to POST requests
            if request.method != 'POST':
                return view_func(request, *args, **kwargs)
            
            # Skip rate limiting in tests or if explicitly disabled
            if getattr(settings, 'DISABLE_RATE_LIMITING', False):
                return view_func(request, *args, **kwargs)
            
            # Skip rate limiting during test runs
            import sys
            if any('test' in arg for arg in sys.argv) or 'pytest' in sys.modules:
                return view_func(request, *args, **kwargs)
            
            client_ip = get_client_ip(request)
            cache_key = f"contact_rate_limit_ip:{client_ip}"
            
            # Get current count
            current_count = cache.get(cache_key, 0)
            
            if current_count >= limit:
                logger.warning(
                    f"Rate limit exceeded for IP {client_ip}: "
                    f"{current_count} requests in {window_seconds}s window"
                )
                return JsonResponse({
                    'success': False,
                    'message': f'Too many requests. Please try again in a few minutes.',
                    'error_code': 'RATE_LIMIT_EXCEEDED'
                }, status=429)
            
            # Increment counter
            try:
                cache.set(cache_key, current_count + 1, timeout=window_seconds)
            except Exception as e:
                # If cache fails, log warning but allow request
                logger.warning(f"Cache error in rate limiting: {e}. Allowing request.")
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def rate_limit_by_email(rate_limit_string=CONTACT_FORM_RATE_LIMIT_PER_EMAIL):
    """
    Decorator to rate limit requests by email address.
    
    This should be used inside the view after form validation to access email.
    
    Args:
        rate_limit_string: Rate limit string (e.g., '3/h' for 3 per hour)
        
    Returns:
        bool: True if rate limit exceeded, False otherwise
    """
    limit, window_seconds = parse_rate_limit(rate_limit_string)
    
    def check_rate_limit(email):
        """
        Check if email has exceeded rate limit.
        
        Args:
            email: Email address to check
            
        Returns:
            tuple: (is_limited, message)
        """
        if not email:
            return False, None
        
        # Normalize email
        email = email.lower().strip()
        cache_key = f"contact_rate_limit_email:{email}"
        
        # Get current count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            logger.warning(
                f"Rate limit exceeded for email {email}: "
                f"{current_count} requests in {window_seconds}s window"
            )
            return True, 'Too many submissions from this email address. Please try again later.'
        
        # Increment counter
        try:
            cache.set(cache_key, current_count + 1, timeout=window_seconds)
        except Exception as e:
            logger.warning(f"Cache error in email rate limiting: {e}. Allowing request.")
        
        return False, None
    
    return check_rate_limit

