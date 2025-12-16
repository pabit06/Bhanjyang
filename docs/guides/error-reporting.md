# Error Reporting Configuration Guide
# ===================================

## Overview
This guide explains how to configure error reporting for the Bhanjyang Cooperative Django application. When a 500 error occurs in production, administrators will be automatically notified via email.

## Configuration Steps

### 1. Environment Variables
Create a `.env` file in your project root with the following variables:

```bash
# Email Configuration for Error Reporting
SEND_REAL_EMAILS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587

# Admin Emails - These people will receive error notifications
ADMIN_EMAIL=admin@bhanjyang.coop.np
DEVELOPER_EMAIL=developer@bhanjyang.coop.np

# Security Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# CSRF Settings
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Gmail Configuration
If using Gmail for error reporting:

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password in `EMAIL_HOST_PASSWORD`

### 3. Error Reporting Features

#### Automatic Error Emails
- **When**: 500 errors occur in production (DEBUG=False)
- **Who**: All emails listed in `ADMINS` setting
- **What**: Full error traceback, request details, user information
- **Format**: HTML email with detailed error information

#### Logged Errors
- **File**: `logs/django_error.log`
- **Level**: ERROR and above
- **Rotation**: 5MB max, 5 backup files
- **Format**: Detailed with timestamps, process IDs, stack traces

#### Security Errors
- **When**: Security-related errors (CSRF, XSS attempts, etc.)
- **Action**: Logged and emailed to admins
- **Level**: WARNING and above

### 4. Testing Error Reporting

#### Method 1: Trigger a 500 Error
1. Set `DEBUG=False` in your environment
2. Set `SEND_REAL_EMAILS=True`
3. Visit a non-existent service URL: `/services/invalid-service/999/`
4. Check your email for the error notification

#### Method 2: Manual Error Logging
```python
import logging
logger = logging.getLogger('django.request')
logger.error('Test error message', exc_info=True)
```

### 5. Production Checklist

- [ ] `DEBUG=False` in production
- [ ] `SEND_REAL_EMAILS=True` in production
- [ ] Valid email credentials configured
- [ ] `ADMINS` list contains real email addresses
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] Error logging directory exists (`logs/`)
- [ ] Test error reporting works

### 6. Error Email Content

Error emails include:
- **Subject**: `[Bhanjyang Coop Error] Error (500): /path/to/error`
- **Body**: HTML formatted with:
  - Error message and traceback
  - Request details (URL, method, headers)
  - User information (if authenticated)
  - Server environment details
  - Full stack trace

### 7. Monitoring and Alerts

#### Log Files to Monitor
- `logs/django_error.log` - Application errors
- `logs/django.log` - General application logs
- `logs/performance.log` - Performance metrics

#### Email Notifications
- **Immediate**: 500 errors sent to admins
- **Security**: Suspicious activity logged and emailed
- **Performance**: Slow queries and timeouts logged

### 8. Troubleshooting

#### No Error Emails Received
1. Check `SEND_REAL_EMAILS=True`
2. Verify email credentials
3. Check spam folder
4. Test SMTP connection
5. Verify `ADMINS` configuration

#### Email Delivery Issues
1. Check SMTP server settings
2. Verify firewall/network access
3. Check email provider limits
4. Test with different email provider

#### Log File Issues
1. Ensure `logs/` directory exists
2. Check file permissions
3. Verify disk space
4. Check log rotation settings

## Security Considerations

- Never commit `.env` file to version control
- Use strong, unique passwords for email accounts
- Regularly rotate email passwords
- Monitor error logs for suspicious activity
- Consider using dedicated error reporting services (Sentry, Rollbar) for large-scale applications

## Advanced Configuration

### Custom Error Handlers
You can create custom error handlers in `coop/urls.py`:

```python
from django.conf.urls import handler500, handler404

handler500 = 'coop.views.server_error'
handler404 = 'coop.views.page_not_found'
```

### Third-Party Error Reporting
Consider integrating with services like:
- **Sentry**: Advanced error tracking and monitoring
- **Rollbar**: Real-time error tracking
- **LogRocket**: Session replay and error tracking
- **Bugsnag**: Error monitoring and reporting
