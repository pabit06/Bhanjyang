from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from apps.dashboard.models import PageView, PerformanceMetric, ErrorLog


class Command(BaseCommand):
    help = 'Generate sample data for dashboard testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to generate data for (default: 30)'
        )

    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(f'Generating sample data for {days} days...')
        
        # Clear existing data
        PageView.objects.all().delete()
        PerformanceMetric.objects.all().delete()
        ErrorLog.objects.all().delete()
        
        # Generate sample data
        pages = [
            {'url': '/', 'title': 'Homepage'},
            {'url': '/about/', 'title': 'About Us'},
            {'url': '/services/', 'title': 'Services'},
            {'url': '/contact/', 'title': 'Contact'},
            {'url': '/members/', 'title': 'Member Login'},
            {'url': '/dashboard/', 'title': 'Dashboard'},
        ]
        
        browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
        error_types = ['404 Not Found', '500 Internal Server Error', 'Database Error', 'Timeout Error', 'Validation Error']
        
        for day in range(days):
            current_date = timezone.now() - timedelta(days=day)
            
            # Generate page views for this day
            for _ in range(random.randint(20, 100)):
                page = random.choice(pages)
                PageView.objects.create(
                    page_url=page['url'],
                    page_title=page['title'],
                    load_time=random.randint(800, 3000),
                    is_mobile=random.choice([True, False]),
                    browser=random.choice(browsers),
                    timestamp=current_date + timedelta(
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                )
            
            # Generate performance metrics
            for metric_type in ['database_query', 'api_response', 'memory_usage']:
                for _ in range(random.randint(5, 20)):
                    if metric_type == 'memory_usage':
                        value = random.randint(100, 500)  # MB
                    else:
                        value = random.randint(50, 2000)  # ms
                    
                    PerformanceMetric.objects.create(
                        metric_type=metric_type,
                        value=value,
                        timestamp=current_date + timedelta(
                            hours=random.randint(0, 23),
                            minutes=random.randint(0, 59)
                        )
                    )
            
            # Generate error logs
            for _ in range(random.randint(0, 10)):
                ErrorLog.objects.create(
                    error_type=random.choice(error_types),
                    error_message=f'Sample error message {random.randint(1, 1000)}',
                    page_url=random.choice(pages)['url'],
                    timestamp=current_date + timedelta(
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    ),
                    resolved=random.choice([True, False])
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated sample data:\n'
                f'- {PageView.objects.count()} page views\n'
                f'- {PerformanceMetric.objects.count()} performance metrics\n'
                f'- {ErrorLog.objects.count()} error logs'
            )
        )
