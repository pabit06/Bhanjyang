"""
Django management command to clear all project data for a fresh start.
Usage: python manage.py clear_all_data [--populate] [--no-input] [--keep-media] [--keep-logs]
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.core.cache import cache
from django.db import connection
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Clear all project data (database, media, logs, cache) for a fresh start'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Skip confirmation prompt (for automation)',
        )
        parser.add_argument(
            '--populate',
            action='store_true',
            help='Automatically populate sample data after clearing',
        )
        parser.add_argument(
            '--keep-media',
            action='store_true',
            help='Keep media files (only clear database)',
        )
        parser.add_argument(
            '--keep-logs',
            action='store_true',
            help='Keep log files',
        )

    def handle(self, *args, **options):
        # Display warning
        self.stdout.write(self.style.WARNING('\n' + '='*70))
        self.stdout.write(self.style.WARNING('WARNING: This will delete ALL project data!'))
        self.stdout.write(self.style.WARNING('='*70))
        self.stdout.write('')
        self.stdout.write('This command will:')
        self.stdout.write('  • Delete database file (db.sqlite3)')
        if not options['keep_media']:
            self.stdout.write('  • Delete all media files')
        if not options['keep_logs']:
            self.stdout.write('  • Delete all log files')
        self.stdout.write('  • Clear Python cache (__pycache__)')
        self.stdout.write('  • Clear staticfiles directory')
        self.stdout.write('  • Clear Django cache tables')
        self.stdout.write('  • Recreate database with migrations')
        if options['populate']:
            self.stdout.write('  • Populate sample data')
        self.stdout.write('')

        # Ask for confirmation
        if not options['no_input']:
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return

        # Start clearing
        self.stdout.write(self.style.WARNING('\nStarting data clearing process...\n'))

        try:
            # 1. Delete database file
            self._clear_database()

            # 2. Clear media files
            if not options['keep_media']:
                self._clear_media_files()

            # 3. Clear log files
            if not options['keep_logs']:
                self._clear_log_files()

            # 4. Clear Python cache
            self._clear_python_cache()

            # 5. Clear staticfiles
            self._clear_staticfiles()

            # 6. Recreate database
            self._recreate_database()

            # 7. Clear cache tables
            self._clear_cache_tables()

            # 8. Populate sample data if requested
            if options['populate']:
                self._populate_sample_data()

            # Success message
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(self.style.SUCCESS('SUCCESS: All data cleared successfully!'))
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write('')
            self.stdout.write('Next steps:')
            if not options['populate']:
                self.stdout.write('  • Create superuser: python manage.py createsuperuser')
                self.stdout.write('  • Populate sample data: python manage.py populate_services')
                self.stdout.write('  • Populate home data: python manage.py populate_home_data')
            else:
                self.stdout.write('  • Create superuser: python manage.py createsuperuser')
            self.stdout.write('  • Start server: python manage.py runserver')
            self.stdout.write('')

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('='*70))
            self.stdout.write(self.style.ERROR(f'ERROR: {str(e)}'))
            self.stdout.write(self.style.ERROR('='*70))
            self.stdout.write('')
            raise

    def _clear_database(self):
        """Delete the database file"""
        self.stdout.write('1. Deleting database...', ending=' ')
        db_path = Path('db.sqlite3')
        if db_path.exists():
            db_path.unlink()
            self.stdout.write(self.style.SUCCESS('OK'))
        else:
            self.stdout.write(self.style.WARNING('(not found)'))

    def _clear_media_files(self):
        """Clear all media files while preserving directory structure"""
        self.stdout.write('2. Clearing media files...', ending=' ')
        media_path = Path(settings.MEDIA_ROOT)
        if media_path.exists():
            deleted_count = 0
            for item in media_path.iterdir():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                        deleted_count += 1
                    else:
                        item.unlink()
                        deleted_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'\n   Warning: Could not delete {item}: {e}'))
            # Ensure media directory exists
            media_path.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f'OK ({deleted_count} items)'))
        else:
            media_path.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.WARNING('(directory not found, created)'))

    def _clear_log_files(self):
        """Clear all log files"""
        self.stdout.write('3. Clearing log files...', ending=' ')
        logs_path = Path('logs')
        if logs_path.exists():
            deleted_count = 0
            for log_file in logs_path.glob('*.log'):
                try:
                    log_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'\n   Warning: Could not delete {log_file}: {e}'))
            # Ensure logs directory exists
            logs_path.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f'OK ({deleted_count} files)'))
        else:
            logs_path.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.WARNING('(directory not found, created)'))

    def _clear_python_cache(self):
        """Clear all Python cache directories"""
        self.stdout.write('4. Clearing Python cache...', ending=' ')
        deleted_count = 0
        for pycache in Path('.').rglob('__pycache__'):
            try:
                shutil.rmtree(pycache)
                deleted_count += 1
            except Exception as e:
                # Ignore errors for cache cleanup
                pass
        self.stdout.write(self.style.SUCCESS(f'OK ({deleted_count} directories)'))

    def _clear_staticfiles(self):
        """Clear staticfiles directory"""
        self.stdout.write('5. Clearing staticfiles...', ending=' ')
        staticfiles_path = Path('staticfiles')
        if staticfiles_path.exists():
            try:
                shutil.rmtree(staticfiles_path)
                self.stdout.write(self.style.SUCCESS('OK'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'({str(e)})'))
        else:
            self.stdout.write(self.style.WARNING('(not found)'))

    def _recreate_database(self):
        """Recreate database by running migrations"""
        self.stdout.write('6. Recreating database...', ending=' ')
        try:
            call_command('migrate', verbosity=0, interactive=False)
            self.stdout.write(self.style.SUCCESS('OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n   Error: {str(e)}'))
            raise

    def _clear_cache_tables(self):
        """Clear Django cache tables"""
        self.stdout.write('7. Clearing cache tables...', ending=' ')
        try:
            # Clear all cache
            cache.clear()
            # Clear database cache tables if they exist
            with connection.cursor() as cursor:
                try:
                    cursor.execute("DELETE FROM django_cache_sessions")
                except Exception:
                    # Table might not exist, ignore
                    pass
            self.stdout.write(self.style.SUCCESS('OK'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'({str(e)})'))

    def _populate_sample_data(self):
        """Populate sample data using available populate commands"""
        self.stdout.write('8. Populating sample data...')
        
        populate_commands = [
            ('populate_services', 'Populating services data...'),
            ('populate_home_data', 'Populating home data...'),
            ('seed_news_events', 'Seeding news and events...'),
        ]

        for command_name, description in populate_commands:
            try:
                self.stdout.write(f'   {description}', ending=' ')
                call_command(command_name, verbosity=0)
                self.stdout.write(self.style.SUCCESS('OK'))
            except Exception as e:
                # Command might not exist or might fail, continue with others
                self.stdout.write(self.style.WARNING(f'(skipped: {str(e)[:50]})'))

