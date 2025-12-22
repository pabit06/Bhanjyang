# भञ्ज्याङ सहकारी (Bhanjyang Cooperative)

A modern, enterprise-grade website for Bhanjyang Cooperative built with Django 5.2.3 and Tailwind CSS, featuring comprehensive API, monitoring, and development tools.

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Setup](#-project-setup)
- [Running Tests](#-running-tests)
- [Adding New Features](#-adding-new-features)
- [Development Guide](#-development-guide)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

## 🌟 Features

### Core Features
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Multi-language Support**: Nepali and English content
- **Financial Services**: Savings accounts, loans, fixed deposits, remittance
- **Team Management**: Committee and member management system
- **News & Updates**: Blog-style updates and events
- **Contact Forms**: User-friendly contact system with file uploads
- **File Downloads**: Secure document sharing with analytics
- **Gallery**: Image gallery with smart collections
- **Admin Panel**: Comprehensive Django admin interface

### Enterprise Features
- **REST API**: Comprehensive API with OpenAPI documentation
- **Performance Monitoring**: Real-time performance tracking
- **Health Checks**: Kubernetes-ready health endpoints
- **Security**: Advanced security middleware, CSP, and Admin 2FA
- **Caching**: Redis-based caching system
- **Error Tracking**: Sentry integration for production monitoring
- **Database Indexing**: Optimized queries with 60+ indexes

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher (for Tailwind CSS)
- **PostgreSQL**: 15+ (for production, SQLite for development)
- **Redis**: 7+ (optional, for caching and Celery)
- **Git**: For version control

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Bhanjyang
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   
   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install Node.js dependencies**
   ```bash
   npm install
   ```

5. **Set up environment variables**
   ```bash
   # Copy template
   cp env.template .env
   
   # Edit .env file with your settings
   # Minimum required: SECRET_KEY, DEBUG
   ```

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

9. **Start development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Website: http://127.0.0.1:8000/
    - Admin Panel: http://127.0.0.1:8000/admin/

### Quick Setup Script

For faster setup, use the provided script:

```bash
python scripts/setup_dev.py
```

This script automates:
- Virtual environment creation
- Dependency installation
- Environment file setup
- Database migrations
- Static files collection

## 🧪 Running Tests

### Using pytest (Recommended)

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=apps --cov-report=html

# Run specific app tests
pytest apps/services/tests/

# Run specific test file
pytest apps/services/tests/test_views.py

# Run with verbose output
pytest -v

# Run only fast tests (skip slow ones)
pytest -m "not slow"
```

### Using Django Test Runner

```bash
# Run all tests
python manage.py test

# Run specific app
python manage.py test apps.services

# Run specific test class
python manage.py test apps.services.tests.test_views.ServicesViewsTest

# Run with verbosity
python manage.py test --verbosity=2
```

### Test Coverage

The project maintains >80% test coverage. To check coverage:

```bash
# Generate HTML coverage report
pytest --cov=apps --cov-report=html

# View report
# Open htmlcov/index.html in your browser
```

### Test Markers

Tests are organized with markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only security tests
pytest -m security

# Run only performance tests
pytest -m performance
```

### Continuous Testing

For development, run tests in watch mode:

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw
```

## ➕ Adding New Features

### Step-by-Step Guide

#### 1. Create a New App (if needed)

```bash
# Create new Django app
python manage.py startapp myapp apps/

# Add to INSTALLED_APPS in config/settings.py
```

#### 2. Create Models

```python
# apps/myapp/models.py
from django.db import models
from apps.core.query_utils import get_active_queryset

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
        ]
```

#### 3. Create Service Layer

```python
# apps/myapp/services.py
"""
Service layer for MyApp business logic.
"""
from typing import Dict, Any, List
from .models import MyModel

class MyService:
    """
    Service class for handling MyApp business logic.
    
    This service handles data fetching, processing, and business rules
    separate from views, making code more maintainable and testable.
    """
    
    @staticmethod
    def get_active_items() -> List[MyModel]:
        """
        Retrieve all active items.
        
        Returns:
            QuerySet of active MyModel instances
        """
        return MyModel.objects.filter(is_active=True)
    
    @staticmethod
    def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Processed data dictionary
        """
        # Business logic here
        return processed_data
```

#### 4. Create Views

```python
# apps/myapp/views.py
from typing import Dict, Any
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from apps.core.view_mixins import BreadcrumbMixin, create_breadcrumbs
from apps.core.query_utils import get_active_queryset
from .models import MyModel
from .services import MyService

def my_view(request: HttpRequest) -> HttpResponse:
    """
    Display my view page.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered template response
    """
    items = MyService.get_active_items()
    context = {
        'items': items,
        'breadcrumbs': create_breadcrumbs(
            ('Home', '/'),
            ('My Page', None)
        )
    }
    return render(request, 'myapp/my_template.html', context)
```

#### 5. Create URLs

```python
# apps/myapp/urls.py
from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.my_view, name='my_view'),
]
```

#### 6. Register URLs in Main URLs

```python
# config/urls.py
urlpatterns = [
    # ... existing patterns
    path('myapp/', include('apps.myapp.urls')),
]
```

#### 7. Create Templates

```html
<!-- apps/myapp/templates/myapp/my_template.html -->
{% extends 'base.html' %}

{% block content %}
<h1>My Page</h1>
<!-- Content here -->
{% endblock %}
```

#### 8. Create Tests

```python
# apps/myapp/tests/test_views.py
from django.test import TestCase
from django.urls import reverse

class MyViewTest(TestCase):
    """Test suite for my view"""
    
    def test_my_view_renders(self):
        """Test that my view renders correctly"""
        response = self.client.get(reverse('myapp:my_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Page')
```

#### 9. Create Migrations

```bash
# Create migrations
python manage.py makemigrations myapp

# Apply migrations
python manage.py migrate myapp
```

#### 10. Run Tests

```bash
# Run tests for new app
pytest apps/myapp/tests/

# Check coverage
pytest apps/myapp/tests/ --cov=apps.myapp
```

### Best Practices

1. **Service Layer Pattern**: Always use service classes for business logic
2. **Type Hints**: Add type hints to all functions
3. **Docstrings**: Document all classes and functions
4. **Database Indexes**: Add indexes to frequently queried fields
5. **Error Handling**: Use `apps.core.error_handling` utilities
6. **Query Optimization**: Use `apps.core.query_utils` for common queries
7. **View Mixins**: Use `apps.core.view_mixins` for common view patterns
8. **Tests**: Write tests for all new functionality

## 📚 Development Guide

### Project Structure

```
Bhanjyang/
├── apps/                    # Django applications
│   ├── about/               # About Us app
│   ├── contact/             # Contact forms app
│   ├── core/                # Core utilities and shared code
│   ├── dashboard/           # Dashboard and analytics
│   ├── downloads/           # File downloads
│   ├── gallery/             # Image gallery
│   ├── home/                # Homepage
│   ├── news_events/         # News and events
│   ├── search/              # Search functionality
│   └── services/            # Financial services
├── config/                  # Django configuration
├── docs/                    # Documentation
├── static/                  # Static files (CSS, JS, images)
├── templates/               # Base templates
├── tests/                   # Integration tests
├── scripts/                 # Utility scripts
├── manage.py                # Django management script
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── README.md                # This file
```

### Code Organization

#### Service Layer Pattern

All business logic is separated into service classes:

```python
# ✅ Good: Service layer
class MyService:
    @staticmethod
    def process_data(data):
        # Business logic here
        return result

# ❌ Bad: Logic in views
def my_view(request):
    # Business logic mixed with view logic
    result = complex_calculation()
    return render(...)
```

#### View Mixins

Use mixins for common view patterns:

```python
from apps.core.view_mixins import ServiceDetailViewMixin, create_breadcrumbs

class MyDetailView(ServiceDetailViewMixin, DetailView):
    model = MyModel
    service_type = 'my_service'
    breadcrumbs = create_breadcrumbs(
        ('Home', '/'),
        ('My Service', None)
    )
```

#### Query Utilities

Use query utilities for optimized queries:

```python
from apps.core.query_utils import get_active_queryset, get_featured_queryset

# Get active items
active_items = get_active_queryset(
    MyModel,
    fields=['id', 'name', 'slug'],
    order_by=['-created_at']
)

# Get featured items
featured_items = get_featured_queryset(
    MyModel,
    fields=['id', 'name'],
    limit=5
)
```

### Available Commands

#### Using Make (Linux/Mac)

```bash
make dev              # Start development server
make test             # Run tests
make test-coverage    # Run tests with coverage
make lint             # Run linting
make format           # Format code
make check            # Run all checks
make migrate          # Run migrations
make shell            # Django shell
```

#### Using PowerShell (Windows)

```powershell
.\make.ps1 dev              # Start development server
.\make.ps1 test             # Run tests
.\make.ps1 test-coverage    # Run tests with coverage
.\make.ps1 lint             # Run linting
.\make.ps1 format           # Format code
.\make.ps1 check            # Run all checks
```

#### Using Django Management

```bash
python manage.py runserver          # Start server
python manage.py migrate            # Run migrations
python manage.py makemigrations    # Create migrations
python manage.py shell              # Django shell
python manage.py createsuperuser    # Create admin user
python manage.py collectstatic     # Collect static files
```

### Development Tools

- **Code Formatting**: Black, isort
- **Linting**: flake8, mypy
- **Security**: bandit, safety
- **Testing**: pytest, coverage
- **Type Checking**: mypy
- **Pre-commit Hooks**: Automated quality checks

## 🔧 Configuration

### Environment Variables

Copy `env.template` to `.env` and configure:

```env
# Required
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (Production)
DB_NAME=bhanjyang_coop
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Email
SEND_REAL_EMAILS=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Settings Files

- `config/settings.py` - Base settings
- `config/settings_dev.py` - Development overrides
- `config/production.py` - Production settings

## 📖 Documentation

### Code Documentation

All services and functions include comprehensive docstrings:

```python
def my_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of what the function does.
    
    More detailed explanation of the function's purpose, behavior,
    and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        
    Example:
        >>> result = my_function('test', 42)
        >>> result['status']
        'success'
    """
    # Implementation
```

### Documentation Structure

- **`docs/`**: Main documentation directory
  - **`development/`**: Development guides and refactoring docs
  - **`api/`**: API documentation
  - **`guides/`**: How-to guides
  - **`deployment/`**: Deployment guides
  - **`apps/`**: App-specific documentation

## 🔌 API Documentation

### REST API Endpoints

- **Services API**: `/api/v1/savings-accounts/`, `/api/v1/loan-types/`
- **Health Checks**: `/health/`, `/health/readiness/`, `/health/liveness/`
- **API Docs**: `/api/docs/` (Swagger UI)
- **API Schema**: `/api/schema/` (OpenAPI schema)

See [API Documentation](./docs/api/README.md) for details.

## 🐳 Docker Support

### Development with Docker

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Stop services
docker-compose down
```

## 🔒 Security

### Security Features

- Rate limiting (per IP and per user)
- Input validation and sanitization
- Brute force protection
- Security headers (CSP, HSTS, XSS protection)
- File upload validation
- API authentication and permissions

See [SECURITY.md](./SECURITY.md) for details.

## 📊 Monitoring

### Health Checks

- `/health/` - Comprehensive health status
- `/health/readiness/` - Kubernetes readiness probe
- `/health/liveness/` - Kubernetes liveness probe

### Performance Monitoring

- Real-time metrics tracking
- Database query monitoring
- Cache performance metrics
- User analytics

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG=False`
2. Configure PostgreSQL database
3. Set up Redis cache
4. Configure email backend
5. Set up SSL/HTTPS
6. Configure security headers
7. Set up monitoring (Sentry)
8. Run migrations
9. Collect static files
10. Set up backup strategy

See [Deployment Guide](./docs/deployment/README.md) for details.

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Run tests: `pytest`
5. Run checks: `make check`
6. Commit: `git commit -m "Add my feature"`
7. Push: `git push origin feature/my-feature`
8. Create Pull Request

### Code Standards

- **Formatting**: Black, isort
- **Linting**: flake8, mypy
- **Testing**: pytest with >80% coverage
- **Documentation**: Comprehensive docstrings
- **Type Hints**: Required for all functions

## 📞 Support

- **Documentation**: Check `docs/` directory
- **Issues**: Create GitHub issues for bugs
- **Questions**: Use GitHub discussions

---

**Built with ❤️ for Bhanjyang Cooperative**

For detailed documentation, see [docs/README.md](./docs/README.md)

