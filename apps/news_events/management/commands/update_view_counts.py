"""
Management command to recalculate view counts from analytics.

This command is useful for syncing view counts from ContentAnalytics
to NewsArticle and Event models.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from apps.news_events.models import NewsArticle, Event, ContentAnalytics


class Command(BaseCommand):
    help = 'Recalculate view counts from ContentAnalytics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--content-type',
            type=str,
            choices=['articles', 'events', 'both'],
            default='both',
            help='Type of content to update (default: both)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        content_type = options['content_type']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        total_updated = 0
        
        # Update articles
        if content_type in ['articles', 'both']:
            articles = NewsArticle.objects.all()
            article_count = 0
            
            for article in articles:
                # Get total views from analytics
                analytics = ContentAnalytics.objects.filter(
                    content_type='article',
                    object_id=article.id
                ).aggregate(total_views=Sum('view_count'))
                
                new_view_count = analytics['total_views'] or 0
                
                if article.view_count != new_view_count:
                    if not dry_run:
                        article.view_count = new_view_count
                        article.save(update_fields=['view_count'])
                    article_count += 1
                    self.stdout.write(
                        f'Article {article.id} ({article.title[:50]}): '
                        f'{article.view_count} -> {new_view_count}'
                    )
            
            if article_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {article_count} articles')
                )
                total_updated += article_count
            else:
                self.stdout.write('No articles need view count updates')
        
        # Update events
        if content_type in ['events', 'both']:
            events = Event.objects.all()
            event_count = 0
            
            for event in events:
                # Get total views from analytics
                analytics = ContentAnalytics.objects.filter(
                    content_type='event',
                    object_id=event.id
                ).aggregate(total_views=Sum('view_count'))
                
                new_view_count = analytics['total_views'] or 0
                
                if event.view_count != new_view_count:
                    if not dry_run:
                        event.view_count = new_view_count
                        event.save(update_fields=['view_count'])
                    event_count += 1
                    self.stdout.write(
                        f'Event {event.id} ({event.title[:50]}): '
                        f'{event.view_count} -> {new_view_count}'
                    )
            
            if event_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {event_count} events')
                )
                total_updated += event_count
            else:
                self.stdout.write('No events need view count updates')
        
        if total_updated == 0:
            self.stdout.write(self.style.SUCCESS('All view counts are up to date'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nTotal updated: {total_updated} items')
            )

