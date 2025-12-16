from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponse
import re


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security headers to all responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_response(self, request, response):
        """Add security headers to response"""
        
        # Content Security Policy (CSP) is handled by django-csp middleware
        
        # Strict Transport Security (HSTS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        permissions_policy = self.get_permissions_policy()
        if permissions_policy:
            response['Permissions-Policy'] = permissions_policy
        
        # Cross-Origin Embedder Policy
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        
        # Cross-Origin Opener Policy
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        
        # Cross-Origin Resource Policy
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        
        return response
    
    def get_csp_policy(self):
        """Get Content Security Policy"""
        policies = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
            "img-src 'self' data: https:",
            "media-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "connect-src 'self'",
            "manifest-src 'self'",
        ]
        
        # Add nonce for inline scripts if available
        if hasattr(settings, 'CSP_NONCE'):
            policies.append(f"script-src 'self' 'nonce-{settings.CSP_NONCE}'")
        
        return '; '.join(policies)
    
    def get_permissions_policy(self):
        """Get Permissions Policy"""
        permissions = [
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "accelerometer=()",
            "gyroscope=()",
            "fullscreen=(self)",
            "picture-in-picture=()",
        ]
        
        return ', '.join(permissions)


class RateLimitMiddleware(MiddlewareMixin):
    """Middleware for rate limiting"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        self.request_counts = {}
        self.rate_limits = {
            'api': {'limit': 100, 'window': 60},  # 100 requests per minute
            'contact': {'limit': 5, 'window': 300},  # 5 requests per 5 minutes
            'search': {'limit': 50, 'window': 60},  # 50 requests per minute
        }
    
    def process_request(self, request):
        """Check rate limits"""
        client_ip = self.get_client_ip(request)
        path = request.path
        
        # Determine rate limit type
        rate_limit_type = self.get_rate_limit_type(path)
        if not rate_limit_type:
            return None
        
        # Check rate limit
        if self.is_rate_limited(client_ip, rate_limit_type):
            return HttpResponse(
                'Rate limit exceeded. Please try again later.',
                status=429,
                content_type='text/plain'
            )
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_rate_limit_type(self, path):
        """Determine rate limit type from path"""
        if path.startswith('/api/'):
            return 'api'
        elif path.startswith('/about/contact/'):
            return 'contact'
        elif path.startswith('/search/'):
            return 'search'
        return None
    
    def is_rate_limited(self, client_ip, rate_limit_type):
        """Check if client is rate limited"""
        import time
        
        current_time = time.time()
        limit_config = self.rate_limits[rate_limit_type]
        limit = limit_config['limit']
        window = limit_config['window']
        
        # Clean old entries
        self.clean_old_entries(current_time, window)
        
        # Check current count
        key = f"{client_ip}:{rate_limit_type}"
        if key not in self.request_counts:
            self.request_counts[key] = []
        
        requests = self.request_counts[key]
        
        # Remove requests outside the window
        requests[:] = [req_time for req_time in requests if current_time - req_time < window]
        
        # Check if limit exceeded
        if len(requests) >= limit:
            return True
        
        # Add current request
        requests.append(current_time)
        return False
    
    def clean_old_entries(self, current_time, window):
        """Clean old rate limit entries"""
        for key in list(self.request_counts.keys()):
            requests = self.request_counts[key]
            requests[:] = [req_time for req_time in requests if current_time - req_time < window]
            if not requests:
                del self.request_counts[key]


class SecurityMiddleware(MiddlewareMixin):
    """General security middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process request for security checks"""
        
        # Block suspicious user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if self.is_suspicious_user_agent(user_agent):
            return HttpResponse('Access denied', status=403)
        
        # Block suspicious paths
        path = request.path
        if self.is_suspicious_path(path):
            return HttpResponse('Access denied', status=403)
        
        # Block suspicious query parameters
        if self.has_suspicious_params(request.GET):
            return HttpResponse('Access denied', status=403)
        
        return None
    
    def is_suspicious_user_agent(self, user_agent):
        """Check if user agent is suspicious"""
        suspicious_patterns = [
            r'sqlmap',
            r'nmap',
            r'nikto',
            r'havij',
            r'w3af',
            r'zap',
            r'burp',
            r'nessus',
            r'openvas',
            r'acunetix',
        ]
        
        user_agent_lower = user_agent.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent_lower):
                return True
        
        return False
    
    def is_suspicious_path(self, path):
        """Check if path is suspicious"""
        suspicious_patterns = [
            r'\.\./',  # Directory traversal
            r'<script',  # XSS attempts
            r'javascript:',  # JavaScript injection
            r'data:text/html',  # Data URI XSS
            r'vbscript:',  # VBScript injection
            r'onload=',  # Event handler injection
            r'onerror=',  # Event handler injection
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        
        return False
    
    def has_suspicious_params(self, params):
        """Check if query parameters contain suspicious content"""
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            r'\.\./',
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
        ]
        
        for param_name, param_values in params.items():
            for param_value in param_values:
                for pattern in suspicious_patterns:
                    if re.search(pattern, param_value, re.IGNORECASE):
                        return True
        
        return False


class CSRFProtectionMiddleware(MiddlewareMixin):
    """Enhanced CSRF protection middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process request for CSRF protection"""
        
        # Skip CSRF for safe methods
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return None
        
        # Skip CSRF for API endpoints (if using token authentication)
        if request.path.startswith('/api/'):
            return None
        
        # Check CSRF token
        if not self.has_valid_csrf_token(request):
            return HttpResponse('CSRF token missing or incorrect', status=403)
        
        return None
    
    def has_valid_csrf_token(self, request):
        """Check if request has valid CSRF token"""
        csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        if not csrf_token:
            csrf_token = request.POST.get('csrfmiddlewaretoken')
        
        if not csrf_token:
            return False
        
        # Validate CSRF token
        from django.middleware.csrf import get_token
        expected_token = get_token(request)
        
        return csrf_token == expected_token


class ContentTypeMiddleware(MiddlewareMixin):
    """Middleware to enforce content type validation"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Validate content type for POST requests"""
        
        if request.method == 'POST':
            content_type = request.META.get('CONTENT_TYPE', '')
            
            # Allow multipart/form-data for file uploads
            if 'multipart/form-data' in content_type:
                return None
            
            # Allow application/x-www-form-urlencoded for forms
            if 'application/x-www-form-urlencoded' in content_type:
                return None
            
            # Allow application/json for API requests
            if 'application/json' in content_type:
                return None
            
            # Block other content types
            return HttpResponse('Invalid content type', status=415)
        
        return None


