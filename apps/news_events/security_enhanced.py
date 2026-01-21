"""
Enhanced Security Module for News Events App
Additional security layers beyond the existing security.py

This module adds:
- IP-based blacklisting
- Honeypot field protection
- Advanced CSRF validation
- File upload security
- Request signature validation
- Security headers management
- Captcha integration support
- Session security
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

# Enhanced Security Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.pdf', '.doc', '.docx']
IP_BLACKLIST_DURATION = 86400  # 24 hours
HONEYPOT_FIELD_NAME = 'website'  # Common honeypot field
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB


class IPBlacklistManager:
    """
    Manage IP-based blacklisting for malicious actors
    """
    
    @staticmethod
    def add_to_blacklist(ip_address: str, reason: str, duration: int = IP_BLACKLIST_DURATION) -> None:
        """
        Add an IP address to the blacklist
        
        Args:
            ip_address: IP address to blacklist
            reason: Reason for blacklisting
            duration: Duration in seconds (default 24 hours)
        """
        cache_key = f"blacklist_ip_{ip_address}"
        blacklist_data = {
            'ip': ip_address,
            'reason': reason,
            'blacklisted_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(seconds=duration)).isoformat()
        }
        cache.set(cache_key, blacklist_data, duration)
        logger.warning(f"IP blacklisted: {ip_address} - Reason: {reason}")
    
    @staticmethod
    def is_blacklisted(ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if an IP address is blacklisted
        
        Returns:
            Tuple of (is_blacklisted, reason)
        """
        cache_key = f"blacklist_ip_{ip_address}"
        blacklist_data = cache.get(cache_key)
        if blacklist_data:
            return True, blacklist_data.get('reason', 'Unknown')
        return False, None
    
    @staticmethod
    def remove_from_blacklist(ip_address: str) -> None:
        """Remove an IP from blacklist"""
        cache_key = f"blacklist_ip_{ip_address}"
        cache.delete(cache_key)
        logger.info(f"IP removed from blacklist: {ip_address}")
    
    @staticmethod
    def get_violation_count(ip_address: str) -> int:
        """Get violation count for an IP"""
        cache_key = f"violations_{ip_address}"
        return cache.get(cache_key, 0)
    
    @staticmethod
    def record_violation(ip_address: str, violation_type: str) -> int:
        """
        Record a security violation for an IP
        
        Returns:
            Total violation count
        """
        cache_key = f"violations_{ip_address}"
        violations = cache.get(cache_key, 0) + 1
        cache.set(cache_key, violations, 3600)  # 1 hour
        
        logger.warning(f"Security violation recorded: {ip_address} - Type: {violation_type} - Count: {violations}")
        
        # Auto-blacklist after 5 violations
        if violations >= 5:
            IPBlacklistManager.add_to_blacklist(
                ip_address, 
                f"Auto-blacklisted: {violations} violations ({violation_type})"
            )
        
        return violations


class HoneypotProtection:
    """
    Honeypot field protection against spam bots
    """
    
    @staticmethod
    def validate_honeypot(request: HttpRequest, field_name: str = HONEYPOT_FIELD_NAME) -> bool:
        """
        Check if honeypot field was filled (indicates bot)
        
        Args:
            request: HTTP request object
            field_name: Name of honeypot field
            
        Returns:
            True if valid (field empty), False if bot detected
        """
        honeypot_value = request.POST.get(field_name, '')
        if honeypot_value:
            ip_address = request.META.get('REMOTE_ADDR', 'unknown')
            IPBlacklistManager.record_violation(ip_address, 'honeypot_filled')
            logger.warning(f"Honeypot triggered by IP: {ip_address}")
            return False
        return True
    
    @staticmethod
    def add_honeypot_to_form(form_html: str, field_name: str = HONEYPOT_FIELD_NAME) -> str:
        """
        Add invisible honeypot field to form HTML
        
        Args:
            form_html: Original form HTML
            field_name: Name of honeypot field
            
        Returns:
            Form HTML with honeypot field added
        """
        honeypot_field = f'''
        <div class="hidden" style="position:absolute;left:-5000px;" aria-hidden="true">
            <label for="id_{field_name}">Leave this field blank</label>
            <input type="text" name="{field_name}" id="id_{field_name}" tabindex="-1" autocomplete="off">
        </div>
        '''
        return form_html + honeypot_field


