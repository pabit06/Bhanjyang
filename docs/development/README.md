# Development Documentation

This directory contains guides for developers working on the Bhanjyang Cooperative project.

## Structure

```
development/
├── README.md                # This file
├── DEVELOPMENT_HISTORY.md  # Comprehensive history of all improvements
├── DEVELOPMENT_STATUS.md    # Current development status
├── NEXT_STEPS.md            # Next steps for development
├── TEST_COVERAGE_SUMMARY.md # Test coverage summary and status
├── PROJECT_REVIEW_SUGGESTIONS.md # Project review and recommendations
├── ALL_APPS_DETAILED_REPORTS.md # Detailed reports for all apps
├── APP_COMPARISON_RATING.md # Apps comparison and ratings
├── CATEGORY_RATINGS_SUMMARY.md # Category-wise ratings breakdown
└── FINAL_RATING_SUMMARY.md # News Events app final rating summary
```

## Getting Started

1. Review [DEVELOPMENT_STATUS.md](./DEVELOPMENT_STATUS.md) for current project status
2. Check [TEST_COVERAGE_SUMMARY.md](./TEST_COVERAGE_SUMMARY.md) for test coverage information
3. Read [NEXT_STEPS.md](./NEXT_STEPS.md) for recommended next steps
4. Review [DEVELOPMENT_HISTORY.md](./DEVELOPMENT_HISTORY.md) for comprehensive history of all improvements

## Documentation Overview

### [DEVELOPMENT_HISTORY.md](./DEVELOPMENT_HISTORY.md)
Comprehensive record of all development improvements including:
- Critical fixes applied
- Code quality and refactoring improvements
- Error handling improvements
- Database indexing improvements
- Documentation improvements
- Project review and recommendations

### [DEVELOPMENT_STATUS.md](./DEVELOPMENT_STATUS.md)
Current development status, completed tasks, and remaining work.

### [NEXT_STEPS.md](./NEXT_STEPS.md)
Recommended next steps and priorities for continued development.

### [TEST_COVERAGE_SUMMARY.md](./TEST_COVERAGE_SUMMARY.md)
Current test coverage status, metrics, and recommendations.

### [PROJECT_REVIEW_SUGGESTIONS.md](./PROJECT_REVIEW_SUGGESTIONS.md)
Comprehensive project review with recommendations and action items.

### [ALL_APPS_DETAILED_REPORTS.md](./ALL_APPS_DETAILED_REPORTS.md)
Detailed reports for all 10 apps including structure, features, statistics, strengths, weaknesses, and recommendations.

### [APP_COMPARISON_RATING.md](./APP_COMPARISON_RATING.md)
Comprehensive comparison and rating of all apps with category-wise breakdowns.

### [CATEGORY_RATINGS_SUMMARY.md](./CATEGORY_RATINGS_SUMMARY.md)
Category-wise ratings breakdown (Features, Code Quality, Documentation, Testing, API Design, Complexity Management).

### [FINAL_RATING_SUMMARY.md](./FINAL_RATING_SUMMARY.md)
News Events app final rating summary after re-evaluation and upgrades.

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

