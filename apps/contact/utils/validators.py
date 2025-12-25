"""
Custom validators for the Contact app.
"""

from django.core.exceptions import ValidationError
from .constants import (
    MAX_CONTACT_FILE_SIZE_BYTES,
    ALLOWED_CONTACT_FILE_EXTENSIONS,
    ALLOWED_CONTACT_MIME_TYPES,
)


def validate_contact_file_size(value):
    """
    Validate that uploaded file size does not exceed maximum allowed size.
    
    Args:
        value: FileField or ImageField value
        
    Raises:
        ValidationError: If file size exceeds maximum allowed size
    """
    if value.size > MAX_CONTACT_FILE_SIZE_BYTES:
        max_size_mb = MAX_CONTACT_FILE_SIZE_BYTES / (1024 * 1024)
        raise ValidationError(
            f'File size cannot exceed {max_size_mb}MB. '
            f'Your file is {value.size / (1024 * 1024):.2f}MB.'
        )


def validate_contact_file_extension(value):
    """
    Validate that uploaded file has an allowed extension.
    
    Args:
        value: FileField or ImageField value
        
    Raises:
        ValidationError: If file extension is not allowed
    """
    import os
    file_extension = os.path.splitext(value.name)[1].lower()
    
    # Remove leading dot for comparison if present
    ext_without_dot = file_extension.lstrip('.')
    
    if ext_without_dot not in ALLOWED_CONTACT_FILE_EXTENSIONS:
        raise ValidationError(
            f'File type "{file_extension}" is not allowed. '
            f'Allowed types: {", ".join(ALLOWED_CONTACT_FILE_EXTENSIONS)}'
        )


def validate_contact_mime_type(value):
    """
    Validate that uploaded file has an allowed MIME type.
    
    Args:
        value: FileField or ImageField value
        
    Raises:
        ValidationError: If MIME type is not allowed
    """
    if hasattr(value, 'content_type') and value.content_type:
        if value.content_type not in ALLOWED_CONTACT_MIME_TYPES:
            raise ValidationError(
                f'File type "{value.content_type}" is not allowed. '
                f'Allowed types: {", ".join(ALLOWED_CONTACT_MIME_TYPES)}'
            )

