"""
Security Middleware for Downloads App
=====================================

Applies security checks to all downloads requests including:
- IP blacklist checking
- Rate limiting
- Security headers
- Request validation

Author: Prem Bhandari
Date: January 6, 2026
"""

import logging
from django.http import HttpResponseForbidden, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render

from .security_enhanced import (
    IPBlacklistManager,
    RateLimitManager,
    SecurityAuditEnhancedLogger,
    RequestValidator
)

logger = logging.getLogger(__name__)


# ============================================================================
# DOWNLOADS SECURITY MIDDLEWARE
# ============================================================================

class DownloadsSecurityMiddleware(MiddlewareMixin):
    """
    Applies security checks to downloads requests.
    
    Checks performed:
    1. IP blacklist
    2. Rate limiting
    3. Request validation
    
    Only processes requests to /downloads/ URLs.
    """
    
    EXEMPT_PATHS = [
        '/downloads/static/',  # Static files
        '/downloads/admin/',   # Admin URLs
    ]
    
    def process_request(self, request):
        """
        Process incoming request.
        
        Args:
            request: HttpRequest object
            
        Returns:
            HttpResponse or None
        """
        # Only apply to downloads URLs
        if not request.path.startswith('/downloads/'):
            return None
        
        # Check if path is exempt
        for exempt_path in self.EXEMPT_PATHS:
            if request.path.startswith(exempt_path):
                return None
        
        # Get client IP
        client_ip = RequestValidator.get_client_ip(request)
        
        # 1. Check IP blacklist
        if IPBlacklistManager.is_blacklisted(client_ip):
            blacklist_info = IPBlacklistManager.get_blacklist_info(client_ip)
            reason = blacklist_info.get('reason', 'Security violation') if blacklist_info else 'Security violation'
            
            logger.warning(
                f"Blocked blacklisted IP: {client_ip} "
                f"on {request.path}. Reason: {reason}"
            )
            
            SecurityAuditEnhancedLogger.log_event(
                'BLACKLIST_BLOCK',
                request.user if request.user.is_authenticated else 'Anonymous',
                client_ip,
                {
                    'path': request.path,
                    'reason': reason
                },
                'WARNING'
            )
            
            return self._render_error_page(
                request,
                title="Access Denied",
                message="Your IP address has been temporarily blocked due to security reasons.",
                status_code=403
            )
        
        # 2. Check rate limit for download endpoints
        if '/download/' in request.path or '/bulk-download/' in request.path:
            # Determine identifier (user ID or IP)
            identifier = (
                str(request.user.id)
                if request.user.is_authenticated
                else client_ip
            )
            
            # Determine action type
            action = 'bulk_download' if '/bulk-download/' in request.path else 'download'
            
            # Check rate limit
            allowed, count, reset_time = RateLimitManager.check_rate_limit(
                identifier,
                action=action
            )
            
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for {identifier} on {action}. "
                    f"Count: {count}, Reset in: {reset_time}s"
                )
                
                SecurityAuditEnhancedLogger.log_rate_limit_exceeded(
                    identifier,
                    client_ip,
                    action,
                    count
                )
                
                # Calculate minutes for user-friendly message
                reset_minutes = max(1, reset_time // 60)
                
                return self._render_error_page(
                    request,
                    title="Rate Limit Exceeded",
                    message=f"You have exceeded the download limit. Please try again in {reset_minutes} minute(s).",
                    status_code=429
                )
        
        # 3. Request validation (placeholder for future)
        if not RequestValidator.validate_request_signature(request):
            logger.error(f"Invalid request signature from {client_ip}")
            return HttpResponseForbidden("Invalid request")
        
        return None
    
    def _render_error_page(self, request, title, message, status_code):
        """
        Render a user-friendly error page.
        
        Args:
            request: HttpRequest object
            title: Error title
            message: Error message
            status_code: HTTP status code
            
        Returns:
            HttpResponse
        """
        context = {
            'title': title,
            'message': message,
            'status_code': status_code
        }
        
        # Try to render template, fallback to simple response
        try:
            return render(
                request,
                'downloads/error.html',
                context,
                status=status_code
            )
        except Exception:
            # Fallback to simple HTML
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 600px;
                        margin: 100px auto;
                        padding: 20px;
                        text-align: center;
                    }}
                    h1 {{ color: #d32f2f; }}
                    p {{ color: #666; line-height: 1.6; }}
                </style>
            </head>
            <body>
                <h1>{title}</h1>
                <p>{message}</p>
                <p><a href="/downloads/">← Back to Downloads</a></p>
            </body>
            </html>
            """
            return HttpResponse(html, status=status_code)


# ============================================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================================

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds security headers to responses.
    
    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: (restrictive)
    """
    
    HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }
    
    def process_response(self, request, response):
        """
        Add security headers to response.
        
        Args:
            request: HttpRequest object
            response: HttpResponse object
            
        Returns:
            HttpResponse with added headers
        """
        # Only apply to downloads app responses
        if request.path.startswith('/downloads/'):
            for header, value in self.HEADERS.items():
                # Don't override existing headers
                if header not in response:
                    response[header] = value
        
        return response


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'DownloadsSecurityMiddleware',
    'SecurityHeadersMiddleware',
]
