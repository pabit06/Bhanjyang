# Makefile for Bhanjyang Cooperative Django project

.PHONY: help install dev-install test lint format clean run migrate makemigrations shell superuser collectstatic build-docs deploy

# Default target
help: ## Show this help message
	@echo "Bhanjyang Cooperative Django Project"
	@echo "===================================="
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation targets
install: ## Install production dependencies
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	pip install -r requirements-dev.txt
	npm install
	pre-commit install

# Development targets
dev: ## Start development server (accessible from network)
	python manage.py runserver 0.0.0.0:8000

run: ## Start production server
	gunicorn coop.wsgi:application --bind 0.0.0.0:8000

shell: ## Start Django shell
	python manage.py shell

superuser: ## Create superuser
	python manage.py createsuperuser

# Database targets
migrate: ## Run database migrations
	python manage.py migrate

makemigrations: ## Create new migrations
	python manage.py makemigrations

migrate-check: ## Check for pending migrations
	python manage.py makemigrations --check --dry-run

# Static files targets
collectstatic: ## Collect static files
	python manage.py collectstatic --noinput

build-css: ## Build CSS assets
	npm run build

watch-css: ## Watch CSS changes
	npm run dev

# Testing targets
test: ## Run tests
	python manage.py test

test-coverage: ## Run tests with coverage
	coverage run --source='.' manage.py test
	coverage report
	coverage html

test-verbose: ## Run tests with verbose output
	python manage.py test --verbosity=2

# Code quality targets
lint: ## Run linting checks
	flake8 apps/
	mypy apps/ --ignore-missing-imports

format: ## Format code
	black apps/
	isort apps/

format-check: ## Check code formatting
	black --check apps/
	isort --check-only apps/

# Security targets
security-check: ## Run security checks
	bandit -r apps/ -f json -o bandit-report.json
	safety check --json --output safety-report.json

# Docker targets
docker-build: ## Build Docker image
	docker build -t bhanjyang-coop .

docker-run: ## Run Docker container
	docker run -p 8000:8000 bhanjyang-coop

docker-compose-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-compose-down: ## Stop all Docker Compose services
	docker-compose down

docker-compose-logs: ## View Docker Compose logs
	docker-compose logs -f

docker-compose-shell: ## Access Django shell in Docker container
	docker-compose exec web python manage.py shell

# Database management targets
db-backup: ## Create database backup
	python scripts/backup_manager.py full

db-restore: ## Restore database from backup
	@echo "Please specify backup file: make db-restore BACKUP_FILE=backup_file.json"
	@if [ -z "$(BACKUP_FILE)" ]; then echo "Error: BACKUP_FILE not specified"; exit 1; fi
	python manage.py loaddata $(BACKUP_FILE)

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f db.sqlite3; \
		python manage.py migrate; \
		python manage.py createsuperuser; \
	fi

# Performance targets
optimize-images: ## Optimize images
	python scripts/optimize_images.py

performance-test: ## Run performance tests
	python manage.py test apps.dashboard.tests.PerformanceTest

# Documentation targets
build-docs: ## Build documentation
	sphinx-build -b html docs/ docs/_build/

serve-docs: ## Serve documentation locally
	cd docs/_build && python -m http.server 8001

# Deployment targets
deploy-staging: ## Deploy to staging environment
	@echo "Deploying to staging..."
	# Add your staging deployment commands here

deploy-production: ## Deploy to production environment
	@echo "Deploying to production..."
	# Add your production deployment commands here

# Health check targets
health-check: ## Check application health
	curl -f http://localhost:8000/health/ || echo "Health check failed"

# Cleanup targets
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -f bandit-report.json safety-report.json

clean-docker: ## Clean up Docker resources
	docker system prune -f
	docker volume prune -f

# Setup targets
setup-dev: ## Set up development environment
	python -m venv .venv
	@echo "Virtual environment created. Please activate it:"
	@echo "Windows: .venv\\Scripts\\activate"
	@echo "Linux/Mac: source .venv/bin/activate"
	@echo "Then run: make dev-install"

setup-prod: ## Set up production environment
	pip install -r requirements.txt
	python manage.py migrate
	python manage.py collectstatic --noinput
	python manage.py createsuperuser

# Monitoring targets
logs: ## View application logs
	tail -f logs/django.log

error-logs: ## View error logs
	tail -f logs/django_error.log

performance-logs: ## View performance logs
	tail -f logs/performance.log

# API targets
api-docs: ## Generate API documentation
	python manage.py spectacular --file api-schema.yml
	python manage.py spectacular --file api-schema.json

api-test: ## Test API endpoints
	curl -X GET http://localhost:8000/api/v1/savings-accounts/

# Backup and restore targets
backup-full: ## Create full system backup
	python scripts/backup_manager.py full

backup-db: ## Create database backup only
	python scripts/backup_manager.py database

backup-media: ## Create media files backup only
	python scripts/backup_manager.py media

list-backups: ## List available backups
	python scripts/backup_manager.py list

# Development workflow targets
check: ## Run all checks (lint, format, test, security)
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) security-check

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

ci: ## Run CI pipeline locally
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test-coverage
	$(MAKE) security-check
	$(MAKE) build-css
	$(MAKE) collectstatic

# Quick start targets
quick-start: ## Quick start development environment
	$(MAKE) dev-install
	$(MAKE) migrate
	$(MAKE) build-css
	$(MAKE) superuser
	@echo "Development environment ready! Run 'make dev' to start the server."

quick-test: ## Quick test run
	$(MAKE) format-check
	$(MAKE) test
