"""
Development settings for Bhanjyang Cooperative project.
Optimized for development with lighter middleware and better debugging.
"""

from .settings import *

# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.82', '192.168.1.117']

# Disable heavy middleware in development for better performance
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Removed heavy middleware for development:
    # - SecurityHeadersMiddleware (can be slow)
    # - RateLimitMiddleware (not needed in dev)
    # - InputValidationMiddleware (can be slow)
    # - BruteForceProtectionMiddleware (not needed in dev)
    # - PerformanceMonitoringMiddleware (can be slow)
]

# Disable security features for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Simplified cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'dev-cache',
        'TIMEOUT': 60,  # Shorter timeout for development
        'OPTIONS': {
            'MAX_ENTRIES': 100,  # Smaller cache for development
            'CULL_FREQUENCY': 2,
        }
    }
}

# Disable Celery async processing in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Development email backend (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Simplified logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Development-specific settings
print("=" * 50)
print(" DEVELOPMENT MODE ACTIVE")
print(" - Heavy middleware disabled")
print(" - Security features relaxed")
print(" - Console email backend")
print(" - Simplified logging")
print("=" * 50)
