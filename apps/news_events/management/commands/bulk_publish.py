"""
Management command for bulk publishing/archiving articles and events.

This command allows administrators to perform bulk operations on content.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from apps.news_events.models import NewsArticle, Event


class Command(BaseCommand):
    help = 'Bulk publish, archive, or update articles and events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['publish', 'archive', 'feature', 'unfeature'],
            required=True,
            help='Action to perform'
        )
        parser.add_argument(
            '--content-type',
            type=str,
            choices=['articles', 'events', 'both'],
            default='articles',
            help='Type of content to process (default: articles)'
        )
        parser.add_argument(
            '--ids',
            type=str,
            help='Comma-separated list of IDs to process'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Process all items in this category (slug)'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['draft', 'published', 'archived'],
            help='Process all items with this status'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually doing it'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        action = options['action']
        content_type = options['content_type']
        ids = options.get('ids')
        category_slug = options.get('category')
        status_filter = options.get('status')
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        total_processed = 0
        
        # Process articles
        if content_type in ['articles', 'both']:
            articles = NewsArticle.objects.all()
            
            if ids:
                article_ids = [int(id.strip()) for id in ids.split(',')]
                articles = articles.filter(id__in=article_ids)
            elif category_slug:
                articles = articles.filter(category__slug=category_slug)
            elif status_filter:
                status_map = {
                    'draft': NewsArticle.Status.DRAFT,
                    'published': NewsArticle.Status.PUBLISHED,
                    'archived': NewsArticle.Status.ARCHIVED,
                }
                articles = articles.filter(status=status_map[status_filter])
            else:
                self.stderr.write(self.style.ERROR(
                    'Must specify --ids, --category, or --status'
                ))
                return
            
            article_count = articles.count()
            
            if article_count > 0:
                self.stdout.write(f'\nFound {article_count} articles to process')
                
                if action == 'publish':
                    if not dry_run:
                        updated = articles.update(status=NewsArticle.Status.PUBLISHED)
                        self.stdout.write(
                            self.style.SUCCESS(f'Published {updated} articles')
                        )
                    else:
                        self.stdout.write(f'Would publish {article_count} articles')
                    total_processed += article_count
                
                elif action == 'archive':
                    if not dry_run:
                        updated = articles.update(status=NewsArticle.Status.ARCHIVED)
                        self.stdout.write(
                            self.style.SUCCESS(f'Archived {updated} articles')
                        )
                    else:
                        self.stdout.write(f'Would archive {article_count} articles')
                    total_processed += article_count
                
                elif action == 'feature':
                    if not dry_run:
                        updated = articles.update(is_featured=True)
                        self.stdout.write(
                            self.style.SUCCESS(f'Featured {updated} articles')
                        )
                    else:
                        self.stdout.write(f'Would feature {article_count} articles')
                    total_processed += article_count
                
                elif action == 'unfeature':
                    if not dry_run:
                        updated = articles.update(is_featured=False)
                        self.stdout.write(
                            self.style.SUCCESS(f'Unfeatured {updated} articles')
                        )
                    else:
                        self.stdout.write(f'Would unfeature {article_count} articles')
                    total_processed += article_count
        
        # Process events
        if content_type in ['events', 'both']:
            events = Event.objects.all()
            
            if ids:
                event_ids = [int(id.strip()) for id in ids.split(',')]
                events = events.filter(id__in=event_ids)
            elif category_slug:
                # Events don't have categories directly, skip
                self.stdout.write(self.style.WARNING(
                    'Events do not have categories. Skipping category filter.'
                ))
            elif status_filter:
                status_map = {
                    'draft': Event.Status.DRAFT,
                    'published': Event.Status.PUBLISHED,
                    'archived': Event.Status.COMPLETED,
                }
                events = events.filter(status=status_map[status_filter])
            else:
                if content_type == 'events':
                    self.stderr.write(self.style.ERROR(
                        'Must specify --ids or --status for events'
                    ))
                    return
            
            event_count = events.count()
            
            if event_count > 0:
                self.stdout.write(f'\nFound {event_count} events to process')
                
                if action == 'publish':
                    if not dry_run:
                        updated = events.update(status=Event.Status.PUBLISHED)
                        self.stdout.write(
                            self.style.SUCCESS(f'Published {updated} events')
                        )
                    else:
                        self.stdout.write(f'Would publish {event_count} events')
                    total_processed += event_count
                
                elif action == 'archive':
                    if not dry_run:
                        updated = events.update(status=Event.Status.COMPLETED)
                        self.stdout.write(
                            self.style.SUCCESS(f'Marked {updated} events as completed')
                        )
                    else:
                        self.stdout.write(f'Would mark {event_count} events as completed')
                    total_processed += event_count
                
                elif action == 'feature':
                    if not dry_run:
                        updated = events.update(is_featured=True)
                        self.stdout.write(
                            self.style.SUCCESS(f'Featured {updated} events')
                        )
                    else:
                        self.stdout.write(f'Would feature {event_count} events')
                    total_processed += event_count
                
                elif action == 'unfeature':
                    if not dry_run:
                        updated = events.update(is_featured=False)
                        self.stdout.write(
                            self.style.SUCCESS(f'Unfeatured {updated} events')
                        )
                    else:
                        self.stdout.write(f'Would unfeature {event_count} events')
                    total_processed += event_count
        
        if total_processed == 0:
            self.stdout.write(self.style.WARNING('No items found to process'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nTotal processed: {total_processed} items')
            )

