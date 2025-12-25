# Contact App - Quick Reference

## Overview
Contact app handles contact form submissions and KYM (Know Your Member) form submissions.

## Key Components

### Models
- **ContactSubmission** - General contact form submissions
- **KYMSubmission** - Know Your Member form submissions (NEW)

### Views
- `contact_view` - Main contact form (GET/POST)
- `kym_form_view` - KYM form (GET/POST) - NOW SAVES TO DATABASE
- `privacy_policy_view` - Privacy policy page

### Forms
- **ContactForm** - General contact form
- **KYMForm** - Member registration form

### Admin
- ContactSubmissionAdmin - Manage contact submissions
- KYMSubmissionAdmin - Manage KYM submissions (NEW)

## Recent Changes

### ✅ Implemented Features
1. **Rate Limiting** - Implemented using Django cache (no external dependencies)
   - IP-based: 5 requests/minute for contact form, 3 requests/minute for KYM form
   - Email-based: 3 requests/hour for contact form, 2 requests/hour for KYM form
2. **Office Locations** - Database-driven location management with `OfficeLocation` model
3. **Performance Monitoring** - Real performance stats implementation (replaced placeholders)
4. **Celery Integration** - Clean conditional decorator support (works with or without Celery)
5. **Map Views** - Database-driven map locations with proper error handling
6. **KYM Form** - Saves data to `KYMSubmission` model
7. **RTI Integration** - Information Officer display on contact page

### ✅ Code Quality Improvements
1. **Logging** - Replaced all `print()` statements with proper `logger` calls
2. **HTTP Methods** - Added `@require_http_methods` decorators where needed
3. **Error Handling** - Enhanced Celery error handling with graceful fallback
4. **Admin Interface** - Added `OfficeLocationAdmin` for location management
5. **Tests** - All 160 tests passing with comprehensive coverage

## Quick Commands

### Create Migration (after model changes)
```bash
python manage.py makemigrations contact
python manage.py migrate contact
```

### Run Tests
```bash
python manage.py test apps.contact
```

### Clean Old Submissions
```python
from apps.contact.tasks import cleanup_old_contact_submissions
cleanup_old_contact_submissions()
```

## Rate Limiting

The contact app implements rate limiting to prevent abuse:

- **IP-based limiting**: 
  - Contact form: 5 requests per minute per IP
  - KYM form: 3 requests per minute per IP (more restrictive)
- **Email-based limiting**:
  - Contact form: 3 requests per hour per email
  - KYM form: 2 requests per hour per email (more restrictive)

Rate limiting uses Django's cache framework (no external dependencies required). 
Rate limiting is automatically disabled during test runs.

To disable rate limiting in development, add to `settings.py`:
```python
DISABLE_RATE_LIMITING = True
```

## File Locations

- **Models:** `apps/contact/models.py`
- **Views:** `apps/contact/views.py`
- **Forms:** `apps/contact/forms.py`
- **Admin:** `apps/contact/admin.py`
- **Templates:** `apps/contact/templates/contact/`
- **Utils:** `apps/contact/utils/rate_limiting.py` (rate limiting)
- **Shared Component:** `templates/partials/_info_card.html`

## Documentation
See `docs/CONTACT_APP_MANAGEMENT.md` for complete documentation.

