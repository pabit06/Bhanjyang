from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Avg, Count
from apps.dashboard.models import PerformanceAlert, AlertLog, PageView, ErrorLog

class Command(BaseCommand):
    help = 'Check performance thresholds and create alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-load-time',
            action='store_true',
            help='Check load time thresholds'
        )
        parser.add_argument(
            '--check-error-rate',
            action='store_true',
            help='Check error rate thresholds'
        )
        parser.add_argument(
            '--check-all',
            action='store_true',
            help='Check all thresholds'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Performance Alert Checker')
        )
        self.stdout.write('=' * 50)
        
        if options['check_all']:
            self.check_load_time_thresholds()
            self.check_error_rate_thresholds()
        elif options['check_load_time']:
            self.check_load_time_thresholds()
        elif options['check_error_rate']:
            self.check_error_rate_thresholds()
        else:
            self.check_load_time_thresholds()
            self.check_error_rate_thresholds()

    def check_load_time_thresholds(self):
        """Check load time thresholds and create alerts"""
        self.stdout.write('Checking load time thresholds...')
        
        # Get active load time alerts
        load_time_alerts = PerformanceAlert.objects.filter(
            alert_type='load_time',
            is_active=True
        )
        
        # Calculate current average load time (last hour)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        current_avg_load_time = PageView.objects.filter(
            timestamp__gte=one_hour_ago
        ).aggregate(avg=Avg('load_time'))['avg'] or 0
        
        for alert in load_time_alerts:
            if alert.check_threshold(current_avg_load_time):
                # Check if alert already exists for this threshold
                existing_alert = AlertLog.objects.filter(
                    alert=alert,
                    is_resolved=False,
                    triggered_at__gte=one_hour_ago
                ).first()
                
                if not existing_alert:
                    AlertLog.objects.create(
                        alert=alert,
                        current_value=current_avg_load_time,
                        message=f"Average load time ({current_avg_load_time:.1f}ms) exceeds threshold ({alert.threshold_value}ms)"
                    )
                    self.stdout.write(
                        self.style.WARNING(f"Alert created: Load time {current_avg_load_time:.1f}ms > {alert.threshold_value}ms")
                    )

    def check_error_rate_thresholds(self):
        """Check error rate thresholds and create alerts"""
        self.stdout.write('Checking error rate thresholds...')
        
        # Get active error rate alerts
        error_rate_alerts = PerformanceAlert.objects.filter(
            alert_type='error_rate',
            is_active=True
        )
        
        # Calculate current error rate (last hour)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        total_requests = PageView.objects.filter(timestamp__gte=one_hour_ago).count()
        total_errors = ErrorLog.objects.filter(timestamp__gte=one_hour_ago).count()
        
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        for alert in error_rate_alerts:
            if alert.check_threshold(error_rate):
                # Check if alert already exists for this threshold
                existing_alert = AlertLog.objects.filter(
                    alert=alert,
                    is_resolved=False,
                    triggered_at__gte=one_hour_ago
                ).first()
                
                if not existing_alert:
                    AlertLog.objects.create(
                        alert=alert,
                        current_value=error_rate,
                        message=f"Error rate ({error_rate:.2f}%) exceeds threshold ({alert.threshold_value}%)"
                    )
                    self.stdout.write(
                        self.style.WARNING(f"Alert created: Error rate {error_rate:.2f}% > {alert.threshold_value}%")
                    )

    def create_default_alerts(self):
        """Create default performance alerts"""
        self.stdout.write('Creating default performance alerts...')
        
        default_alerts = [
            {
                'alert_type': 'load_time',
                'threshold_value': 3000,
                'severity': 'high',
                'description': 'Alert when average page load time exceeds 3 seconds'
            },
            {
                'alert_type': 'load_time',
                'threshold_value': 5000,
                'severity': 'critical',
                'description': 'Alert when average page load time exceeds 5 seconds'
            },
            {
                'alert_type': 'error_rate',
                'threshold_value': 5.0,
                'severity': 'medium',
                'description': 'Alert when error rate exceeds 5%'
            },
            {
                'alert_type': 'error_rate',
                'threshold_value': 10.0,
                'severity': 'high',
                'description': 'Alert when error rate exceeds 10%'
            }
        ]
        
        for alert_data in default_alerts:
            alert, created = PerformanceAlert.objects.get_or_create(
                alert_type=alert_data['alert_type'],
                threshold_value=alert_data['threshold_value'],
                defaults=alert_data
            )
            
            if created:
                self.stdout.write(f"Created alert: {alert}")
            else:
                self.stdout.write(f"Alert already exists: {alert}")
