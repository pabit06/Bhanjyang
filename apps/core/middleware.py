from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time
import hashlib
import logging
from django.db import connection
from django.utils import timezone
from apps.dashboard.models import PerformanceMetric, UserSession, ErrorLog


logger = logging.getLogger('coop')

class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limits (requests per minute)
        self.rate_limits = {
            'default': 200,      # Increased from 100
            'api': 120,          # Increased from 60
            'login': 10,         # Increased from 5
            'contact': 20,       # Increased from 3 - much more reasonable for contact forms
            'search': 60,        # Increased from 30
            'performance': 2000, # Increased from 1000
        }
        super().__init__(get_response)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_rate_limit_key(self, request, limit_type='default'):
        """Generate cache key for rate limiting"""
        ip = self.get_client_ip(request)
        # Check if user is authenticated (middleware runs after auth middleware)
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id
        else:
            user_id = 'anonymous'
        return f"rate_limit:{limit_type}:{ip}:{user_id}"
    
    def is_rate_limited(self, request, limit_type='default'):
        """Check if request exceeds rate limit"""
        try:
            key = self.get_rate_limit_key(request, limit_type)
            current_time = int(time.time())
            minute_window = current_time // 60
            
            # Get current count for this minute
            cache_key = f"{key}:{minute_window}"
            try:
                current_count = cache.get(cache_key, 0)
            except Exception as e:
                # If cache is unavailable (e.g., Redis not running), allow request
                logger.warning(f"Cache unavailable for rate limiting: {e}. Allowing request.")
                return False
            
            # Get rate limit for this type
            limit = self.rate_limits.get(limit_type, self.rate_limits['default'])
            
            if current_count >= limit:
                logger.warning(f"Rate limit exceeded for {limit_type}: {self.get_client_ip(request)}")
                return True
            
            # Increment counter
            try:
                cache.set(cache_key, current_count + 1, timeout=120)  # 2 minutes timeout
            except Exception as e:
                # If cache is unavailable, log warning but allow request
                logger.warning(f"Cache unavailable for rate limiting: {e}. Allowing request.")
            
            return False
        except Exception as e:
            # If any error occurs, log it but allow the request to proceed
            logger.warning(f"Error in rate limiting: {e}. Allowing request.")
            return False
    
    def determine_limit_type(self, request):
        """Determine rate limit type based on request path"""
        path = request.path
        
        if path.startswith('/api/'):
            return 'api'
        elif path.startswith('/admin/login/'):
            return 'login'
        elif path.startswith('/contact/') and request.method == 'POST':
            # Only apply contact rate limiting to POST requests (form submissions)
            return 'contact'
        elif path.startswith('/search/'):
            return 'search'
        elif path.startswith('/performance/'):
            return 'performance'
        else:
            return 'default'
    
    def process_request(self, request):
        """Process request for rate limiting"""
        # Skip rate limiting for certain paths
        skip_paths = ['/static/', '/media/', '/favicon.ico', '/admin/logout/', '/admin/jsi18n/']
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        limit_type = self.determine_limit_type(request)
        
        if self.is_rate_limited(request, limit_type):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Limit: {self.rate_limits[limit_type]} requests per minute',
                'retry_after': 60
            }, status=429)
        
        return None

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add comprehensive security headers"""
    
    def process_response(self, request, response):
        """Add security headers to response"""
        
        # Skip security headers for static files to avoid interfering with font loading
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return response
        
        # Content Security Policy - Handled by django-csp middleware
        # response['Content-Security-Policy'] = ...

        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        # X-Frame-Options is handled by CSP frame-ancestors directive
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Allow fonts to load properly by not being too restrictive
        if request.path.startswith('/static/') and 'font' in request.path:
            response['X-Content-Type-Options'] = ''
        
        # HSTS (only for HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        
        return response

class InputValidationMiddleware(MiddlewareMixin):
    """Enhanced input validation and sanitization"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Suspicious patterns
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'<style[^>]*>',
            r'expression\s*\(',
            r'url\s*\(',
            r'@import',
            r'\.\.\/',
            r'\.\.\\',
            r'\/etc\/passwd',
            r'\/proc\/',
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
            r'exec\s*\(',
            r'eval\s*\(',
            r'system\s*\(',
            r'shell_exec\s*\(',
        ]
        super().__init__(get_response)
    
    def contains_suspicious_content(self, data):
        """Check if data contains suspicious patterns"""
        import re
        
        if isinstance(data, str):
            for pattern in self.suspicious_patterns:
                if re.search(pattern, data, re.IGNORECASE):
                    return True
        elif isinstance(data, dict):
            for value in data.values():
                if self.contains_suspicious_content(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self.contains_suspicious_content(item):
                    return True
        
        return False
    
    def process_request(self, request):
        """Validate request data"""
        # Check POST data
        if request.method == 'POST':
            if hasattr(request, 'POST') and request.POST:
                if self.contains_suspicious_content(request.POST.dict()):
                    logger.warning(f"Suspicious POST data detected from {self.get_client_ip(request)}")
                    return JsonResponse({
                        'error': 'Invalid input detected',
                        'message': 'Request contains potentially malicious content'
                    }, status=400)
        
        # Check GET parameters
        if request.GET:
            if self.contains_suspicious_content(request.GET.dict()):
                logger.warning(f"Suspicious GET data detected from {self.get_client_ip(request)}")
                return JsonResponse({
                    'error': 'Invalid input detected',
                    'message': 'Request contains potentially malicious content'
                }, status=400)
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class BruteForceProtectionMiddleware(MiddlewareMixin):
    """Protect against brute force attacks"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 minutes
        super().__init__(get_response)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_ip_blocked(self, ip):
        """Check if IP is blocked due to brute force attempts"""
        try:
            key = f"brute_force:{ip}"
            attempts = cache.get(key, 0)
            return attempts >= self.max_attempts
        except Exception as e:
            # If cache is unavailable, don't block (allow request)
            logger.warning(f"Cache unavailable for brute force protection: {e}. Allowing request.")
            return False
    
    def record_failed_attempt(self, ip):
        """Record a failed login attempt"""
        try:
            key = f"brute_force:{ip}"
            attempts = cache.get(key, 0) + 1
            cache.set(key, attempts, timeout=self.lockout_duration)
            
            if attempts >= self.max_attempts:
                logger.warning(f"IP {ip} blocked due to brute force attempts")
        except Exception as e:
            # If cache is unavailable, log warning but continue
            logger.warning(f"Cache unavailable for brute force protection: {e}.")
    
    def process_request(self, request):
        """Check for brute force attempts"""
        # Only check login attempts
        if not (request.path.startswith('/admin/login/') and request.method == 'POST'):
            return None
        
        ip = self.get_client_ip(request)
        
        if self.is_ip_blocked(ip):
            logger.warning(f"Blocked brute force attempt from {ip}")
            return JsonResponse({
                'error': 'Access denied',
                'message': 'Too many failed login attempts. Please try again later.',
                'retry_after': self.lockout_duration
            }, status=429)
        
        return None
    
    def process_response(self, request, response):
        """Record failed login attempts"""
        if (request.path.startswith('/admin/login/') and 
            request.method == 'POST' and 
            response.status_code == 200 and 
            'error' in str(response.content)):
            
            ip = self.get_client_ip(request)
            self.record_failed_attempt(ip)
        
        return response


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to track server-side performance metrics"""
    
    def process_request(self, request):
        """Start timing the request"""
        request._start_time = time.time()
        request._db_queries_start = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """Track request performance and create metrics"""
        if hasattr(request, '_start_time'):
            # Calculate request duration
            duration = (time.time() - request._start_time) * 1000  # Convert to milliseconds
            
            # Count database queries
            db_queries = len(connection.queries) - getattr(request, '_db_queries_start', 0)
            
            # Track performance metrics
            try:
                PerformanceMetric.objects.create(
                    metric_type='page_load',
                    page_url=request.build_absolute_uri(),
                    value=duration,
                    unit='ms',
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    ip_address=self.get_client_ip(request),
                    session_id=request.session.session_key,
                    user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                    additional_data={
                        'method': request.method,
                        'status_code': response.status_code,
                        'db_queries': db_queries,
                        'response_size': len(response.content) if hasattr(response, 'content') else 0,
                        'path': request.path,
                        'query_params': dict(request.GET),
                        'user_authenticated': hasattr(request, 'user') and request.user.is_authenticated,
                        'is_ajax': request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest',
                        'referer': request.META.get('HTTP_REFERER', ''),
                    }
                )
                
                # Track user session
                self.track_user_session(request, duration)
                
            except Exception as e:
                logger.error(f"Failed to track performance metric: {e}")
        
        return response
    
    def process_exception(self, request, exception):
        """Track exceptions and errors"""
        try:
            ErrorLog.objects.create(
                error_type='500',
                error_message=str(exception),
                page_url=request.build_absolute_uri(),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=self.get_client_ip(request),
                session_id=request.session.session_key,
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                stack_trace=self.get_stack_trace(exception),
                additional_data={
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.GET),
                    'post_data': dict(request.POST) if request.method == 'POST' else {},
                    'user_authenticated': hasattr(request, 'user') and request.user.is_authenticated,
                    'is_ajax': request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest',
                    'referer': request.META.get('HTTP_REFERER', ''),
                }
            )
        except Exception as e:
            logger.error(f"Failed to track error: {e}")
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_stack_trace(self, exception):
        """Get stack trace for exception"""
        import traceback
        return traceback.format_exc()
    
    def track_user_session(self, request, duration):
        """Track or update user session"""
        session_id = request.session.session_key
        if not session_id:
            return
        
        try:
            # Get or create session
            session, created = UserSession.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'ip_address': self.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'user': request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                    'is_mobile': self.is_mobile(request),
                    'browser': self.get_browser(request),
                    'os': self.get_os(request),
                }
            )
            
            # Update session data
            session.page_views += 1
            session.total_load_time += duration
            
            # Update end time if this is likely the last request
            if not request.META.get('HTTP_X_REQUESTED_WITH'):  # Not an AJAX request
                session.end_time = timezone.now()
            
            session.save()
            
        except Exception as e:
            logger.error(f"Failed to track user session: {e}")
    
    def is_mobile(self, request):
        """Check if request is from mobile device"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'blackberry', 'windows phone']
        return any(indicator in user_agent for indicator in mobile_indicators)
    
    def get_browser(self, request):
        """Extract browser from user agent"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'chrome' in user_agent.lower():
            return 'Chrome'
        elif 'firefox' in user_agent.lower():
            return 'Firefox'
        elif 'safari' in user_agent.lower():
            return 'Safari'
        elif 'edge' in user_agent.lower():
            return 'Edge'
        elif 'opera' in user_agent.lower():
            return 'Opera'
        else:
            return 'Unknown'
    
    def get_os(self, request):
        """Extract OS from user agent"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'windows' in user_agent.lower():
            return 'Windows'
        elif 'mac' in user_agent.lower():
            return 'macOS'
        elif 'linux' in user_agent.lower():
            return 'Linux'
        elif 'android' in user_agent.lower():
            return 'Android'
        elif 'ios' in user_agent.lower():
            return 'iOS'
        else:
            return 'Unknown'