class FileUploadSecurity:
    """
    Enhanced file upload security validation
    """
    
    @staticmethod
    def validate_file_upload(uploaded_file, allowed_types: List[str] = None, max_size: int = MAX_FILE_SIZE) -> Dict[str, Any]:
        """
        Comprehensive file upload validation
        
        Args:
            uploaded_file: Django UploadedFile object
            allowed_types: List of allowed MIME types
            max_size: Maximum file size in bytes
            
        Returns:
            Validation result dictionary
        """
        if allowed_types is None:
            allowed_types = ALLOWED_IMAGE_TYPES
        
        errors = []
        
        # Check file size
        if uploaded_file.size > max_size:
            errors.append(f"File size ({uploaded_file.size} bytes) exceeds maximum allowed ({max_size} bytes)")
        
        # Check file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if f'.{file_extension}' not in ALLOWED_FILE_EXTENSIONS:
            errors.append(f"File extension '.{file_extension}' not allowed")
        
        # Check MIME type
        content_type = uploaded_file.content_type
        if content_type not in allowed_types:
            errors.append(f"File type '{content_type}' not allowed")
        
        # Validate file content matches extension
        try:
            guessed_type = mimetypes.guess_type(uploaded_file.name)[0]
            if guessed_type and guessed_type != content_type:
                logger.warning(f"MIME type mismatch: declared={content_type}, guessed={guessed_type}")
        except Exception as e:
            logger.error(f"Error validating file type: {e}")
        
        # Check for executable content (basic check)
        dangerous_patterns = [
            b'<?php',  # PHP code
            b'<script',  # JavaScript
            b'<%',  # ASP/JSP
            b'#!/',  # Shebang
        ]
        
        try:
            file_content = uploaded_file.read(1024)  # Read first 1KB
            uploaded_file.seek(0)  # Reset file pointer
            
            for pattern in dangerous_patterns:
                if pattern in file_content:
                    errors.append("File contains potentially dangerous content")
                    break
        except Exception as e:
            logger.error(f"Error scanning file content: {e}")
        
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
        """
        Sanitize uploaded filename
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove special characters except dots and underscores
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Replace multiple spaces with single underscore
        filename = re.sub(r'\s+', '_', filename)
        
        # Limit length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:95] + (f'.{ext}' if ext else '')
        
        return filename


class RequestSignatureValidator:
    """
    Validate request signatures for sensitive operations
    """
    
    @staticmethod
    def generate_signature(data: str, secret_key: Optional[str] = None) -> str:
        """
        Generate HMAC signature for data
        
        Args:
            data: Data to sign
            secret_key: Secret key for signing (uses Django SECRET_KEY if not provided)
            
        Returns:
            Hex-encoded signature
        """
        if secret_key is None:
            secret_key = settings.SECRET_KEY
        
        signature = hmac.new(
            secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    @staticmethod
    def validate_signature(data: str, provided_signature: str, secret_key: Optional[str] = None) -> bool:
        """
        Validate request signature
        
        Args:
            data: Original data
            provided_signature: Signature to validate
            secret_key: Secret key used for signing
            
        Returns:
            True if signature is valid
        """
        expected_signature = RequestSignatureValidator.generate_signature(data, secret_key)
        return hmac.compare_digest(expected_signature, provided_signature)
    
    @staticmethod
    def sign_request_data(request_data: Dict[str, Any]) -> str:
        """
        Generate signature for request data
        
        Args:
            request_data: Dictionary of request data
            
        Returns:
            Signature string
        """
        # Sort keys for consistent signatures
        sorted_data = '&'.join([f"{k}={v}" for k, v in sorted(request_data.items())])
        return RequestSignatureValidator.generate_signature(sorted_data)


class SecurityHeadersManager:
    """
    Manage security headers for responses
    """
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Get recommended security headers
        
        Returns:
            Dictionary of security headers
        """
        return {
            # Prevent clickjacking
            'X-Frame-Options': 'SAMEORIGIN',
            
            # Prevent MIME type sniffing
            'X-Content-Type-Options': 'nosniff',
            
            # Enable XSS protection
            'X-XSS-Protection': '1; mode=block',
            
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Permissions policy
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            
            # Content Security Policy
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.googletagmanager.com https://www.google-analytics.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://www.google-analytics.com https://analytics.google.com https://stats.g.doubleclick.net; "
                "frame-src https://www.google.com; "
                "frame-ancestors 'self';"
            ),
            
            # Strict Transport Security (HTTPS only)
            # 'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        }
    
    @staticmethod
    def apply_security_headers(response):
        """
        Apply security headers to response
        
        Args:
            response: Django HttpResponse object
            
        Returns:
            Response with security headers applied
        """
        headers = SecurityHeadersManager.get_security_headers()
        for header, value in headers.items():
            response[header] = value
        return response


