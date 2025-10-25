from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count, Q, F, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import PerformanceMetric, PageView, ErrorLog, UserSession, PerformanceReport
from apps.downloads.models import DownloadableFile
from apps.news_events.models import NewsArticle
from apps.about.models import Person, Staff
from apps.contact.models import ContactSubmission
from .cache_utils import DashboardDataProvider, DashboardCache
import logging

logger = logging.getLogger(__name__)

@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    """Main website dashboard with comprehensive analytics"""
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Time ranges
            now = timezone.now()
            today = now.date()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # Performance thresholds
            context['performance_thresholds'] = {
                'excellent_load_time': 1000,  # ms
                'good_load_time': 2000,
                'poor_load_time': 3000,
            }
            
            # Page load performance with error handling
            try:
                context['avg_load_time_today'] = PageView.objects.filter(
                    timestamp__date=today
                ).aggregate(avg=Avg('load_time'))['avg'] or 0
            except Exception as e:
                logger.error(f"Error calculating avg_load_time_today: {e}")
                context['avg_load_time_today'] = 0
            
            try:
                context['avg_load_time_week'] = PageView.objects.filter(
                    timestamp__gte=week_ago
                ).aggregate(avg=Avg('load_time'))['avg'] or 0
            except Exception as e:
                logger.error(f"Error calculating avg_load_time_week: {e}")
                context['avg_load_time_week'] = 0
            
            try:
                context['avg_load_time_month'] = PageView.objects.filter(
                    timestamp__gte=month_ago
                ).aggregate(avg=Avg('load_time'))['avg'] or 0
            except Exception as e:
                logger.error(f"Error calculating avg_load_time_month: {e}")
                context['avg_load_time_month'] = 0
            
            # Page views with error handling
            try:
                context['page_views_today'] = PageView.objects.filter(
                    timestamp__date=today
                ).count()
            except Exception as e:
                logger.error(f"Error calculating page_views_today: {e}")
                context['page_views_today'] = 0
            
            try:
                context['page_views_week'] = PageView.objects.filter(
                    timestamp__gte=week_ago
                ).count()
            except Exception as e:
                logger.error(f"Error calculating page_views_week: {e}")
                context['page_views_week'] = 0
            
            try:
                context['page_views_month'] = PageView.objects.filter(
                    timestamp__gte=month_ago
                ).count()
            except Exception as e:
                logger.error(f"Error calculating page_views_month: {e}")
                context['page_views_month'] = 0
            
            # Error tracking with error handling
            try:
                context['errors_today'] = ErrorLog.objects.filter(
                    timestamp__date=today
                ).count()
            except Exception as e:
                logger.error(f"Error calculating errors_today: {e}")
                context['errors_today'] = 0
            
            try:
                context['errors_week'] = ErrorLog.objects.filter(
                    timestamp__gte=week_ago
                ).count()
            except Exception as e:
                logger.error(f"Error calculating errors_week: {e}")
                context['errors_week'] = 0
            
            try:
                context['unresolved_errors'] = ErrorLog.objects.filter(
                    resolved=False
                ).count()
            except Exception as e:
                logger.error(f"Error calculating unresolved_errors: {e}")
                context['unresolved_errors'] = 0
            
            # Top pages by load time (use cached data)
            try:
                context['slowest_pages'] = DashboardDataProvider.get_slowest_pages(7, use_cache=True)
            except Exception as e:
                logger.error(f"Error calculating slowest_pages: {e}")
                context['slowest_pages'] = []
            
            # Most visited pages (use cached data)
            try:
                context['most_visited'] = DashboardDataProvider.get_most_visited_pages(7, use_cache=True)
            except Exception as e:
                logger.error(f"Error calculating most_visited: {e}")
                context['most_visited'] = []
            
            # Error types
            try:
                context['error_types'] = ErrorLog.objects.filter(
                    timestamp__gte=week_ago
                ).values('error_type').annotate(
                    count=Count('id')
                ).order_by('-count')
            except Exception as e:
                logger.error(f"Error calculating error_types: {e}")
                context['error_types'] = []
            
            # Mobile vs Desktop (use cached data)
            try:
                context['mobile_stats'] = DashboardDataProvider.get_device_stats(7, use_cache=True)
            except Exception as e:
                logger.error(f"Error calculating mobile_stats: {e}")
                context['mobile_stats'] = []
            
            # Browser statistics (use cached data)
            try:
                context['browser_stats'] = DashboardDataProvider.get_browser_stats(7, use_cache=True)
            except Exception as e:
                logger.error(f"Error calculating browser_stats: {e}")
                context['browser_stats'] = []
            
            # Downloads Statistics
            try:
                context['total_downloads'] = DownloadableFile.objects.count()
                context['active_downloads'] = DownloadableFile.objects.filter(is_active=True).count()
                context['featured_downloads'] = DownloadableFile.objects.filter(is_featured=True).count()
                context['total_download_count'] = DownloadableFile.objects.aggregate(
                    total=Count('download_count')
                )['total'] or 0
                
                context['popular_files'] = DownloadableFile.objects.filter(
                    is_active=True
                ).order_by('-download_count')[:5]
                
                context['recent_downloads'] = DownloadableFile.objects.filter(
                    uploaded_at__gte=week_ago
                ).count()
            except Exception as e:
                logger.error(f"Error calculating download stats: {e}")
                context.update({
                    'total_downloads': 0,
                    'active_downloads': 0,
                    'featured_downloads': 0,
                    'total_download_count': 0,
                    'popular_files': [],
                    'recent_downloads': 0,
                })
            
            # Updates Statistics
            try:
                context['total_updates'] = NewsArticle.objects.count()
                context['published_updates'] = NewsArticle.objects.filter(status='PB').count()
                context['recent_updates'] = NewsArticle.objects.filter(
                    created_at__gte=week_ago
                ).count()
                
                context['latest_updates'] = NewsArticle.objects.filter(
                    status='PB'
                ).order_by('-created_at')[:5]
            except Exception as e:
                logger.error(f"Error calculating update stats: {e}")
                context.update({
                    'total_updates': 0,
                    'published_updates': 0,
                    'recent_updates': 0,
                    'latest_updates': [],
                })
            
            # Team Statistics
            try:
                context['total_team_members'] = Person.objects.count()
                context['active_team_members'] = Staff.objects.filter(is_active=True).count()
                context['recent_team_additions'] = Person.objects.filter(
                    id__in=Staff.objects.filter(
                        start_date__gte=month_ago.date()
                    ).values_list('person_id', flat=True)
                ).count()
                
                context['latest_team_members'] = Staff.objects.filter(
                    is_active=True
                ).select_related('person').order_by('-start_date')[:5]
            except Exception as e:
                logger.error(f"Error calculating team stats: {e}")
                context.update({
                    'total_team_members': 0,
                    'active_team_members': 0,
                    'recent_team_additions': 0,
                    'latest_team_members': [],
                })
            
            # Contact Statistics
            try:
                context['total_contacts'] = ContactSubmission.objects.count()
                context['recent_contacts'] = ContactSubmission.objects.filter(
                    created_at__gte=week_ago
                ).count()
                context['unread_contacts'] = ContactSubmission.objects.filter(
                    status='new'
                ).count()
                
                context['latest_contacts'] = ContactSubmission.objects.order_by('-created_at')[:5]
            except Exception as e:
                logger.error(f"Error calculating contact stats: {e}")
                context.update({
                    'total_contacts': 0,
                    'recent_contacts': 0,
                    'unread_contacts': 0,
                    'latest_contacts': [],
                })
            
            # Search Statistics (Note: Search app doesn't have a SearchLog model)
            context['total_searches'] = 0  # Placeholder since no search logging model exists
            context['recent_searches'] = 0  # Placeholder since no search logging model exists
            context['popular_searches'] = []  # Placeholder since no search logging model exists
            
        except Exception as e:
            logger.error(f"Critical error in dashboard view: {e}")
            # Set default values for all metrics
            context.update({
                'avg_load_time_today': 0,
                'avg_load_time_week': 0,
                'avg_load_time_month': 0,
                'page_views_today': 0,
                'page_views_week': 0,
                'page_views_month': 0,
                'errors_today': 0,
                'errors_week': 0,
                'unresolved_errors': 0,
                'slowest_pages': [],
                'most_visited': [],
                'error_types': [],
                'mobile_stats': [],
                'browser_stats': [],
                'total_downloads': 0,
                'active_downloads': 0,
                'featured_downloads': 0,
                'total_download_count': 0,
                'popular_files': [],
                'recent_downloads': 0,
                'total_updates': 0,
                'published_updates': 0,
                'recent_updates': 0,
                'latest_updates': [],
                'total_team_members': 0,
                'active_team_members': 0,
                'recent_team_additions': 0,
                'latest_team_members': [],
                'total_contacts': 0,
                'recent_contacts': 0,
                'unread_contacts': 0,
                'latest_contacts': [],
                'total_searches': 0,
                'recent_searches': 0,
                'popular_searches': [],
            })
        
        # Add breadcrumbs
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Dashboard', 'url': '/dashboard/'}
        ]
        
        return context

