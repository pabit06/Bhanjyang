"""
Management command to cleanup old content (archive old articles/events).

This command helps maintain the database by archiving or deleting old content
based on configurable criteria.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from apps.news_events.models import NewsArticle, Event
from apps.news_events.constants import ANALYTICS_DEFAULT_DAYS


class Command(BaseCommand):
    help = 'Cleanup old articles and events (archive or delete based on age)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Archive content older than this many days (default: 365)'
        )
        parser.add_argument(
            '--archive',
            action='store_true',
            help='Archive old content instead of deleting'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete old content (use with caution)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without actually doing it'
        )
        parser.add_argument(
            '--content-type',
            type=str,
            choices=['articles', 'events', 'both'],
            default='both',
            help='Type of content to cleanup (default: both)'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        days = options['days']
        archive = options['archive']
        delete = options['delete']
        dry_run = options['dry_run']
        content_type = options['content_type']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        if not archive and not delete:
            self.stderr.write(self.style.ERROR(
                'You must specify either --archive or --delete'
            ))
            return
        
        if archive and delete:
            self.stderr.write(self.style.ERROR(
                'Cannot use both --archive and --delete. Choose one.'
            ))
            return
        
        total_processed = 0
        
        # Process articles
        if content_type in ['articles', 'both']:
            articles = NewsArticle.objects.filter(
                published_date__lt=cutoff_date,
                status=NewsArticle.Status.PUBLISHED
            )
            article_count = articles.count()
            
            if article_count > 0:
                self.stdout.write(f'\nFound {article_count} articles older than {days} days')
                
                if archive:
                    if not dry_run:
                        updated = articles.update(status=NewsArticle.Status.ARCHIVED)
                        self.stdout.write(
                            self.style.SUCCESS(f'Archived {updated} articles')
                        )
                    else:
                        self.stdout.write(f'Would archive {article_count} articles')
                    total_processed += article_count
                elif delete:
                    if not dry_run:
                        deleted_count, _ = articles.delete()
                        self.stdout.write(
                            self.style.SUCCESS(f'Deleted {deleted_count} articles')
                        )
                    else:
                        self.stdout.write(f'Would delete {article_count} articles')
                    total_processed += article_count
        
        # Process events
        if content_type in ['events', 'both']:
            events = Event.objects.filter(
                event_date__lt=cutoff_date,
                status=Event.Status.PUBLISHED
            )
            event_count = events.count()
            
            if event_count > 0:
                self.stdout.write(f'\nFound {event_count} events older than {days} days')
                
                if archive:
                    if not dry_run:
                        updated = events.update(status=Event.Status.COMPLETED)
                        self.stdout.write(
                            self.style.SUCCESS(f'Marked {updated} events as completed')
                        )
                    else:
                        self.stdout.write(f'Would mark {event_count} events as completed')
                    total_processed += event_count
                elif delete:
                    if not dry_run:
                        deleted_count, _ = events.delete()
                        self.stdout.write(
                            self.style.SUCCESS(f'Deleted {deleted_count} events')
                        )
                    else:
                        self.stdout.write(f'Would delete {event_count} events')
                    total_processed += event_count
        
        if total_processed == 0:
            self.stdout.write(self.style.SUCCESS('No content found to cleanup'))
        else:
            action = 'archived' if archive else 'deleted'
            self.stdout.write(
                self.style.SUCCESS(f'\nTotal {action}: {total_processed} items')
            )

