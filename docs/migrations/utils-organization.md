# Utils Organization Guide

This document outlines the standard structure for organizing utility functions, validators, helpers, and constants across the Bhanjyang Cooperative project.

## Standard Utils Structure

Each app should have a `utils/` directory with the following structure:

```
apps/{app_name}/
├── utils/
│   ├── __init__.py          # Export main utilities
│   ├── validators.py        # Custom validators
│   ├── helpers.py           # Helper functions
│   └── constants.py         # App-specific constants
```

## File Purposes

### `validators.py`
Custom validation functions and classes.

**Example:**
```python
from django.core.exceptions import ValidationError

def validate_file_size(value, max_size_mb=10):
    """Validate file size."""
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB')

def validate_image_dimensions(value, min_width=100, max_width=5000):
    """Validate image dimensions."""
    from PIL import Image
    img = Image.open(value)
    if img.width < min_width or img.width > max_width:
        raise ValidationError(f'Image width must be between {min_width} and {max_width}px')
```

### `helpers.py`
Helper functions for common operations.

**Example:**
```python
from django.utils import timezone
from datetime import timedelta

def calculate_read_time(content, words_per_minute=200):
    """Calculate estimated reading time."""
    word_count = len(content.split())
    return max(1, round(word_count / words_per_minute))

def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

### `constants.py`
App-specific constants and configuration values.

**Example:**
```python
# File Upload Constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_FILE_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.png']

# Pagination Constants
DEFAULT_PAGE_SIZE = 20
ADMIN_LIST_PER_PAGE = 25
MAX_PAGE_SIZE = 100

# Image Processing Constants
THUMBNAIL_SIZE = (300, 200)
MOBILE_IMAGE_SIZE = (800, 600)
IMAGE_QUALITY = 85

# String Length Limits
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
MAX_URL_LENGTH = 500
```

### `__init__.py`
Export commonly used utilities.

**Example:**
```python
from .validators import validate_file_size, validate_image_dimensions
from .helpers import calculate_read_time, format_file_size, get_client_ip
from .constants import (
    MAX_FILE_SIZE_MB,
    DEFAULT_PAGE_SIZE,
    THUMBNAIL_SIZE,
)

__all__ = [
    # Validators
    'validate_file_size',
    'validate_image_dimensions',
    # Helpers
    'calculate_read_time',
    'format_file_size',
    'get_client_ip',
    # Constants
    'MAX_FILE_SIZE_MB',
    'DEFAULT_PAGE_SIZE',
    'THUMBNAIL_SIZE',
]
```

## Usage Examples

### In Models
```python
from django.db import models
from .utils.validators import validate_file_size
from .utils.constants import MAX_FILE_SIZE_MB

class MyModel(models.Model):
    file = models.FileField(
        upload_to='uploads/',
        validators=[validate_file_size]
    )
```

### In Views
```python
from .utils.helpers import get_client_ip, format_file_size
from .utils.constants import DEFAULT_PAGE_SIZE

def my_view(request):
    ip = get_client_ip(request)
    # ... rest of view
```

### In Forms
```python
from django import forms
from .utils.validators import validate_file_size
from .utils.constants import ALLOWED_FILE_EXTENSIONS

class MyForm(forms.Form):
    file = forms.FileField(validators=[validate_file_size])
```

## Migration Guide

### For Existing Apps

1. **Create utils directory:**
   ```bash
   mkdir apps/{app_name}/utils
   touch apps/{app_name}/utils/__init__.py
   ```

2. **Move constants:**
   - If you have a `constants.py` at app root, move it to `utils/constants.py`
   - Update imports in other files

3. **Extract validators:**
   - Find validation functions in models/forms
   - Move to `utils/validators.py`
   - Update imports

4. **Extract helpers:**
   - Find helper functions scattered in views/models
   - Move to `utils/helpers.py`
   - Update imports

5. **Update `__init__.py`:**
   - Export commonly used utilities
   - Make imports easier

## Best Practices

1. **Keep functions pure:** Avoid side effects when possible
2. **Document functions:** Add docstrings to all functions
3. **Type hints:** Use type hints for better code clarity
4. **Single responsibility:** Each function should do one thing
5. **Reusability:** Make functions generic and reusable
6. **Testing:** Write tests for utility functions

## Current Status

### Apps with utils structure:
- ✅ `gallery` - Has `constants.py` (should move to `utils/constants.py`)

### Apps needing utils structure:
- ⚠️ `contact` - Has validators in forms, should extract
- ⚠️ `downloads` - Has validators in security.py, should extract
- ⚠️ `news_events` - Has validators in security.py, should extract
- ⚠️ `services` - Has validators in serializers, should extract
- ⚠️ `home` - Has validators in forms, should extract

## Next Steps

1. Create `utils/` directories for apps that need them
2. Extract validators from forms/models to `utils/validators.py`
3. Extract helper functions to `utils/helpers.py`
4. Move constants to `utils/constants.py`
5. Update all imports
6. Write tests for utility functions

