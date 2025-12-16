# भञ्ज्याङ सहकारी (Bhanjyang Cooperative)

A modern, enterprise-grade website for Bhanjyang Cooperative built with Django 5.2.3 and Tailwind CSS, featuring comprehensive API, monitoring, and development tools.

## 🌟 Features

### Core Features
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Multi-language Support**: Nepali and English content
- **Team Management**: Committee and member management system
- **News & Updates**: Blog-style updates and events
- **Contact Forms**: User-friendly contact system with file uploads
- **File Downloads**: Secure document sharing with analytics
- **Admin Panel**: Comprehensive Django admin interface

### Enterprise Features
- **REST API**: Comprehensive API with OpenAPI documentation
- **Performance Monitoring**: Real-time performance tracking
- **Health Checks**: Kubernetes-ready health endpoints
- **Security**: Advanced security middleware and rate limiting
- **Caching**: Redis-based caching system
- **Error Tracking**: Sentry integration for production monitoring
- **CI/CD**: GitHub Actions pipeline with automated testing

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (for production)
- Redis 7+ (for production)
- pip and npm

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Bhanjyang
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source .venv/bin/activate      # Linux/Mac
   ```

3. **Quick setup (recommended)**
   ```bash
   python scripts/setup_dev.py
   ```

4. **Manual setup**
   ```bash
   # Install dependencies
   pip install -r requirements-dev.txt
   npm install
   
   # Set up environment
   cp env.template .env
   # Edit .env with your configuration
   
   # Database setup
   python manage.py migrate
   python manage.py createsuperuser
   
   # Build assets
   npm run build
   python manage.py collectstatic --noinput
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   # or
   make dev
   ```

## 🎨 Development

### Available Scripts

#### Using Make (Recommended)
- `make dev` - Start development server
- `make test` - Run tests with coverage
- `make lint` - Run linting checks
- `make format` - Format code
- `make check` - Run all checks
- `make docker-compose-up` - Start with Docker Compose
- `make quick-start` - Complete development setup

#### Using npm
- `npm run dev` - Watch mode for Tailwind CSS compilation
- `npm run build` - Build production CSS
- `npm run start` - Start Django development server

#### Using Python
- `python manage.py runserver` - Start development server
- `python manage.py test` - Run tests
- `python manage.py shell` - Django shell

### Development Tools

The project includes comprehensive development tools:

- **Code Formatting**: Black, isort
- **Linting**: flake8, mypy
- **Security**: bandit, safety
- **Testing**: pytest, coverage
- **Pre-commit Hooks**: Automated code quality checks
- **Docker**: Containerized development environment

## 🔧 Configuration

### Environment Variables

Copy `env.template` to `.env` and configure:

```env
# Security
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (Production)
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

### Django Settings

The project uses multiple settings files:
- `coop/settings.py` - Base settings
- `coop/settings_dev.py` - Development settings
- `coop/production.py` - Production settings

## 📚 Documentation Structure

The documentation is organized into the following directories:

### 📖 [Guides](./guides/)
User guides and how-to documentation:
- [Next Steps Guide](./guides/next-steps.md) - Deployment and setup guide
- [Error Reporting Guide](./guides/error-reporting.md) - Error reporting configuration
- [Performance Monitoring](./guides/performance-monitoring.md) - Performance monitoring system
- [Static Files Guide](./guides/static-files.md) - Static files organization
- [Image Upload Guidelines](./guides/image-upload-guidelines.md) - Image upload best practices

### 🔄 [Migrations](./migrations/)
Migration and refactoring history:
- Folder structure improvements
- Standardization progress
- Migration completion status

### 📱 [Apps](./apps/)
App-specific documentation:
- [Contact App](./apps/contact-app.md) - Contact app management
- [Gallery App](./apps/gallery/) - Gallery app documentation

### 📐 [Standards](./standards/)
Design and coding standards:
- [Design System Standards](./standards/design-system.md) - Design system guidelines

### 🚀 [Deployment](./deployment/)
Deployment guides and configuration:
- Production deployment
- Docker setup
- Nginx configuration

### 💻 [Development](./development/)
Development guides and workflows

### 🔌 [API](./api/)
API documentation:
- REST API endpoints
- Authentication
- API usage examples

### 📦 [Archive](./archive/)
Historical documentation and archived files

## 📱 API Documentation

### REST API Endpoints

- **Services API**: `/api/v1/savings-accounts/`, `/api/v1/loan-types/`, etc.
- **Health Checks**: `/health/`, `/health/readiness/`, `/health/liveness/`
- **API Documentation**: `/api/docs/` (Swagger UI)
- **API Schema**: `/api/schema/` (OpenAPI schema)

