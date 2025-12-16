# API Authentication

Documentation for API authentication and authorization.

## Authentication Methods

### 1. Session Authentication

For web applications using the same domain:

```python
import requests

session = requests.Session()
session.get('http://api.example.com/api/endpoint/')
```

### 2. Token Authentication

For API clients:

```python
import requests

headers = {
    'Authorization': 'Token your-token-here'
}
response = requests.get('http://api.example.com/api/endpoint/', headers=headers)
```

### 3. Basic Authentication

For simple API access:

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    'http://api.example.com/api/endpoint/',
    auth=HTTPBasicAuth('username', 'password')
)
```

## Getting an API Token

1. Log in to the admin panel
2. Navigate to your user profile
3. Generate an API token
4. Use the token in API requests

## Token Usage

Include the token in the Authorization header:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Rate Limiting

Authenticated requests have higher rate limits:
- **Unauthenticated:** 60 requests/hour
- **Authenticated:** 1000 requests/hour

## Security Best Practices

1. **Never commit tokens** to version control
2. **Use environment variables** for tokens
3. **Rotate tokens** regularly
4. **Use HTTPS** in production
5. **Implement token expiration**

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

