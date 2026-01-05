"""
Management command to export news articles and events to JSON or CSV format.

This command is useful for backups, migrations, or data analysis.
"""

import json
import csv
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from apps.news_events.models import NewsArticle, Event, Category
from apps.news_events.constants import DEFAULT_RECENT_LIMIT


class Command(BaseCommand):
    help = 'Export news articles and events to JSON or CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv'],
            default='json',
            help='Export format (default: json)'
        )
        parser.add_argument(
            '--output',
            type=str,
            required=True,
            help='Output file path'
        )
        parser.add_argument(
            '--content-type',
            type=str,
            choices=['articles', 'events', 'both'],
            default='both',
            help='Type of content to export (default: both)'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['published', 'draft', 'archived', 'all'],
            default='published',
            help='Filter by status (default: published)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of items to export'
        )

    def handle(self, *args, **options):
        output_format = options['format']
        output_path = options['output']
        content_type = options['content_type']
        status_filter = options['status']
        limit = options.get('limit')
        
        data = {}
        
        # Export articles
        if content_type in ['articles', 'both']:
            articles = NewsArticle.objects.all()
            
            if status_filter == 'published':
                articles = articles.filter(status=NewsArticle.Status.PUBLISHED)
            elif status_filter == 'draft':
                articles = articles.filter(status=NewsArticle.Status.DRAFT)
            elif status_filter == 'archived':
                articles = articles.filter(status=NewsArticle.Status.ARCHIVED)
            
            articles = articles.select_related('author', 'category').order_by('-published_date')
            
            if limit:
                articles = articles[:limit]
            
            data['articles'] = [
                {
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'category': article.category.name if article.category else None,
                    'author': article.author.username if article.author else None,
                    'excerpt': article.excerpt,
                    'status': article.status,
                    'priority': article.priority,
                    'is_featured': article.is_featured,
                    'published_date': article.published_date.isoformat() if article.published_date else None,
                    'view_count': article.view_count,
                    'share_count': article.share_count,
                    'comment_count': article.comment_count,
                    'created_at': article.created_at.isoformat(),
                    'updated_at': article.updated_at.isoformat(),
                }
                for article in articles
            ]
        
        # Export events
        if content_type in ['events', 'both']:
            events = Event.objects.all()
            
            if status_filter == 'published':
                events = events.filter(status=Event.Status.PUBLISHED)
            elif status_filter == 'draft':
                events = events.filter(status=Event.Status.DRAFT)
            elif status_filter == 'archived':
                events = events.filter(status=Event.Status.COMPLETED)
            
            events = events.order_by('-event_date')
            
            if limit:
                events = events[:limit]
            
            data['events'] = [
                {
                    'id': event.id,
                    'title': event.title,
                    'slug': event.slug,
                    'event_type': event.event_type,
                    'description': event.short_description,
                    'location': event.location,
                    'event_date': event.event_date.isoformat() if event.event_date else None,
                    'end_date': event.end_date.isoformat() if event.end_date else None,
                    'status': event.status,
                    'is_featured': event.is_featured,
                    'view_count': event.view_count,
                    'registration_count': event.registration_count,
                    'created_at': event.created_at.isoformat(),
                    'updated_at': event.updated_at.isoformat(),
                }
                for event in events
            ]
        
        # Export categories
        if content_type == 'both':
            categories = Category.objects.filter(is_active=True)
            data['categories'] = [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'slug': cat.slug,
                    'description': cat.description,
                    'color': cat.color,
                    'icon': cat.icon,
                }
                for cat in categories
            ]
        
        # Write to file
        try:
            if output_format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully exported to {output_path} (JSON)')
                )
            elif output_format == 'csv':
                # For CSV, we'll create separate files for articles and events
                base_path = output_path.replace('.csv', '')
                
                if 'articles' in data:
                    articles_path = f'{base_path}_articles.csv'
                    with open(articles_path, 'w', newline='', encoding='utf-8') as f:
                        if data['articles']:
                            writer = csv.DictWriter(f, fieldnames=data['articles'][0].keys())
                            writer.writeheader()
                            writer.writerows(data['articles'])
                    self.stdout.write(
                        self.style.SUCCESS(f'Exported articles to {articles_path}')
                    )
                
                if 'events' in data:
                    events_path = f'{base_path}_events.csv'
                    with open(events_path, 'w', newline='', encoding='utf-8') as f:
                        if data['events']:
                            writer = csv.DictWriter(f, fieldnames=data['events'][0].keys())
                            writer.writeheader()
                            writer.writerows(data['events'])
                    self.stdout.write(
                        self.style.SUCCESS(f'Exported events to {events_path}')
                    )
            
            # Print summary
            total_items = sum(len(v) for v in data.values() if isinstance(v, list))
            self.stdout.write(
                self.style.SUCCESS(f'\nTotal items exported: {total_items}')
            )
            
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Error exporting data: {str(e)}')
            )
            raise

