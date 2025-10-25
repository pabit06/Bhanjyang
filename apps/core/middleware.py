from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time
import hashlib
import logging

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
        key = self.get_rate_limit_key(request, limit_type)
        current_time = int(time.time())
        minute_window = current_time // 60
        
        # Get current count for this minute
        cache_key = f"{key}:{minute_window}"
        current_count = cache.get(cache_key, 0)
        
        # Get rate limit for this type
        limit = self.rate_limits.get(limit_type, self.rate_limits['default'])
        
        if current_count >= limit:
            logger.warning(f"Rate limit exceeded for {limit_type}: {self.get_client_ip(request)}")
            return True
        
        # Increment counter
        cache.set(cache_key, current_count + 1, timeout=120)  # 2 minutes timeout
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
        
        # Content Security Policy - Temporarily more permissive for debugging
        csp = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "font-src 'self' data: https:; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "frame-src 'self' https:; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response['Content-Security-Policy'] = csp
        
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
        key = f"brute_force:{ip}"
        attempts = cache.get(key, 0)
        return attempts >= self.max_attempts
    
    def record_failed_attempt(self, ip):
        """Record a failed login attempt"""
        key = f"brute_force:{ip}"
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, timeout=self.lockout_duration)
        
        if attempts >= self.max_attempts:
            logger.warning(f"IP {ip} blocked due to brute force attempts")
    
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
