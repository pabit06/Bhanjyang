from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.dashboard.models import PageView, PerformanceMetric, ErrorLog


class Command(BaseCommand):
    help = 'Check dashboard data and populate if empty'

    def handle(self, *args, **options):
        self.stdout.write('Checking dashboard data...')
        
        # Check existing data
        page_views_count = PageView.objects.count()
        performance_count = PerformanceMetric.objects.count()
        error_count = ErrorLog.objects.count()
        
        self.stdout.write(f'Current data:')
        self.stdout.write(f'- Page Views: {page_views_count}')
        self.stdout.write(f'- Performance Metrics: {performance_count}')
        self.stdout.write(f'- Error Logs: {error_count}')
        
        if page_views_count == 0 and performance_count == 0 and error_count == 0:
            self.stdout.write('No data found. Generating sample data...')
            
            # Generate some basic data
            pages = [
                {'url': '/', 'title': 'Homepage'},
                {'url': '/about/', 'title': 'About Us'},
                {'url': '/services/', 'title': 'Services'},
                {'url': '/contact/', 'title': 'Contact'},
                {'url': '/members/', 'title': 'Member Login'},
                {'url': '/dashboard/', 'title': 'Dashboard'},
            ]
            
            browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
            error_types = ['404 Not Found', '500 Internal Server Error', 'Database Error']
            
            # Generate data for the last 7 days
            for day in range(7):
                current_date = timezone.now() - timedelta(days=day)
                
                # Generate page views
                for _ in range(10, 30):  # 10-30 page views per day
                    page = pages[day % len(pages)]  # Cycle through pages
                    PageView.objects.create(
                        page_url=page['url'],
                        page_title=page['title'],
                        load_time=800 + (day * 100) + (hash(str(current_date)) % 500),  # Varying load times
                        is_mobile=day % 2 == 0,  # Alternate mobile/desktop
                        browser=browsers[day % len(browsers)],
                        timestamp=current_date + timedelta(
                            hours=hash(str(current_date)) % 24,
                            minutes=hash(str(current_date)) % 60
                        )
                    )
                
                # Generate performance metrics
                for metric_type in ['database_query', 'api_response', 'memory_usage']:
                    for _ in range(5, 15):  # 5-15 metrics per type per day
                        if metric_type == 'memory_usage':
                            value = 100 + (day * 20) + (hash(str(current_date)) % 200)  # MB
                        else:
                            value = 50 + (day * 50) + (hash(str(current_date)) % 1000)  # ms
                        
                        PerformanceMetric.objects.create(
                            metric_type=metric_type,
                            value=value,
                            timestamp=current_date + timedelta(
                                hours=hash(str(current_date)) % 24,
                                minutes=hash(str(current_date)) % 60
                            )
                        )
                
                # Generate some errors (not every day)
                if day % 3 == 0:  # Errors every 3rd day
                    for _ in range(1, 5):  # 1-5 errors
                        ErrorLog.objects.create(
                            error_type=error_types[day % len(error_types)],
                            error_message=f'Error occurred on {current_date.strftime("%Y-%m-%d")}',
                            page_url=pages[day % len(pages)]['url'],
                            timestamp=current_date + timedelta(
                                hours=hash(str(current_date)) % 24,
                                minutes=hash(str(current_date)) % 60
                            ),
                            resolved=day % 2 == 0  # Alternate resolved/unresolved
                        )
            
            # Check final counts
            final_page_views = PageView.objects.count()
            final_performance = PerformanceMetric.objects.count()
            final_errors = ErrorLog.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Generated sample data:\n'
                    f'- Page Views: {final_page_views}\n'
                    f'- Performance Metrics: {final_performance}\n'
                    f'- Error Logs: {final_errors}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Data already exists in the database!')
            )
