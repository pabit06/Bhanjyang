"""
Shared Security Module for Bhanjyang Project

This module provides reusable security features for all Django apps.
It extracts the best security practices from news_events app and makes
them available project-wide.

Usage:
    from apps.shared_security import (
        IPBlacklistManager,
        HoneypotProtection,
        FileUploadSecurity,
        SecurityHeadersManager,
        SessionSecurityManager
    )
"""

import hashlib
import hmac
import re
import mimetypes
from datetime import timedelta
from typing import Dict, Any, Optional, List, Tuple
from django.core.cache import cache
from django.core.exceptions import ValidationError, PermissionDenied
from django.conf import settings
from django.utils import timezone
from django.http import HttpRequest
import logging

logger = logging.getLogger(__name__)

# Security Constants
MAX_FILE_SIZE = getattr(settings, 'MAX_FILE_SIZE', 5 * 1024 * 1024)  # 5MB default
ALLOWED_IMAGE_TYPES = getattr(settings, 'ALLOWED_IMAGE_TYPES', [
    'image/jpeg', 'image/png', 'image/webp', 'image/gif'
])
ALLOWED_FILE_EXTENSIONS = getattr(settings, 'ALLOWED_FILE_EXTENSIONS', [
    '.jpg', '.jpeg', '.png', '.webp', '.gif', '.pdf', '.doc', '.docx'
])
IP_BLACKLIST_DURATION = getattr(settings, 'IP_BLACKLIST_DURATION', 86400)  # 24 hours
HONEYPOT_FIELD_NAME = getattr(settings, 'HONEYPOT_FIELD_NAME', 'website')
MAX_REQUEST_SIZE = getattr(settings, 'MAX_REQUEST_SIZE', 10 * 1024 * 1024)  # 10MB
MAX_VIOLATION_THRESHOLD = getattr(settings, 'MAX_VIOLATION_THRESHOLD', 5)


class IPBlacklistManager:
    """
    IP blacklist management for all apps
    
    Features:
    - Dynamic IP blacklisting
    - Violation tracking
    - Auto-blacklisting
    - Manual whitelist/blacklist
    """
    
    @staticmethod
    def add_to_blacklist(ip_address: str, reason: str, duration: int = None) -> None:
        """Add IP to blacklist"""
        if duration is None:
            duration = IP_BLACKLIST_DURATION
        
        cache_key = f"blacklist_ip_{ip_address}"
        blacklist_data = {
            'ip': ip_address,
            'reason': reason,
            'blacklisted_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(seconds=duration)).isoformat()
        }
        cache.set(cache_key, blacklist_data, duration)
        logger.warning(f"[SECURITY] IP blacklisted: {ip_address} - Reason: {reason}")
    
    @staticmethod
    def is_blacklisted(ip_address: str) -> Tuple[bool, Optional[str]]:
        """Check if IP is blacklisted"""
        cache_key = f"blacklist_ip_{ip_address}"
        blacklist_data = cache.get(cache_key)
        if blacklist_data:
            return True, blacklist_data.get('reason', 'Unknown')
        return False, None
    
    @staticmethod
    def remove_from_blacklist(ip_address: str) -> None:
        """Remove IP from blacklist"""
        cache_key = f"blacklist_ip_{ip_address}"
        cache.delete(cache_key)
        logger.info(f"[SECURITY] IP removed from blacklist: {ip_address}")
    
    @staticmethod
    def get_violation_count(ip_address: str) -> int:
        """Get violation count for IP"""
        cache_key = f"violations_{ip_address}"
        return cache.get(cache_key, 0)
    
    @staticmethod
    def record_violation(ip_address: str, violation_type: str) -> int:
        """Record security violation and auto-blacklist if threshold reached"""
        cache_key = f"violations_{ip_address}"
        violations = cache.get(cache_key, 0) + 1
        cache.set(cache_key, violations, 3600)  # 1 hour window
        
        logger.warning(
            f"[SECURITY] Violation recorded: IP={ip_address}, "
            f"Type={violation_type}, Count={violations}"
        )
        
        # Auto-blacklist after threshold
        if violations >= MAX_VIOLATION_THRESHOLD:
            IPBlacklistManager.add_to_blacklist(
                ip_address,
                f"Auto-blacklisted: {violations} violations ({violation_type})"
            )
        
        return violations


class HoneypotProtection:
    """
    Honeypot field protection for form spam prevention
    
    Usage:
        @honeypot_protected
        def my_view(request):
            ...
    """
    
    @staticmethod
    def validate_honeypot(request: HttpRequest, field_name: str = None) -> bool:
        """Check if honeypot field was filled (bot detected)"""
        if field_name is None:
            field_name = HONEYPOT_FIELD_NAME
        
        honeypot_value = request.POST.get(field_name, '')
        if honeypot_value:
            ip_address = get_client_ip(request)
            IPBlacklistManager.record_violation(ip_address, 'honeypot_filled')
            logger.warning(f"[SECURITY] Honeypot triggered: IP={ip_address}")
            return False
        return True
    
    @staticmethod
    def get_honeypot_field_html(field_name: str = None) -> str:
        """Generate honeypot field HTML"""
        if field_name is None:
            field_name = HONEYPOT_FIELD_NAME
        
        return f'''
        <div class="hidden" style="position:absolute;left:-5000px;" aria-hidden="true">
            <label for="id_{field_name}">Leave this field blank</label>
            <input type="text" name="{field_name}" id="id_{field_name}" 
                   tabindex="-1" autocomplete="off">
        </div>
        '''


