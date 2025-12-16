# Folder Structure Improvements - High Priority

This document outlines the high-priority improvements made to the Bhanjyang Cooperative project folder structure.

## ✅ Completed Improvements

### 1. Root-Level Tests Folder Structure

**Location:** `tests/`

Created a dedicated folder for integration tests that test multiple components working together.

**Structure:**
```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest configuration and shared fixtures
├── test_integration.py      # Main integration tests
└── README.md                # Test documentation
```

**Features:**
- Integration tests for page loads
- Form submission tests
- Cross-app integration tests
- Shared fixtures for common test setup
- Pytest configuration

**Usage:**
```bash
# Run all integration tests
pytest tests/

# Run with coverage
pytest tests/ --cov=apps --cov-report=html
```

### 2. Locale Folder Structure

**Location:** `locale/`

Created folder structure for internationalization (i18n) support with Nepali and English translations.

**Structure:**
```
locale/
├── en/                      # English translations
│   └── LC_MESSAGES/
│       ├── django.po        # Translation source (generated)
│       └── django.mo        # Compiled translations (generated)
├── ne/                      # Nepali (नेपाली) translations
│   └── LC_MESSAGES/
│       ├── django.po        # Translation source (generated)
│       └── django.mo        # Compiled translations (generated)
└── README.md                # Translation documentation
```

**Django Settings Updated:**
- Added `LANGUAGES` configuration
- Added `LOCALE_PATHS` pointing to `locale/` directory
- Enabled `USE_L10N` for localization

**Usage:**
```bash
# Extract translatable strings
python manage.py makemessages -l ne
python manage.py makemessages -l en

# Compile translations
python manage.py compilemessages
```

**In Templates:**
```django
{% load i18n %}
<h1>{% trans "Welcome" %}</h1>
```

**In Python Code:**
```python
from django.utils.translation import gettext as _
message = _("Welcome to Bhanjyang Cooperative")
```

### 3. Services Layer Consistency

Created `services.py` files for apps that were missing them, ensuring consistent business logic organization.

#### Contact App Services

**Location:** `apps/contact/services.py`

**Services Created:**
- `ContactService` - Handles contact form submissions
  - `get_contact_page_context()` - Get page context
  - `create_contact_submission()` - Create submission from form data
  - `send_contact_notification_emails()` - Send notification emails
  - `get_performance_metrics()` - Calculate performance metrics

- `KYMService` - Handles KYM (Know Your Member) form submissions
  - `get_kym_page_context()` - Get page context
  - `create_kym_submission()` - Create KYM submission

- `ContactAnalyticsService` - Contact analytics and statistics
  - `get_submission_stats()` - Get contact submission statistics
  - `get_kym_stats()` - Get KYM submission statistics

#### Downloads App Services

**Location:** `apps/downloads/services.py`

**Services Created:**
- `DownloadsService` - Handles download center operations
  - `get_download_center_context()` - Get download center page context
  - `_get_filtered_files()` - Get filtered files (private)
  - `_group_files_by_category()` - Group files by category (private)
  - `_get_featured_files()` - Get featured files (private)

- `FileDownloadService` - Handles file download operations
  - `process_file_download()` - Process file download request
  - `process_file_view()` - Process file view request

- `BulkDownloadService` - Handles bulk download operations
  - `get_accessible_files()` - Get files user can download
  - `create_zip_file()` - Create ZIP file from multiple files

- `DownloadsAnalyticsService` - Download analytics and statistics
  - `get_download_stats()` - Get download statistics

## Benefits

### 1. Better Test Organization
- Separation of unit tests (in apps) and integration tests (in root tests/)
- Easier to run comprehensive test suites
- Better test coverage tracking

### 2. Internationalization Support
- Ready for Nepali/English translations
- Follows Django i18n best practices
- Easy to add more languages in the future

### 3. Consistent Code Organization
- All apps now have services layer
- Business logic separated from views
- More maintainable and testable code
- Easier to refactor and extend

## Next Steps (Medium Priority)

1. **Static Files Reorganization** - Better categorization of CSS/JS files
2. **Utils Organization** - Create utils folders with validators, helpers, constants
3. **Documentation Structure** - Add API and deployment documentation folders

## Migration Notes

### For Developers

When working with the new structure:

1. **Integration Tests:** Add new integration tests to `tests/test_integration.py` or create new test files in `tests/`

2. **Translations:** 
   - Mark strings for translation using `{% trans %}` in templates
   - Use `_()` function in Python code
   - Run `makemessages` to extract strings
   - Translate in `.po` files
   - Run `compilemessages` to compile

3. **Services Layer:**
   - Move business logic from views to services
   - Keep views thin - they should only handle HTTP requests/responses
   - Services should be stateless and testable

### For Views Refactoring

Example of how to use services in views:

**Before:**
```python
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Business logic here...
            submission = ContactSubmission.objects.create(...)
            # Send emails...
```

**After:**
```python
from .services import ContactService

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            submission = ContactService.create_contact_submission(
                form.cleaned_data, request.FILES, request.META
            )
            ContactService.send_contact_notification_emails(submission)
```

## Files Created/Modified

### Created:
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_integration.py`
- `tests/README.md`
- `locale/README.md`
- `locale/en/LC_MESSAGES/.gitkeep`
- `locale/ne/LC_MESSAGES/.gitkeep`
- `apps/contact/services.py`
- `apps/downloads/services.py`
- `docs/FOLDER_STRUCTURE_IMPROVEMENTS.md`

### Modified:
- `config/settings.py` - Added locale configuration

## Testing

To verify the improvements:

1. **Run integration tests:**
   ```bash
   pytest tests/
   ```

2. **Check locale setup:**
   ```bash
   python manage.py makemessages -l ne
   ```

3. **Verify services:**
   ```python
   from apps.contact.services import ContactService
   from apps.downloads.services import DownloadsService
   ```

## References

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django Internationalization](https://docs.djangoproject.com/en/stable/topics/i18n/)
- [Django Best Practices - Services Layer](https://docs.djangoproject.com/en/stable/topics/db/models/#organizing-models-in-a-package)

