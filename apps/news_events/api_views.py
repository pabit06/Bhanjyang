# news_events/api_views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Count, Avg, Q, F, Sum
from django.db.models.functions import TruncHour
from django.core.exceptions import PermissionDenied
from datetime import timedelta
import logging

from .models import NewsArticle, Event, ContentAnalytics
from apps.dashboard.models import UserSession, PageView

logger = logging.getLogger(__name__)


def check_analytics_permission(request):
    """
    Additional security check for analytics data access.
    Verifies user is staff and has proper permissions.
    """
    if not request.user.is_authenticated:
        raise PermissionDenied("Authentication required")
    
    if not request.user.is_staff:
        raise PermissionDenied("Staff access required")
    
    # Additional check: verify user has analytics permission
    # This can be extended to check specific permissions
    if not request.user.is_superuser:
        # Check if user has specific permission (if using Django permissions)
        if not request.user.has_perm('news_events.view_analytics'):
            logger.warning(f"Unauthorized analytics access attempt by {request.user.username}")
            raise PermissionDenied("Insufficient permissions for analytics access")
    
    return True


@staff_member_required
@require_http_methods(["GET"])
def get_real_time_metrics(request):
    """
    Get real-time analytics metrics.
    
    Currently uses base logic with UserSession and PageView models.
    Future enhancements:
    - Integrate django-user-visit package for more accurate active user tracking
    - Connect to Google Analytics API for comprehensive analytics
    - Add WebSocket support for true real-time updates
    """
    try:
        # Additional security check
        check_analytics_permission(request)
        
        # Rate limiting check (prevent abuse)
        # This is a simple check - can be enhanced with django-ratelimit
        if hasattr(request, 'session'):
            analytics_access_count = request.session.get('analytics_access_count', 0)
            if analytics_access_count > 100:  # Max 100 requests per session
                logger.warning(f"Rate limit exceeded for analytics access by {request.user.username}")
                return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            request.session['analytics_access_count'] = analytics_access_count + 1
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        two_hours_ago = now - timedelta(hours=2)
        
        # Active Users: Sessions active in the last hour
        # Base logic: Count unique sessions that have activity in the last hour
        active_sessions = UserSession.objects.filter(
            Q(start_time__gte=one_hour_ago) | 
            Q(end_time__gte=one_hour_ago) |
            Q(end_time__isnull=True, start_time__gte=one_hour_ago)
        ).distinct('session_id').count()
        
        # Previous hour for comparison
        previous_active_sessions = UserSession.objects.filter(
            start_time__gte=two_hours_ago,
            start_time__lt=one_hour_ago
        ).distinct('session_id').count()
        
        # Calculate percentage change
        if previous_active_sessions > 0:
            active_users_change = round(
                ((active_sessions - previous_active_sessions) / previous_active_sessions) * 100, 1
            )
        else:
            active_users_change = 100.0 if active_sessions > 0 else 0.0
        
        # Page Views: Total page views in the last hour
        current_page_views = PageView.objects.filter(
            timestamp__gte=one_hour_ago
        ).count()
        
        previous_page_views = PageView.objects.filter(
            timestamp__gte=two_hours_ago,
            timestamp__lt=one_hour_ago
        ).count()
        
        if previous_page_views > 0:
            page_views_change = round(
                ((current_page_views - previous_page_views) / previous_page_views) * 100, 1
            )
        else:
            page_views_change = 100.0 if current_page_views > 0 else 0.0
        
        # Bounce Rate: Single-page sessions / Total sessions
        # A bounce is a session with only 1 page view
        total_sessions = UserSession.objects.filter(start_time__gte=one_hour_ago).count()
        bounced_sessions = UserSession.objects.filter(
            start_time__gte=one_hour_ago,
            page_views=1
        ).count()
        
        bounce_rate = round((bounced_sessions / total_sessions * 100), 1) if total_sessions > 0 else 0.0
        
        # Previous hour bounce rate
        prev_total_sessions = UserSession.objects.filter(
            start_time__gte=two_hours_ago,
            start_time__lt=one_hour_ago
        ).count()
        prev_bounced_sessions = UserSession.objects.filter(
            start_time__gte=two_hours_ago,
            start_time__lt=one_hour_ago,
            page_views=1
        ).count()
        
        prev_bounce_rate = round((prev_bounced_sessions / prev_total_sessions * 100), 1) if prev_total_sessions > 0 else 0.0
        bounce_rate_change = round(bounce_rate - prev_bounce_rate, 1)
        
        # Average Session Duration: Average time spent per session
        sessions_with_duration = UserSession.objects.filter(
            start_time__gte=one_hour_ago,
            end_time__isnull=False
        ).annotate(
            duration=F('end_time') - F('start_time')
        )
        
        if sessions_with_duration.exists():
            # Calculate average duration in minutes
            avg_duration_seconds = sessions_with_duration.aggregate(
                avg_duration=Avg('total_load_time')
            )['avg_duration'] or 0
            
            # Use page_views and total_load_time to estimate session duration
            # If we have end_time, calculate actual duration
            avg_duration_minutes = 0
            durations = []
            for session in sessions_with_duration[:100]:  # Limit for performance
                if session.end_time:
                    duration = (session.end_time - session.start_time).total_seconds() / 60
                    durations.append(duration)
            
            if durations:
                avg_duration_minutes = round(sum(durations) / len(durations), 1)
            else:
                # Fallback: estimate from page views and load time
                avg_duration_minutes = round(avg_duration_seconds / 60, 1) if avg_duration_seconds > 0 else 0
        else:
            avg_duration_minutes = 0
        
        # Previous hour average session duration
        prev_sessions_with_duration = UserSession.objects.filter(
            start_time__gte=two_hours_ago,
            start_time__lt=one_hour_ago,
            end_time__isnull=False
        )
        
        prev_avg_duration_minutes = 0
        if prev_sessions_with_duration.exists():
            prev_durations = []
            for session in prev_sessions_with_duration[:100]:
                if session.end_time:
                    duration = (session.end_time - session.start_time).total_seconds() / 60
                    prev_durations.append(duration)
            
            if prev_durations:
                prev_avg_duration_minutes = round(sum(prev_durations) / len(prev_durations), 1)
        
        if prev_avg_duration_minutes > 0:
            avg_session_change = round(
                ((avg_duration_minutes - prev_avg_duration_minutes) / prev_avg_duration_minutes) * 100, 1
            )
        else:
            avg_session_change = 100.0 if avg_duration_minutes > 0 else 0.0
        
        return JsonResponse({
            'active_users': active_sessions,
            'active_users_change': active_users_change,
            'page_views': current_page_views,
            'page_views_change': page_views_change,
            'bounce_rate': bounce_rate,
            'bounce_rate_change': bounce_rate_change,
            'avg_session_duration': avg_duration_minutes,
            'avg_session_change': avg_session_change,
            'timestamp': now.isoformat(),
        })
        
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to fetch real-time metrics',
            'active_users': 0,
            'active_users_change': 0,
            'page_views': 0,
            'page_views_change': 0,
            'bounce_rate': 0,
            'bounce_rate_change': 0,
            'avg_session_duration': 0,
            'avg_session_change': 0,
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def get_traffic_sources(request):
    """Get traffic sources data for chart"""
    try:
        check_analytics_permission(request)
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Get page views with referrer data
        page_views = PageView.objects.filter(
            timestamp__gte=thirty_days_ago
        ).exclude(referrer__isnull=True).exclude(referrer='')
        
        # Categorize traffic sources
        organic = 0
        social = 0
        direct = 0
        referral = 0
        other = 0
        
        for pv in page_views[:1000]:  # Limit for performance
            if not pv.referrer:
                direct += 1
                continue
            referrer = pv.referrer.lower()
            if 'direct' in referrer:
                direct += 1
            elif any(domain in referrer for domain in ['google', 'bing', 'yahoo', 'duckduckgo']):
                organic += 1
            elif any(domain in referrer for domain in ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']):
                social += 1
            else:
                referral += 1
        
        # Count direct traffic (no referrer) - already counted in loop, but add any remaining
        direct_count = PageView.objects.filter(
            timestamp__gte=thirty_days_ago
        ).filter(
            Q(referrer__isnull=True) | Q(referrer='')
        ).count()
        direct += direct_count
        
        total = organic + social + direct + referral + other
        
        return JsonResponse({
            'labels': ['Organic Search', 'Social Media', 'Direct', 'Referral', 'Other'],
            'data': [organic, social, direct, referral, other],
            'total': total,
        })
        
    except Exception as e:
        logger.error(f"Error getting traffic sources: {e}", exc_info=True)
        return JsonResponse({
            'labels': [],
            'data': [],
            'total': 0,
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def get_content_performance(request):
    """Get content performance data for chart"""
    try:
        check_analytics_permission(request)
        # Get top articles by views
        top_articles = NewsArticle.objects.filter(
            status=NewsArticle.Status.PUBLISHED
        ).order_by('-view_count')[:10]
        
        labels = [article.title[:30] + '...' if len(article.title) > 30 else article.title 
                  for article in top_articles]
        views = [article.view_count for article in top_articles]
        shares = [article.share_count for article in top_articles]
        
        return JsonResponse({
            'labels': labels,
            'views': views,
            'shares': shares,
        })
        
    except Exception as e:
        logger.error(f"Error getting content performance: {e}", exc_info=True)
        return JsonResponse({
            'labels': [],
            'views': [],
            'shares': [],
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def get_user_demographics(request):
    """Get user demographics data for chart"""
    try:
        check_analytics_permission(request)
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Get device breakdown
        mobile_sessions = UserSession.objects.filter(
            start_time__gte=thirty_days_ago,
            is_mobile=True
        ).count()
        
        desktop_sessions = UserSession.objects.filter(
            start_time__gte=thirty_days_ago,
            is_mobile=False
        ).count()
        
        # Get browser breakdown
        browser_stats = UserSession.objects.filter(
            start_time__gte=thirty_days_ago
        ).exclude(browser='').values('browser').annotate(
            count=Count('id')
        ).order_by('-count')[:4]
        
        browsers = [stat['browser'] for stat in browser_stats]
        browser_counts = [stat['count'] for stat in browser_stats]
        
        return JsonResponse({
            'labels': browsers if browsers else ['Mobile', 'Desktop'],
            'data': browser_counts if browser_counts else [mobile_sessions, desktop_sessions],
        })
        
    except Exception as e:
        logger.error(f"Error getting user demographics: {e}", exc_info=True)
        return JsonResponse({
            'labels': [],
            'data': [],
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def get_device_usage(request):
    """Get device usage data for chart"""
    try:
        check_analytics_permission(request)
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        mobile = UserSession.objects.filter(
            start_time__gte=thirty_days_ago,
            is_mobile=True
        ).count()
        
        desktop = UserSession.objects.filter(
            start_time__gte=thirty_days_ago,
            is_mobile=False
        ).count()
        
        tablet = UserSession.objects.filter(
            start_time__gte=thirty_days_ago
        ).exclude(browser='').filter(
            Q(browser__icontains='ipad') | Q(user_agent__icontains='tablet')
        ).count()
        
        return JsonResponse({
            'labels': ['Mobile', 'Desktop', 'Tablet'],
            'data': [mobile, desktop, tablet],
        })
        
    except Exception as e:
        logger.error(f"Error getting device usage: {e}", exc_info=True)
        return JsonResponse({
            'labels': [],
            'data': [],
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def get_top_articles(request):
    """Get top articles for dashboard"""
    try:
        check_analytics_permission(request)
        top_articles = NewsArticle.objects.filter(
            status=NewsArticle.Status.PUBLISHED
        ).select_related('category').order_by('-view_count')[:10]
        
        articles_data = [{
            'id': article.id,
            'title': article.title,
            'category': article.category.name if article.category else 'Uncategorized',
            'views': article.view_count,
            'url': article.get_absolute_url(),
        } for article in top_articles]
        
        return JsonResponse(articles_data, safe=False)
        
    except Exception as e:
        logger.error(f"Error getting top articles: {e}", exc_info=True)
        return JsonResponse([], safe=False, status=500)


@staff_member_required
@require_http_methods(["GET"])
def get_top_events(request):
    """Get top events for dashboard"""
    try:
        check_analytics_permission(request)
        top_events = Event.objects.filter(
            status=Event.Status.PUBLISHED
        ).order_by('-view_count')[:10]
        
        events_data = [{
            'id': event.id,
            'title': event.title,
            'category': event.get_event_type_display(),
            'views': event.view_count,
            'url': event.get_absolute_url(),
        } for event in top_events]
        
        return JsonResponse(events_data, safe=False)
        
    except Exception as e:
        logger.error(f"Error getting top events: {e}", exc_info=True)
        return JsonResponse([], safe=False, status=500)