class FileUploadSecurity:
    """
    File upload security validation
    
    Features:
    - Size validation
    - MIME type checking
    - Extension whitelisting
    - Content scanning
    - Filename sanitization
    """
    
    @staticmethod
    def validate_file_upload(
        uploaded_file,
        allowed_types: List[str] = None,
        max_size: int = None
    ) -> Dict[str, Any]:
        """Comprehensive file upload validation"""
        if allowed_types is None:
            allowed_types = ALLOWED_IMAGE_TYPES
        if max_size is None:
            max_size = MAX_FILE_SIZE
        
        errors = []
        
        # File size check
        if uploaded_file.size > max_size:
            errors.append(
                f"File size ({uploaded_file.size} bytes) exceeds "
                f"maximum allowed ({max_size} bytes)"
            )
        
        # File extension check
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if f'.{file_extension}' not in ALLOWED_FILE_EXTENSIONS:
            errors.append(f"File extension '.{file_extension}' not allowed")
        
        # MIME type check
        content_type = uploaded_file.content_type
        if content_type not in allowed_types:
            errors.append(f"File type '{content_type}' not allowed")
        
        # Content scanning for dangerous patterns
        dangerous_patterns = [
            b'<?php', b'<script', b'<%', b'#!/'
        ]
        
        try:
            file_content = uploaded_file.read(1024)
            uploaded_file.seek(0)
            
            for pattern in dangerous_patterns:
                if pattern in file_content:
                    errors.append("File contains potentially dangerous content")
                    logger.warning(
                        f"[SECURITY] Dangerous content detected in file: "
                        f"{uploaded_file.name}"
                    )
                    break
        except Exception as e:
            logger.error(f"[SECURITY] Error scanning file: {e}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'file_info': {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'content_type': content_type,
                'extension': file_extension
            }
        }
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize uploaded filename"""
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove special characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Replace spaces with underscores
        filename = re.sub(r'\s+', '_', filename)
        
        # Limit length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:95] + (f'.{ext}' if ext else '')
        
        return filename


class SecurityHeadersManager:
    """
    Security headers management
    
    Automatically applies security headers to responses
    """
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://www.googletagmanager.com https://www.google-analytics.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://www.google-analytics.com https://analytics.google.com https://stats.g.doubleclick.net; "
                "frame-src https://www.google.com; "
                "frame-ancestors 'self';"
            ),
        }
    
    @staticmethod
    def apply_security_headers(response):
        """Apply security headers to response"""
        headers = SecurityHeadersManager.get_security_headers()
        for header, value in headers.items():
            response[header] = value
        return response


class SessionSecurityManager:
    """
    Enhanced session security
    
    Features:
    - User agent validation
    - Activity timeout
    - Session integrity checks
    """
    
    @staticmethod
    def validate_session_integrity(request: HttpRequest) -> bool:
        """Validate session integrity"""
        if not request.user.is_authenticated:
            return True
        
        session = request.session
        current_user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check user agent consistency
        stored_user_agent = session.get('_auth_user_agent')
        if stored_user_agent is None:
            session['_auth_user_agent'] = current_user_agent
        elif stored_user_agent != current_user_agent:
            logger.warning(
                f"[SECURITY] User agent mismatch for user {request.user.id}"
            )
            return False
        
        # Update last activity
        session['_last_activity'] = timezone.now().isoformat()
        
        return True
    
    @staticmethod
    def check_session_timeout(
        request: HttpRequest,
        timeout_minutes: int = 30
    ) -> bool:
        """Check if session has timed out"""
        if not request.user.is_authenticated:
            return True
        
        last_activity = request.session.get('_last_activity')
        if not last_activity:
            request.session['_last_activity'] = timezone.now().isoformat()
            return True
        
        try:
            from django.utils.dateparse import parse_datetime
            last_activity_time = parse_datetime(last_activity)
            if timezone.now() - last_activity_time > timedelta(minutes=timeout_minutes):
                logger.info(f"[SECURITY] Session timeout for user {request.user.id}")
                return False
        except (ValueError, TypeError):
            pass
        
        request.session['_last_activity'] = timezone.now().isoformat()
        return True


# Utility Functions

def get_client_ip(request: HttpRequest) -> str:
    """Get client IP address from request (handles proxies)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def log_security_event(
    event_type: str,
    details: Dict[str, Any],
    request: Optional[HttpRequest] = None
):
    """Log security events"""
    event_data = {
        'timestamp': timestamp timezone.now().isoformat(),
        'event_type': event_type,
        'details': details
    }
    
    if request:
        event_data.update({
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'user_id': request.user.id if request.user.is_authenticated else None,
            'path': request.path,
            'method': request.method
        })
    
    logger.warning(f"[SECURITY EVENT] {event_type}: {event_data}")
    
    # Store in cache for monitoring
    cache_key = f"security_events_{timezone.now().strftime('%Y%m%d')}"
    events = cache.get(cache_key, [])
    events.append(event_data)
    cache.set(cache_key, events, 86400)


# Decorators

def honeypot_protected(func):
    """Decorator to protect views with honeypot"""
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.method == 'POST':
            if not HoneypotProtection.validate_honeypot(request):
                raise ValidationError("Invalid form submission")
        return func(request, *args, **kwargs)
    return wrapper


def check_request_security(func):
    """Decorator to check request security"""
    def wrapper(request: HttpRequest, *args, **kwargs):
        ip_address = get_client_ip(request)
        
        # Check IP blacklist
        is_blacklisted, reason = IPBlacklistManager.is_blacklisted(ip_address)
        if is_blacklisted:
            log_security_event(
                'blocked_blacklisted_ip',
                {'ip': ip_address, 'reason': reason},
                request
            )
            raise PermissionDenied("Access denied")
        
        # Check session integrity
        if request.user.is_authenticated:
            if not SessionSecurityManager.validate_session_integrity(request):
                raise PermissionDenied("Session validation failed")
        
        return func(request, *args, **kwargs)
    
    return wrapper
