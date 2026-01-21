"""
Downloads app utilities.

This package contains validators, helpers, constants, error codes, and performance tracking for the downloads app.
"""

from .constants import (
    MAX_DOWNLOAD_FILE_SIZE_MB,
    MAX_DOWNLOAD_FILE_SIZE_BYTES,
    ALLOWED_DOWNLOAD_FILE_EXTENSIONS,
    ALLOWED_DOWNLOAD_MIME_TYPES,
    DANGEROUS_EXTENSIONS,
    FILES_PER_CATEGORY_DEFAULT,
)

from .error_codes import (
    DownloadsErrorCodes,
    ERROR_STATUS_MAP,
    get_status_code_for_error,
    get_user_friendly_message,
)

from .helpers import (
    get_client_ip,
    format_file_size_display,
    sanitize_filename,
    is_recent_download,
    get_file_extension,
    validate_file_extension,
)

from .performance import (
    track_performance,
    track_download_performance,
    track_bulk_download_performance,
    track_api_response_time,
    track_cache_performance,
    SLOW_OPERATION_THRESHOLD_MS,
)

from .cdn import (
    CDNManager,
)

__all__ = [
    # Constants
    'MAX_DOWNLOAD_FILE_SIZE_MB',
    'MAX_DOWNLOAD_FILE_SIZE_BYTES',
    'ALLOWED_DOWNLOAD_FILE_EXTENSIONS',
    'ALLOWED_DOWNLOAD_MIME_TYPES',
    'DANGEROUS_EXTENSIONS',
    'FILES_PER_CATEGORY_DEFAULT',
    
    # Error Codes
    'DownloadsErrorCodes',
    'ERROR_STATUS_MAP',
    'get_status_code_for_error',
    'get_user_friendly_message',
    
    # Helpers
    'get_client_ip',
    'format_file_size_display',
    'sanitize_filename',
    'is_recent_download',
    'get_file_extension',
    'validate_file_extension',
    
    # Performance
    'track_performance',
    'track_download_performance',
    'track_bulk_download_performance',
    'track_api_response_time',
    'track_cache_performance',
    'SLOW_OPERATION_THRESHOLD_MS',
    # CDN
    'CDNManager',
]

