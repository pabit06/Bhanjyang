"""
Management command to clear news events app cache.

This command helps clear specific cache keys or all cache related to
the news events app.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.core.cache.utils import make_key
from apps.news_events.performance import NewsEventsCache


class Command(BaseCommand):
    help = 'Clear news events app cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all news events related cache'
        )
        parser.add_argument(
            '--articles',
            action='store_true',
            help='Clear article list cache'
        )
        parser.add_argument(
            '--events',
            action='store_true',
            help='Clear event list cache'
        )
        parser.add_argument(
            '--analytics',
            action='store_true',
            help='Clear analytics cache'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Clear statistics cache'
        )
        parser.add_argument(
            '--invalid-slugs',
            action='store_true',
            help='Clear invalid slug cache'
        )

    def handle(self, *args, **options):
        cleared_count = 0
        
        if options['all']:
            # Clear all cache keys that start with news events prefixes
            cache_patterns = [
                'article_list',
                'event_list',
                'category_stats',
                'analytics_',
                'invalid_slug_',
            ]
            
            # Note: Django cache doesn't support pattern deletion directly
            # This is a simplified version - in production, use Redis with pattern matching
            self.stdout.write(self.style.WARNING(
                'Clearing all news events cache (pattern-based clearing may be limited)'
            ))
            cache.clear()
            cleared_count = 1
            self.stdout.write(self.style.SUCCESS('All cache cleared'))
        else:
            # Clear specific cache types
            if options['articles']:
                # Clear article list cache
                cache_keys = [
                    NewsEventsCache.get_article_list_cache_key(),
                    NewsEventsCache.get_article_list_cache_key(limit=6),
                    NewsEventsCache.get_article_list_cache_key(limit=10),
                ]
                for key in cache_keys:
                    cache.delete(key)
                cleared_count += len(cache_keys)
                self.stdout.write(self.style.SUCCESS('Article cache cleared'))
            
            if options['events']:
                # Clear event list cache
                cache_keys = [
                    NewsEventsCache.get_event_list_cache_key(),
                    NewsEventsCache.get_event_list_cache_key(limit=3),
                    NewsEventsCache.get_event_list_cache_key(limit=10),
                ]
                for key in cache_keys:
                    cache.delete(key)
                cleared_count += len(cache_keys)
                self.stdout.write(self.style.SUCCESS('Event cache cleared'))
            
            if options['analytics']:
                # Clear analytics cache
                cache_keys = [
                    NewsEventsCache.get_analytics_cache_key('article', '30d'),
                    NewsEventsCache.get_analytics_cache_key('event', '30d'),
                ]
                for key in cache_keys:
                    cache.delete(key)
                cleared_count += len(cache_keys)
                self.stdout.write(self.style.SUCCESS('Analytics cache cleared'))
            
            if options['stats']:
                # Clear statistics cache
                cache_key = NewsEventsCache.get_category_stats_cache_key()
                cache.delete(cache_key)
                cleared_count += 1
                self.stdout.write(self.style.SUCCESS('Statistics cache cleared'))
            
            if options['invalid_slugs']:
                # Note: Invalid slug cache uses hashed keys, so we can't easily clear all
                # This would require iterating through all possible slugs, which is not practical
                self.stdout.write(self.style.WARNING(
                    'Invalid slug cache uses hashed keys. Use --all to clear all cache.'
                ))
        
        if cleared_count == 0 and not options['all']:
            self.stdout.write(self.style.WARNING(
                'No cache cleared. Use --all or specify cache types (--articles, --events, etc.)'
            ))
        elif cleared_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nCleared {cleared_count} cache entries')
            )

