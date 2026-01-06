# Contact API Documentation

## Overview
REST API endpoints for Contact app (Planned - Priority 3)

**Base URL:** `/api/v1/contact/`  
**Auth:** Session or Token  
**Format:** JSON

---

## 📍 Endpoints

### 1. Submit Contact Form
**POST** `/api/v1/contact/submit/`

Submit a contact form programmatically.

**Request:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+977-9841234567",
    "subject": "Query about services",
    "message": "I would like to know more about your savings accounts.",
    "attachment": null
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Thank you! We'll respond within 24-48 hours.",
    "submission_id": 123
}
```

**Response (Error):**
```json
{
    "success": false,
    "errors": {
        "email": ["Invalid email format"],
        "message": ["Message too short (min 10 chars)"]
    }
}
```

**Rate Limit:** 5 requests/hour  
**Auth Required:** No

---

### 2. Get RTI Officer
**GET** `/api/v1/contact/officer/`

Get current Right to Information Officer details.

**Response:**
```json
{
    "full_name": "सोचना श्रेष्ठ",
    "position": "सूचना अधिकारी",
    "email": "rti@bhanjyang.coop.np",
    "phone": "+977-9856083101",
    "photo_url": "/media/staff/sochana.jpg",
    "appointed_date": "2024-01-15"
}
```

**Rate Limit:** 100 requests/hour  
**Auth Required:** No

---

### 3. Get Privacy Policy
**GET** `/api/v1/contact/privacy/`

Get current privacy policy content.

**Response:**
```json
{
    "title": "Privacy Policy",
    "content": "...",
    "last_updated": "2026-01-01",
    "version": "2.0"
}
```

**Rate Limit:** 100 requests/hour  
**Auth Required:** No

---

## 🔧 Usage Examples

### Python (requests)
```python
import requests

# Submit contact form
response = requests.post(
    'http://localhost:8000/api/v1/contact/submit/',
    json={
        'name': 'John Doe',
        'email': 'john@example.com',
        'subject': 'Inquiry',
        'message': 'Hello, I need information about...'
    }
)

print(response.json())
```

### JavaScript (fetch)
```javascript
// Submit contact form
fetch('/api/v1/contact/submit/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        name: 'John Doe',
        email: 'john@example.com',
        subject: 'Inquiry',
        message: 'Hello, I need...'
    })
})
.then(res => res.json())
.then(data => console.log(data));
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/contact/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Inquiry",
    "message": "Hello, I need information..."
  }'
```

---

## 🔐 Authentication

### Session Auth
Use Django session cookies (default for web).

### Token Auth
```bash
# Get token (admin users only)
curl -X POST /api/token/ \
  -d "username=admin&password=xxx"

# Use token
curl -H "Authorization: Token abc123..." \
  /api/v1/contact/submit/
```

---

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 429 | Rate Limit Exceeded |
| 500 | Server Error |

---

## 🎯 Coming Soon

- File upload via API
- Submission status check
- Admin endpoints (list, update submissions)
- Webhook notifications

---

**Status:** 📋 Planned for Priority 3  
**ETA:** 2 hours implementation
