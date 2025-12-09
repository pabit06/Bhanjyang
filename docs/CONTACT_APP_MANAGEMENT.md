# Contact App Management Documentation

**Last Updated:** December 9, 2025  
**App Location:** `apps/contact/`

## Overview

The Contact app handles all contact-related functionality for the Bhanjyang Cooperative website, including:
- General contact form submissions
- Know Your Member (KYM) form submissions
- Privacy policy page
- Email notifications
- Admin management interface

---

## Table of Contents

1. [App Structure](#app-structure)
2. [Models](#models)
3. [Views](#views)
4. [Forms](#forms)
5. [Admin Interface](#admin-interface)
6. [Templates](#templates)
7. [Tasks & Background Jobs](#tasks--background-jobs)
8. [Configuration](#configuration)
9. [Common Issues & Solutions](#common-issues--solutions)
10. [Maintenance Tasks](#maintenance-tasks)

---

## App Structure

```
apps/contact/
├── __init__.py
├── admin.py              # Admin interface configuration
├── apps.py               # App configuration
├── forms.py              # Form definitions (ContactForm, KYMForm)
├── models.py             # Database models (ContactSubmission, KYMSubmission)
├── performance.py        # Performance monitoring utilities
├── tasks.py              # Background tasks (email sending)
├── test_security.py      # Security tests
├── tests.py              # Unit tests
├── urls.py               # URL routing
├── views.py              # View functions
├── management/
│   └── commands/
│       └── contact_analytics.py  # Management command for analytics
├── migrations/           # Database migrations
└── templates/
    └── contact/
        ├── contact.html          # Main contact page
        ├── kym_form.html         # KYM form page
        └── privacy_policy.html   # Privacy policy page
```

---

## Models

### 1. ContactSubmission

Stores general contact form submissions.

**Fields:**
- `name` - Full name (CharField, max 100)
- `email` - Email address (EmailField)
- `phone` - Phone number (CharField, max 20, optional)
- `subject` - Subject of inquiry (CharField, max 200)
- `message` - Message content (TextField)
- `attachment` - Optional file attachment (FileField)
- `ip_address` - Submitter's IP (GenericIPAddressField)
- `user_agent` - Browser user agent (TextField)
- `status` - Status (choices: new, in_progress, resolved, spam)
- `admin_notes` - Internal admin notes (TextField)
- `resolved_at` - Resolution timestamp (DateTimeField)
- `created_at` - Creation timestamp (auto)
- `updated_at` - Last update timestamp (auto)

**Key Methods:**
- `is_recent()` - Check if submission is from last 24 hours
- `mark_as_resolved()` - Mark as resolved
- `mark_as_spam()` - Mark as spam
- `has_attachment()` - Check if has attachment
- `get_attachment_filename()` - Get attachment filename
- `get_attachment_size_display()` - Get human-readable file size

### 2. KYMSubmission

Stores Know Your Member (KYM) form submissions.

**Fields:**
- Personal: `full_name`, `dob`, `gender`, `marital_status`, `nationality`
- Contact: `phone`, `email`, `permanent_address`, `district`, `province`
- Family: `father_name`, `mother_name`, `spouse_name`, `grand_father_name`, `nominee_name`
- Occupation: `occupation`, `income_source`, `estimated_income`
- Documents: `citizenship_front`, `citizenship_back`, `passport_photo`, `address_proof`, `income_proof`
- Technical: `ip_address`, `user_agent`
- Management: `status`, `admin_notes`, `reviewed_at`, `reviewed_by`
- Timestamps: `created_at`, `updated_at`

**Status Choices:**
- `pending` - Pending Review
- `under_review` - Under Review
- `approved` - Approved
- `rejected` - Rejected

**Key Methods:**
- `is_recent()` - Check if submission is from last 24 hours
- `get_status_display_color()` - Get CSS color class for status

---

## Views

### 1. `contact_view(request)`

Handles contact form display and submission.

**GET Request:**
- Displays contact form page
- Returns: `contact/contact.html`

**POST Request (AJAX only):**
- Validates form data
- Saves to `ContactSubmission` model
- Sends email notifications (via Celery if available)
- Returns: JSON response

**Response Format:**
```json
{
    "success": true,
    "message": "Thank you! Your message has been sent successfully.",
    "submission_id": 123
}
```

### 2. `kym_form_view(request)`

Handles KYM form display and submission.

**GET Request:**
- Displays KYM form page
- Returns: `contact/kym_form.html`

**POST Request:**
- Validates form data
- Saves to `KYMSubmission` model
- Returns: JSON response

### 3. `privacy_policy_view(request)`

Displays privacy policy page.

**Returns:** `contact/privacy_policy.html`

---

## Forms

### 1. ContactForm

General contact form with fields:
- `name` (required)
- `email` (required)
- `phone` (optional)
- `subject` (required)
- `message` (required, min 10 chars)
- `attachment` (optional, max 5MB, allowed: PDF, DOC, DOCX, JPG, PNG, TXT, XLS, XLSX)

**Validation:**
- Email format validation
- Message length validation (min 10 characters)
- File type and size validation

### 2. KYMForm

Know Your Member form with comprehensive fields:
- Personal details (name, DOB, gender, marital status, nationality)
- Contact information (phone, email, address, district, province)
- Family details (father, mother, spouse, grandfather, nominee)
- Occupation & income details
- Document uploads (citizenship, passport photo, address proof, income proof)

**Validation:**
- All required fields validated
- File size limit: 5MB per file
- File type validation for each document type

---

## Admin Interface

### ContactSubmissionAdmin

**List Display:**
- Name, Email, Subject
- Status badge (colored)
- Attachment info
- Created date
- Recent badge (if < 24 hours)

**Filters:**
- Status
- Created date

**Search:**
- Name, Email, Subject, Message

**Actions:**
- Mark as resolved
- Mark as spam
- Mark as in progress

**Features:**
- Status badges with colors
- Attachment preview
- Message preview
- Recent submissions highlighted
- Cannot add new submissions through admin (must come from form)

### KYMSubmissionAdmin

**List Display:**
- Full name, Email, Phone
- Status badge
- Occupation
- Created date
- Recent badge

**Filters:**
- Status
- Created date
- District
- Gender

**Search:**
- Full name, Email, Phone, Address, Occupation

**Actions:**
- Mark as approved
- Mark as rejected
- Mark as under review

**Features:**
- Document links preview
- Status badges
- Review tracking (reviewed_by, reviewed_at)
- Cannot add new submissions through admin

---

## Templates

### 1. `contact/contact.html`

Main contact page featuring:
- Contact information cards (using `_info_card.html` partial)
- Contact form with AJAX submission
- Google Maps integration
- Responsive design

**Uses:**
- `templates/partials/_info_card.html` - Reusable info card component

### 2. `contact/kym_form.html`

KYM form page with:
- Multi-section form
- Document upload fields
- Form validation
- AJAX submission

### 3. `contact/privacy_policy.html`

Privacy policy page.

---

## Tasks & Background Jobs

### Email Tasks (in `tasks.py`)

**Note:** Celery integration is optional. Tasks work synchronously if Celery is not installed.

#### 1. `send_contact_email(submission_data)`

Sends contact form submission email to admin.

**Parameters:**
- `submission_data` (dict): Contains subject, message, submission_id

**Returns:** Boolean (success/failure)

#### 2. `send_auto_response_email(user_email, user_name, subject, submission_id)`

Sends auto-response email to user.

**Parameters:**
- `user_email` - User's email address
- `user_name` - User's name
- `subject` - Original subject
- `submission_id` - Submission ID

**Returns:** Boolean (success/failure)

#### 3. `cleanup_old_contact_submissions()`

Cleans up old resolved submissions (older than 1 year).

**Returns:** Number of deleted submissions

**Usage:**
```python
# Run via management command or scheduled task
from apps.contact.tasks import cleanup_old_contact_submissions
cleanup_old_contact_submissions()
```

---

## Configuration

### URLs

**Main URLs** (`config/urls.py`):
```python
path('contact/', include('apps.contact.urls')),
```

**App URLs** (`apps/contact/urls.py`):
- `/contact/` - Contact form page
- `/contact/kym-form/` - KYM form page
- `/contact/privacy-policy/` - Privacy policy page

### Settings

**INSTALLED_APPS:**
```python
'apps.contact',
```

**Email Configuration:**
- Uses `settings.DEFAULT_FROM_EMAIL` for sending emails
- Admin email: `admin@bhanjyang.coop.np` (hardcoded in tasks.py)

**File Upload:**
- Contact attachments: `media/contact_attachments/YYYY/MM/DD/`
- KYM documents: `media/kym_documents/YYYY/MM/DD/`
- Max file size: 5MB (enforced in forms)

---

## Common Issues & Solutions

### Issue 1: Emails Not Sending

**Symptoms:** Form submissions succeed but no emails received.

**Solutions:**
1. Check `settings.DEFAULT_FROM_EMAIL` is configured
2. Check `SEND_REAL_EMAILS` setting (if False, emails print to console)
3. Check email backend configuration in `settings.py`
4. Check Celery is running (if using async emails)
5. Check logs for email errors

### Issue 2: File Upload Fails

**Symptoms:** Form submission fails with file upload error.

**Solutions:**
1. Check file size (max 5MB)
2. Check file type is allowed
3. Check `MEDIA_ROOT` is writable
4. Check disk space
5. Verify file upload path permissions

### Issue 3: Form Validation Errors

**Symptoms:** Form shows validation errors even with valid data.

**Solutions:**
1. Check form field requirements
2. Verify JavaScript validation matches server-side validation
3. Check for special characters in fields
4. Verify email format
5. Check message length (min 10 characters)

### Issue 4: KYM Form Not Saving

**Symptoms:** KYM form submits but data not saved.

**Solutions:**
1. Run migrations: `python manage.py makemigrations contact`
2. Run migrations: `python manage.py migrate contact`
3. Check database permissions
4. Check form validation errors
5. Check logs for database errors

---

## Maintenance Tasks

### Regular Maintenance

1. **Clean Old Submissions** (Monthly)
   ```bash
   python manage.py shell
   >>> from apps.contact.tasks import cleanup_old_contact_submissions
   >>> cleanup_old_contact_submissions()
   ```

2. **Review Pending Submissions** (Daily)
   - Check admin for new submissions
   - Respond to inquiries
   - Update status appropriately

3. **Monitor Performance** (Weekly)
   - Check performance logs
   - Review submission trends
   - Monitor email delivery rates

4. **Backup Submissions** (Before major updates)
   ```bash
   python manage.py dumpdata contact --indent 2 > contact_backup.json
   ```

### Database Migrations

After adding new fields or models:

```bash
# Create migrations
python manage.py makemigrations contact

# Apply migrations
python manage.py migrate contact
```

### Testing

Run tests:
```bash
python manage.py test apps.contact
```

Test coverage:
- Form validation
- View responses
- Model methods
- Security measures
- File uploads

---

## Performance Monitoring

### Performance Metrics

The app includes performance monitoring via `performance.py`:

- Processing time tracking
- Database query counting
- Success rate monitoring
- Performance threshold checking

### Analytics

Use management command for analytics:
```bash
python manage.py contact_analytics
```

---

## Security Features

1. **File Upload Security:**
   - Filename sanitization
   - File type validation
   - File size limits
   - Secure upload paths

2. **Input Validation:**
   - Email format validation
   - Phone number validation
   - XSS protection (HTML sanitization)
   - SQL injection protection (Django ORM)

3. **Rate Limiting:**
   - Commented out (requires django-ratelimit)
   - Can be enabled by uncommenting decorators in `views.py`

4. **IP Tracking:**
   - All submissions track IP address
   - Useful for spam detection

---

## Dependencies

### Required:
- Django 5.2+
- Python 3.8+

### Optional:
- Celery (for async email sending)
- django-ratelimit (for rate limiting)

### External Services:
- Email backend (SMTP or console)
- File storage (local or cloud)

---

## Future Improvements

1. **Rate Limiting:**
   - Install `django-ratelimit`
   - Uncomment rate limit decorators in `views.py`

2. **Celery Integration:**
   - Install Celery
   - Configure Celery broker
   - Uncomment `@shared_task` decorators in `tasks.py`
   - Update task function signatures to include `self` parameter

3. **Email Templates:**
   - Create HTML email templates
   - Add email template customization

4. **Analytics Dashboard:**
   - Create admin dashboard for analytics
   - Add charts and graphs
   - Export functionality

5. **API Endpoints:**
   - Create REST API for submissions
   - Add API authentication
   - Document with OpenAPI/Swagger

---

## Related Files

- **Shared Components:**
  - `templates/partials/_info_card.html` - Reusable info card component

- **Configuration:**
  - `config/settings.py` - App registration and email settings
  - `config/urls.py` - URL routing

- **Documentation:**
  - This file: `docs/CONTACT_APP_MANAGEMENT.md`

---

**Last Updated:** December 9, 2025  
**Maintained By:** Development Team