### API Features

- **Authentication**: Token and session authentication
- **Rate Limiting**: Configurable rate limits
- **Filtering**: Advanced filtering and search
- **Pagination**: Page-based pagination
- **Documentation**: Auto-generated OpenAPI docs

For detailed API documentation, see [API Documentation](./api/README.md).

## 🐳 Docker Support

### Development with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access Django shell
docker-compose exec web python manage.py shell

# Stop services
docker-compose down
```

### Production Docker

```bash
# Build image
docker build -t bhanjyang-coop .

# Run container
docker run -p 8000:8000 bhanjyang-coop
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific app tests
python manage.py test apps.services

# Run with pytest
pytest
```

### Test Coverage

The project maintains >80% test coverage across all apps.

## 🔒 Security

### Security Features

- **Rate Limiting**: Per-IP and per-user rate limits
- **Input Validation**: Comprehensive input sanitization
- **Brute Force Protection**: Login attempt monitoring
- **Security Headers**: CSP, HSTS, XSS protection
- **File Upload Security**: Type and size validation
- **API Security**: Token authentication and permissions

### Security Tools

- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Trivy**: Container vulnerability scanning

## 📊 Monitoring & Observability

### Health Checks

- **Health Check**: `/health/` - Comprehensive health status
- **Readiness**: `/health/readiness/` - Kubernetes readiness probe
- **Liveness**: `/health/liveness/` - Kubernetes liveness probe
- **Metrics**: `/health/metrics/` - Application metrics

### Performance Monitoring

- **Real-time Metrics**: Page load times, error rates
- **Database Monitoring**: Query performance tracking
- **Cache Monitoring**: Redis performance metrics
- **User Analytics**: Session tracking and behavior analysis

### Error Tracking

- **Sentry Integration**: Production error tracking
- **Log Aggregation**: Structured logging with rotation
- **Alert System**: Configurable performance alerts

## 🚀 Deployment

### Production Checklist

1. **Environment Setup**
   - Set `DEBUG=False`
   - Configure PostgreSQL database
   - Set up Redis cache
   - Configure email backend
   - Set up Sentry monitoring

2. **Security Configuration**
   - Enable HTTPS/SSL
   - Set secure cookie settings
   - Configure CORS origins
   - Set up security headers

3. **Performance Optimization**
   - Enable Redis caching
   - Configure CDN for static files
   - Set up database connection pooling
   - Enable compression

### Deployment Options

- **VPS**: DigitalOcean, Linode, AWS EC2
- **Platform**: Heroku, Railway, PythonAnywhere
- **Container**: Docker, Kubernetes
- **Cloud**: AWS, Google Cloud, Azure

## 🔄 CI/CD Pipeline

### GitHub Actions

The project includes a comprehensive CI/CD pipeline:

- **Testing**: Automated test execution
- **Code Quality**: Linting, formatting, security checks
- **Build**: Docker image building
- **Deployment**: Staging and production deployments
- **Security**: Vulnerability scanning

### Pipeline Stages

1. **Test**: Run tests, linting, security checks
2. **Build**: Create deployment artifacts
3. **Deploy**: Deploy to staging/production
4. **Notify**: Send notifications on success/failure

## 📈 Performance

### Optimization Features

- **Database**: Query optimization, indexing, connection pooling
- **Caching**: Redis-based multi-level caching
- **Static Files**: CDN integration, compression
- **Images**: Automatic optimization and WebP support
- **API**: Response caching and pagination

### Performance Metrics

- **Page Load Time**: < 2 seconds
- **API Response Time**: < 500ms
- **Error Rate**: < 0.1%
- **Uptime**: > 99.9%

## 🤝 Contributing

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Run** tests and checks: `make check`
5. **Commit** with conventional commits
6. **Push** to your fork
7. **Submit** a pull request

### Code Standards

- **Formatting**: Black, isort
- **Linting**: flake8, mypy
- **Testing**: pytest with >80% coverage
- **Documentation**: Comprehensive docstrings
- **Security**: Bandit, safety checks

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check the [Guides](./guides/) directory for how-to guides
- **API Documentation**: See [API Documentation](./api/README.md) for API details
- **Deployment**: See [Deployment Guide](./deployment/README.md) for deployment help
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Email**: Contact the development team

### Maintenance

- **Regular Updates**: Monthly dependency updates
- **Security Patches**: Immediate security updates
- **Feature Releases**: Quarterly feature releases
- **Bug Fixes**: Weekly bug fix releases

This project is licensed under the MIT License.

## 📞 Support

For support or questions, please contact the development team or create an issue in the repository.

---

**Built with ❤️ for Bhanjyang Cooperative**
