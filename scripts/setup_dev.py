#!/usr/bin/env python
"""
Enhanced development setup script for Bhanjyang Cooperative Django project.
This script helps set up the development environment with all modern tools.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"⚠️ {description} completed with warnings: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        return False
    
    # Check if pip is available
    if not shutil.which("pip"):
        print("❌ pip is not installed")
        return False
    
    # Check if Node.js is available
    if not shutil.which("node"):
        print("❌ Node.js is not installed")
        return False
    
    # Check if npm is available
    if not shutil.which("npm"):
        print("❌ npm is not installed")
        return False
    
    print("✅ All prerequisites are met")
    return True

def setup_development():
    """Set up the development environment."""
    print("🚀 Setting up Bhanjyang Cooperative Django project...")
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    if not run_command("pip install -r requirements-dev.txt", "Installing development dependencies"):
        print("⚠️ Failed to install dev dependencies, trying production dependencies...")
        if not run_command("pip install -r requirements.txt", "Installing production dependencies"):
            sys.exit(1)
    
    # Install Node.js dependencies
    print("\n📦 Installing Node.js dependencies...")
    if not run_command("npm install", "Installing Node.js dependencies"):
        sys.exit(1)
    
    # Build CSS assets
    print("\n🎨 Building CSS assets...")
    if not run_command("npm run build", "Building CSS assets"):
        print("⚠️ CSS build failed, continuing...")
    
    # Create necessary directories
    print("\n📁 Creating necessary directories...")
    directories = ['logs', 'media', 'staticfiles', 'backups']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Run migrations
    print("\n🗄️ Setting up database...")
    if not run_command("python manage.py migrate", "Running database migrations"):
        sys.exit(1)
    
    # Collect static files
    print("\n📄 Collecting static files...")
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("⚠️ Static files collection failed, continuing...")
    
    # Check Django configuration
    print("\n🔍 Checking Django configuration...")
    if not run_command("python manage.py check", "Checking Django configuration"):
        sys.exit(1)
    
    # Set up pre-commit hooks
    print("\n🔧 Setting up pre-commit hooks...")
    if shutil.which("pre-commit"):
        run_command("pre-commit install", "Installing pre-commit hooks", check=False)
    else:
        print("⚠️ pre-commit not installed, skipping hooks setup")
    
    # Create .env file if it doesn't exist
    if not Path(".env").exists():
        print("\n📝 Creating .env file...")
        if Path("env.template").exists():
            shutil.copy("env.template", ".env")
            print("✅ Created .env file from template")
            print("⚠️ Please update .env file with your configuration")
        else:
            print("⚠️ env.template not found, please create .env file manually")
    
    print("\n🎉 Development environment setup complete!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your configuration")
    print("2. Create a superuser: python manage.py createsuperuser")
    print("3. Start the development server: python manage.py runserver")
    print("4. Visit http://localhost:8000 to see your application")
    print("\n🛠️ Available commands:")
    print("- make dev          : Start development server")
    print("- make test         : Run tests")
    print("- make lint         : Run linting")
    print("- make format       : Format code")
    print("- make check        : Run all checks")

if __name__ == "__main__":
    setup_development()
