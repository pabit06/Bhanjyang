"""
Helper functions for the Downloads app.
"""

import os
import re
import uuid
from typing import Union, Dict, Any, Optional
from django.utils import timezone
from django.http import HttpRequest


def get_client_ip(request_or_meta: Union[HttpRequest, Dict[str, Any]]) -> str:
    """
    Extract client IP address from request or META dictionary.
    
    Args:
        request_or_meta: Django HTTP request object or META dictionary
        
    Returns:
        str: Client IP address
    """
    if hasattr(request_or_meta, 'META'):
        meta = request_or_meta.META
    else:
        meta = request_or_meta
        
    x_forwarded_for = meta.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = meta.get('REMOTE_ADDR', '')
    return ip


def format_file_size_display(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        str: Human-readable file size (e.g., "2.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other security issues.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename with UUID prefix
    """
    # Remove directory path components
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\s\-_\.]', '', filename)
    
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    
    # Add UUID prefix for uniqueness and security
    unique_id = str(uuid.uuid4())[:8]
    name, ext = os.path.splitext(filename)
    return f"{unique_id}_{name}{ext}"


def is_recent_download(accessed_at: Any, hours: int = 24) -> bool:
    """
    Check if download is recent (within specified hours).
    
    Args:
        accessed_at: Datetime of file access
        hours: Number of hours to check (default: 24)
        
    Returns:
        bool: True if download is recent, False otherwise
    """
    if not accessed_at:
        return False
    time_diff = timezone.now() - accessed_at
    return time_diff.total_seconds() < (hours * 3600)


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: File name
        
    Returns:
        str: File extension (lowercase, without dot)
    """
    _, ext = os.path.splitext(filename)
    return ext.replace('.', '').lower() if ext else ''


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate file extension against allowed list.
    
    Args:
        filename: File name to validate
        allowed_extensions: List of allowed extensions (with or without dot)
        
    Returns:
        bool: True if extension is allowed, False otherwise
    """
    ext = get_file_extension(filename)
    # Normalize allowed extensions (remove dots, lowercase)
    normalized_allowed = [e.replace('.', '').lower() for e in allowed_extensions]
    return ext in normalized_allowed
