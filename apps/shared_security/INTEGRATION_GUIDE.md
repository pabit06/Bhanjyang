# Security Integration Guide for All Apps
# (सबै एप्सका लागि सुरक्षा एकीकरण गाइड)

This guide shows how to integrate the shared security features into any Bhanjyang app.

---

## 📦 Shared Security Module

The `apps/shared_security` module provides enterprise-grade security features that can be used by all apps:

- **IPBlacklistManager** - IP-based access control
- **HoneypotProtection** - Bot detection
- **FileUploadSecurity** - File validation
- **SecurityHeadersManager** - HTTP headers
- **SessionSecurityManager** - Session protection

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Enable Global Middleware

```python
# settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # Add shared security middleware (AFTER session middleware)
    'apps.shared_security.middleware.BhanjyangSecurityMiddleware',
    'apps.shared_security.middleware.GlobalRateLimitMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    # ... rest of middleware
]
```

### Step 2: Configure Security Settings

```python
# settings.py

# File upload limits
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.pdf']

# IP blacklisting
IP_BLACKLIST_DURATION = 86400  # 24 hours
MAX_VIOLATION_THRESHOLD = 5  # Auto-blacklist after 5 violations

# Session security
SESSION_TIMEOUT_MINUTES = 30
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# Honeypot
HONEYPOT_FIELD_NAME = 'website'

# Rate limiting (customize per app)
GLOBAL_RATE_LIMITS = {
    r'/contact/.*': 5,  # 5 requests/minute for contact forms
    r'/subscribe/.*': 3,  # 3 requests/minute for subscriptions
    r'/comment/.*': 10,  # 10 requests/minute for comments
}

# Exempt paths from security checks
SECURITY_EXEMPT_PATHS = [
    '/admin/',
    '/static/',
    '/media/',
]
```

### Step 3: Done! ✅

All apps now have baseline security. See below for app-specific enhancements.

---

## 📋 Integration by App

### 🏢 Services App (`apps/services`)

#### Features to Add:
- Honeypot on contact/inquiry forms
- File upload validation for documents
- Rate limiting on inquiry submissions

#### Implementation:

**1. Add honeypot to forms:**

```python
# apps/services/forms.py
from apps.shared_security import HoneypotProtection

class ServiceInquiryForm(forms.Form):
    # ... existing fields ...
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add honeypot field
        self.fields['website'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                'style': 'display:none',
                'tabindex': '-1',
                'autocomplete': 'off'
            })
        )
    
    def clean_website(self):
        """Honeypot validation"""
        if self.cleaned_data.get('website'):
            raise forms.ValidationError("Invalid submission detected")
        return ''
```

**2. Protect views:**

```python
# apps/services/views.py
from apps.shared_security import honeypot_protected, check_request_security

@honeypot_protected
@check_request_security
class ServiceInquiryView(View):
    def post(self, request):
        # ... handle inquiry ...
        pass
```

**3. Add to templates:**

```html
<!-- apps/services/templates/services/inquiry_form.html -->
<form method="post">
    {% csrf_token %}
    
    <!-- Honeypot field -->
    {{ form.honeypot_field_html }}
    
    <!-- Rest of form -->
    {{ form.as_p }}
</form>
```

---

### 📰 About App (`apps/about`)

#### Features to Add:
- File upload validation for team photos
- Form protection for contact forms

#### Implementation:

**1. Validate team photo uploads:**

```python
# apps/about/views.py
from apps.shared_security import FileUploadSecurity

class TeamMemberCreateView(CreateView):
    def form_valid(self, form):
        if 'photo' in self.request.FILES:
            photo = self.request.FILES['photo']
            
            # Validate file
            result = FileUploadSecurity.validate_file_upload(photo)
            if not result['is_valid']:
                form.add_error('photo', result['errors'])
                return self.form_invalid(form)
            
            # Sanitize filename
            photo.name = FileUploadSecurity.sanitize_filename(photo.name)
        
        return super().form_valid(form)
```

**2. Add honeypot to contact forms:**

```python
# apps/about/forms.py
from apps.shared_security import HoneypotProtection

class AboutContactForm(forms.Form):
    # Add honeypot protection
    website = forms.CharField(required=False, widget=forms.HiddenInput())
    
    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError("Invalid submission")
        return ''
```

---

### 📞 Contact App (`apps/contact`)

#### Features to Add:
- Honeypot on all contact forms
- Rate limiting
- Spam detection

#### Implementation:

**1. Enhance contact form:**