def dashboard_api(request):
    """Enhanced API endpoint for dashboard data with filtering capabilities"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        metric_type = request.GET.get('type', 'page_load')
        days = int(request.GET.get('days', 7))
        
        # Add filtering capabilities
        filters = {
            'date_range': request.GET.get('date_range', f'{days}d'),
            'device_type': request.GET.get('device_type'),
            'browser': request.GET.get('browser'),
            'page_type': request.GET.get('page_type'),
        }
        
        start_date = timezone.now() - timedelta(days=days)
        
        if metric_type == 'page_load':
            # Use cached data if no filters are applied
            if not filters['device_type'] and not filters['browser']:
                data = DashboardDataProvider.get_page_views_data(days, use_cache=True)
                return JsonResponse({
                    **data,
                    'filters_applied': filters,
                    'total_records': sum(data['counts'])
                })
            else:
                # Apply filters - no cache for filtered data
                queryset = PageView.objects.filter(timestamp__gte=start_date)
                
                if filters['device_type']:
                    queryset = queryset.filter(is_mobile=(filters['device_type'] == 'mobile'))
                if filters['browser']:
                    queryset = queryset.filter(browser=filters['browser'])
                
                data = queryset.values('timestamp__date').annotate(
                    avg_load_time=Avg('load_time'),
                    count=Count('id')
                ).order_by('timestamp__date')
                
                return JsonResponse({
                    'labels': [item['timestamp__date'].strftime('%Y-%m-%d') for item in data],
                    'data': [float(item['avg_load_time']) for item in data],
                    'counts': [item['count'] for item in data],
                    'filters_applied': filters,
                    'total_records': queryset.count()
                })
        
        elif metric_type == 'errors':
            # Use cached data if no filters are applied
            if not filters['page_type']:
                data = DashboardDataProvider.get_error_data(days, use_cache=True)
                return JsonResponse({
                    **data,
                    'filters_applied': filters,
                    'total_records': sum(data['data'])
                })
            else:
                # Apply filters - no cache for filtered data
                queryset = ErrorLog.objects.filter(timestamp__gte=start_date)
                
                if filters['page_type']:
                    queryset = queryset.filter(error_type=filters['page_type'])
                
                data = queryset.values('timestamp__date').annotate(
                    count=Count('id')
                ).order_by('timestamp__date')
                
                return JsonResponse({
                    'labels': [item['timestamp__date'].strftime('%Y-%m-%d') for item in data],
                    'data': [item['count'] for item in data],
                    'filters_applied': filters,
                    'total_records': queryset.count()
                })
        
        elif metric_type == 'traffic':
            queryset = PageView.objects.filter(timestamp__gte=start_date)
            
            # Apply filters
            if filters['device_type']:
                queryset = queryset.filter(is_mobile=(filters['device_type'] == 'mobile'))
            
            data = queryset.values('timestamp__date').annotate(
                count=Count('id'),
                unique_sessions=Count('session_id', distinct=True)
            ).order_by('timestamp__date')
            
            return JsonResponse({
                'labels': [item['timestamp__date'].strftime('%Y-%m-%d') for item in data],
                'data': [item['count'] for item in data],
                'unique_sessions': [item['unique_sessions'] for item in data],
                'filters_applied': filters,
                'total_records': queryset.count()
            })
        
        return JsonResponse({'error': 'Invalid metric type'}, status=400)
        
    except Exception as e:
        logger.error(f"Error in dashboard API: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
def track_page_view(request):
    """Track page view performance"""
    if request.method == 'POST':
        try:
            # Handle both JSON and FormData
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Handle FormData from sendBeacon
                data_str = request.POST.get('data', '{}')
                data = json.loads(data_str)
            
            PageView.objects.create(
                page_url=data.get('url', ''),
                page_title=data.get('title', ''),
                load_time=data.get('load_time', 0),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                session_id=request.session.session_key,
                user=request.user if request.user.is_authenticated else None,
                referrer=data.get('referrer', ''),
                is_mobile=data.get('is_mobile', False),
                browser=data.get('browser', ''),
                os=data.get('os', '')
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def track_error(request):
    """Track errors and exceptions"""
    if request.method == 'POST':
        try:
            # Handle both JSON and FormData
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Handle FormData from sendBeacon
                data_str = request.POST.get('data', '{}')
                data = json.loads(data_str)
            
            ErrorLog.objects.create(
                error_type=data.get('error_type', '500'),
                error_message=data.get('error_message', ''),
                page_url=data.get('page_url', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                session_id=request.session.session_key,
                user=request.user if request.user.is_authenticated else None,
                stack_trace=data.get('stack_trace', ''),
                additional_data=data.get('additional_data', {})
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def generate_dashboard_report(request):
    """Generate dashboard report"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_type = data.get('type', 'weekly')
            start_date = datetime.fromisoformat(data.get('start_date'))
            end_date = datetime.fromisoformat(data.get('end_date'))
            
            # Generate report data
            report_data = {
                'page_views': PageView.objects.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).count(),
                'avg_load_time': PageView.objects.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).aggregate(avg=Avg('load_time'))['avg'] or 0,
                'errors': ErrorLog.objects.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).count(),
                'unique_sessions': UserSession.objects.filter(
                    start_time__gte=start_date,
                    start_time__lte=end_date
                ).count(),
                'top_pages': list(PageView.objects.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).values('page_url', 'page_title').annotate(
                    count=Count('id'),
                    avg_load_time=Avg('load_time')
                ).order_by('-count')[:10]),
                'error_types': list(ErrorLog.objects.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).values('error_type').annotate(
                    count=Count('id')
                ).order_by('-count'))
            }
            
            # Create report
            report = PerformanceReport.objects.create(
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
                generated_by=request.user,
                report_data=report_data,
                summary=f"Performance report for {start_date.date()} to {end_date.date()}"
            )
            
            return JsonResponse({
                'success': True,
                'report_id': report.id,
                'data': report_data
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_alerts(request):
    """Get active alerts for dashboard"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        from .models import AlertLog
        alerts = AlertLog.objects.filter(is_resolved=False).order_by('-triggered_at')[:10]
        
        alert_data = []
        for alert in alerts:
            alert_data.append({
                'id': alert.id,
                'type': alert.alert.alert_type,
                'severity': alert.alert.severity,
                'message': alert.message,
                'current_value': alert.current_value,
                'threshold': alert.alert.threshold_value,
                'triggered_at': alert.triggered_at.isoformat(),
            })
        
        return JsonResponse({'alerts': alert_data})
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def resolve_alert(request, alert_id):
    """Resolve an alert"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        try:
            from .models import AlertLog
            from django.utils import timezone
            
            alert = AlertLog.objects.get(id=alert_id)
            alert.is_resolved = True
            alert.resolved_at = timezone.now()
            alert.resolved_by = request.user
            alert.save()
            
            return JsonResponse({'success': True})
        except AlertLog.DoesNotExist:
            return JsonResponse({'error': 'Alert not found'}, status=404)
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def export_dashboard_data(request):
    """Export dashboard data in various formats"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        format_type = request.GET.get('format', 'csv')
        data_type = request.GET.get('data_type', 'page_views')
        days = int(request.GET.get('days', 7))
        
        start_date = timezone.now() - timedelta(days=days)
        
        if data_type == 'page_views':
            queryset = PageView.objects.filter(timestamp__gte=start_date)
        elif data_type == 'errors':
            queryset = ErrorLog.objects.filter(timestamp__gte=start_date)
        else:
            return JsonResponse({'error': 'Invalid data type'}, status=400)
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{data_type}_{datetime.now().strftime("%Y%m%d")}.csv"'
            
            writer = csv.writer(response)
            
            if data_type == 'page_views':
                writer.writerow(['Timestamp', 'Page URL', 'Page Title', 'Load Time (ms)', 'Is Mobile', 'Browser', 'User'])
                for item in queryset:
                    writer.writerow([
                        item.timestamp,
                        item.page_url,
                        item.page_title,
                        item.load_time,
                        item.is_mobile,
                        item.browser,
                        item.user.username if item.user else 'Anonymous'
                    ])
            elif data_type == 'errors':
                writer.writerow(['Timestamp', 'Error Type', 'Error Message', 'Page URL', 'Resolved', 'User'])
                for item in queryset:
                    writer.writerow([
                        item.timestamp,
                        item.error_type,
                        item.error_message,
                        item.page_url,
                        item.resolved,
                        item.user.username if item.user else 'Anonymous'
                    ])
            
            return response
        
        return JsonResponse({'error': 'Unsupported format'}, status=400)
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def dashboard_widgets(request):
    """Get dashboard widgets configuration"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        from .models import DashboardWidget, UserDashboardPreference
        
        # Get user preferences
        user_prefs, created = UserDashboardPreference.objects.get_or_create(
            user=request.user,
            defaults={'theme': 'light', 'refresh_interval': 30}
        )
        
        # Get active widgets
        widgets = DashboardWidget.objects.filter(is_active=True).order_by('position_y', 'position_x')
        
        widget_data = []
        for widget in widgets:
            widget_data.append({
                'id': widget.id,
                'name': widget.name,
                'type': widget.widget_type,
                'position': {'x': widget.position_x, 'y': widget.position_y},
                'size': {'width': widget.width, 'height': widget.height},
                'config': widget.config,
            })
        
        return JsonResponse({
            'widgets': widget_data,
            'user_preferences': {
                'theme': user_prefs.theme,
                'refresh_interval': user_prefs.refresh_interval,
                'layout_config': user_prefs.layout_config,
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard widgets: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def update_user_preferences(request):
    """Update user dashboard preferences"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        try:
            from .models import UserDashboardPreference
            
            data = json.loads(request.body)
            
            user_prefs, created = UserDashboardPreference.objects.get_or_create(
                user=request.user,
                defaults={'theme': 'light', 'refresh_interval': 30}
            )
            
            if 'theme' in data:
                user_prefs.theme = data['theme']
            if 'refresh_interval' in data:
                user_prefs.refresh_interval = data['refresh_interval']
            if 'layout_config' in data:
                user_prefs.layout_config = data['layout_config']
            
            user_prefs.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# Specialized Dashboard Views

@method_decorator(staff_member_required, name='dispatch')
class PerformanceDashboardView(TemplateView):
    """Dedicated Performance Monitoring Dashboard"""
    template_name = 'dashboard/performance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            now = timezone.now()
            today = now.date()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # Performance Metrics
            context['performance_metrics'] = {
                'avg_load_time_today': PageView.objects.filter(
                    timestamp__date=today
                ).aggregate(avg=Avg('load_time'))['avg'] or 0,
                'avg_load_time_week': PageView.objects.filter(
                    timestamp__gte=week_ago
                ).aggregate(avg=Avg('load_time'))['avg'] or 0,
                'avg_load_time_month': PageView.objects.filter(
                    timestamp__gte=month_ago
                ).aggregate(avg=Avg('load_time'))['avg'] or 0,
            }
            
            # Database Performance
            context['db_performance'] = PerformanceMetric.objects.filter(
                metric_type='database_query',
                timestamp__gte=week_ago
            ).aggregate(
                avg_time=Avg('value'),
                max_time=Max('value'),
                min_time=Min('value')
            )
            
            # API Performance
            context['api_performance'] = PerformanceMetric.objects.filter(
                metric_type='api_response',
                timestamp__gte=week_ago
            ).aggregate(
                avg_time=Avg('value'),
                max_time=Max('value'),
                min_time=Min('value')
            )
            
            # Memory Usage
            context['memory_usage'] = PerformanceMetric.objects.filter(
                metric_type='memory_usage',
                timestamp__gte=week_ago
            ).aggregate(
                avg_usage=Avg('value'),
                max_usage=Max('value'),
                min_usage=Min('value')
            )
            
            # Slowest Pages
            context['slowest_pages'] = PageView.objects.filter(
                timestamp__gte=week_ago
            ).values('page_url', 'page_title').annotate(
                avg_load_time=Avg('load_time'),
                count=Count('id')
            ).order_by('-avg_load_time')[:10]
            
            # Performance Thresholds
            context['performance_thresholds'] = {
                'excellent_load_time': 1000,
                'good_load_time': 2000,
                'poor_load_time': 3000,
            }
            
        except Exception as e:
            logger.error(f"Error in performance dashboard: {e}")
            context.update({
                'performance_metrics': {'avg_load_time_today': 0, 'avg_load_time_week': 0, 'avg_load_time_month': 0},
                'db_performance': {'avg_time': 0, 'max_time': 0, 'min_time': 0},
                'api_performance': {'avg_time': 0, 'max_time': 0, 'min_time': 0},
                'memory_usage': {'avg_usage': 0, 'max_usage': 0, 'min_usage': 0},
                'slowest_pages': [],
                'performance_thresholds': {'excellent_load_time': 1000, 'good_load_time': 2000, 'poor_load_time': 3000}
            })
        
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Performance', 'url': '/dashboard/performance/'}
        ]
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class AnalyticsDashboardView(TemplateView):
    """Dedicated Analytics Dashboard"""
    template_name = 'dashboard/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            now = timezone.now()
            today = now.date()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # Page Views Analytics
            context['page_views'] = {
                'today': PageView.objects.filter(timestamp__date=today).count(),
                'week': PageView.objects.filter(timestamp__gte=week_ago).count(),
                'month': PageView.objects.filter(timestamp__gte=month_ago).count(),
            }
            
            # Most Visited Pages
            context['most_visited'] = PageView.objects.filter(
                timestamp__gte=week_ago
            ).values('page_url', 'page_title').annotate(
                count=Count('id'),
                avg_load_time=Avg('load_time')
            ).order_by('-count')[:10]
            
            # Device Statistics
            context['device_stats'] = PageView.objects.filter(
                timestamp__gte=week_ago
            ).values('is_mobile').annotate(
                count=Count('id')
            )
            
            # Browser Statistics
            context['browser_stats'] = PageView.objects.filter(
                timestamp__gte=week_ago
            ).values('browser').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            # User Sessions
            context['user_sessions'] = UserSession.objects.filter(
                start_time__gte=week_ago
            ).aggregate(
                total_sessions=Count('id'),
                avg_duration=Avg('duration'),
                unique_users=Count('user', distinct=True)
            )
            
            # Traffic Trends
            context['traffic_trends'] = PageView.objects.filter(
                timestamp__gte=week_ago
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
        except Exception as e:
            logger.error(f"Error in analytics dashboard: {e}")
            context.update({
                'page_views': {'today': 0, 'week': 0, 'month': 0},
                'most_visited': [],
                'device_stats': [],
                'browser_stats': [],
                'user_sessions': {'total_sessions': 0, 'avg_duration': 0, 'unique_users': 0},
                'traffic_trends': []
            })
        
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Analytics', 'url': '/dashboard/analytics/'}
        ]
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class ErrorDashboardView(TemplateView):
    """Dedicated Error Tracking Dashboard"""
    template_name = 'dashboard/errors.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            now = timezone.now()
            today = now.date()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # Error Statistics
            context['error_stats'] = {
                'today': ErrorLog.objects.filter(timestamp__date=today).count(),
                'week': ErrorLog.objects.filter(timestamp__gte=week_ago).count(),
                'month': ErrorLog.objects.filter(timestamp__gte=month_ago).count(),
                'unresolved': ErrorLog.objects.filter(resolved=False).count(),
            }
            
            # Error Types
            context['error_types'] = ErrorLog.objects.filter(
                timestamp__gte=week_ago
            ).values('error_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Recent Errors
            context['recent_errors'] = ErrorLog.objects.filter(
                timestamp__gte=week_ago
            ).order_by('-timestamp')[:20]
            
            # Error Trends
            context['error_trends'] = ErrorLog.objects.filter(
                timestamp__gte=week_ago
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
            # Most Error-Prone Pages
            context['error_prone_pages'] = ErrorLog.objects.filter(
                timestamp__gte=week_ago
            ).values('page_url').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
        except Exception as e:
            logger.error(f"Error in error dashboard: {e}")
            context.update({
                'error_stats': {'today': 0, 'week': 0, 'month': 0, 'unresolved': 0},
                'error_types': [],
                'recent_errors': [],
                'error_trends': [],
                'error_prone_pages': []
            })
        
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Error Tracking', 'url': '/dashboard/errors/'}
        ]
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class ReportsDashboardView(TemplateView):
    """Dedicated Reports Dashboard"""
    template_name = 'dashboard/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Recent Reports
            context['recent_reports'] = PerformanceReport.objects.all().order_by('-created_at')[:10]
            
            # Report Statistics
            context['report_stats'] = {
                'total_reports': PerformanceReport.objects.count(),
                'this_month': PerformanceReport.objects.filter(
                    created_at__gte=timezone.now().replace(day=1)
                ).count(),
                'this_week': PerformanceReport.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count(),
            }
            
        except Exception as e:
            logger.error(f"Error in reports dashboard: {e}")
            context.update({
                'recent_reports': [],
                'report_stats': {'total_reports': 0, 'this_month': 0, 'this_week': 0}
            })
        
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Reports', 'url': '/dashboard/reports/'}
        ]
        
        return context


# Specialized API Views

def performance_api(request):
    """API endpoint for performance data"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        days = int(request.GET.get('days', 7))
        metric = request.GET.get('metric', 'load_time')
        start_date = timezone.now() - timedelta(days=days)
        
        # Generate date labels for the past N days
        labels = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            labels.append(date)
        labels.reverse()
        
        if metric == 'load_time':
            # Load time data
            load_times = PageView.objects.filter(
                timestamp__gte=start_date
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                avg_load_time=Avg('load_time')
            ).order_by('day')
            
            # Create data array matching labels
            data = []
            load_times_dict = {item['day'].strftime('%Y-%m-%d'): item['avg_load_time'] for item in load_times}
            for label in labels:
                data.append(load_times_dict.get(label, 0) or 0)
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Load Time (ms)'
            })
            
        elif metric == 'db_performance':
            # Database performance data
            db_perf = PerformanceMetric.objects.filter(
                metric_type='database_query',
                timestamp__gte=start_date
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                avg_time=Avg('value')
            ).order_by('day')
            
            data = []
            db_perf_dict = {item['day'].strftime('%Y-%m-%d'): item['avg_time'] for item in db_perf}
            for label in labels:
                data.append(db_perf_dict.get(label, 0) or 0)
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'DB Query Time (ms)'
            })
            
        elif metric == 'api_performance':
            # API performance data
            api_perf = PerformanceMetric.objects.filter(
                metric_type='api_response',
                timestamp__gte=start_date
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                avg_time=Avg('value')
            ).order_by('day')
            
            data = []
            api_perf_dict = {item['day'].strftime('%Y-%m-%d'): item['avg_time'] for item in api_perf}
            for label in labels:
                data.append(api_perf_dict.get(label, 0) or 0)
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'API Response Time (ms)'
            })
            
        elif metric == 'memory_usage':
            # Memory usage data
            memory_data = PerformanceMetric.objects.filter(
                metric_type='memory_usage',
                timestamp__gte=start_date
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                avg_usage=Avg('value')
            ).order_by('day')
            
            data = []
            memory_dict = {item['day'].strftime('%Y-%m-%d'): item['avg_usage'] for item in memory_data}
            for label in labels:
                data.append(memory_dict.get(label, 0) or 0)
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Memory Usage (MB)'
            })
        
        else:
            # Default: return load time data
            load_times = PageView.objects.filter(
                timestamp__gte=start_date
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                avg_load_time=Avg('load_time')
            ).order_by('day')
            
            data = []
            load_times_dict = {item['day'].strftime('%Y-%m-%d'): item['avg_load_time'] for item in load_times}
            for label in labels:
                data.append(load_times_dict.get(label, 0) or 0)
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Load Time (ms)'
            })
        
    except Exception as e:
        logger.error(f"Error in performance API: {e}")
        # Return empty data on error
        labels = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            labels.append(date)
        labels.reverse()
        
        return JsonResponse({
            'labels': labels,
            'data': [0] * days,
            'metric': 'No Data Available'
        })


