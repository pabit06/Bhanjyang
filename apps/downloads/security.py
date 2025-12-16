"""
Downloads Security Module
Enhanced security features for file uploads and downloads
"""

import os
import hashlib
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils import timezone
# from django_ratelimit.decorators import ratelimit  # Commented out until installed
# from django_ratelimit.exceptions import Ratelimited  # Commented out until installed
import logging

# Try to import magic, fallback to Django's content type detection
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logging.getLogger(__name__).warning("python-magic not available, using Django's content type detection")

logger = logging.getLogger(__name__)

# Security constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
}

DANGEROUS_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.php', '.asp', '.aspx', '.jsp', '.py', '.rb', '.pl', '.sh', '.ps1'
}

SUSPICIOUS_PATTERNS = [
    b'<script', b'javascript:', b'vbscript:', b'onload=', b'onerror=',
    b'eval(', b'exec(', b'system(', b'shell_exec('
]


class FileSecurityValidator:
    """Enhanced file security validation"""
    
    @staticmethod
    def validate_file_security(file):
        """Comprehensive file security validation"""
        try:
            # Check file size
            if file.size > MAX_FILE_SIZE:
                raise ValidationError(f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB")
            
            # Check file extension
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension in DANGEROUS_EXTENSIONS:
                raise ValidationError(f"Dangerous file type '{file_extension}' is not allowed")
            
            # Check MIME type
            file_mime_type = FileSecurityValidator.get_mime_type(file)
            if file_mime_type not in ALLOWED_MIME_TYPES:
                raise ValidationError(f"File type '{file_mime_type}' is not allowed")
            
            # Check for suspicious content
            FileSecurityValidator.scan_file_content(file)
            
            # Generate file hash for tracking
            file_hash = FileSecurityValidator.generate_file_hash(file)
            
            return {
                'mime_type': file_mime_type,
                'file_hash': file_hash,
                'size': file.size,
                'extension': file_extension
            }
            
        except Exception as e:
            logger.warning(f"File security validation failed: {e}")
            raise ValidationError(f"File security validation failed: {str(e)}")
    
    @staticmethod
    def get_mime_type(file):
        """Get MIME type using python-magic or fallback to Django's content type detection"""
        try:
            if MAGIC_AVAILABLE:
                # Reset file pointer
                file.seek(0)
                mime_type = magic.from_buffer(file.read(1024), mime=True)
                file.seek(0)  # Reset again
                return mime_type
            else:
                # Fallback to Django's content type detection
                if hasattr(file, 'content_type') and file.content_type:
                    return file.content_type
                # If no content_type, try to detect from file extension
                if hasattr(file, 'name') and file.name:
                    import mimetypes
                    mime_type, _ = mimetypes.guess_type(file.name)
                    return mime_type or 'application/octet-stream'
                return 'application/octet-stream'
        except Exception:
            # Fallback to Django's content type detection
            if hasattr(file, 'content_type') and file.content_type:
                return file.content_type
            return 'application/octet-stream'
    
    @staticmethod
    def scan_file_content(file):
        """Scan file content for suspicious patterns"""
        try:
            file.seek(0)
            content = file.read(1024)  # Read first 1KB
            
            for pattern in SUSPICIOUS_PATTERNS:
                if pattern in content.lower():
                    raise ValidationError("File contains suspicious content patterns")
            
            file.seek(0)  # Reset file pointer
        except Exception as e:
            logger.warning(f"Content scanning failed: {e}")
            raise ValidationError("Unable to scan file content")
    
    @staticmethod
    def generate_file_hash(file):
        """Generate SHA-256 hash of file content"""
        try:
            file.seek(0)
            file_hash = hashlib.sha256(file.read()).hexdigest()
            file.seek(0)
            return file_hash
        except Exception:
            return None


class DownloadRateLimiter:
    """Rate limiting for downloads"""
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def check_download_rate_limit(request, file_id):
        """Check if user has exceeded download rate limit"""
        ip = DownloadRateLimiter.get_client_ip(request)
        cache_key = f"download_rate_limit_{ip}_{file_id}"
        
        # Allow 5 downloads per hour per file per IP
        downloads_count = cache.get(cache_key, 0)
        
        if downloads_count >= 5:
            logger.warning(f"Download rate limit exceeded for IP {ip}, file {file_id}")
            raise Ratelimited("Download rate limit exceeded. Please try again later.")
        
        # Increment counter
        cache.set(cache_key, downloads_count + 1, 3600)  # 1 hour expiry
    
    @staticmethod
    def check_bulk_download_limit(request):
        """Check bulk download limits"""
        ip = DownloadRateLimiter.get_client_ip(request)
        cache_key = f"bulk_download_limit_{ip}"
        
        bulk_downloads = cache.get(cache_key, 0)
        
        if bulk_downloads >= 3:  # Max 3 bulk downloads per day
            logger.warning(f"Bulk download limit exceeded for IP {ip}")
            raise Ratelimited("Bulk download limit exceeded. Please try again tomorrow.")
        
        cache.set(cache_key, bulk_downloads + 1, 86400)  # 24 hours expiry


class AccessControlManager:
    """Role-based access control for downloads"""
    
    @staticmethod
    def can_download_file(user, file_obj):
        """Check if user can download specific file"""
        # Check if file requires login
        if file_obj.requires_login and not user.is_authenticated:
            return False, "Login required to download this file"
        
        # Check if file has expired
        if file_obj.is_expired:
            return False, "This file has expired"
        
        # Check if file is active
        if not file_obj.is_active:
            return False, "This file is not available"
        
        # Check user permissions for sensitive files
        if file_obj.category == 'RPT' and not AccessControlManager.has_financial_access(user):
            return False, "Insufficient permissions for financial reports"
        
        if file_obj.category == 'PCY' and not AccessControlManager.has_admin_access(user):
            return False, "Insufficient permissions for policy documents"
        
        return True, "Access granted"
    
    @staticmethod
    def has_financial_access(user):
        """Check if user has financial report access"""
        if not user.is_authenticated:
            return False
        
        # Check if user is staff or has specific permission
        return user.is_staff or user.has_perm('downloads.view_financial_reports')
    
    @staticmethod
    def has_admin_access(user):
        """Check if user has admin access"""
        if not user.is_authenticated:
            return False
        
        return user.is_staff or user.is_superuser


class SecurityAuditLogger:
    """Log security events for audit trail"""
    
    @staticmethod
    def log_download_attempt(request, file_obj, success=True, reason=""):
        """Log download attempt"""
        ip = DownloadRateLimiter.get_client_ip(request)
        user_id = request.user.id if request.user.is_authenticated else None
        
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'ip_address': ip,
            'user_id': user_id,
            'file_id': file_obj.id,
            'file_title': file_obj.title,
            'file_category': file_obj.category,
            'success': success,
            'reason': reason,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', '')
        }
        
        if success:
            logger.info(f"Download successful: {log_data}")
        else:
            logger.warning(f"Download blocked: {log_data}")
    
    @staticmethod
    def log_file_upload(request, file_obj, success=True, reason=""):
        """Log file upload attempt"""
        ip = DownloadRateLimiter.get_client_ip(request)
        user_id = request.user.id if request.user.is_authenticated else None
        
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'ip_address': ip,
            'user_id': user_id,
            'file_id': file_obj.id,
            'file_title': file_obj.title,
            'file_size': file_obj.file.size,
            'file_type': file_obj.file_type,
            'success': success,
            'reason': reason
        }
        
        if success:
            logger.info(f"File upload successful: {log_data}")
        else:
            logger.warning(f"File upload blocked: {log_data}")


