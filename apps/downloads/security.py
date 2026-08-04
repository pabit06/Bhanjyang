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

# Define Ratelimited exception if not available
try:
    from django_ratelimit.exceptions import Ratelimited
except ImportError:
    class Ratelimited(Exception):
        """Custom rate limit exception"""
        pass

# Try to import magic, fallback to Django's content type detection
try:
    import magic
    # Test if magic actually works (Windows sometimes has import issues)
    try:
        _test_magic = magic.Magic(mime=True)
        _test_magic.from_buffer(b'test')
        MAGIC_AVAILABLE = True
    except (OSError, AttributeError):
        # Magic imported but doesn't work (e.g., missing DLL on Windows)
        MAGIC_AVAILABLE = False
        magic = None  # Set to None to avoid NameError
except (ImportError, OSError):
    MAGIC_AVAILABLE = False
    magic = None

logger = logging.getLogger(__name__)

# Only log warning once if magic is not available
if not MAGIC_AVAILABLE:
    logger.debug("python-magic not available, using Django's content type detection")

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
    
    @staticmethod
    def verify_file_hash(file_path, expected_hash):
        """
        Verify file integrity by comparing current hash with expected hash.
        
        Args:
            file_path: Path to the file on disk
            expected_hash: SHA-256 hash stored in database
            
        Returns:
            tuple: (is_valid: bool, current_hash: str or None, error_message: str or None)
        """
        if not expected_hash:
            # If no hash was stored, we can't verify but don't block
            logger.warning("No hash stored for file, skipping integrity check")
            return True, None, None
        
        try:
            import os
            if not os.path.exists(file_path):
                return False, None, "File not found on disk"
            
            # Read file and calculate hash
            with open(file_path, 'rb') as f:
                file_content = f.read()
                current_hash = hashlib.sha256(file_content).hexdigest()
            
            # Compare hashes
            if current_hash == expected_hash:
                return True, current_hash, None
            else:
                logger.error(
                    f"File integrity check failed for {file_path}. "
                    f"Expected: {expected_hash[:16]}..., Got: {current_hash[:16]}..."
                )
                return False, current_hash, "File hash mismatch - file may have been tampered with"
                
        except Exception as e:
            logger.error(f"Error verifying file hash for {file_path}: {e}", exc_info=True)
            return False, None, f"Error during integrity check: {str(e)}"


class DownloadRateLimiter:
    """
    Rate limiting for downloads.
    
    Note: This is a legacy rate limiter used by decorators.
    The middleware uses RateLimitManager from security_enhanced.py for more advanced rate limiting.
    Both are kept for backward compatibility and different use cases.
    """
    
    @staticmethod
    def check_download_rate_limit(request, file_id):
        """Check if user has exceeded download rate limit"""
        from .utils.helpers import get_client_ip
        ip = get_client_ip(request)
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
        from .utils.helpers import get_client_ip
        ip = get_client_ip(request)
        cache_key = f"bulk_download_limit_{ip}"
        
        bulk_downloads = cache.get(cache_key, 0)
        
        if bulk_downloads >= 3:  # Max 3 bulk downloads per day
            logger.warning(f"Bulk download limit exceeded for IP {ip}")
            raise Ratelimited("Bulk download limit exceeded. Please try again tomorrow.")
        
        cache.set(cache_key, bulk_downloads + 1, 86400)  # 24 hours expiry


class AccessControlManager:
    """Role-based access control for downloads"""

    @staticmethod
    def filter_accessible_queryset(user, queryset):
        """Return only files the user is allowed to discover via list/detail APIs."""
        if getattr(user, 'is_staff', False):
            return queryset

        if not getattr(user, 'is_authenticated', False):
            return queryset.filter(requires_login=False).exclude(
                category__in=['RPT', 'PCY']
            )

        if not AccessControlManager.has_admin_access(user):
            queryset = queryset.exclude(category='PCY')

        if not AccessControlManager.has_financial_access(user):
            queryset = queryset.exclude(category='RPT')

        return queryset
    
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


