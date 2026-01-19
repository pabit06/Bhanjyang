"""
Contact app utilities.

This package contains validators, helpers, and constants for the contact app.
"""

from .validators import validate_contact_file_size, validate_phone_number, validate_nepali_phone
from .helpers import get_client_ip, format_file_size_display, get_attachment_filename
from .constants import (
    MAX_CONTACT_FILE_SIZE_MB,
    MAX_CONTACT_FILE_SIZE_BYTES,
    ALLOWED_CONTACT_FILE_EXTENSIONS,
    ALLOWED_CONTACT_MIME_TYPES,
    DISPOSABLE_EMAIL_DOMAINS,
    SPAM_PATTERNS,
)

__all__ = [
    # Constants
    'MAX_CONTACT_FILE_SIZE_MB',
    'MAX_CONTACT_FILE_SIZE_BYTES',
    'ALLOWED_CONTACT_FILE_EXTENSIONS',
    'ALLOWED_CONTACT_MIME_TYPES',
    'DISPOSABLE_EMAIL_DOMAINS',
    'SPAM_PATTERNS',
    
    # Helpers
    'get_client_ip',
    'get_attachment_filename',
    'format_file_size_display',
    
    # Validators
    'validate_contact_file_size',
    'validate_phone_number',
    'validate_nepali_phone',
]
