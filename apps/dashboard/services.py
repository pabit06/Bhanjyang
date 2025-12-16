from datetime import timedelta
from django.db.models import Avg, Count, Max, Min, Q, F, Sum
from django.utils import timezone
from django.conf import settings
from .models import (
    PerformanceMetric, PageView, ErrorLog, UserSession, PerformanceReport,
    PerformanceAlert, AlertLog, DashboardWidget, UserDashboardPreference, AuditLog
)
from apps.downloads.models import DownloadableFile
from apps.news_events.models import NewsArticle
from apps.about.models import Person, Staff
from apps.contact.models import ContactSubmission
import logging
import csv
from io import StringIO
import json

logger = logging.getLogger(__name__)

class DashboardAnalyticsService:
    """Service for handling dashboard analytics and metrics"""
    
    @staticmethod
    def get_dashboard_summary():
        """Get high-level summary stats for the main dashboard"""
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # 1. Page Load Performance
        avg_today = PageView.objects.filter(timestamp__date=today).aggregate(avg=Avg('load_time'))['avg'] or 0
        avg_week = PageView.objects.filter(timestamp__gte=week_ago).aggregate(avg=Avg('load_time'))['avg'] or 0
        avg_month = PageView.objects.filter(timestamp__gte=month_ago).aggregate(avg=Avg('load_time'))['avg'] or 0
        
        # 2. View Counts
        views_today = PageView.objects.filter(timestamp__date=today).count()
        views_week = PageView.objects.filter(timestamp__gte=week_ago).count()
        views_month = PageView.objects.filter(timestamp__gte=month_ago).count()
        
        # 3. Error Tracking
        errors_today = ErrorLog.objects.filter(timestamp__date=today).count()
        errors_week = ErrorLog.objects.filter(timestamp__gte=week_ago).count()
        unresolved = ErrorLog.objects.filter(resolved=False).count()
        
        # 4. Top/Slow Pages (Efficiently limited)
        slowest_pages = list(PageView.objects.filter(timestamp__gte=week_ago)
                             .values('page_url', 'page_title')
                             .annotate(avg_load_time=Avg('load_time'), count=Count('id'))
                             .order_by('-avg_load_time')[:7])
                             
        most_visited = list(PageView.objects.filter(timestamp__gte=week_ago)
                            .values('page_url', 'page_title')
                            .annotate(count=Count('id'), avg_load_time=Avg('load_time')) # Added load time for context
                            .order_by('-count')[:7])
        
        # 5. Device/Browser Stats
        total_week_views = views_week if views_week > 0 else 1
        mobile_count = PageView.objects.filter(timestamp__gte=week_ago, is_mobile=True).count()
        mobile_percent = round((mobile_count / total_week_views) * 100, 1)
        
        browser_stats = list(PageView.objects.filter(timestamp__gte=week_ago)
                             .values('browser')
                             .annotate(count=Count('id'))
                             .order_by('-count')[:5])

        return {
            'performance': {
                'today': avg_today, 'week': avg_week, 'month': avg_month,
                'thresholds': {'excellent': 1000, 'good': 2000, 'poor': 3000}
            },
            'views': {'today': views_today, 'week': views_week, 'month': views_month},
            'errors': {'today': errors_today, 'week': errors_week, 'unresolved': unresolved},
            'pages': {'slowest': slowest_pages, 'popular': most_visited},
            'tech': {'mobile_percent': mobile_percent, 'browsers': browser_stats}
        }

    @staticmethod
    def get_domain_stats():
        """Get stats from other domains (Downloads, News, Team, etc.)"""
        week_ago = timezone.now() - timedelta(days=7)
        month_ago = timezone.now() - timedelta(days=30)
        
        # Use simple try-except blocks individually to prevent whole failure
        try:
            downloads = {
                'total': DownloadableFile.objects.count(),
                'active': DownloadableFile.objects.filter(is_active=True).count(),
                'total_downloads': DownloadableFile.objects.aggregate(t=Sum('download_count'))['t'] or 0
            }
        except Exception: downloads = {}

        try:
            updates = {
                'total': NewsArticle.objects.count(),
                'published': NewsArticle.objects.filter(status='PB').count(),
                'recent': NewsArticle.objects.filter(created_at__gte=week_ago).count()
            }
        except Exception: updates = {}
        
        try:
            team = {
                'total': Person.objects.count(),
                'active_staff': Staff.objects.filter(is_active=True).count()
            }
        except Exception: team = {}
        
        try:
            contacts = {
                'total': ContactSubmission.objects.count(),
                'new': ContactSubmission.objects.filter(status='new').count()
            }
        except Exception: contacts = {}
        
        return {'downloads': downloads, 'updates': updates, 'team': team, 'contacts': contacts}

    @staticmethod
    def get_chart_data(metric_type, days=7, filters=None):
        """Get aggregated data for charts"""
        start_date = timezone.now() - timedelta(days=days)
        filters = filters or {}
        
        if metric_type == 'page_load':
            qs = PageView.objects.filter(timestamp__gte=start_date)
            if filters.get('device_type'):
                qs = qs.filter(is_mobile=(filters['device_type'] == 'mobile'))
            if filters.get('browser'): qs = qs.filter(browser=filters['browser'])
            
            data = qs.values('timestamp__date').annotate(
                val=Avg('load_time'), count=Count('id')
            ).order_by('timestamp__date')
            
            return {
                'labels': [x['timestamp__date'].strftime('%Y-%m-%d') for x in data],
                'data': [round(x['val'], 2) for x in data],
                'meta': {'counts': [x['count'] for x in data]}
            }
            
        elif metric_type == 'errors':
            qs = ErrorLog.objects.filter(timestamp__gte=start_date)
            if filters.get('page_type'): # Mapping error_type to page_type param
                qs = qs.filter(error_type=filters['page_type'])
                
            data = qs.values('timestamp__date').annotate(val=Count('id')).order_by('timestamp__date')
            return {
                'labels': [x['timestamp__date'].strftime('%Y-%m-%d') for x in data],
                'data': [x['val'] for x in data]
            }
            
        elif metric_type == 'traffic':
            qs = PageView.objects.filter(timestamp__gte=start_date)
            if filters.get('page_url'):
                qs = qs.filter(page_url__contains=filters['page_url'])
            
            data = qs.values('timestamp__date').annotate(
                val=Count('id'), unique=Count('session_id', distinct=True)
            ).order_by('timestamp__date')
            
            return {
                'labels': [x['timestamp__date'].strftime('%Y-%m-%d') for x in data],
                'data': [x['val'] for x in data],
                'meta': {'unique': [x['unique'] for x in data]}
            }
            
        return {}

    @staticmethod
    def record_page_view(data, request_meta):
        """Record a page view efficiently"""
        try:
            user = request_meta.get('user') if request_meta.get('user') and request_meta['user'].is_authenticated else None
            
            PageView.objects.create(
                page_url=data.get('page_url', '')[:500],
                page_title=data.get('page_title', '')[:200],
                load_time=data.get('load_time', 0),
                user_agent=request_meta.get('HTTP_USER_AGENT', '')[:500],
                ip_address=request_meta.get('REMOTE_ADDR', ''),
                session_id=request_meta.get('session_id', '')[:100],
                user=user,
                referrer=data.get('referrer', '')[:500],
                is_mobile=data.get('is_mobile', False),
                browser=data.get('browser', '')[:50]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to record page view: {e}")
            return False

    @staticmethod
    def record_error(data, request_meta):
        """Record an error log"""
        try:
            user = request_meta.get('user') if request_meta.get('user') and request_meta['user'].is_authenticated else None
            
            ErrorLog.objects.create(
                error_type=data.get('error_type', 'unknown')[:20],
                error_message=data.get('error_message', 'No message'),
                page_url=data.get('page_url', '')[:500],
                stack_trace=data.get('stack_trace', ''),
                user_agent=request_meta.get('HTTP_USER_AGENT', ''),
                ip_address=request_meta.get('REMOTE_ADDR', ''),
                session_id=request_meta.get('session_id', '')[:100],
                user=user
            )
            return True
        except Exception as e:
            logger.error(f"Failed to record error: {e}")
            return False


class DashboardReportingService:
    """Service for generating reports and exports"""

    @staticmethod
    def generate_report(user, report_type, start_date, end_date):
        """Generate a summarized performance report"""
        # Gather data
        views_qs = PageView.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date)
        error_qs = ErrorLog.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date)
        
        report_data = {
            'total_views': views_qs.count(),
            'avg_load_time': views_qs.aggregate(avg=Avg('load_time'))['avg'] or 0,
            'total_errors': error_qs.count(),
            'unique_visitors': views_qs.aggregate(u=Count('session_id', distinct=True))['u'] or 0,
            'top_pages': list(views_qs.values('page_url').annotate(c=Count('id')).order_by('-c')[:10]),
            'error_breakdown': list(error_qs.values('error_type').annotate(c=Count('id')).order_by('-c'))
        }
        
        # Save Report
        report = PerformanceReport.objects.create(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            generated_by=user,
            report_data=report_data,
            summary=f"Report for {start_date.date()} to {end_date.date()}"
        )
        return report

    @staticmethod
    def export_data_csv(data_type, days=7):
        """Export raw data as CSV"""
        start_date = timezone.now() - timedelta(days=days)
        output = StringIO()
        writer = csv.writer(output)
        
        if data_type == 'page_views':
            writer.writerow(['Timestamp', 'URL', 'Load Time(ms)', 'User', 'Mobile'])
            qs = PageView.objects.filter(timestamp__gte=start_date).select_related('user')
            for item in qs.iterator():
                writer.writerow([
                    item.timestamp.isoformat(),
                    item.page_url,
                    item.load_time,
                    item.user.username if item.user else 'Guest',
                    item.is_mobile
                ])
                
        elif data_type == 'errors':
            writer.writerow(['Timestamp', 'Type', 'Message', 'URL', 'Resolved'])
            qs = ErrorLog.objects.filter(timestamp__gte=start_date)
            for item in qs.iterator():
                writer.writerow([
                    item.timestamp.isoformat(),
                    item.error_type,
                    item.error_message,
                    item.page_url,
                    "Yes" if item.resolved else "No"
                ])
                
        return output.getvalue()


class DashboardMonitoringService:
    """Service for Alerts and Security"""
    
    @staticmethod
    def get_active_alerts():
        return AlertLog.objects.filter(is_resolved=False).select_related('alert').order_by('-triggered_at')[:20]

    @staticmethod
    def resolve_alert(alert_id, user):
        try:
            alert = AlertLog.objects.get(id=alert_id)
            alert.is_resolved = True
            alert.resolved_at = timezone.now()
            alert.resolved_by = user
            alert.save()
            return True
        except AlertLog.DoesNotExist:
            return False


class DashboardWidgetService:
    """Service for User Preferences"""
    
    @staticmethod
    def get_user_config(user):
        pref, _ = UserDashboardPreference.objects.get_or_create(user=user)
        # If no widgets, could load defaults here
        return {
            'theme': pref.theme,
            'refresh_interval': pref.refresh_interval,
            'widgets': list(pref.widgets.values('id', 'name', 'widget_type', 'config'))
        }

    @staticmethod
    def update_preferences(user, data):
        pref, _ = UserDashboardPreference.objects.get_or_create(user=user)
        if 'theme' in data: pref.theme = data['theme']
        if 'refresh_interval' in data: pref.refresh_interval = data['refresh_interval']
        pref.save()
        return True