class VirusScanManager:
    """Manages virus scanning using ClamAV"""
    
    # ClamAV connection settings
    CLAMAV_SOCKET = '/var/run/clamav/clamd.ctl'  # Unix socket
    CLAMAV_HOST = '127.0.0.1'  # TCP host
    CLAMAV_PORT = 3310  # TCP port
    CLAMAV_TIMEOUT = 30  # seconds
    
    @staticmethod
    def is_clamav_available() -> bool:
        """
        Check if ClamAV is available and running.
        
        Returns:
            bool: True if ClamAV is available, False otherwise
        """
        try:
            import pyclamd
            # Try to connect to ClamAV daemon
            cd = pyclamd.ClamdUnixSocket()
            cd.ping()
            return True
        except ImportError:
            # pyclamd not installed
            logger.debug("pyclamd not installed, ClamAV scanning unavailable")
            return False
        except Exception as e:
            # Unix socket failed, try TCP if configured
            try:
                from django.conf import settings
                downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
                host = downloads_settings.get('CLAMAV_HOST', VirusScanManager.CLAMAV_HOST)
                port = downloads_settings.get('CLAMAV_PORT', VirusScanManager.CLAMAV_PORT)
                
                cd = pyclamd.ClamdNetworkSocket(host, port)
                cd.ping()
                return True
            except Exception as tcp_e:
                logger.debug(f"ClamAV not available (Unix: {e}, TCP: {tcp_e})")
                return False
    
    @staticmethod
    def scan_file(file_path: str) -> tuple[bool, str]:
        """
        Scan a file for viruses using ClamAV.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            tuple: (is_clean: bool, scan_result: str)
                - is_clean: True if file is clean, False if virus detected
                - scan_result: Detailed scan result message
        """
        if not os.path.exists(file_path):
            return False, "File not found"
        
        # Check if virus scanning is enabled
        from django.conf import settings
        downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
        if not downloads_settings.get('ENABLE_VIRUS_SCAN', False):
            logger.debug("Virus scanning is disabled in settings")
            return True, "Virus scanning disabled"
        
        # Check if ClamAV is available
        if not VirusScanManager.is_clamav_available():
            logger.warning("ClamAV not available, skipping virus scan")
            # If ClamAV is required but not available, we might want to block
            # For now, we'll allow but log a warning
            return True, "ClamAV not available - scan skipped"
        
        try:
            import pyclamd
            import time
            
            # Try Unix socket first (faster), fallback to TCP
            try:
                cd = pyclamd.ClamdUnixSocket()
            except Exception:
                # Fallback to TCP connection
                host = downloads_settings.get('CLAMAV_HOST', VirusScanManager.CLAMAV_HOST)
                port = downloads_settings.get('CLAMAV_PORT', VirusScanManager.CLAMAV_PORT)
                cd = pyclamd.ClamdNetworkSocket(host, port)
            
            # Get timeout from settings
            timeout = downloads_settings.get('VIRUS_SCAN_TIMEOUT', VirusScanManager.CLAMAV_TIMEOUT)
            
            # Scan the file
            start_time = time.time()
            scan_result = cd.scan_file(file_path)
            scan_time = time.time() - start_time
            
            if scan_result is None:
                # File is clean
                logger.info(f"Virus scan passed for {file_path} (took {scan_time:.2f}s)")
                return True, f"File is clean (scan time: {scan_time:.2f}s)"
            else:
                # Virus detected
                virus_name = scan_result.get(file_path, ['Unknown virus'])[0]
                logger.error(
                    f"Virus detected in {file_path}: {virus_name} "
                    f"(scan time: {scan_time:.2f}s)"
                )
                return False, f"Virus detected: {virus_name}"
                
        except ImportError:
            logger.warning("pyclamd not installed. Install with: pip install pyclamd")
            return True, "pyclamd not installed - scan skipped"
        except Exception as e:
            logger.error(f"Error scanning file {file_path} for viruses: {e}", exc_info=True)
            # On error, we might want to block or allow
            # For security, we'll block if scan fails
            return False, f"Scan error: {str(e)}"
    
    @staticmethod
    def scan_file_content(file_content: bytes) -> tuple[bool, str]:
        """
        Scan file content in memory for viruses.
        
        Args:
            file_content: File content as bytes
            
        Returns:
            tuple: (is_clean: bool, scan_result: str)
        """
        from django.conf import settings
        downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
        if not downloads_settings.get('ENABLE_VIRUS_SCAN', False):
            return True, "Virus scanning disabled"
        
        if not VirusScanManager.is_clamav_available():
            return True, "ClamAV not available - scan skipped"
        
        try:
            import pyclamd
            
            # Try Unix socket first, fallback to TCP
            try:
                cd = pyclamd.ClamdUnixSocket()
            except Exception:
                host = downloads_settings.get('CLAMAV_HOST', VirusScanManager.CLAMAV_HOST)
                port = downloads_settings.get('CLAMAV_PORT', VirusScanManager.CLAMAV_PORT)
                cd = pyclamd.ClamdNetworkSocket(host, port)
            
            # Scan the content
            scan_result = cd.scan_stream(file_content)
            
            if scan_result is None:
                return True, "File content is clean"
            else:
                virus_name = scan_result.get('stream', ['Unknown virus'])[0]
                logger.error(f"Virus detected in file content: {virus_name}")
                return False, f"Virus detected: {virus_name}"
                
        except ImportError:
            return True, "pyclamd not installed - scan skipped"
        except Exception as e:
            logger.error(f"Error scanning file content for viruses: {e}", exc_info=True)
            return False, f"Scan error: {str(e)}"


class SecurityAuditLogger:
    """Log security events for audit trail"""
    
    @staticmethod
    def log_download_attempt(request, file_obj, success=True, reason=""):
        """Log download attempt"""
        from .utils.helpers import get_client_ip
        ip = get_client_ip(request)
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
        from .utils.helpers import get_client_ip
        ip = get_client_ip(request)
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
