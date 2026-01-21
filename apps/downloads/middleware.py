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
from typing import Optional
from django.http import HttpResponseForbidden, HttpResponse, HttpRequest, HttpResponseBase
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render

from .security_enhanced import (
    IPBlacklistManager,
    RateLimitManager,
    SecurityAuditEnhancedLogger,
    RequestValidator
)
from .utils.error_codes import DownloadsErrorCodes, get_user_friendly_message
from .utils.helpers import get_client_ip

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
        client_ip = get_client_ip(request)
        
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
                    'reason': reason,
                    'error_code': DownloadsErrorCodes.IP_BLACKLISTED
                },
                'WARNING'
            )
            
            return self._render_error_page(
                request,
                title="Access Denied",
                message=get_user_friendly_message(DownloadsErrorCodes.IP_BLACKLISTED),
                status_code=403,
                error_code=DownloadsErrorCodes.IP_BLACKLISTED
            )
        
        # 2. Check rate limit for download endpoints (per-user and per-IP)
        if '/download/' in request.path or '/bulk-download/' in request.path:
            # Determine identifiers (both user ID and IP for comprehensive rate limiting)
            user_identifier = (
                str(request.user.id)
                if request.user.is_authenticated
                else None
            )
            ip_identifier = client_ip
            
            # Determine action type
            action = 'bulk_download' if '/bulk-download/' in request.path else 'download'
            
            # Check rate limit for user (if authenticated)
            if user_identifier:
                user_allowed, user_count, user_reset_time = RateLimitManager.check_rate_limit(
                    user_identifier,
                    action=f'{action}_user'
                )
                if not user_allowed:
                    logger.warning(
                        f"Rate limit exceeded for user {user_identifier} on {action}. "
                        f"Count: {user_count}, Reset in: {user_reset_time}s"
                    )
                    SecurityAuditEnhancedLogger.log_rate_limit_exceeded(
                        user_identifier,
                        client_ip,
                        action,
                        user_count
                    )
                    reset_minutes = max(1, user_reset_time // 60)
                    return self._render_error_page(
                        request,
                        title="Rate Limit Exceeded",
                        message=get_user_friendly_message(DownloadsErrorCodes.RATE_LIMIT_EXCEEDED),
                        status_code=429,
                        error_code=DownloadsErrorCodes.RATE_LIMIT_EXCEEDED
                    )
            
            # Check rate limit for IP (always check)
            ip_allowed, ip_count, ip_reset_time = RateLimitManager.check_rate_limit(
                ip_identifier,
                action=action
            )
            if not ip_allowed:
                logger.warning(
                    f"Rate limit exceeded for IP {ip_identifier} on {action}. "
                    f"Count: {ip_count}, Reset in: {ip_reset_time}s"
                )
                SecurityAuditEnhancedLogger.log_rate_limit_exceeded(
                    ip_identifier,
                    client_ip,
                    action,
                    ip_count
                )
                reset_minutes = max(1, ip_reset_time // 60)
                return self._render_error_page(
                    request,
                    title="Rate Limit Exceeded",
                    message=get_user_friendly_message(DownloadsErrorCodes.RATE_LIMIT_EXCEEDED),
                    status_code=429,
                    error_code=DownloadsErrorCodes.RATE_LIMIT_EXCEEDED
                )
        
        # 3. Request validation (placeholder for future)
        if not RequestValidator.validate_request_signature(request):
            logger.error(f"Invalid request signature from {client_ip}")
            return HttpResponseForbidden("Invalid request")
        
        return None
    
    def _render_error_page(
        self,
        request: HttpRequest,
        title: str,
        message: str,
        status_code: int,
        error_code: Optional[str] = None
    ) -> HttpResponse:
        """
        Render a user-friendly error page.
        
        Args:
            request: HttpRequest object
            title: Error title
            message: Error message
            status_code: HTTP status code
            error_code: Optional error code for logging
            
        Returns:
            HttpResponse
        """
        context = {
            'title': title,
            'message': message,
            'status_code': status_code,
            'error_code': error_code
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
    Adds security headers to responses including Content Security Policy (CSP).
    
    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: (restrictive)
    - Content-Security-Policy: (CSP policy for downloads)
    """
    
    HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }
    
    # Content Security Policy for downloads pages
    # Allows necessary external resources (CDN, fonts) while maintaining security
    # Note: frame-src includes 'self' to allow same-origin iframes for PDF previews
    CSP_POLICY = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "https://cdnjs.cloudflare.com https://unpkg.com https://cdn.jsdelivr.net "
        "https://www.googletagmanager.com https://www.google-analytics.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://unpkg.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
        "img-src 'self' data: https: blob:; "
        "connect-src 'self' https://www.google-analytics.com https://analytics.google.com https://stats.g.doubleclick.net; "
        "frame-src 'self' https://www.google.com https://maps.google.com https://maps.googleapis.com; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none';"
    )
    
    def process_response(
        self,
        request: HttpRequest,
        response: HttpResponseBase
    ) -> HttpResponseBase:
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
            # Add standard security headers
            for header, value in self.HEADERS.items():
                # Don't override existing headers
                if header not in response:
                    response[header] = value
            
            # Add Content Security Policy header
            if 'Content-Security-Policy' not in response:
                response['Content-Security-Policy'] = self.CSP_POLICY
        
        return response


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'DownloadsSecurityMiddleware',
    'SecurityHeadersMiddleware',
]