class SecurityLoggingMiddleware(MiddlewareMixin):
    """Middleware to log security events"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Log suspicious requests"""
        
        # Log failed authentication attempts
        if hasattr(request, 'user') and not request.user.is_authenticated:
            if request.method == 'POST' and 'login' in request.path:
                self.log_security_event('failed_login', request)
        
        # Log suspicious user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if self.is_suspicious_user_agent(user_agent):
            self.log_security_event('suspicious_user_agent', request)
        
        # Log suspicious paths
        if self.is_suspicious_path(request.path):
            self.log_security_event('suspicious_path', request)
        
        return None
    
    def is_suspicious_user_agent(self, user_agent):
        """Check if user agent is suspicious"""
        suspicious_patterns = [
            r'sqlmap', r'nmap', r'nikto', r'havij',
            r'w3af', r'zap', r'burp', r'nessus'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(re.search(pattern, user_agent_lower) for pattern in suspicious_patterns)
    
    def is_suspicious_path(self, path):
        """Check if path is suspicious"""
        suspicious_patterns = [
            r'\.\./', r'<script', r'javascript:', r'vbscript:'
        ]
        
        return any(re.search(pattern, path, re.IGNORECASE) for pattern in suspicious_patterns)
    
    def log_security_event(self, event_type, request):
        """Log security event"""
        import logging
        
        logger = logging.getLogger('security')
        
        log_data = {
            'event_type': event_type,
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'path': request.path,
            'method': request.method,
            'timestamp': timezone.now().isoformat(),
        }
        
        logger.warning(f"Security event: {log_data}")
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
