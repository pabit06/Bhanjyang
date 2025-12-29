from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils.translation import activate
from datetime import datetime
import json
import logging

from apps.core.view_mixins import NepaliLanguageMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .serializers import (
    PageViewSerializer, ErrorLogSerializer, DashboardFilterSerializer,
    AlertLogSerializer, DashboardWidgetSerializer,
    DashboardDataResponseSerializer, DashboardReportRequestSerializer,
    DashboardReportResponseSerializer
)
from .services import (
    DashboardAnalyticsService, DashboardReportingService,
    DashboardMonitoringService, DashboardWidgetService
)

logger = logging.getLogger(__name__)

@method_decorator(staff_member_required, name='dispatch')
class DashboardView(NepaliLanguageMixin, TemplateView):
    """Main website dashboard with comprehensive analytics"""
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # 1. Dashboard Core Analytics
            summary = DashboardAnalyticsService.get_dashboard_summary()
            
            # Map service response to template keys (Legacy compatibility)
            context['avg_load_time_today'] = summary['performance']['today']
            context['avg_load_time_week'] = summary['performance']['week']
            context['avg_load_time_month'] = summary['performance']['month']
            context['performance_thresholds'] = summary['performance']['thresholds']
            
            context['page_views_today'] = summary['views']['today']
            context['page_views_week'] = summary['views']['week']
            context['page_views_month'] = summary['views']['month']
            
            context['errors_today'] = summary['errors']['today']
            context['errors_week'] = summary['errors']['week']
            context['unresolved_errors'] = summary['errors']['unresolved']
            
            context['slowest_pages'] = summary['pages']['slowest']
            context['most_visited'] = summary['pages']['popular']
            
            context['browser_stats'] = summary['tech']['browsers']
            context['mobile_stats'] = [] 
            
            # 2. Domain Stats
            domain_stats = DashboardAnalyticsService.get_domain_stats()
            
            # Downloads
            downloads = domain_stats.get('downloads', {})
            context['total_downloads'] = downloads.get('total', 0)
            context['active_downloads'] = downloads.get('active', 0)
            context['total_download_count'] = downloads.get('total_downloads', 0)
            
            # Updates
            updates = domain_stats.get('updates', {})
            context['total_updates'] = updates.get('total', 0)
            context['published_updates'] = updates.get('published', 0)
            context['recent_updates'] = updates.get('recent', 0)
            
            # Team
            team = domain_stats.get('team', {})
            context['total_team_members'] = team.get('total', 0)
            context['active_team_members'] = team.get('active_staff', 0)
            
            # Contact
            contacts = domain_stats.get('contacts', {})
            context['total_contacts'] = contacts.get('total', 0)
            context['unread_contacts'] = contacts.get('new', 0)
            
        except Exception as e:
            logger.error(f"Critical error in dashboard view: {e}", exc_info=True)
            
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Dashboard', 'url': '/dashboard/'}
        ]
        return context


class DashboardDataView(APIView):
    """Enhanced API endpoint for dashboard data with filtering capabilities"""
    permission_classes = [IsAdminUser]
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
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
        filters = {k: v for k, v in data.items() if v and k not in ['type', 'days']}
        
        try:
            result = DashboardAnalyticsService.get_chart_data(metric_type, days, filters)
            result['filters_applied'] = filters
            return Response(result)
        except Exception as e:
            logger.error(f"Error in dashboard API: {e}", exc_info=True)
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrackPageView(APIView):
    """Track page view performance"""
    permission_classes = [AllowAny]
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    @extend_schema(request=PageViewSerializer, responses={200: dict})
    def post(self, request):
        try:
            raw_data = request.data
            if not raw_data and request.body:
                try: raw_data = json.loads(request.body)
                except: pass
            
            if isinstance(raw_data, dict) and 'data' in raw_data and isinstance(raw_data['data'], str):
                 try: raw_data = json.loads(raw_data['data'])
                 except: pass
            
            if not isinstance(raw_data, dict): raw_data = {}
            
            if 'url' in raw_data: raw_data['page_url'] = raw_data.pop('url')
            if 'title' in raw_data: raw_data['page_title'] = raw_data.pop('title')
            
            raw_data['page_url'] = raw_data.get('page_url') or request.META.get('HTTP_REFERER') or ''
            raw_data['session_id'] = request.session.session_key
            
            request_meta = {
                'HTTP_USER_AGENT': request.META.get('HTTP_USER_AGENT', ''),
                'REMOTE_ADDR': request.META.get('REMOTE_ADDR', ''),
                'session_id': request.session.session_key,
                'user': request.user
            }
            
            if DashboardAnalyticsService.record_page_view(raw_data, request_meta):
                return Response({'success': True})
            return Response({'success': False, 'error': 'Failed to record'}, status=400)
            
        except Exception as e:
            logger.error(f'Error tracking view: {e}', exc_info=True)
            return Response({'success': False}, status=500)


