# Complete Project Recreation Guide for Bhanjyang Cooperative Website

## Overview
This is a comprehensive guide to recreate the exact Bhanjyang Cooperative website project. This document contains every detail you need to rebuild this Django-based cooperative management system from scratch.

## Project Information
- **Project Name**: Bhanjyang Saving & Credit Cooperative Society Ltd. (भञ्ज्याङ सहकारी)
- **Framework**: Django 5.2.3
- **Styling**: Tailwind CSS 4.1.10
- **Database**: SQLite (development), PostgreSQL (production)
- **Cache**: Redis
- **Task Queue**: Celery
- **Language Support**: English and Nepali

## Table of Contents
1. [Project Structure](#project-structure)
2. [Environment Setup](#environment-setup)
3. [Core Dependencies](#core-dependencies)
4. [Application Architecture](#application-architecture)
5. [Detailed App Implementation](#detailed-app-implementation)
6. [Settings Configuration](#settings-configuration)
7. [Templates and Frontend](#templates-and-frontend)
8. [Static Files Configuration](#static-files-configuration)
9. [Security Features](#security-features)
10. [Performance Optimization](#performance-optimization)
11. [Deployment Configuration](#deployment-configuration)

---

## Project Structure

```
Bhanjyang/
├── apps/
│   ├── __init__.py
│   ├── about/          # About us, team management, cooperative info
│   ├── contact/        # Contact form with attachments
│   ├── core/           # Core utilities, security, health checks
│   ├── dashboard/      # Performance monitoring dashboard
│   ├── downloads/       # File download management
│   ├── home/           # Home page functionality
│   ├── news_events/    # News and events management
│   ├── search/         # Global search functionality
│   └── services/       # Financial services (savings, loans, etc.)
├── coop/               # Main Django project folder
│   ├── settings.py     # Main settings
│   ├── settings_dev.py # Development settings
│   ├── production.py    # Production settings
│   ├── urls.py         # Main URL routing
│   ├── urls_api.py     # API URL routing
│   ├── asgi.py         # ASGI configuration
│   ├── wsgi.py         # WSGI configuration
│   └── celery.py       # Celery configuration
├── gallery/            # Dedicated gallery app
├── members/            # Member management system
├── templates/           # Global templates
│   ├── base.html       # Base template
│   ├── 403.html, 404.html, 500.html
│   └── partials/       # Header, footer, etc.
├── static/             # Static files
│   ├── css/
│   ├── js/
│   ├── images/
│   ├── dist/          # Compiled Tailwind CSS
│   └── favicon/
├── media/             # User uploaded files
├── logs/              # Log files
├── config/            # Configuration files
├── docs/              # Documentation
├── scripts/           # Utility scripts
├── manage.py
├── requirements.txt
├── requirements-dev.txt
├── package.json
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── env.template
```

---

## Environment Setup

### Step 1: Create Python Virtual Environment

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Production dependencies
pip install Django>=5.2.7,<5.3
pip install python-decouple>=3.8
pip install Pillow>=12.0.0
pip install django-crispy-forms>=2.0
pip install crispy-tailwind>=0.5.0
pip install django-ckeditor>=6.7.0
pip install django-cleanup>=8.1.0
pip install whitenoise>=6.11.0
pip install gunicorn>=21.2.0
pip install bleach>=6.1.0
pip install django-ratelimit>=3.0.0
pip install redis>=4.0.0
pip install celery>=5.3.0
pip install python-magic>=0.4.27
pip install psycopg2-binary>=2.9.0
pip install djangorestframework>=3.16.0
pip install django-filter>=25.0
pip install django-redis>=5.4.0
pip install django-cors-headers>=4.3.0
pip install drf-spectacular>=0.26.0
pip install sentry-sdk[django]>=1.38.0
pip install django-extensions>=3.2.0
pip install django-debug-toolbar>=4.2.0
```

### Step 3: Node.js Setup

```bash
npm install
```

Install packages:
- @tailwindcss/cli: ^4.1.10
- tailwindcss: ^4.1.10
- rimraf: ^6.0.1 (dev dependency)

### Step 4: Create Environment File

Copy `env.template` to `.env` and configure:

```env
# Security
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=bhanjyang_coop
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
SEND_REAL_EMAILS=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

---

## Core Dependencies

### Complete requirements.txt:

```
Django>=5.2.7,<5.3
python-decouple>=3.8
Pillow>=12.0.0
django-crispy-forms>=2.0
crispy-tailwind>=0.5.0
django-ckeditor>=6.7.0
django-cleanup>=8.1.0
whitenoise>=6.11.0
gunicorn>=21.2.0
bleach>=6.1.0
django-ratelimit>=3.0.0
redis>=4.0.0
celery>=5.3.0
python-magic>=0.4.27
psycopg2-binary>=2.9.0
djangorestframework>=3.16.0
django-filter>=25.0
django-redis>=5.4.0
django-cors-headers>=4.3.0
drf-spectacular>=0.26.0
sentry-sdk[django]>=1.38.0
django-extensions>=3.2.0
django-debug-toolbar>=4.2.0
```

### package.json:

```json
{
  "name": "bhanjyang-cooperative",
  "version": "1.0.0",
  "description": "Bhanjyang Cooperative website with Django and Tailwind CSS",
  "scripts": {
    "dev": "npx @tailwindcss/cli -i ./static/css/input.css -o ./static/dist/output.css --watch",
    "build": "npx @tailwindcss/cli -i ./static/css/input.css -o ./static/dist/output.css --minify",
    "build:watch": "npx @tailwindcss/cli -i ./static/css/input.css -o ./static/dist/output.css --watch --minify",
    "clean": "rimraf ./static/dist",
    "start": "python manage.py runserver",
    "migrate": "python manage.py migrate",
    "makemigrations": "python manage.py makemigrations",
    "collectstatic": "python manage.py collectstatic --noinput",
    "test": "python manage.py test",
    "shell": "python manage.py shell",
    "install": "npm install",
    "build:prod": "npm run build && npm run collectstatic"
  },
  "dependencies": {
    "@tailwindcss/cli": "^4.1.10",
    "tailwindcss": "^4.1.10"
  },
  "devDependencies": {
    "rimraf": "^6.0.1"
  },
  "keywords": [
    "django",
    "tailwindcss",
    "cooperative",
    "nepal"
  ],
  "author": "Bhanjyang Cooperative",
  "license": "MIT",
  "engines": {
    "node": ">=18.0.0"
  }
}
```

---

## Application Architecture

### INSTALLED_APPS Order (Critical for proper initialization):

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'apps.core',                    # Core utilities FIRST
    'apps.home',
    'apps.about',                   # About Us (includes team)
    'apps.contact',
    'apps.news_events',
    'apps.downloads',
    'apps.services',
    'apps.search',
    'apps.dashboard',
    'gallery.apps.GalleryConfig',  # Gallery
    'members',                      # Members (commented out for migration issues)
    'django.contrib.staticfiles',
]
```

### MIDDLEWARE Stack:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.core.middleware.SecurityHeadersMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.RateLimitMiddleware',
    'apps.core.middleware.InputValidationMiddleware',
    'apps.core.middleware.BruteForceProtectionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.dashboard.middleware.PerformanceMonitoringMiddleware',
]
```

---

## Detailed App Implementation

### 1. CORE App (apps/core/)

**Purpose**: Core utilities, security, and health checks

**Models** (`apps/core/models.py`):
- `APIKey`: For API authentication
- `SecurityLog`: Security event logging

**Key Files**:
- `middleware.py`: Custom middleware for security
- `security_middleware.py`: Advanced security features
- `security_decorators.py`: Security decorators
- `security_admin.py`: Security admin interface
- `admin_site.py`: Custom admin site
- `admin.py`: APIKey and SecurityLog admin
- `health_views.py`: Health check endpoints
- `urls.py`: Health check routes

**Security Features**:
- Rate limiting per IP
- Input validation
- Brute force protection
- Security headers middleware
- API key management

**Health Endpoints**:
- `/health/` - General health check
- `/health/readiness/` - Kubernetes readiness probe
- `/health/liveness/` - Kubernetes liveness probe
- `/health/metrics/` - Application metrics

### 2. ABOUT App (apps/about/)

**Purpose**: About us content, team management, cooperative information

**Models**:
- `CooperativeInfo`: Main cooperative information
- `CooperativeTimeline`: Timeline events
- `CooperativeAchievement`: Awards and achievements
- `CooperativeStatistic`: Display statistics
- `CooperativeAffiliation`: Partnerships and affiliations
- `LeadershipMessage`: Messages from leadership
- `Person`: People in the cooperative
- `Committee`: Committees with tenure
- `Membership`: Links Person to Committee
- `Staff`: Staff members

**Features**:
- Bilingual support (English/Nepali)
- Team management with committees
- Timeline display
- Achievement showcase
- Leadership messages

**Key Files**:
- `models.py`: All models listed above
- `views.py`: Display views
- `admin.py`: Admin configuration
- `forms.py`: Forms for editing
- `serializers.py`: API serializers
- `api_views.py`: API endpoints
- `cache_utils.py`: Cache utilities
- `analytics.py`: Analytics for team page
- `map_views.py`: Map-related views

**Templates**: 12 HTML files in `templates/about/`

**Custom Templatetags**: `about_extras.py`

### 3. CONTACT App (apps/contact/)

**Purpose**: Contact form with file uploads

**Model**: `ContactSubmission`
- Status tracking (new, in_progress, resolved, spam)
- File attachment support
- IP and user agent tracking
- Security features

**Features**:
- File upload with security validation
- Status management
- Spam detection
- Email notifications
- Admin notes

**Key Files**:
- `models.py`: ContactSubmission model
- `views.py`: Submit and list views
- `forms.py`: Contact form
- `tasks.py`: Celery tasks for email
- `performance.py`: Performance optimization
- `test_security.py`: Security tests
- `security.py`: Security validators

**Management Commands**:
- Clean old submissions
- Export submissions

### 4. NEWS & EVENTS App (apps/news_events/)

**Purpose**: News articles and events management

**Models**:
- `Category`: News categories
- `NewsArticle`: News articles with status, priority, SEO
- `Event`: Events with registration
- `Subscriber`: Newsletter subscribers
- `Comment`: Article comments
- `Newsletter`: Newsletter campaigns
- `ContentAnalytics`: Analytics tracking

**Features**:
- Article management (Draft, Published, Archived, Scheduled)
- SEO fields (meta_title, meta_description, meta_keywords)
- Reading time calculation
- View/share/comment counts
- Content hash for security
- Featured articles
- Comment moderation
- Newsletter system
- Analytics tracking

**Key Files**:
- `models.py`: All models
- `views.py`: Article and event views
- `forms.py`: Article editing forms
- `admin.py`: Admin configuration
- `performance.py`: Performance optimization
- `security.py`: Security features

**Management Commands**:
- Publish scheduled articles
- Send newsletters
- Clean analytics

### 5. DOWNLOADS App (apps/downloads/)

**Purpose**: File download management

**Model**: `DownloadableFile`
- Categories (Form, Report, Policy, Publication, Manual, Certificate, Brochure, Other)
- Priority levels (Low, Medium, High, Urgent)
- File validation
- Download/view tracking
- Security hash
- Expiration dates

**Features**:
- File categorization
- Priority-based display
- Download analytics
- File size display
- Expiration handling
- Access control

**Key Files**:
- `models.py`: DownloadableFile model
- `views.py`: Download views
- `admin.py`: Admin configuration
- `context_processors.py`: Admin stats context
- `performance.py`: Performance optimization
- `security.py`: File security validation
- `tests.py`: Test suite

**Management Commands**:
- Clean expired files
- Generate download reports

### 6. SERVICES App (apps/services/)

**Purpose**: Financial services management

**Models**:
- `BaseServiceModel`: Abstract base for services
- `SavingsAccount`: Various savings account types
- `FixedDeposit`: Fixed deposit schemes
- `LoanType`: Different loan types
- `RemittanceService`: Money transfer services
- `MemberRelief`: Relief and support programs
- `ServiceApplication`: Track service applications
- `ServiceAnalytics`: Service analytics
- `ServiceRecommendation`: Service recommendations

**Features**:
- Bilingual service names
- Interest rate management
- Feature lists
- Requirements tracking
- Application tracking
- Analytics

**Key Files**:
- `models.py`: All service models
- `views.py`: Service display views
- `forms.py`: Application forms
- `admin.py`: Admin configuration
- `serializers.py`: API serializers
- `api_views.py`: API endpoints
- `utils.py`: Utility functions

**Templates**: 14 HTML files

### 7. GALLERY App (gallery/)

**Purpose**: Image gallery with advanced features

**Models**:
- `GalleryAlbum`: Album organization with hierarchy
- `GalleryImage`: Images with AI features
- `GalleryImageLike`: Like tracking
- `GalleryImageComment`: Comment system
- `GalleryImageShare`: Share tracking
- `GalleryImageDownload`: Download tracking
- `SmartCollection`: AI-powered collections
- `SmartCollectionImage`: Collection images
- `AutoCategorizationRule`: Auto categorization rules
- `ImageAnalysisJob`: Background analysis jobs

**AI Features**:
- AI tags
- AI descriptions
- AI color palette detection
- AI object detection
- AI scene type detection
- AI sentiment analysis
- AI quality scoring

**Social Features**:
- Likes, shares, views, comments
- Public/private visibility
- Comment control
- Download permissions

**Key Files**:
- `models.py`: All gallery models
- `constants.py`: Image size/dimension constants
- `views.py`: Gallery views
- `admin.py`: Admin configuration
- `urls.py`: Gallery routes

**Templates**: 10 HTML files

**Management Commands**: 9 commands for gallery management

### 8. MEMBERS App (members/)

**Purpose**: Member management and CBS integration

**Models**:
- `Ward`: Location-based wards
- `MemberRegistration`: Pre-membership registration
- `Member`: Active members
- `KYCDocument`: KYC documents
- `MemberAccount`: Financial accounts
- `MemberTransaction`: Transaction history
- `MemberLoan`: Loan management
- `MemberNotification`: Notifications

**Features**:
- Location verification (Rupa RM)
- Two-step registration (Location → KYC)
- CBS integration for financial data
- Account management
- Transaction tracking
- Loan applications
- Notification system

**Key Files**:
- `models.py`: All member models
- `managers.py`: Custom managers
- `services/`: Business logic (6 services)
- `repositories/`: Data access (4 repositories)
- `dto/`: Data transfer objects (6 DTOs)
- `validators/`: Custom validators (4 validators)
- `permissions.py`: Permission management
- `middleware.py`: Member-specific middleware
- `forms.py`: Registration forms
- `serializers.py`: API serializers

**Directory Structure**:
```
members/
├── services/        # Business logic
├── repositories/    # Data access
├── dto/             # Data transfer objects
├── exceptions/      # Custom exceptions
├── integrations/    # External integrations
└── validators/      # Custom validators
```

### 9. DASHBOARD App (apps/dashboard/)

**Purpose**: Performance monitoring and analytics

**Models**:
- `PerformanceMetric`: Performance tracking
- `PageView`: Page view analytics
- `ErrorLog`: Error tracking
- `UserSession`: Session tracking
- `PerformanceReport`: Generated reports
- `PerformanceAlert`: Alert configuration
- `AlertLog`: Triggered alerts
- `DashboardWidget`: Widget configuration
- `UserDashboardPreference`: User preferences
- `AuditLog`: Security audit logs

**Features**:
- Real-time performance monitoring
- Error tracking
- User behavior analytics
- Customizable dashboard
- Alert system
- Report generation

**Key Files**:
- `models.py`: All dashboard models
- `views.py`: Dashboard views
- `middleware.py`: Performance monitoring middleware
- `consumers.py`: WebSocket consumers
- `cache_utils.py`: Cache utilities
- `security.py`: Security features

**Templates**: 5 HTML files

**Management Commands**: 6 commands

### 10. HOME App (apps/home/)

**Purpose**: Home page and landing features

**Features**:
- Hero section
- Featured content display
- Service highlights
- News/events preview
- Gallery preview

**Key Files**:
- `views.py`: Home page view
- `models.py`: Home-specific models
- `forms.py`: Contact/newsletter forms
- `urls.py`: Home routes

**Templates**: 3 HTML files

### 11. SEARCH App (apps/search/)

**Purpose**: Global search functionality

**Features**:
- Full-text search
- Multi-model search
- Search suggestions
- Search analytics

**Key Files**:
- `models.py`: Search models
- `views.py`: Search views
- `forms.py`: Search form
- `templatetags/`: Search template tags

**Templates**: 2 HTML files

---

## Settings Configuration

### Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production (use PostgreSQL):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

### Cache Configuration

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_sessions',
        'TIMEOUT': 1209600,
    },
    'performance': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'performance-cache',
        'TIMEOUT': 600,
    }
}
```

### Static Files

```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Security Settings

```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
```

### Celery Configuration

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60
```

### Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '[{asctime}] {levelname} {name} {process:d} {thread:d} {pathname}:{lineno:d} {funcName}() {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django_error.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'performance': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'performance.log',
            'maxBytes': 1024*1024*10,
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {'handlers': ['file', 'console'], 'level': 'INFO'},
        'django.request': {'handlers': ['error_file', 'console'], 'level': 'ERROR'},
        'coop': {'handlers': ['file', 'console'], 'level': 'INFO'},
        'performance': {'handlers': ['performance'], 'level': 'INFO'},
    },
}
```

---

## Templates and Frontend

### Base Template Structure

The `templates/base.html` includes:
- Meta tags (SEO, Open Graph, Twitter Cards)
- Structured data (JSON-LD)
- Tailwind CSS compilation
- Alpine.js for interactivity
- GSAP for animations
- Custom CSS files:
  - animations.css
  - about-animations.css
  - advanced-animations.css
  - dark-mode.css
  - gallery-lightbox.css
- Custom JS files:
  - performance-monitor.js
  - animations.js
  - gsap-init.js
  - pwa-installer.js
  - dark-mode.js
  - advanced-animations.js

### Key Template Features

1. **Responsive Navigation**: Mobile-first with hamburger menu
2. **Breadcrumbs**: Automatic breadcrumb navigation
3. **Notice Toast System**: Sticky notifications
4. **PWA Support**: Service worker, manifest.json
5. **Dark Mode**: Toggle support
6. **Animations**: GSAP-powered animations
7. **Bilingual**: Nepali and English content support

### Static Files Organization

```
static/
├── css/
│   ├── input.css (Tailwind source)
│   ├── animations.css
│   ├── about-animations.css
│   ├── advanced-animations.css
│   ├── dark-mode.css
│   ├── gallery-lightbox.css
│   └── components/
├── js/
│   ├── animations.js
│   ├── advanced-animations.js
│   ├── performance-monitor.js
│   ├── dark-mode.js
│   ├── gsap-init.js
│   ├── pwa-installer.js
│   └── components/
├── images/
├── dist/ (compiled CSS)
├── favicon/
└── vendor/
```

---

## Security Features

### 1. Core Security Middleware

**Rate Limiting**: Prevents abuse with per-IP limits
**Input Validation**: Sanitizes all user input
**Brute Force Protection**: Monitors login attempts
**Security Headers**: CSP, HSTS, XSS protection

### 2. File Upload Security

- File type validation
- Size limits (10MB for images)
- File hash generation
- Path sanitization
- MIME type checking

### 3. API Security

- API key authentication
- Rate limiting per key
- Token expiration
- Request signing

### 4. Session Security

- Secure session cookies
- CSRF protection
- IP-based session validation
- Session timeout

---

## Performance Optimization

### 1. Caching Strategy

- Page-level caching (5 minutes)
- Query result caching
- Fragment caching for expensive queries
- Cache invalidation signals

### 2. Database Optimization

- Selective prefetch_related and select_related
- Database indexes on frequently queried fields
- Query optimization
- Connection pooling

### 3. Static Files

- WhiteNoise for serving static files
- Compression (gzip/brotli)
- CDN integration ready
- Image optimization

### 4. Celery Tasks

- Async email sending
- Image processing
- Report generation
- Cleanup jobs

---

## Deployment Configuration

### Dockerfile (Multi-stage)

```dockerfile
# Stage 1: Frontend build
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY package*.json ./
RUN npm ci --only=production
COPY static/ ./static/
RUN npm run build

# Stage 2: Python application
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client redis-tools curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Copy frontend assets
COPY --from=frontend-builder /app/frontend/static/dist/ ./static/dist/

# Create directories
RUN mkdir -p logs media staticfiles backups
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "coop.wsgi:application"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: bhanjyang_coop
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  web:
    build: .
    command: sh -c "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - SECRET_KEY=dev-secret-key
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A coop worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    command: celery -A coop beat -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:
```

### Makefile Commands

```makefile
dev: ## Start development server
	python manage.py runserver

test: ## Run tests
	python manage.py test

test-coverage: ## Run tests with coverage
	coverage run --source='.' manage.py test
	coverage report

lint: ## Run linting
	flake8 apps/
	mypy apps/

format: ## Format code
	black apps/
	isort apps/

docker-compose-up: ## Start with Docker Compose
	docker-compose up -d

quick-start: ## Complete setup
	make dev-install
	make migrate
	make build-css
	make superuser
```

---

## URL Configuration

### Main URLs (coop/urls.py)

```python
urlpatterns = [
    path('admin/', admin_site.urls),
    path('about/', include('apps.about.urls')),
    path('search/', include('apps.search.urls')),
    path('contact/', include('apps.contact.urls')),
    path('news-events/', include('apps.news_events.urls')),
    path('downloads/', include('apps.downloads.urls')),
    path('services/', include('apps.services.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('gallery/', include('gallery.urls')),
    path('members/', include('members.urls')),
    path('health/', include('apps.core.urls')),
    path('', include('apps.home.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Key Configuration Details

### 1. Language and Timezone

```python
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
```

### 2. Authentication

```python
AUTH_USER_MODEL = 'members.MemberUser'  # Temporarily commented out
LOGIN_URL = '/members/login/'
LOGIN_REDIRECT_URL = '/members/dashboard/'
LOGOUT_REDIRECT_URL = '/members/login/'
```

### 3. Password Validation

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### 4. File Upload Settings

```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
FILE_UPLOAD_PERMISSIONS = 0o644
```

---

## Critical Implementation Notes

### 1. App Initialization Order

The INSTALLED_APPS order is critical:
- `apps.core` must be first for middleware
- User model apps before apps that reference users
- Static files must be last

### 2. Middleware Order

Middleware stack order is critical for proper security:
1. Security headers first
2. WhiteNoise for static files
3. Session after authentication
4. Custom middleware after core
5. Performance monitoring last

### 3. Template Context Processors

```python
'context_processors': [
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'apps.downloads.context_processors.admin_stats',
]
```

### 4. Custom Admin Site

Using custom admin site (`apps.core.admin_site`) for:
- Custom branding
- Enhanced security
- Custom dashboard

---

## Testing and Quality

### Running Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.services

# With coverage
coverage run --source='.' manage.py test
coverage report
```

### Code Quality

```bash
# Format code
black apps/
isort apps/

# Lint
flake8 apps/
mypy apps/

# Security
bandit -r apps/
safety check
```

---

## Important Files and Their Purpose

1. **manage.py**: Django management commands
2. **coop/settings.py**: Main configuration
3. **coop/urls.py**: URL routing
4. **coop/celery.py**: Celery configuration
5. **coop/asgi.py**: ASGI for WebSocket support
6. **templates/base.html**: Base template
7. **static/css/input.css**: Tailwind source
8. **static/css/dist/output.css**: Compiled CSS
9. **Makefile**: Development commands
10. **Dockerfile**: Container build

---

## Final Setup Steps

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Build CSS**:
   ```bash
   npm run build
   ```

5. **Collect Static**:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Start Server**:
   ```bash
   python manage.py runserver
   ```

7. **Access Admin**:
   ```
   http://localhost:8000/admin/
   ```

---

## Support and Documentation

- **Main README**: `docs/README.md`
- **Gallery Documentation**: `docs/GALLERY_MASTER_DOCUMENTATION.md`
- **Image Guidelines**: `docs/IMAGE_UPLOAD_GUIDELINES.md`
- **Performance Guide**: `docs/PERFORMANCE_MONITORING_GUIDE.md`
- **Error Reporting**: `docs/ERROR_REPORTING_GUIDE.md`

---

This document provides every detail needed to recreate this project exactly as it is. Follow each section carefully, and you'll have an identical copy of the Bhanjyang Cooperative website.

