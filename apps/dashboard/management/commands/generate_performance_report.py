from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Avg, Count, Q
from apps.dashboard.models import PerformanceMetric, PageView, ErrorLog, UserSession, PerformanceReport

class Command(BaseCommand):
    help = 'Generate performance reports and cleanup old data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['daily', 'weekly', 'monthly'],
            default='daily',
            help='Type of report to generate'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old performance data'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep data (for cleanup)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Performance Report Generator')
        )
        self.stdout.write('=' * 50)
        
        if options['cleanup']:
            self.cleanup_old_data(options['days'])
        
        self.generate_report(options['type'])

    def generate_report(self, report_type):
        """Generate performance report"""
        now = timezone.now()
        
        if report_type == 'daily':
            start_date = now - timedelta(days=1)
            end_date = now
        elif report_type == 'weekly':
            start_date = now - timedelta(days=7)
            end_date = now
        else:  # monthly
            start_date = now - timedelta(days=30)
            end_date = now
        
        self.stdout.write(f'Generating {report_type} report...')
        self.stdout.write(f'Period: {start_date.date()} to {end_date.date()}')
        
        # Collect metrics
        metrics = self.collect_metrics(start_date, end_date)
        
        # Create report
        report = PerformanceReport.objects.create(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            report_data=metrics,
            summary=f"{report_type.title()} performance report"
        )
        
        # Display summary
        self.display_summary(metrics)
        
        self.stdout.write(
            self.style.SUCCESS(f'Report generated successfully! ID: {report.id}')
        )

    def collect_metrics(self, start_date, end_date):
        """Collect performance metrics for the period"""
        metrics = {}
        
        # Page views
        page_views = PageView.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        metrics['total_page_views'] = page_views.count()
        metrics['avg_load_time'] = page_views.aggregate(avg=Avg('load_time'))['avg'] or 0
        metrics['unique_sessions'] = UserSession.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        ).count()
        
        # Top pages
        metrics['top_pages'] = list(
            page_views.values('page_url', 'page_title')
            .annotate(
                count=Count('id'),
                avg_load_time=Avg('load_time')
            )
            .order_by('-count')[:10]
        )
        
        # Slowest pages
        metrics['slowest_pages'] = list(
            page_views.values('page_url', 'page_title')
            .annotate(
                count=Count('id'),
                avg_load_time=Avg('load_time')
            )
            .order_by('-avg_load_time')[:10]
        )
        
        # Errors
        errors = ErrorLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        metrics['total_errors'] = errors.count()
        metrics['error_types'] = list(
            errors.values('error_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Device types
        metrics['device_stats'] = list(
            page_views.values('is_mobile')
            .annotate(
                count=Count('id'),
                avg_load_time=Avg('load_time')
            )
        )
        
        # Browser stats
        metrics['browser_stats'] = list(
            page_views.values('browser')
            .annotate(
                count=Count('id'),
                avg_load_time=Avg('load_time')
            )
            .order_by('-count')[:10]
        )
        
        # Performance trends
        metrics['daily_trends'] = list(
            page_views.extra(
                select={'day': 'date(timestamp)'}
            ).values('day')
            .annotate(
                views=Count('id'),
                avg_load_time=Avg('load_time')
            )
            .order_by('day')
        )
        
        return metrics

    def display_summary(self, metrics):
        """Display report summary"""
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('PERFORMANCE SUMMARY')
        self.stdout.write('=' * 50)
        
        self.stdout.write(f"Total Page Views: {metrics['total_page_views']}")
        self.stdout.write(f"Average Load Time: {metrics['avg_load_time']:.1f}ms")
        self.stdout.write(f"Unique Sessions: {metrics['unique_sessions']}")
        self.stdout.write(f"Total Errors: {metrics['total_errors']}")
        
        self.stdout.write('\nTop Pages:')
        for page in metrics['top_pages'][:5]:
            self.stdout.write(f"  {page['page_title'] or page['page_url']}: {page['count']} views")
        
        self.stdout.write('\nSlowest Pages:')
        for page in metrics['slowest_pages'][:5]:
            self.stdout.write(f"  {page['page_title'] or page['page_url']}: {page['avg_load_time']:.1f}ms")
        
        self.stdout.write('\nError Types:')
        for error in metrics['error_types']:
            self.stdout.write(f"  {error['error_type']}: {error['count']}")

    def cleanup_old_data(self, days):
        """Clean up old performance data"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Cleaning up data older than {days} days...')
        
        # Clean up old metrics
        old_metrics = PerformanceMetric.objects.filter(timestamp__lt=cutoff_date)
        metrics_count = old_metrics.count()
        old_metrics.delete()
        
        # Clean up old page views
        old_views = PageView.objects.filter(timestamp__lt=cutoff_date)
        views_count = old_views.count()
        old_views.delete()
        
        # Clean up old errors (keep resolved ones longer)
        old_errors = ErrorLog.objects.filter(
            timestamp__lt=cutoff_date,
            resolved=True
        )
        errors_count = old_errors.count()
        old_errors.delete()
        
        # Clean up old sessions
        old_sessions = UserSession.objects.filter(start_time__lt=cutoff_date)
        sessions_count = old_sessions.count()
        old_sessions.delete()
        
        self.stdout.write(f'Cleaned up:')
        self.stdout.write(f'  {metrics_count} performance metrics')
        self.stdout.write(f'  {views_count} page views')
        self.stdout.write(f'  {errors_count} resolved errors')
        self.stdout.write(f'  {sessions_count} user sessions')
