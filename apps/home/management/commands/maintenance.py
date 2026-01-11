"""
Production maintenance command for the home app
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

from apps.home.models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    NewsletterSubscriber, ContactInquiry, PageView
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Perform maintenance tasks for the home app'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old data and optimize database',
        )
        parser.add_argument(
            '--cache-clear',
            action='store_true',
            help='Clear all home app cache',
        )
        parser.add_argument(
            '--expired-announcements',
            action='store_true',
            help='Deactivate expired announcements',
        )
        parser.add_argument(
            '--analytics-cleanup',
            action='store_true',
            help='Clean up old analytics data',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all maintenance tasks',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days for cleanup operations (default: 90)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting home app maintenance...')
        )
        
        if options['all'] or options['cleanup']:
            self.cleanup_old_data(options['days'])
        
        if options['all'] or options['cache_clear']:
            self.clear_cache()
        
        if options['all'] or options['expired_announcements']:
            self.deactivate_expired_announcements()
        
        if options['all'] or options['analytics_cleanup']:
            self.cleanup_analytics(options['days'])
        
        self.stdout.write(
            self.style.SUCCESS('Maintenance completed successfully!')
        )

    def cleanup_old_data(self, days):
        """Clean up old data"""
        self.stdout.write('Cleaning up old data...')
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        with transaction.atomic():
            # Clean up old page views
            old_views = PageView.objects.filter(created_at__lt=cutoff_date)
            views_count = old_views.count()
            old_views.delete()
            
            if views_count > 0:
                self.stdout.write(f'Deleted {views_count} old page views')
            
            # Clean up resolved contact inquiries older than specified days
            old_inquiries = ContactInquiry.objects.filter(
                is_resolved=True,
                resolved_at__lt=cutoff_date
            )
            inquiries_count = old_inquiries.count()
            old_inquiries.delete()
            
            if inquiries_count > 0:
                self.stdout.write(f'Deleted {inquiries_count} old resolved inquiries')
            
            # Clean up inactive newsletter subscribers older than specified days
            old_subscribers = NewsletterSubscriber.objects.filter(
                is_active=False,
                unsubscribed_at__lt=cutoff_date
            )
            subscribers_count = old_subscribers.count()
            old_subscribers.delete()
            
            if subscribers_count > 0:
                self.stdout.write(f'Deleted {subscribers_count} old inactive subscribers')

    def clear_cache(self):
        """Clear all home app cache"""
        self.stdout.write('Clearing home app cache...')
        
        # Clear specific cache keys
        cache_keys_to_clear = [
            'homepage_data',
            'about_page_data',
            'gallery_data',
            'api_statistics',
            'api_testimonials',
        ]
        
        cleared_count = 0
        for key_pattern in cache_keys_to_clear:
            # Clear both staff and non-staff versions
            for staff_suffix in ['', '_staff']:
                cache_key = f'{key_pattern}{staff_suffix}'
                if cache.get(cache_key):
                    cache.delete(cache_key)
                    cleared_count += 1
        
        self.stdout.write(f'Cleared {cleared_count} cache entries')

    def deactivate_expired_announcements(self):
        """Deactivate expired announcements"""
        self.stdout.write('Deactivating expired announcements...')
        
        expired_announcements = Announcement.objects.filter(
            expiry_date__lt=timezone.now(),
            is_active=True
        )
        
        count = expired_announcements.count()
        expired_announcements.update(is_active=False)
        
        if count > 0:
            self.stdout.write(f'Deactivated {count} expired announcements')

    def cleanup_analytics(self, days):
        """Clean up old analytics data"""
        self.stdout.write('Cleaning up analytics data...')
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        # Clean up old page views
        old_views = PageView.objects.filter(created_at__lt=cutoff_date)
        views_count = old_views.count()
        old_views.delete()
        
        if views_count > 0:
            self.stdout.write(f'Deleted {views_count} old analytics records')

    def optimize_database(self):
        """Optimize database tables"""
        self.stdout.write('Optimizing database...')
        
        # This would typically involve database-specific optimization commands
        # For SQLite, we can use VACUUM
        from django.db import connection
        
        with connection.cursor() as cursor:
            try:
                cursor.execute("VACUUM")
                self.stdout.write('Database vacuum completed')
            except Exception as e:
                self.stdout.write(f'Database optimization failed: {e}')

    def generate_report(self):
        """Generate maintenance report"""
        self.stdout.write('Generating maintenance report...')
        
        report = {
            'total_homepage_content': HomePageContent.objects.count(),
            'active_testimonials': Testimonial.objects.filter(is_active=True).count(),
            'featured_testimonials': Testimonial.objects.filter(is_featured=True, is_active=True).count(),
            'active_statistics': Statistic.objects.filter(is_active=True).count(),
            'active_announcements': Announcement.objects.filter(is_active=True).count(),
            'expired_announcements': Announcement.objects.filter(
                expiry_date__lt=timezone.now(),
                is_active=True
            ).count(),


            'newsletter_subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
            'unresolved_inquiries': ContactInquiry.objects.filter(is_resolved=False).count(),
            'total_page_views': PageView.objects.count(),
        }
        
        self.stdout.write('\n=== Home App Status Report ===')
        for key, value in report.items():
            self.stdout.write(f'{key.replace("_", " ").title()}: {value}')
        
        return report