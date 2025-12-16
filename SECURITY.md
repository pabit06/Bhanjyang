# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| v1.x    | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Bhanjyang Cooperative's digital infrastructure seriously. If you discover a security vulnerability, please follow these steps:

1.  **Do not disclose publically** until we have had a chance to fix it.
2.  **Email us** at `security@bhanjyangcoop.com` (or the generic developer contact).
3.  Include a proof of concept or detailed steps to reproduce the issue.

We will acknowledge your report within 48 hours and provide a timeline for a fix.

## Security Measures

This application implements several layers of security to protect user data and administrative access:

### 1. Two-Factor Authentication (2FA)
- Admin accounts require TOTP-based 2FA (e.g., Google Authenticator, Authy).
- Brute-force protection is enabled on login endpoints.

### 2. Content Security Policy (CSP)
- A strict CSP is enforced to prevent Cross-Site Scripting (XSS) attacks.
- Only trusted sources (self, safe-inline for specific needs) are allowed.

### 3. Rate Limiting
- Global and per-endpoint rate limits are applied to prevent abuse and DoS attacks.
- API keys are rate-limited by hour and day.

### 4. Data Protection
- Passwords are hashed using PBKDF2 with SHA256.
- All sessions are encrypted and stored securely (Redis/DB).
- HTTPS is enforced in production.

## Developers

Please refer to `docs/production.md` for secure deployment guidelines.
