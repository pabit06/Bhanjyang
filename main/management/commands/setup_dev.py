"""
Django management command to set up development environment.
Usage: python manage.py setup_dev
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Set up development environment for Bhanjyang Cooperative'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force setup even if already configured',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up Bhanjyang Cooperative development environment...')
        )

        # Create necessary directories
        directories = [
            'logs',
            'staticfiles',
            'media/downloads',
            'media/person_photos',
            'media/updates/images',
        ]

        for directory in directories:
            dir_path = os.path.join(settings.BASE_DIR, directory)
            os.makedirs(dir_path, exist_ok=True)
            self.stdout.write(f'✅ Created directory: {directory}')

        # Run migrations
        self.stdout.write('🔄 Running database migrations...')
        try:
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✅ Database migrations completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Migration failed: {e}'))

        # Collect static files
        self.stdout.write('📁 Collecting static files...')
        try:
            call_command('collectstatic', '--noinput', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✅ Static files collected'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Static collection failed: {e}'))

        # Check for superuser
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('⚠️  No superuser found. Run "python manage.py createsuperuser" to create one.')
            )

        # Check system status
        self.stdout.write('🔍 Checking system status...')
        try:
            call_command('check', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✅ System check passed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ System check failed: {e}'))

        self.stdout.write(
            self.style.SUCCESS('🎉 Development environment setup completed!')
        )
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Create a superuser: python manage.py createsuperuser')
        self.stdout.write('2. Start the development server: python manage.py runserver')
        self.stdout.write('3. Build CSS assets: npm run build (if Node.js is available)')
        self.stdout.write('4. Access the admin panel at: http://127.0.0.1:8000/admin/')
