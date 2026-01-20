"""
Helper functions for the Contact app.
"""

import os
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


def get_attachment_filename(file_field: Any) -> Optional[str]:
    """
    Get the filename of an attachment.
    
    Args:
        file_field: FileField or ImageField instance
        
    Returns:
        str or None: Filename if file exists, None otherwise
    """
    if file_field and file_field.name:
        return os.path.basename(file_field.name)
    return None


def is_recent_submission(created_at: Any, hours: int = 24) -> bool:
    """
    Check if submission is recent (within specified hours).
    
    Args:
        created_at: Datetime of submission creation
        hours: Number of hours to check (default: 24)
        
    Returns:
        bool: True if submission is recent, False otherwise
    """
    time_diff = timezone.now() - created_at
    return time_diff.total_seconds() < (hours * 3600)

