# news_events/management/commands/monitor_news.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db.models import Count, Q
from apps.news_events.models import NewsArticle, Event, Category, Subscriber, Comment
from apps.news_events.performance import NewsEventsPerformanceMonitor
from apps.news_events.security import SpamProtectionManager

class Command(BaseCommand):
    help = 'Monitor news and events system health and performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-cache',
            action='store_true',
            help='Check cache performance'
        )
        parser.add_argument(
            '--check-security',
            action='store_true',
            help='Check security metrics'
        )
        parser.add_argument(
            '--check-performance',
            action='store_true',
            help='Check performance metrics'
        )
        parser.add_argument(
            '--check-content',
            action='store_true',
            help='Check content health'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all checks'
        )

    def handle(self, *args, **options):
        checks_run = 0
        
        if options['all'] or options['check_cache']:
            self.check_cache_performance()
            checks_run += 1
        
        if options['all'] or options['check_security']:
            self.check_security_metrics()
            checks_run += 1
        
        if options['all'] or options['check_performance']:
            self.check_performance_metrics()
            checks_run += 1
        
        if options['all'] or options['check_content']:
            self.check_content_health()
            checks_run += 1
        
        if checks_run == 0:
            self.stdout.write("No checks specified. Use --help for available options.")
            return
        
        self.stdout.write(f"\nMonitoring completed. {checks_run} check(s) run.")

    def check_cache_performance(self):
        """Check cache performance"""
        self.stdout.write("\nCACHE PERFORMANCE CHECK")
        self.stdout.write("-" * 40)
        
        try:
            # Test cache operations
            test_key = 'news_monitor_test'
            test_data = {'test': 'data', 'timestamp': timezone.now().isoformat()}
            
            # Set cache
            cache.set(test_key, test_data, timeout=60)
            
            # Get cache
            cached_data = cache.get(test_key)
            
            if cached_data and cached_data['test'] == 'data':
                self.stdout.write(self.style.SUCCESS("Cache operations working correctly"))
            else:
                self.stdout.write(self.style.ERROR("Cache operations failed"))
            
            # Check cache status
            cache_status = "Active" if cached_data else "Inactive"
            self.stdout.write(f"Cache Status: {cache_status}")
            self.stdout.write(f"Cache Timeout: 60 seconds")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Cache check failed: {e}"))

    def check_security_metrics(self):
        """Check security metrics"""
        self.stdout.write("\nSECURITY METRICS CHECK")
        self.stdout.write("-" * 40)
        
        try:
            # Check for spam comments
            spam_comments = Comment.objects.filter(status=Comment.Status.SPAM).count()
            pending_comments = Comment.objects.filter(status=Comment.Status.PENDING).count()
            total_comments = Comment.objects.count()
            
            spam_rate = (spam_comments / total_comments * 100) if total_comments > 0 else 0
            
            self.stdout.write(f"Spam comments: {spam_comments}")
            self.stdout.write(f"Pending comments: {pending_comments}")
            self.stdout.write(f"Spam rate: {spam_rate:.1f}%")
            
            if spam_rate > 20:
                self.stdout.write(self.style.WARNING("High spam rate detected"))
            else:
                self.stdout.write(self.style.SUCCESS("Spam rate within acceptable limits"))
            
            # Check subscriber security
            unconfirmed_subscribers = Subscriber.objects.filter(is_confirmed=False).count()
            total_subscribers = Subscriber.objects.count()
            
            unconfirmed_rate = (unconfirmed_subscribers / total_subscribers * 100) if total_subscribers > 0 else 0
            
            self.stdout.write(f"Unconfirmed subscribers: {unconfirmed_subscribers}")
            self.stdout.write(f"Unconfirmed rate: {unconfirmed_rate:.1f}%")
            
            if unconfirmed_rate > 50:
                self.stdout.write(self.style.WARNING("High unconfirmed subscription rate"))
            else:
                self.stdout.write(self.style.SUCCESS("Subscription confirmation rate acceptable"))
            
            # Check for suspicious content
            suspicious_articles = NewsArticle.objects.filter(
                Q(title__icontains='spam') | Q(content__icontains='spam')
            ).count()
            
            if suspicious_articles > 0:
                self.stdout.write(self.style.WARNING(f"{suspicious_articles} potentially suspicious articles found"))
            else:
                self.stdout.write(self.style.SUCCESS("No suspicious content detected"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Security check failed: {e}"))

    def check_performance_metrics(self):
        """Check performance metrics"""
        self.stdout.write("\nPERFORMANCE METRICS CHECK")
        self.stdout.write("-" * 40)
        
        try:
            # Database query performance
            start_time = timezone.now()
            articles = list(NewsArticle.objects.all()[:100])
            query_time = (timezone.now() - start_time).total_seconds()
            
            if query_time < 0.1:
                self.stdout.write(self.style.SUCCESS(f"Database query performance: {query_time:.3f}s"))
            elif query_time < 0.5:
                self.stdout.write(self.style.WARNING(f"Database query performance: {query_time:.3f}s"))
            else:
                self.stdout.write(self.style.ERROR(f"Database query performance: {query_time:.3f}s"))
            
            # Content statistics
            total_articles = NewsArticle.objects.count()
            published_articles = NewsArticle.objects.filter(status=NewsArticle.Status.PUBLISHED).count()
            draft_articles = NewsArticle.objects.filter(status=NewsArticle.Status.DRAFT).count()
            featured_articles = NewsArticle.objects.filter(is_featured=True).count()
            
            self.stdout.write(f"Total articles: {total_articles}")
            self.stdout.write(f"Published articles: {published_articles}")
            self.stdout.write(f"Draft articles: {draft_articles}")
            self.stdout.write(f"Featured articles: {featured_articles}")
            
            # Event statistics
            total_events = Event.objects.count()
            upcoming_events = Event.objects.filter(
                event_date__gt=timezone.now(),
                status=Event.Status.PUBLISHED
            ).count()
            past_events = Event.objects.filter(
                event_date__lt=timezone.now()
            ).count()
            
            self.stdout.write(f"Total events: {total_events}")
            self.stdout.write(f"Upcoming events: {upcoming_events}")
            self.stdout.write(f"Past events: {past_events}")
            
            # Recent activity
            recent_articles = NewsArticle.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            recent_events = Event.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            self.stdout.write(f"Recent articles (7 days): {recent_articles}")
            self.stdout.write(f"Recent events (7 days): {recent_events}")
            
            # Performance recommendations
            if draft_articles > published_articles * 0.5:
                self.stdout.write(self.style.WARNING("High ratio of draft articles - consider publishing more content"))
            
            if upcoming_events < 3:
                self.stdout.write(self.style.WARNING("Low number of upcoming events"))
            
            if recent_articles < 2:
                self.stdout.write(self.style.WARNING("Low recent article activity"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Performance check failed: {e}"))

    def check_content_health(self):
        """Check content health"""
        self.stdout.write("\nCONTENT HEALTH CHECK")
        self.stdout.write("-" * 40)
        
        try:
            # Check for articles without images
            articles_without_images = NewsArticle.objects.filter(
                image__isnull=True,
                status=NewsArticle.Status.PUBLISHED
            ).count()
            
            total_published = NewsArticle.objects.filter(status=NewsArticle.Status.PUBLISHED).count()
            image_coverage = ((total_published - articles_without_images) / total_published * 100) if total_published > 0 else 0
            
            self.stdout.write(f"Articles without images: {articles_without_images}")
            self.stdout.write(f"Image coverage: {image_coverage:.1f}%")
            
            if image_coverage < 70:
                self.stdout.write(self.style.WARNING("Low image coverage - consider adding more images"))
            else:
                self.stdout.write(self.style.SUCCESS("Good image coverage"))
            
            # Check for articles without excerpts
            articles_without_excerpts = NewsArticle.objects.filter(
                Q(excerpt__isnull=True) | Q(excerpt=''),
                status=NewsArticle.Status.PUBLISHED
            ).count()
            
            excerpt_coverage = ((total_published - articles_without_excerpts) / total_published * 100) if total_published > 0 else 0
            
            self.stdout.write(f"Articles without excerpts: {articles_without_excerpts}")
            self.stdout.write(f"Excerpt coverage: {excerpt_coverage:.1f}%")
            
            if excerpt_coverage < 80:
                self.stdout.write(self.style.WARNING("Low excerpt coverage - consider adding excerpts"))
            else:
                self.stdout.write(self.style.SUCCESS("Good excerpt coverage"))
            
            # Check for events without descriptions
            events_without_descriptions = Event.objects.filter(
                Q(description__isnull=True) | Q(description=''),
                status=Event.Status.PUBLISHED
            ).count()
            
            total_events = Event.objects.filter(status=Event.Status.PUBLISHED).count()
            description_coverage = ((total_events - events_without_descriptions) / total_events * 100) if total_events > 0 else 0
            
            self.stdout.write(f"Events without descriptions: {events_without_descriptions}")
            self.stdout.write(f"Description coverage: {description_coverage:.1f}%")
            
            if description_coverage < 90:
                self.stdout.write(self.style.WARNING("Low event description coverage"))
            else:
                self.stdout.write(self.style.SUCCESS("Good event description coverage"))
            
            # Check for empty categories
            empty_categories = Category.objects.filter(
                articles__isnull=True,
                is_active=True
            ).count()
            
            total_categories = Category.objects.filter(is_active=True).count()
            
            self.stdout.write(f"Empty categories: {empty_categories}")
            self.stdout.write(f"Total active categories: {total_categories}")
            
            if empty_categories > 0:
                self.stdout.write(self.style.WARNING("Some categories have no articles"))
            else:
                self.stdout.write(self.style.SUCCESS("All categories have content"))
            
            # Check for outdated content
            old_articles = NewsArticle.objects.filter(
                published_date__lt=timezone.now() - timedelta(days=365),
                status=NewsArticle.Status.PUBLISHED
            ).count()
            
            self.stdout.write(f"Articles older than 1 year: {old_articles}")
            
            if old_articles > total_published * 0.3:
                self.stdout.write(self.style.WARNING("High number of outdated articles - consider updating"))
            else:
                self.stdout.write(self.style.SUCCESS("Content freshness is good"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Content health check failed: {e}"))