class TrackErrorView(APIView):
    """Track errors and exceptions"""
    permission_classes = [AllowAny]
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    @extend_schema(request=ErrorLogSerializer, responses={200: dict})
    def post(self, request):
        try:
            raw_data = request.data
            request_meta = {
                'HTTP_USER_AGENT': request.META.get('HTTP_USER_AGENT', ''),
                'REMOTE_ADDR': request.META.get('REMOTE_ADDR', ''),
                'session_id': request.session.session_key,
                'user': request.user
            }
            
            if DashboardAnalyticsService.record_error(raw_data, request_meta):
                return Response({'success': True})
            return Response({'success': False}, status=400)
        except Exception as e:
            logger.error(f'Error tracking error: {e}', exc_info=True)
            return Response({'success': False}, status=500)


class DashboardReportView(APIView):
    """Generate dashboard report"""
    permission_classes = [IsAdminUser]
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)

    @extend_schema(
        request=DashboardReportRequestSerializer,
        responses=DashboardReportResponseSerializer
    )
    def post(self, request):
        try:
            data = request.data
            report_type = data.get('type', 'weekly')
            start = datetime.fromisoformat(data.get('start_date'))
            end = datetime.fromisoformat(data.get('end_date'))
            
            report = DashboardReportingService.generate_report(request.user, report_type, start, end)
            
            return Response({
                'success': True,
                'report_id': report.id,
                'data': report.report_data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ExportDashboardDataView(APIView):
    """Export dashboard data"""
    permission_classes = [IsAdminUser]
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter('format', str, required=False),
            OpenApiParameter('data_type', str, required=False),
            OpenApiParameter('days', int, required=False),
        ]
    )
    def get(self, request):
        try:
            data_type = request.GET.get('data_type', 'page_views')
            days = int(request.GET.get('days', 7))
            
            csv_content = DashboardReportingService.export_data_csv(data_type, days)
            
            response = HttpResponse(csv_content, content_type='text/csv')
            filename = f"{data_type}_{datetime.now().strftime('%Y%m%d')}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}", exc_info=True)
            return Response({'error': 'Internal server error'}, status=500)


class AlertsView(APIView):
    """Get active alerts"""
    permission_classes = [IsAdminUser]
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    @extend_schema(responses=AlertLogSerializer(many=True))
    def get(self, request):
        alerts = DashboardMonitoringService.get_active_alerts()
        serializer = AlertLogSerializer(alerts, many=True)
        return Response({'alerts': serializer.data})


class ResolveAlertView(APIView):
    """Resolve an alert"""
    permission_classes = [IsAdminUser]
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, alert_id):
        if DashboardMonitoringService.resolve_alert(alert_id, request.user):
            return Response({'success': True})
        return Response({'error': 'Alert not found'}, status=404)


class DashboardWidgetsView(APIView):
    """Get dashboard widgets configuration"""
    permission_classes = [IsAdminUser]
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    @extend_schema(responses=DashboardWidgetSerializer(many=True))
    def get(self, request):
        config = DashboardWidgetService.get_user_config(request.user)
        return Response({'widgets': config['widgets']})


class UserPreferenceView(APIView):
    """Update user dashboard preferences"""
    permission_classes = [IsAdminUser]
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        if DashboardWidgetService.update_preferences(request.user, request.data):
             return Response({'success': True})
        return Response({'error': 'Failed'}, status=500)


@method_decorator(staff_member_required, name='dispatch')
class PerformanceDashboardView(NepaliLanguageMixin, TemplateView):
    """Dedicated Performance Monitoring Dashboard"""
    template_name = 'dashboard/performance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = DashboardAnalyticsService.get_dashboard_summary()
        context['performance_metrics'] = {
            'avg_load_time_today': summary['performance']['today'],
            'avg_load_time_week': summary['performance']['week'],
            'avg_load_time_month': summary['performance']['month'],
        }
        context['slowest_pages'] = summary['pages']['slowest']
        return context

# Wrappers for legacy URLs
@method_decorator(staff_member_required, name='dispatch')
class AnalyticsDashboardView(NepaliLanguageMixin, TemplateView):
    template_name = 'dashboard/analytics.html'

@method_decorator(staff_member_required, name='dispatch')
class ErrorDashboardView(NepaliLanguageMixin, TemplateView):
    template_name = 'dashboard/errors.html'

@method_decorator(staff_member_required, name='dispatch')
class ReportsDashboardView(NepaliLanguageMixin, TemplateView):
    template_name = 'dashboard/reports.html'

class PerformanceDataView(DashboardDataView):
    """Performance data view - inherits dispatch from DashboardDataView"""
    def get(self, request):
        request.GET = request.GET.copy()
        request.GET['type'] = 'page_load'
        return super().get(request)

class AnalyticsDataView(DashboardDataView):
    """Analytics data view - inherits dispatch from DashboardDataView"""
    def get(self, request):
        request.GET = request.GET.copy()
        request.GET['type'] = 'traffic'
        return super().get(request)

class ErrorsDataView(DashboardDataView):
    """Errors data view - inherits dispatch from DashboardDataView"""
    def get(self, request):
        request.GET = request.GET.copy()
        request.GET['type'] = 'errors'
        return super().get(request)