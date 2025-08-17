#!/usr/bin/env python3
"""
Deployment script for Bhanjyang Cooperative project.
This script helps automate common deployment tasks.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_requirements():
    """Check if required tools are available."""
    print("🔍 Checking requirements...")
    
    # Check Python
    if not shutil.which('python'):
        print("❌ Python not found")
        return False
    
    # Check pip
    if not shutil.which('pip'):
        print("❌ pip not found")
        return False
    
    print("✅ All requirements met")
    return True


def install_dependencies():
    """Install Python dependencies."""
    return run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies"
    )


def run_migrations():
    """Run database migrations."""
    return run_command(
        "python manage.py migrate",
        "Running database migrations"
    )


def collect_static():
    """Collect static files."""
    return run_command(
        "python manage.py collectstatic --noinput",
        "Collecting static files"
    )


def check_system():
    """Run Django system check."""
    return run_command(
        "python manage.py check --deploy",
        "Running system deployment check"
    )


def create_superuser():
    """Create a superuser if none exists."""
    print("🔍 Checking for existing superuser...")
    
    # Check if superuser exists
    result = subprocess.run(
        "python manage.py shell -c \"from django.contrib.auth.models import User; print('SUPERUSER_EXISTS' if User.objects.filter(is_superuser=True).exists() else 'NO_SUPERUSER')\"",
        shell=True, capture_output=True, text=True
    )
    
    if 'NO_SUPERUSER' in result.stdout:
        print("⚠️  No superuser found. You should create one manually:")
        print("   python manage.py createsuperuser")
    else:
        print("✅ Superuser already exists")
    
    return True


def main():
    """Main deployment function."""
    print("🚀 Bhanjyang Cooperative Deployment Script")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    # Collect static files
    if not collect_static():
        sys.exit(1)
    
    # Check system
    if not check_system():
        print("⚠️  System check warnings - review before production deployment")
    
    # Check superuser
    create_superuser()
    
    print("\n🎉 Deployment completed successfully!")
    print("\nNext steps:")
    print("1. Configure your web server (nginx, Apache, etc.)")
    print("2. Set up environment variables in .env file")
    print("3. Configure your database")
    print("4. Set up SSL certificates")
    print("5. Test your deployment")
    
    print("\nFor production deployment:")
    print("- Set DEBUG=False in environment variables")
    print("- Use production database (PostgreSQL recommended)")
    print("- Configure proper email backend")
    print("- Set up monitoring and logging")


if __name__ == "__main__":
    main()
