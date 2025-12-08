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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .serializers import (
    PageViewSerializer, ErrorLogSerializer, DashboardFilterSerializer,
    PerformanceAlertSerializer, AlertLogSerializer, DashboardWidgetSerializer,
    DashboardDataResponseSerializer, DashboardReportRequestSerializer,
    DashboardReportResponseSerializer, ExportDataRequestSerializer
)

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

class DashboardDataView(APIView):
    """Enhanced API endpoint for dashboard data with filtering capabilities"""
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        parameters=[DashboardFilterSerializer],
        responses=DashboardDataResponseSerializer
    )
    def get(self, request):
        serializer = DashboardFilterSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        metric_type = data.get('type', 'page_load')
        days = data.get('days', 7)
        device_type = data.get('device_type')
        browser = data.get('browser')
        page_type = data.get('page_type')
        
        start_date = timezone.now() - timedelta(days=days)
        filters = {k: v for k, v in data.items() if v}
        
        try:
            if metric_type == 'page_load':
                queryset = PageView.objects.filter(timestamp__gte=start_date)
                
                if device_type:
                    queryset = queryset.filter(is_mobile=(device_type == 'mobile'))
                if browser:
                    queryset = queryset.filter(browser=browser)
                
                # If no specific filters, try cache (logic simplified for DRF for now)
                # In a real DRF implementation, we might skip the custom caching logic 
                # or wrap it in a service layer. For now, let's keep it direct for clarity.
                
                data_points = queryset.values('timestamp__date').annotate(
                    avg_load_time=Avg('load_time'),
                    count=Count('id')
                ).order_by('timestamp__date')
                
                return Response({
                    'labels': [item['timestamp__date'].strftime('%Y-%m-%d') for item in data_points],
                    'data': [float(item['avg_load_time']) for item in data_points],
                    'counts': [item['count'] for item in data_points],
                    'filters_applied': filters,
                    'total_records': queryset.count()
                })
        
            elif metric_type == 'errors':
                queryset = ErrorLog.objects.filter(timestamp__gte=start_date)
                
                if page_type:
                    queryset = queryset.filter(error_type=page_type)
                
                data_points = queryset.values('timestamp__date').annotate(
                    count=Count('id')
                ).order_by('timestamp__date')
                
                return Response({
                    'labels': [item['timestamp__date'].strftime('%Y-%m-%d') for item in data_points],
                    'data': [item['count'] for item in data_points],
                    'filters_applied': filters,
                    'total_records': queryset.count()
                })
        
            elif metric_type == 'traffic':
                queryset = PageView.objects.filter(timestamp__gte=start_date)
                
                if device_type:
                    queryset = queryset.filter(is_mobile=(device_type == 'mobile'))
                
                data_points = queryset.values('timestamp__date').annotate(
                    count=Count('id'),
                    unique_sessions=Count('session_id', distinct=True)
                ).order_by('timestamp__date')
                
                return Response({
                    'labels': [item['timestamp__date'].strftime('%Y-%m-%d') for item in data_points],
                    'data': [item['count'] for item in data_points],
                    'unique_sessions': [item['unique_sessions'] for item in data_points],
                    'filters_applied': filters,
                    'total_records': queryset.count()
                })
            
            return Response({'error': 'Invalid metric type'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error in dashboard API: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TrackPageView(APIView):
    """Track page view performance"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=PageViewSerializer,
        responses={200: dict}
    )
    def post(self, request):
        # Handle sendBeacon data which might be text/plain or form data
        data = request.data
        if not data and request.body:
             try:
                 data = json.loads(request.body)
             except:
                 pass
                 
        # If came from formData/beacon as string
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], str):
             try:
                 data = json.loads(data['data'])
             except:
                 pass
        
        # Add request info
        data_to_save = data.copy()
        data_to_save['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        data_to_save['ip_address'] = request.META.get('REMOTE_ADDR', '')
        data_to_save['session_id'] = request.session.session_key
        if request.user.is_authenticated:
            # We can't assign user object directly to serializer field if it expects PK, 
            # but ModelSerializer can handle user from context if we set it in perform_create, 
            # or we just pass it to save if not in validated_data.
            # Simpler: just set it manually after validation or allow it in serializer?
            # ModelSerializer read_only_fields are excluded from validation.
            pass

        serializer = PageViewSerializer(data=data_to_save)
        if serializer.is_valid():
             # Save with read-only fields
             serializer.save(
                 user=request.user if request.user.is_authenticated else None,
                 ip_address=request.META.get('REMOTE_ADDR', ''),
                 user_agent=request.META.get('HTTP_USER_AGENT', ''),
                 session_id=request.session.session_key
             )
             return Response({'success': True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrackErrorView(APIView):
    """Track errors and exceptions"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ErrorLogSerializer,
        responses={200: dict}
    )
    def post(self, request):
        data = request.data
        # Handle different data formats similar to PageView
        if not data and request.body:
             try:
                 data = json.loads(request.body)
             except:
                 pass
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], str):
             try:
                 data = json.loads(data['data'])
             except:
                 pass

        serializer = ErrorLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save(
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_id=request.session.session_key
            )
            return Response({'success': True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardReportView(APIView):
    """Generate dashboard report"""
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=DashboardReportRequestSerializer,
        responses=DashboardReportResponseSerializer
    )
    def post(self, request):
        try:
            data = request.data
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
            
            return Response({
                'success': True,
                'report_id': report.id,
                'data': report_data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AlertsView(APIView):
    """Get active alerts for dashboard"""
    permission_classes = [IsAdminUser]
    
    @extend_schema(responses=AlertLogSerializer(many=True))
    def get(self, request):
        try:
            from .models import AlertLog
            alerts = AlertLog.objects.filter(is_resolved=False).order_by('-triggered_at')[:10]
            serializer = AlertLogSerializer(alerts, many=True)
            return Response({'alerts': serializer.data})
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResolveAlertView(APIView):
    """Resolve an alert"""
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=None,
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request, alert_id):
        try:
            from .models import AlertLog
            alert = AlertLog.objects.get(id=alert_id)
            alert.is_resolved = True
            alert.resolved_at = timezone.now()
            alert.resolved_by = request.user
            alert.save()
            return Response({'success': True})
        except AlertLog.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExportDashboardDataView(APIView):
    """Export dashboard data in various formats"""
    permission_classes = [IsAdminUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='format', description='Export format (csv, json)', required=False, type=str),
            OpenApiParameter(name='data_type', description='Type of data to export', required=False, type=str),
            OpenApiParameter(name='days', description='Number of days to export', required=False, type=int),
        ],
        responses={200: OpenApiTypes.BINARY}
    )
    def get(self, request):
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
                return Response({'error': 'Invalid data type'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            
            return Response({'error': 'Unsupported format'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardWidgetsView(APIView):
    """Get dashboard widgets configuration"""
    permission_classes = [IsAdminUser]
    
    @extend_schema(responses=DashboardWidgetSerializer(many=True))
    def get(self, request):
        try:
            from .models import DashboardWidget, UserDashboardPreference
            # Get user preferences
            pref, created = UserDashboardPreference.objects.get_or_create(user=request.user)
            user_widgets = pref.widgets.all()
            
            # If user has no widgets configured, return defaults
            if not user_widgets.exists():
                default_widgets = DashboardWidget.objects.filter(is_active=True, created_by=None)
                if default_widgets.exists():
                     # Don't automatically add to user prefs, just return defaults to show
                    widgets = default_widgets
                else:
                    widgets = []
            else:
                widgets = user_widgets
                
            serializer = DashboardWidgetSerializer(widgets, many=True)
            return Response({'widgets': serializer.data})
        except Exception as e:
            logger.error(f"Error getting widgets: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserPreferenceView(APIView):
    """Update user dashboard preferences"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        try:
            from .models import UserDashboardPreference
            data = request.data
            
            pref, created = UserDashboardPreference.objects.get_or_create(user=request.user)
            
            if 'theme' in data:
                pref.theme = data['theme']
            
            if 'refresh_interval' in data:
                pref.refresh_interval = int(data['refresh_interval'])
                
            if 'layout_config' in data:
                pref.layout_config = data['layout_config']
                
            pref.save()
            return Response({'success': True})
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

class PerformanceDataView(APIView):
    """API endpoint for performance data"""
    permission_classes = [IsAdminUser]
    
    @extend_schema(parameters=[DashboardFilterSerializer], responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        try:
            days = int(request.GET.get('days', 7))
            metric = request.GET.get('metric', 'load_time')
            start_date = timezone.now() - timedelta(days=days)
            
            # Generate date labels
            labels = [(timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
            labels.reverse()
            
            data = []
            metric_label = 'Load Time (ms)'
            
            if metric == 'load_time':
                queryset = PageView.objects.filter(timestamp__gte=start_date).extra(select={'day': 'date(timestamp)'}).values('day').annotate(val=Avg('load_time')).order_by('day')
            elif metric == 'db_performance':
                 queryset = PerformanceMetric.objects.filter(metric_type='database_query', timestamp__gte=start_date).extra(select={'day': 'date(timestamp)'}).values('day').annotate(val=Avg('value')).order_by('day')
                 metric_label = 'DB Query Time (ms)'
            elif metric == 'api_performance':
                 queryset = PerformanceMetric.objects.filter(metric_type='api_response', timestamp__gte=start_date).extra(select={'day': 'date(timestamp)'}).values('day').annotate(val=Avg('value')).order_by('day')
                 metric_label = 'API Response Time (ms)'
            elif metric == 'memory_usage':
                 queryset = PerformanceMetric.objects.filter(metric_type='memory_usage', timestamp__gte=start_date).extra(select={'day': 'date(timestamp)'}).values('day').annotate(val=Avg('value')).order_by('day')
                 metric_label = 'Memory Usage (MB)'
            else:
                 queryset = PageView.objects.filter(timestamp__gte=start_date).extra(select={'day': 'date(timestamp)'}).values('day').annotate(val=Avg('load_time')).order_by('day')
            
            data_dict = {item['day'].strftime('%Y-%m-%d'): item['val'] for item in queryset}
            data = [data_dict.get(label, 0) or 0 for label in labels]
            
            return Response({
                'labels': labels,
                'data': data,
                'metric': metric_label
            })
            
        except Exception as e:
            logger.error(f"Error in performance API: {e}")
            labels = [(timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
            labels.reverse()
            return Response({'labels': labels, 'data': [0]*days, 'metric': 'No Data Available'})


class AnalyticsDataView(APIView):
    """API endpoint for analytics data"""
    permission_classes = [IsAdminUser]
    
    @extend_schema(parameters=[DashboardFilterSerializer], responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        try:
            days = int(request.GET.get('days', 7))
            metric = request.GET.get('metric', 'page_views')
            start_date = timezone.now() - timedelta(days=days)
            
            labels = [(timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
            labels.reverse()
            data = []
            metric_label = 'Page Views'

            if metric == 'page_views':
                 queryset = PageView.objects.filter(timestamp__gte=start_date).extra(select={'day': 'date(timestamp)'}).values('day').annotate(val=Count('id')).order_by('day')
                 data_dict = {item['day'].strftime('%Y-%m-%d'): item['val'] for item in queryset}
                 data = [data_dict.get(label, 0) or 0 for label in labels]

            elif metric == 'device_stats':
                 device_stats = PageView.objects.filter(timestamp__gte=start_date).values('is_mobile').annotate(count=Count('id'))
                 labels = ['Mobile', 'Desktop']
                 data = [0, 0]
                 for stat in device_stats:
                     if stat['is_mobile']: data[0] = stat['count']
                     else: data[1] = stat['count']
                 metric_label = 'Device Usage'

            elif metric == 'browser_stats':
                 browser_stats = PageView.objects.filter(timestamp__gte=start_date).values('browser').annotate(count=Count('id')).order_by('-count')[:5]
                 labels = [item['browser'] or 'Unknown' for item in browser_stats]
                 data = [item['count'] for item in browser_stats]
                 metric_label = 'Browser Usage'
            else:
                 queryset = PageView.objects.filter(timestamp__gte=start_date).extra(select={'day': 'date(timestamp)'}).values('day').annotate(val=Count('id')).order_by('day')
                 data_dict = {item['day'].strftime('%Y-%m-%d'): item['val'] for item in queryset}
                 data = [data_dict.get(label, 0) or 0 for label in labels]

            return Response({
                'labels': labels,
                'data': data,
                'metric': metric_label
            })
        except Exception as e:
            logger.error(f"Error in analytics API: {e}")
            labels = [(timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
            labels.reverse()
            return Response({'labels': labels, 'data': [0]*days, 'metric': 'No Data Available'})


class ErrorsDataView(APIView):
    """API endpoint for error data"""
    permission_classes = [IsAdminUser]
    
    @extend_schema(parameters=[DashboardFilterSerializer], responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        try:
            days = int(request.GET.get('days', 7))
            metric = request.GET.get('metric', 'error_trends')
            start_date = timezone.now() - timedelta(days=days)
            
            labels = [(timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
            labels.reverse()
            data = []
            metric_label = 'Error Count'

            if metric == 'error_trends':
                 queryset = ErrorLog.objects.filter(timestamp__gte=start_date).extra(select={'day': 'date(timestamp)'}).values('day').annotate(val=Count('id')).order_by('day')
                 data_dict = {item['day'].strftime('%Y-%m-%d'): item['val'] for item in queryset}
                 data = [data_dict.get(label, 0) or 0 for label in labels]

            elif metric == 'error_types':
                 error_types = ErrorLog.objects.filter(timestamp__gte=start_date).values('error_type').annotate(count=Count('id')).order_by('-count')[:5]
                 labels = [item['error_type'] for item in error_types]
                 data = [item['count'] for item in error_types]
                 metric_label = 'Error Types'
            
            elif metric == 'error_prone_pages':
                 error_pages = ErrorLog.objects.filter(timestamp__gte=start_date).values('page_url').annotate(count=Count('id')).order_by('-count')[:5]
                 labels = [item['page_url'][:30] + '...' if len(item['page_url']) > 30 else item['page_url'] for item in error_pages]
                 data = [item['count'] for item in error_pages]
                 metric_label = 'Error Prone Pages'
            
            else:
                 queryset = ErrorLog.objects.filter(timestamp__gte=start_date).extra(select={'day': 'date(timestamp)'}).values('day').annotate(val=Count('id')).order_by('day')
                 data_dict = {item['day'].strftime('%Y-%m-%d'): item['val'] for item in queryset}
                 data = [data_dict.get(label, 0) or 0 for label in labels]

            return Response({
                'labels': labels,
                'data': data,
                'metric': metric_label
            })
        except Exception as e:
            logger.error(f"Error in errors API: {e}")
            labels = [(timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
            labels.reverse()
            return Response({'labels': labels, 'data': [0]*days, 'metric': 'No Data Available'})