```python
# apps/contact/forms.py
from apps.shared_security import HoneypotProtection, IPBlacklistManager

class ContactForm(forms.Form):
    # Existing fields...
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    
    # Honeypot field
    website = forms.CharField(required=False, widget=forms.HiddenInput())
    
    def clean_website(self):
        """Honeypot validation"""
        if self.cleaned_data.get('website'):
            raise forms.ValidationError("Bot detected")
        return ''
    
    def clean_message(self):
        """Basic spam detection"""
        message = self.cleaned_data.get('message', '')
        
        # Check for spam patterns
        spam_keywords = ['viagra', 'casino', 'lottery', 'winner']
        message_lower = message.lower()
        
        spam_count = sum(1 for keyword in spam_keywords if keyword in message_lower)
        if spam_count >= 2:
            raise forms.ValidationError("Message appears to be spam")
        
        return message
```

**2. Protect contact view:**

```python
# apps/contact/views.py
from apps.shared_security import honeypot_protected, check_request_security, get_client_ip, log_security_event

@honeypot_protected
@check_request_security
class ContactFormView(FormView):
    form_class = ContactForm
    
    def form_valid(self, form):
        # Log successful submission
        log_security_event(
            'contact_form_submission',
            {'email': form.cleaned_data['email']},
            self.request
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Log failed submission
        ip = get_client_ip(self.request)
        log_security_event(
            'contact_form_failed',
            {'errors': form.errors.as_json()},
            self.request
        )
        return super().form_invalid(form)
```

**3. Add to template:**

```html
<!-- apps/contact/templates/contact/contact_form.html -->
<form method="post" class="contact-form">
    {% csrf_token %}
    
    <!-- Honeypot field (invisible) -->
    <div style="position:absolute;left:-5000px;" aria-hidden="true">
        {{ form.website }}
    </div>
    
    <!-- Visible fields -->
    <div class="form-group">
        {{ form.name.label_tag }}
        {{ form.name }}
    </div>
    
    <div class="form-group">
        {{ form.email.label_tag }}
        {{ form.email }}
    </div>
    
    <div class="form-group">
        {{ form.message.label_tag }}
        {{ form.message }}
    </div>
    
    <button type="submit">Send Message</button>
</form>
```

---

### 🖼️ Gallery App (`apps/gallery`)

#### Features to Add:
- File upload validation
- Image size limits
- MIME type checking

#### Implementation:

**1. Validate image uploads:**

```python
# apps/gallery/views.py
from apps.shared_security import FileUploadSecurity

class ImageUploadView(CreateView):
    def form_valid(self, form):
        if 'image' in self.request.FILES:
            image = self.request.FILES['image']
            
            # Validate image
            result = FileUploadSecurity.validate_file_upload(
                image,
                allowed_types=['image/jpeg', 'image/png', 'image/webp'],
                max_size=10 * 1024 * 1024  # 10MB for galleries
            )
            
            if not result['is_valid']:
                for error in result['errors']:
                    form.add_error('image', error)
                return self.form_invalid(form)
            
            # Sanitize filename
            image.name = FileUploadSecurity.sanitize_filename(image.name)
        
        return super().form_valid(form)
```

**2. Add form validation:**

```python
# apps/gallery/forms.py
from apps.shared_security import FileUploadSecurity

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['title', 'image', 'description']
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            result = FileUploadSecurity.validate_file_upload(image)
            if not result['is_valid']:
                raise forms.ValidationError(result['errors'])
        return image
```

---

### 📥 Downloads App (`apps/downloads`)

#### Features to Add:
- File upload validation
- Document security
- Download rate limiting

#### Implementation:

**1. Validate document uploads:**

```python
# apps/downloads/views.py
from apps.shared_security import FileUploadSecurity

ALLOWED_DOC_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

class DocumentUploadView(CreateView):
    def form_valid(self, form):
        if 'file' in self.request.FILES:
            file = self.request.FILES['file']
            
            # Validate document
            result = FileUploadSecurity.validate_file_upload(
                file,
                allowed_types=ALLOWED_DOC_TYPES,
                max_size=20 * 1024 * 1024  # 20MB for documents
            )
            
            if not result['is_valid']:
                return JsonResponse({
                    'success': False,
                    'errors': result['errors']
                }, status=400)
            
            # Sanitize filename
            file.name = FileUploadSecurity.sanitize_filename(file.name)
        
        return super().form_valid(form)
```

**2. Rate limit downloads:**

``python
# settings.py
GLOBAL_RATE_LIMITS = {
    r'/downloads/download/.*': 20,  # 20 downloads per minute
}
```

---

### 👤 Dashboard App (`apps/dashboard`)

#### Features to Add:
- Session security (critical for user data)
- Enhanced authentication
- Activity logging

#### Implementation:

**1. Add session security middleware:**

Already enabled globally, but can enhance with dashboard-specific checks:

```python
# apps/dashboard/middleware.py
from apps.shared_security import SessionSecurityManager, log_security_event

class DashboardSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/dashboard/'):
            if request.user.is_authenticated:
                # Stricter timeout for dashboard (15 minutes)
                if not SessionSecurityManager.check_session_timeout(request, 15):
                    from django.contrib.auth import logout
                    logout(request)
                    return redirect('login')
        
        response = self.get_response(request)
        return response
```

**2. Log sensitive operations:**

```python
# apps/dashboard/views.py
from apps.shared_security import log_security_event

class ProfileUpdateView(UpdateView):
    def form_valid(self, form):
        log_security_event(
            'profile_update',
            {
                'user_id': self.request.user.id,
                'fields_changed': list(form.changed_data)
            },
            self.request
        )
        return super().form_valid(form)
```

---

## 🎯 Common Patterns

### Pattern 1: Protect a Form View

```python
from apps.shared_security import honeypot_protected, check_request_security

@honeypot_protected
@check_request_security
def my_form_view(request):
    if request.method == 'POST':
        # Handle form
        pass
    return render(request, 'form.html')
```

### Pattern 2: Validate File Upload

```python
from apps.shared_security import FileUploadSecurity

def handle_upload(request):
    uploaded_file = request.FILES['document']
    
    result = FileUploadSecurity.validate_file_upload(uploaded_file)
    if not result['is_valid']:
        return JsonResponse({'errors': result['errors']}, status=400)
    
    uploaded_file.name = FileUploadSecurity.sanitize_filename(uploaded_file.name)
    # Save file...
```

### Pattern 3: Add Honeypot to Form

```python
# In Form
class MyForm(forms.Form):
    website = forms.CharField(required=False, widget=forms.HiddenInput())
    
    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError("Invalid submission")
        return ''
```

```html
<!-- In Template -->
<form method="post">
    <div style="position:absolute;left:-5000px;">
        {{ form.website }}
    </div>
    <!-- Rest of form -->
</form>
```

### Pattern 4: Log Security Events

```python
from apps.shared_security import log_security_event

log_security_event(
    'suspicious_activity',
    {'detail': 'Multiple failed login attempts'},
    request
)
```

---

## ✅ Integration Checklist

### For Each App:

- [ ] Enable global middleware (settings.py)
- [ ] Add honeypot to public forms
- [ ] Validate file uploads where applicable
- [ ] Add rate limits for sensitive endpoints
- [ ] Log security-relevant events
- [ ] Test with security tests

### Priority Apps:

1. **Contact** - High (public forms, spam target)
2. **Services** - High (inquiry forms)
3. **Dashboard** - High (user data)
4. **Gallery** - Medium (file uploads)
5. **Downloads** - Medium (file uploads)
6. **About** - Low (mostly static)

---

## 🧪 Testing

### Test security for each app:

```bash
# Test shared security module
python manage.py test apps.shared_security

# Test individual app with security
python manage.py test apps.contact
python manage.py test apps.services
```

---

## 📊 Monitoring

### View security events:

```python
from apps.shared_security import log_security_event
from django.core.cache import cache

# Get today's events
events = cache.get(f"security_events_{timezone.now().strftime('%Y%m%d')}", [])

# Filter by type
honeypot_triggers = [e for e in events if e['event_type'] == 'honeypot_filled']
blocked_ips = [e for e in events if e['event_type'] == 'blocked_blacklisted_ip']

print(f"Honeypot triggers: {len(honeypot_triggers)}")
print(f"Blocked IPs: {len(blocked_ips)}")
```

---

## 🔧 Customization Per App

Apps can override default settings:

```python
# settings.py

# Contact app - stricter limits
CONTACT_RATE_LIMIT = 3  # 3 submissions per minute

# Gallery app - larger file size
GALLERY_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Dashboard - shorter session timeout
DASHBOARD_SESSION_TIMEOUT = 15  # 15 minutes
```

---

## 📝 Best Practices

1. **Always use honeypot on public forms**
2. **Validate all file uploads**
3. **Log security-relevant events**
4. **Test with actual attack scenarios**
5. **Review security logs weekly**
6. **Update security settings as needed**

---

**Next:** Choose an app and follow the integration guide above!

**Questions?** Check `SECURITY_QUICK_REFERENCE.md` or review the code in `apps/shared_security/`

---

**Last Updated:** January 6, 2026  
**Version:** 1.0  
**Status:** Ready for Integration
