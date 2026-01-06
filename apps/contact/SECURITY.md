# Contact App Security

## 🔒 Implemented Features

### 1. CSRF Protection
- All forms include CSRF tokens
- Django middleware validates tokens
- Prevents cross-site request forgery

### 2. File Upload Security
```python
# Allowed extensions
ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.png']

# Max file size
MAX_SIZE = 5MB

# Validation in forms.py
```

### 3. XSS Prevention
- Template auto-escaping enabled
- User input sanitized
- Django's built-in protections

### 4. Input Validation
- Email format validation
- Phone number validation (Nepal format)
- Message length requirements
- Subject length limits

### 5. Spam Detection
```python
# Basic spam scoring
- Check spam keywords
- Message length analysis
- Submission frequency tracking
```

---

## 🔜 Planned Features (Priority 2)

### 1. Rate Limiting
```python
# Planned implementation
- 5 submissions per hour per IP
- Cooldown period: 1 hour
- Admin bypass
```

### 2. Honeypot Field
```python
# Hidden field for bot detection
- Invisible to users
- Filled by bots
- Auto-reject if filled
```

### 3. IP Blacklisting
- Integration with downloads security module
- Automatic blacklist after abuse
- Time-based expiration

### 4. Advanced Spam Detection
- AI-based scoring
- Pattern recognition
- Learning from flagged spam

---

## 📋 Security Best Practices

### For Administrators
- Review submissions regularly
- Flag spam promptly
- Monitor for abuse patterns
- Update spam keyword list

### For Developers
- Always validate user input
- Use parameterized queries
- Keep dependencies updated
- Follow OWASP guidelines

---

## 🚨 Security Incidents

### Reporting
**Email:** security@bhanjyang.coop.np  
**Response Time:** Within 24 hours

### Process
1. Report received
2. Investigation (< 24h)
3. Fix deployed (<  48h)
4. Disclosure (after fix)

---

## 📊 Security Metrics

**Current Score:** 70/100  
**Target Score:** 98/100 (after P2)

**Improvements Needed:**
- Rate limiting: +15 points
- Honeypot: +8 points
- IP blacklist: +5 points

---

**Last Updated:** January 6, 2026  
**Status:** Improving to enterprise-grade