# Rate limiting decorators
def rate_limit_downloads(func):
    """Decorator to rate limit downloads"""
    def wrapper(request, *args, **kwargs):
        try:
            file_id = kwargs.get('pk')
            DownloadRateLimiter.check_download_rate_limit(request, file_id)
            return func(request, *args, **kwargs)
        except Ratelimited as e:
            logger.warning(f"Download rate limited: {e}")
            from django.http import JsonResponse
            return JsonResponse({'error': str(e)}, status=429)
    return wrapper


def rate_limit_bulk_downloads(func):
    """Decorator to rate limit bulk downloads"""
    def wrapper(request, *args, **kwargs):
        try:
            DownloadRateLimiter.check_bulk_download_limit(request)
            return func(request, *args, **kwargs)
        except Ratelimited as e:
            logger.warning(f"Bulk download rate limited: {e}")
            from django.http import JsonResponse
            return JsonResponse({'error': str(e)}, status=429)
    return wrapper


def require_download_permission(func):
    """Decorator to check download permissions"""
    def wrapper(request, *args, **kwargs):
        from .models import DownloadableFile
        from django.shortcuts import get_object_or_404
        
        file_obj = get_object_or_404(DownloadableFile, pk=kwargs.get('pk'))
        can_download, reason = AccessControlManager.can_download_file(request.user, file_obj)
        
        if not can_download:
            SecurityAuditLogger.log_download_attempt(request, file_obj, False, reason)
            from django.http import JsonResponse
            return JsonResponse({'error': reason}, status=403)
        
        SecurityAuditLogger.log_download_attempt(request, file_obj, True)
        return func(request, *args, **kwargs)
    return wrapper
