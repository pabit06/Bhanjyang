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

### ✅ Fixed Issues
1. **KYM Form** - Now saves data to `KYMSubmission` model
2. **Tasks** - Fixed Celery compatibility (works without Celery)
3. **Performance** - Fixed missing `Count` import
4. **Info Card** - Moved to shared location: `templates/partials/_info_card.html`

### ⚠️ Known Issues
1. **Tests** - Some tests reference form validation methods that don't exist (clean_name, clean_phone, etc.)
   - Tests will need to be updated or validation methods added
2. **Rate Limiting** - Commented out (requires django-ratelimit package)
3. **Celery** - Optional, tasks work synchronously if not installed

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

## File Locations

- **Models:** `apps/contact/models.py`
- **Views:** `apps/contact/views.py`
- **Forms:** `apps/contact/forms.py`
- **Admin:** `apps/contact/admin.py`
- **Templates:** `apps/contact/templates/contact/`
- **Shared Component:** `templates/partials/_info_card.html`

## Documentation
See `docs/CONTACT_APP_MANAGEMENT.md` for complete documentation.

