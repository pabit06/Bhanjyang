from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction

class Command(BaseCommand):
    help = 'Populate all project data (Services, About, News, Gallery)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting full database population...'))

        with transaction.atomic():
            # 1. Services
            self.stdout.write(self.style.NOTICE('Running: populate_services'))
            call_command('populate_services')
            
            # 2. About
            self.stdout.write(self.style.NOTICE('Running: populate_about'))
            call_command('populate_about')
            
            # 3. News & Events
            self.stdout.write(self.style.NOTICE('Running: seed_news_events'))
            call_command('seed_news_events', articles=10, events=8)
            
            # 4. Gallery
            self.stdout.write(self.style.NOTICE('Running: create_sample_albums'))
            call_command('create_sample_albums')

        self.stdout.write(self.style.SUCCESS('--------------------------------------------------'))
        self.stdout.write(self.style.SUCCESS('✅ ALL DATA POPULATED SUCCESSFULLY!'))
        self.stdout.write(self.style.SUCCESS('--------------------------------------------------'))
