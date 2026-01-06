# Contact App

**Bhanjyang Cooperative Contact & Feedback Management System**

Handle all contact, feedback, and Right to Information (RTI) requests for Bhanjyang Saving & Credit Cooperative Society Ltd.

---

## 📋 Overview

The Contact app provides a comprehensive communication channel between Bhanjyang Cooperative and its members, visitors, and stakeholders. Features include a modern contact form, RTI officer information, interactive map, and automated email notifications.

---

## ✨ Features

### Core Functionality
- 📧 **Contact Form** - Modern, accessible form with real-time validation
- 🔐 **Security** - CSRF protection, file validation, spam detection
- ✉️ **Email Notifications** - Automated emails via Celery tasks
- 🗺️ **Interactive Map** - Toggle between Main Office and Service Center
- ⚖️ **RTI Compliance** - Information Officer details per Nepal's RTI Act 2064
- 💾 **Auto-Save** - Form data persists in localStorage
- 📎 **File Attachments** - Support for PDF, DOC, JPG, PNG (max 5MB)

### Technical Features
- Service layer architecture
- Celery background tasks
- Performance monitoring
- Comprehensive testing (12+ test files)
- Responsive design
- Nepali language support

---

## 📦 Installation

### Prerequisites
```bash
# Django 5.2+
# Celery with Redis
# Email backend configured
```

### Setup
```bash
# 1. Migrations
python manage.py makemigrations contact
python manage.py migrate contact

# 2. Collect static files
python manage.py collectstatic
```

---

## 🗂️ Models

### ContactSubmission
Stores all contact form submissions.

**Fields:**
- `name`, `email`, `phone` (optional)
- `subject`, `message`
- `attachment` (optional, max 5MB)
- `submitted_at`, `ip_address`, `user_agent`
- `status` (pending, replied, spam)

### InformationOfficer
RTI Act 2064 compliance - सूचना अधिकारी

**Fields:**
- `person` (ForeignKey to StaffMember)
- `position`, `appointed_date`, `is_active`
- `rti_email`

---

## 🎨 Views

- **ContactView** - `/contact/` (GET, POST)
- **PrivacyPolicyView** - `/contact/privacy/`

---

## 🔧 Services

### ContactService
Process submissions and send notifications.

```python
result = ContactService.process_submission(form_data, request)
```

---

## 🔒 Security

**Implemented:**
- CSRF tokens
- File validation
- XSS prevention
- Input sanitization

**Planned (P2):**
- Rate limiting
- Honeypot field
- IP blacklisting

See [SECURITY.md](SECURITY.md)

---

## 🧪 Testing

```bash
python manage.py test apps.contact
```

**Coverage:** ~80%

---

## 📚 Usage

See templates and services for implementation examples.

---

**Last Updated:** January 6, 2026  
**Status:** ✅ Production Ready  
**Score:** Improving to 98/100