def analytics_api(request):
    """API endpoint for analytics data"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        days = int(request.GET.get('days', 7))
        metric = request.GET.get('metric', 'page_views')
        start_date = timezone.now() - timedelta(days=days)
        
        # Generate date labels for the past N days
        labels = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            labels.append(date)
        labels.reverse()
        
        if metric == 'page_views':
            # Page views data
            page_views = PageView.objects.filter(
                timestamp__gte=start_date
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
            data = []
            page_views_dict = {item['day'].strftime('%Y-%m-%d'): item['count'] for item in page_views}
            for label in labels:
                data.append(page_views_dict.get(label, 0) or 0)
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Page Views'
            })
            
        elif metric == 'device_stats':
            # Device statistics
            device_stats = PageView.objects.filter(
                timestamp__gte=start_date
            ).values('is_mobile').annotate(
                count=Count('id')
            )
            
            labels = ['Mobile', 'Desktop']
            data = [0, 0]
            for stat in device_stats:
                if stat['is_mobile']:
                    data[0] = stat['count']
                else:
                    data[1] = stat['count']
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Device Usage'
            })
            
        elif metric == 'browser_stats':
            # Browser statistics
            browser_stats = PageView.objects.filter(
                timestamp__gte=start_date
            ).values('browser').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            labels = [item['browser'] or 'Unknown' for item in browser_stats]
            data = [item['count'] for item in browser_stats]
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Browser Usage'
            })
        
        else:
            # Default: return page views data
            page_views = PageView.objects.filter(
                timestamp__gte=start_date
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
            data = []
            page_views_dict = {item['day'].strftime('%Y-%m-%d'): item['count'] for item in page_views}
            for label in labels:
                data.append(page_views_dict.get(label, 0) or 0)
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Page Views'
            })
        
    except Exception as e:
        logger.error(f"Error in analytics API: {e}")
        # Return empty data on error
        labels = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            labels.append(date)
        labels.reverse()
        
        return JsonResponse({
            'labels': labels,
            'data': [0] * days,
            'metric': 'No Data Available'
        })


def errors_api(request):
    """API endpoint for error data"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        days = int(request.GET.get('days', 7))
        metric = request.GET.get('metric', 'error_trends')
        start_date = timezone.now() - timedelta(days=days)
        
        # Generate date labels for the past N days
        labels = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            labels.append(date)
        labels.reverse()
        
        if metric == 'error_trends':
            # Error trends data
            error_trends = ErrorLog.objects.filter(
                timestamp__gte=start_date
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
            data = []
            error_trends_dict = {item['day'].strftime('%Y-%m-%d'): item['count'] for item in error_trends}
            for label in labels:
                data.append(error_trends_dict.get(label, 0) or 0)
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Error Count'
            })
            
        elif metric == 'error_types':
            # Error types data
            error_types = ErrorLog.objects.filter(
                timestamp__gte=start_date
            ).values('error_type').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            labels = [item['error_type'] for item in error_types]
            data = [item['count'] for item in error_types]
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Error Types'
            })
            
        elif metric == 'error_prone_pages':
            # Error prone pages data
            error_pages = ErrorLog.objects.filter(
                timestamp__gte=start_date
            ).values('page_url').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            labels = [item['page_url'][:30] + '...' if len(item['page_url']) > 30 else item['page_url'] for item in error_pages]
            data = [item['count'] for item in error_pages]
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Error Prone Pages'
            })
        
        else:
            # Default: return error trends data
            error_trends = ErrorLog.objects.filter(
                timestamp__gte=start_date
            ).extra(
                select={'day': 'date(timestamp)'}
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
            data = []
            error_trends_dict = {item['day'].strftime('%Y-%m-%d'): item['count'] for item in error_trends}
            for label in labels:
                data.append(error_trends_dict.get(label, 0) or 0)
            
            return JsonResponse({
                'labels': labels,
                'data': data,
                'metric': 'Error Count'
            })
        
    except Exception as e:
        logger.error(f"Error in errors API: {e}")
        # Return empty data on error
        labels = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            labels.append(date)
        labels.reverse()
        
        return JsonResponse({
            'labels': labels,
            'data': [0] * days,
            'metric': 'No Data Available'
        })