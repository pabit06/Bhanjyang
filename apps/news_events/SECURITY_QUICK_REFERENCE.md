# Security Quick Reference Guide
# (सुरक्षा द्रुत सन्दर्भ गाइड)

Quick reference for using enhanced security features in news_events app.

---

## 🚀 Quick Setup (5 Minutes)

### 1. Enable Middleware

```python
# settings.py
MIDDLEWARE = [
    # ... existing middleware
    'apps.news_events.middleware.NewsEventsSecurityMiddleware',
    'apps.news_events.middleware.RateLimitMiddleware',
]
```

### 2. Configure Session Security

```python
# settings.py
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
```

### 3. Done! ✅

The middleware automatically applies all security features.

---

## 📖 Common Use Cases

### Protect a View from Spam

```python
from apps.news_events.security_enhanced import honeypot_protected

@honeypot_protected
def contact_form_view(request):
    # Your view code
    pass
```

### Validate File Uploads

```python
from apps.news_events.security_enhanced import FileUploadSecurity

def handle_upload(request):
    uploaded_file = request.FILES['document']
    
    # Validate
    result = FileUpload Security.validate_file_upload(uploaded_file)
    if not result['is_valid']:
        return JsonResponse({'errors': result['errors']}, status=400)
    
    # Sanitize filename
    uploaded_file.name = FileUploadSecurity.sanitize_filename(uploaded_file.name)
    
    # Save file
    file.save(uploaded_file)
```

### Block an IP Address

```python
from apps.news_events.security_enhanced import IPBlacklistManager

# Block IP for 24 hours
IPBlacklistManager.add_to_blacklist('192.168.1.100', 'Spam bot detected')

# Check if IP is blocked
is_blocked, reason = IPBlacklistManager.is_blacklisted('192.168.1.100')

# Unblock IP
IPBlacklistManager.remove_from_blacklist('192.168.1.100')
```

### Add Honeypot to Form

```html
<!-- In your template -->
<form method="post">
    {% csrf_token %}
    
    <!-- Honeypot field (bots will fill this) -->
    <div class="hidden" style="position:absolute;left:-5000px;" aria-hidden="true">
        <input type="text" name="website" id="id_website" tabindex="-1" autocomplete="off">
    </div>
    
    <!-- Your regular form fields -->
    {{ form.as_p }}
</form>
```

### Monitor Security Events

```python
from apps.news_events.security_enhanced import get_recent_security_events

# Get last 24 hours
events = get_recent_security_events(days=1)

# Filter by type
spam_attempts = [e for e in events if e['event_type'] == 'honeypot_filled']
blocked_ips = [e for e in events if e['event_type'] == 'blocked_blacklisted_ip']

print(f"Spam attempts: {len(spam_attempts)}")
print(f"Blocked IPs: {len(blocked_ips)}")
```

---

## 🔒 Security Checklist

### For All Forms:
- [ ] Add honeypot field
- [ ] Use `@honeypot_protected` decorator
- [ ] Enable CSRF protection
- [ ] Validate all inputs
- [ ] Sanitize content

### For File Uploads:
- [ ] Validate file type
- [ ] Check file size
- [ ] Sanitize filename
- [ ] Scan for malicious content
- [ ] Use whitelisted extensions

### For API Endpoints:
- [ ] Enable DRF throttling
- [ ] Add permission classes
- [ ] Validate request signatures (if needed)
- [ ] Log security events
- [ ] Rate limit by IP

### For User Sessions:
- [ ] Enable session security middleware
- [ ] Set session timeout
- [ ] Use secure cookies
- [ ] Check session integrity

---

## 🛡️ Security Levels

### Basic (Default)
- [x] IP blacklisting
- [x] Security headers
- [x] Rate limiting
- [x] Session security

### Enhanced (Recommended)
- [x] Basic level
- [x] Honeypot protection
- [x] File upload validation
- [x] Security event logging

### Maximum (For Sensitive Operations)
- [x] Enhanced level
- [x] Request signatures
- [x] Custom throttle limits
- [x] Real-time monitoring

---

## 📊 Default Security Settings

| Feature | Default | Customizable |
|---------|---------|--------------|
| IP Blacklist Duration | 24 hours | Yes |
| Max File Size | 5MB | Yes |
| Session Timeout | 30 minutes | Yes |
| Rate Limit (Subscribe) | 3/minute | Yes |
| Rate Limit (Comment) | 5/minute | Yes |
| Max Request Size | 10MB | Yes |
| Auto-Blacklist Threshold | 5 violations | Yes |

---

## 🔧 Customization

### Change Rate Limits

```python
# middleware.py
RATE_LIMITS = {
    '/news-events/subscribe/': 5,  # Changed from 3
    '/news-events/article/.*/comment/': 10,  # Changed from 5
}
```

### Change File Size Limit

```python
from apps.news_events.security_enhanced import FileUploadSecurity

# Validate with custom limit (10MB)
result = FileUploadSecurity.validate_file_upload(
    uploaded_file, 
    max_size=10*1024*1024
)
```

### Change Session Timeout

```python
from apps.news_events.security_enhanced import SessionSecurityManager

# Check with 60-minute timeout
is_valid = SessionSecurityManager.check_session_timeout(
    request, 
    timeout_minutes=60
)
```

---

## 🚨 Troubleshooting

### Legitimate Users Getting Blocked?

```python
# Unblock IP
from apps.news_events.security_enhanced import IPBlacklistManager
IPBlacklistManager.remove_from_blacklist('IP_ADDRESS')

# Clear violations
from django.core.cache import cache
cache.delete(f'violations_IP_ADDRESS')
```

### Forms Being Rejected?

Check if honeypot field is being filled accidentally:
```javascript
// Make sure honeypot field is hidden
document.getElementById('id_website').style.display = 'none';
```

### Rate Limits Too Strict?

Temporarily increase limits or whitelist IPs in middleware.

---

## 📝 Best Practices

1. **Monitor Security Events Daily**
   ```python
   events = get_recent_security_events(days=1)
   ```

2. **Review Blacklisted IPs Weekly**
   - Check for false positives
   - Unblock legitimate users

3. **Update Security Headers**
   - Keep CSP policy current
   - Test in dev before production

4. **Test File Upload Limits**
   - Ensure limits work for your use case
   - Adjust as needed

5. **Log Everything**
   - All security events
   - All failed attempts
   - All blacklist actions

---

## ✅ Testing Your Security

```bash
# Run security tests
python manage.py test apps.news_events.tests.test_security_enhanced

# Expected output: 34 tests passing
```

---

## 📞 Emergency Procedures

### Under Attack?

1. **Check blacklisted IPs:**
   ```python
   from apps.news_events.security_enhanced import get_recent_security_events
   events = get_recent_security_events(days=1)
   ```

2. **Manually blacklist attacking IP:**
   ```python
   from apps.news_events.security_enhanced import IPBlacklistManager
   IPBlacklistManager.add_to_blacklist('ATTACK_IP', 'DoS attack', duration=86400)
   ```

3. **Reduce rate limits temporarily:**
   - Edit `middleware.py`
   - Restart server

4. **Enable emergency mode:**
   - Disable anonymous access
   - Require login for all endpoints

---

**Quick Start:** Just enable the middleware and you're protected! ✅  
**Full Setup:** Add honeypots to forms and validate file uploads  
**Maximum Security:** Enable all features + monitoring

---

**Last Updated:** January 6, 2026  
**Security Version:** 2.0 (Enhanced)
