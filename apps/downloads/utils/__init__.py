"""
Downloads app utilities.

This package contains validators, helpers, and constants for the downloads app.
"""

from .constants import (
    MAX_DOWNLOAD_FILE_SIZE_MB,
    MAX_DOWNLOAD_FILE_SIZE_BYTES,
    ALLOWED_DOWNLOAD_FILE_EXTENSIONS,
    ALLOWED_DOWNLOAD_MIME_TYPES,
    DANGEROUS_EXTENSIONS,
    FILES_PER_CATEGORY_DEFAULT,
)

__all__ = [
    # Constants
    'MAX_DOWNLOAD_FILE_SIZE_MB',
    'MAX_DOWNLOAD_FILE_SIZE_BYTES',
    'ALLOWED_DOWNLOAD_FILE_EXTENSIONS',
    'ALLOWED_DOWNLOAD_MIME_TYPES',
    'DANGEROUS_EXTENSIONS',
    'FILES_PER_CATEGORY_DEFAULT',
]

