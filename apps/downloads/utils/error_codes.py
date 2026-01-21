"""
Error codes for the Downloads app.
"""
from typing import Dict


class DownloadsErrorCodes:
    """Error codes for downloads app operations."""
    
    # General errors
    DOWNLOAD_ERROR = 'DOWNLOAD_ERROR'
    FILE_NOT_FOUND = 'DOWNLOAD_FILE_NOT_FOUND'
    ACCESS_DENIED = 'DOWNLOAD_ACCESS_DENIED'
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = 'DOWNLOAD_RATE_LIMIT_EXCEEDED'
    
    # File errors
    FILE_EXPIRED = 'DOWNLOAD_FILE_EXPIRED'
    INVALID_FILE_TYPE = 'DOWNLOAD_INVALID_FILE_TYPE'
    FILE_SIZE_EXCEEDED = 'DOWNLOAD_FILE_SIZE_EXCEEDED'
    FILE_UPLOAD_ERROR = 'DOWNLOAD_FILE_UPLOAD_ERROR'
    
    # Bulk operations
    BULK_DOWNLOAD_ERROR = 'DOWNLOAD_BULK_DOWNLOAD_ERROR'
    BULK_DOWNLOAD_EMPTY = 'DOWNLOAD_BULK_DOWNLOAD_EMPTY'
    BULK_DOWNLOAD_LIMIT_EXCEEDED = 'DOWNLOAD_BULK_DOWNLOAD_LIMIT_EXCEEDED'
    
    # Security
    VIRUS_DETECTED = 'DOWNLOAD_VIRUS_DETECTED'
    IP_BLACKLISTED = 'DOWNLOAD_IP_BLACKLISTED'
    FILE_INTEGRITY_FAILED = 'DOWNLOAD_FILE_INTEGRITY_FAILED'
    
    # Database
    DATABASE_ERROR = 'DOWNLOAD_DATABASE_ERROR'
    
    # Request errors
    INVALID_REQUEST = 'DOWNLOAD_INVALID_REQUEST'
    AJAX_REQUIRED = 'DOWNLOAD_AJAX_REQUIRED'


ERROR_STATUS_MAP: Dict[str, int] = {
    DownloadsErrorCodes.DOWNLOAD_ERROR: 500,
    DownloadsErrorCodes.FILE_NOT_FOUND: 404,
    DownloadsErrorCodes.ACCESS_DENIED: 403,
    DownloadsErrorCodes.RATE_LIMIT_EXCEEDED: 429,
    DownloadsErrorCodes.FILE_EXPIRED: 410,
    DownloadsErrorCodes.INVALID_FILE_TYPE: 400,
    DownloadsErrorCodes.FILE_SIZE_EXCEEDED: 400,
    DownloadsErrorCodes.FILE_UPLOAD_ERROR: 400,
    DownloadsErrorCodes.BULK_DOWNLOAD_ERROR: 500,
    DownloadsErrorCodes.BULK_DOWNLOAD_EMPTY: 400,
    DownloadsErrorCodes.BULK_DOWNLOAD_LIMIT_EXCEEDED: 400,
    DownloadsErrorCodes.VIRUS_DETECTED: 403,
    DownloadsErrorCodes.IP_BLACKLISTED: 403,
    DownloadsErrorCodes.DATABASE_ERROR: 500,
    DownloadsErrorCodes.INVALID_REQUEST: 400,
    DownloadsErrorCodes.AJAX_REQUIRED: 400,
}


from django.utils.translation import gettext as _


def get_status_code_for_error(error_code: str) -> int:
    """Get HTTP status code for an error code."""
    return ERROR_STATUS_MAP.get(error_code, 500)


def get_user_friendly_message(error_code: str) -> str:
    """Get user-friendly error message for an error code."""
    messages = {
        DownloadsErrorCodes.DOWNLOAD_ERROR: _('An error occurred while processing your download. Please try again.'),
        DownloadsErrorCodes.FILE_NOT_FOUND: _('The requested file could not be found.'),
        DownloadsErrorCodes.ACCESS_DENIED: _('You do not have permission to access this file.'),
        DownloadsErrorCodes.RATE_LIMIT_EXCEEDED: _('Too many download requests. Please wait a moment before trying again.'),
        DownloadsErrorCodes.FILE_EXPIRED: _('This file has expired and is no longer available.'),
        DownloadsErrorCodes.INVALID_FILE_TYPE: _('File type not allowed. Please check the allowed file types.'),
        DownloadsErrorCodes.FILE_SIZE_EXCEEDED: _('File size exceeds the maximum allowed limit.'),
        DownloadsErrorCodes.FILE_UPLOAD_ERROR: _('An error occurred while uploading the file. Please try again.'),
        DownloadsErrorCodes.BULK_DOWNLOAD_ERROR: _('An error occurred while creating the bulk download. Please try again.'),
        DownloadsErrorCodes.BULK_DOWNLOAD_EMPTY: _('No files selected for bulk download.'),
        DownloadsErrorCodes.BULK_DOWNLOAD_LIMIT_EXCEEDED: _('Too many files selected. Please select fewer files.'),
        DownloadsErrorCodes.VIRUS_DETECTED: _('The file was flagged as potentially unsafe and cannot be downloaded.'),
        DownloadsErrorCodes.IP_BLACKLISTED: _('Your IP address has been temporarily blocked due to security reasons.'),
        DownloadsErrorCodes.FILE_INTEGRITY_FAILED: _('File integrity check failed. The file may have been tampered with.'),
        DownloadsErrorCodes.DATABASE_ERROR: _('A database error occurred. Please try again later.'),
        DownloadsErrorCodes.INVALID_REQUEST: _('Invalid request. Please try again.'),
        DownloadsErrorCodes.AJAX_REQUIRED: _('This endpoint only accepts AJAX requests.'),
    }
    return messages.get(error_code, _('An unexpected error occurred. Please try again.'))
