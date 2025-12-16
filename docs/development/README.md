# Development Documentation

This directory contains guides for developers working on the Bhanjyang Cooperative project.

## Structure

```
development/
├── README.md                # This file
├── setup.md                 # Development environment setup
├── contributing.md          # Contribution guidelines
├── coding-standards.md      # Code style and standards
└── workflow.md              # Development workflow
```

## Getting Started

1. Read [setup.md](./setup.md) to set up your development environment
2. Review [coding-standards.md](./coding-standards.md) for code style
3. Check [workflow.md](./workflow.md) for development process
4. Read [contributing.md](./contributing.md) before contributing

## Development Environment

- **Python:** 3.10+
- **Django:** 5.2+
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Node.js:** 18+ (for frontend assets)

## Quick Setup

```bash
# Clone repository
git clone https://github.com/yourusername/bhanjyang.git
cd bhanjyang

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment variables
cp env.template .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Project Structure

See main [README.md](../README.md) for project structure overview.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific app tests
pytest apps/contact/tests.py
```

## Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Project Documentation](../README.md)
- [API Documentation](../api/README.md)

