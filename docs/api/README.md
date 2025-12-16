# API Documentation

This directory contains API documentation for the Bhanjyang Cooperative project.

## Structure

```
api/
├── README.md                # This file
├── endpoints.md             # API endpoints reference
├── authentication.md        # Authentication & authorization
├── examples.md              # API usage examples
└── changelog.md             # API version changelog
```

## API Overview

The Bhanjyang Cooperative API provides programmatic access to various features:

- **News & Events API** - Access news articles and events
- **Services API** - Financial services information
- **Downloads API** - File download management
- **Gallery API** - Image gallery access
- **Contact API** - Contact form submissions

## Base URL

- **Development:** `http://127.0.0.1:8000/api/`
- **Production:** `https://yourdomain.com/api/`

## Authentication

Most API endpoints require authentication. See [authentication.md](./authentication.md) for details.

## Response Format

All API responses follow a standard format:

```json
{
    "success": true,
    "data": { ... },
    "message": "Operation successful"
}
```

Error responses:

```json
{
    "success": false,
    "error": "Error message",
    "errors": { ... }
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse. See individual endpoint documentation for limits.

## Versioning

The API is versioned. Current version: **v1**

## Getting Started

1. Read [authentication.md](./authentication.md) for authentication setup
2. Check [endpoints.md](./endpoints.md) for available endpoints
3. See [examples.md](./examples.md) for usage examples

## Support

For API support, contact: api@bhanjyang.coop.np

