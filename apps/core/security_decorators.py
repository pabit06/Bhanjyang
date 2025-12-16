from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, Union
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.cache import cache
from django.utils import timezone
from .models import APIKey, SecurityLog
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
import logging

logger = logging.getLogger('coop')


class SecurityManager:
    """Minimal security utility for logging events and extracting client IP."""

    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '')

    @staticmethod
    def log_security_event(
        event_type: str, 
        ip_address: str, 
        user: Union[AbstractBaseUser, AnonymousUser, None] = None, 
        details: Optional[Dict[str, Any]] = None, 
        user_agent: Optional[str] = None
    ) -> None:
        try:
            SecurityLog.objects.create(
                event_type=event_type,
                ip_address=ip_address or '',
                user=user,
                details=details or {},
                user_agent=user_agent or ''
            )
        except Exception as exc:
            logger.warning(f"Failed to write SecurityLog: {exc}")


def _check_api_key_rate_limit(api_key_obj: APIKey) -> Tuple[bool, str]:
    """Simple hour/day rate limit using cache based on APIKey limits."""
    now = timezone.now()
    hour_bucket = now.strftime('%Y%m%d%H')
    day_bucket = now.strftime('%Y%m%d')

    key_prefix = f"api_rate:{api_key_obj.key}"
    hour_key = f"{key_prefix}:h:{hour_bucket}"
    day_key = f"{key_prefix}:d:{day_bucket}"

    # Hourly limit
    hourly_count = cache.get(hour_key, 0)
    if hourly_count >= api_key_obj.requests_per_hour:
        return False, f"Hourly rate limit exceeded ({api_key_obj.requests_per_hour}/hour)."

    # Daily limit
    daily_count = cache.get(day_key, 0)
    if daily_count >= api_key_obj.requests_per_day:
        return False, f"Daily rate limit exceeded ({api_key_obj.requests_per_day}/day)."

    # Increment counters
    cache.set(hour_key, hourly_count + 1, timeout=60 * 60 + 30)
    cache.set(day_key, daily_count + 1, timeout=24 * 60 * 60 + 300)
    return True, "OK"

def api_key_required(view_func: Callable) -> Callable:
    """Decorator to require API key authentication"""
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # Get API key from header
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            SecurityManager.log_security_event(
                'api_key_invalid',
                SecurityManager.get_client_ip(request),
                details={'error': 'No API key provided'},
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            return JsonResponse({
                'error': 'API key required',
                'message': 'Please provide a valid API key in the X-API-Key header'
            }, status=401)
        
        # Validate API key
        try:
            api_key_obj = APIKey.objects.get(key=api_key)
        except APIKey.DoesNotExist:
            SecurityManager.log_security_event(
                'api_key_invalid',
                SecurityManager.get_client_ip(request),
                details={'error': 'Invalid API key', 'key': api_key[:8] + '...'},
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            return JsonResponse({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }, status=401)
        
        # Check if API key is valid
        if not api_key_obj.is_valid():
            SecurityManager.log_security_event(
                'api_key_invalid',
                SecurityManager.get_client_ip(request),
                user=api_key_obj.user,
                details={'error': 'API key expired or inactive'},
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            return JsonResponse({
                'error': 'API key invalid',
                'message': 'The API key has expired or is inactive'
            }, status=401)
        
        # Check rate limits
        is_allowed, message = _check_api_key_rate_limit(api_key_obj)
        if not is_allowed:
            SecurityManager.log_security_event(
                'rate_limit_exceeded',
                SecurityManager.get_client_ip(request),
                user=api_key_obj.user,
                details={'error': message, 'key': api_key[:8] + '...'},
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': message
            }, status=429)
        
        # Update last used timestamp
        api_key_obj.update_last_used()
        
        # Log successful API usage
        SecurityManager.log_security_event(
            'api_key_used',
            SecurityManager.get_client_ip(request),
            user=api_key_obj.user,
            details={'endpoint': request.path, 'method': request.method},
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        # Add API key object to request for use in view
        request.api_key = api_key_obj
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def rate_limit(requests_per_minute=60):
    """Decorator for rate limiting specific views"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = SecurityManager.get_client_ip(request)
            cache_key = f"rate_limit:{request.path}:{ip}"
            
            current_time = int(timezone.now().timestamp())
            minute_window = current_time // 60
            
            # Get current count for this minute
            window_key = f"{cache_key}:{minute_window}"
            current_count = cache.get(window_key, 0)
            
            if current_count >= requests_per_minute:
                SecurityManager.log_security_event(
                    'rate_limit_exceeded',
                    ip,
                    details={'endpoint': request.path, 'limit': requests_per_minute},
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {requests_per_minute} requests per minute allowed'
                }, status=429)
            
            # Increment counter
            cache.set(window_key, current_count + 1, timeout=120)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def require_https(view_func):
    """Decorator to require HTTPS"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_secure() and not request.META.get('HTTP_X_FORWARDED_PROTO') == 'https':
            return JsonResponse({
                'error': 'HTTPS required',
                'message': 'This endpoint requires HTTPS'
            }, status=400)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