class SessionSecurityManager:
    """
    Enhanced session security
    """
    
    @staticmethod
    def validate_session_integrity(request: HttpRequest) -> bool:
        """
        Validate session integrity
        
        Checks for:
        - User agent consistency
        - IP address consistency (optional)
        
        Args:
            request: HTTP request object
            
        Returns:
            True if session is valid
        """
        if not request.user.is_authenticated:
            return True  # Skip for anonymous users
        
        session = request.session
        current_user_agent = request.META.get('HTTP_USER_AGENT', '')
        current_ip = request.META.get('REMOTE_ADDR', '')
        
        # Check user agent consistency
        stored_user_agent = session.get('_auth_user_agent')
        if stored_user_agent is None:
            session['_auth_user_agent'] = current_user_agent
        elif stored_user_agent != current_user_agent:
            logger.warning(f"User agent mismatch for user {request.user.id}")
            return False
        
        # Optional: Check IP consistency (can be problematic with mobile users)
        # stored_ip = session.get('_auth_ip')
        # if stored_ip and stored_ip != current_ip:
        #     logger.warning(f"IP change detected for user {request.user.id}")
        #     return False
        
        # Update last activity
        session['_last_activity'] = timezone.now().isoformat()
        
        return True
    
    @staticmethod
    def check_session_timeout(request: HttpRequest, timeout_minutes: int = 30) -> bool:
        """
        Check if session has timed out due to inactivity
        
        Args:
            request: HTTP request object
            timeout_minutes: Timeout in minutes
            
        Returns:
            True if session is still valid
        """
        if not request.user.is_authenticated:
            return True
        
        last_activity = request.session.get('_last_activity')
        if not last_activity:
            request.session['_last_activity'] = timezone.now().isoformat()
            return True
        
        try:
            last_activity_time = timezone.datetime.fromisoformat(last_activity)
            if timezone.now() - last_activity_time > timedelta(minutes=timeout_minutes):
                logger.info(f"Session timeout for user {request.user.id}")
                return False
        except (ValueError, TypeError):
            pass
        
        request.session['_last_activity'] = timezone.now().isoformat()
        return True


class CSRFEnhancedValidator:
    """
    Enhanced CSRF validation for AJAX requests
    """
    
    @staticmethod
    def validate_csrf_for_ajax(request: HttpRequest) -> bool:
        """
        Validate CSRF token for AJAX requests
        
        Args:
            request: HTTP request object
            
        Returns:
            True if CSRF token is valid
        """
        # Django handles CSRF automatically, but we can add extra checks
        csrf_token = request.META.get('HTTP_X_CSRFTOKEN') or request.POST.get('csrfmiddlewaretoken')
        
        if not csrf_token:
            logger.warning(f"Missing CSRF token in AJAX request from {request.META.get('REMOTE_ADDR')}")
            return False
        
        # Additional validation can be added here
        return True
    
    @staticmethod
    def generate_ajax_csrf_token(request: HttpRequest) -> str:
        """
        Generate CSRF token for AJAX requests
        
        Args:
            request: HTTP request object
            
        Returns:
            CSRF token string
        """
        from django.middleware.csrf import get_token
        return get_token(request)


# Security Middleware Functions

def check_request_security(func):
    """
    Decorator to check request security before processing
    
    Checks:
    - IP blacklist
    - Request size
    - Session integrity
    """
    def wrapper(request: HttpRequest, *args, **kwargs):
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Check IP blacklist
        is_blacklisted, reason = IPBlacklistManager.is_blacklisted(ip_address)
        if is_blacklisted:
            logger.warning(f"Blocked request from blacklisted IP: {ip_address} - Reason: {reason}")
            raise PermissionDenied("Access denied")
        
        # Check request size
        content_length = request.META.get('CONTENT_LENGTH', 0)
        try:
            content_length = int(content_length)
            if content_length > MAX_REQUEST_SIZE:
                IPBlacklistManager.record_violation(ip_address, 'oversized_request')
                raise ValidationError(f"Request too large: {content_length} bytes")
        except (ValueError, TypeError):
            pass
        
        # Check session integrity for authenticated users
        if request.user.is_authenticated:
            if not SessionSecurityManager.validate_session_integrity(request):
                logger.warning(f"Session integrity check failed for user {request.user.id}")
                raise PermissionDenied("Session validation failed")
        
        return func(request, *args, **kwargs)
    
    return wrapper


def honeypot_protected(func):
    """
    Decorator to protect forms with honeypot
    """
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.method == 'POST':
            if not HoneypotProtection.validate_honeypot(request):
                raise ValidationError("Invalid form submission")
        return func(request, *args, **kwargs)
    
    return wrapper


# Utility functions

def log_security_event(event_type: str, details: Dict[str, Any], request: Optional[HttpRequest] = None):
    """
    Log security events for monitoring
    
    Args:
        event_type: Type of security event
        details: Event details
        request: HTTP request object (optional)
    """
    event_data = {
        'timestamp': timezone.now().isoformat(),
        'event_type': event_type,
        'details': details
    }
    
    if request:
        event_data.update({
            'ip_address': request.META.get('REMOTE_ADDR', 'unknown'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'user_id': request.user.id if request.user.is_authenticated else None,
            'path': request.path,
            'method': request.method
        })
    
    logger.warning(f"Security Event: {event_type} - {event_data}")
    
    # Store in cache for monitoring dashboard
    cache_key = f"security_events_{timezone.now().strftime('%Y%m%d')}"
    events = cache.get(cache_key, [])
    events.append(event_data)
    cache.set(cache_key, events, 86400)  # 24 hours


def get_recent_security_events(days: int = 1) -> List[Dict[str, Any]]:
    """
    Get recent security events for monitoring
    
    Args:
        days: Number of days to retrieve
        
    Returns:
        List of security events
    """
    all_events = []
    for i in range(days):
        date = (timezone.now() - timedelta(days=i)).strftime('%Y%m%d')
        cache_key = f"security_events_{date}"
        events = cache.get(cache_key, [])
        all_events.extend(events)
    
    return all_events
