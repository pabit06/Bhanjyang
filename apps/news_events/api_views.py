"""
REST API Views for News Events App.

Provides comprehensive REST API endpoints using Django REST Framework ViewSets.
"""
import logging
from typing import Dict, Any, Optional
from django.db.models import Q, QuerySet, Count, Sum, Avg
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.cache import cache

from .models import (
    NewsArticle, Event, Category, Comment, Subscriber, Newsletter, ContentAnalytics
)
from .serializers import (
    NewsArticleSerializer, NewsArticleListSerializer,
    EventSerializer, EventListSerializer,
    CategorySerializer, CommentSerializer,
    SubscriberSerializer, NewsletterSerializer,
    ContentAnalyticsSerializer
)
from .services import NewsService, EventService
from .utils import NewsEventsValidator, NewsEventsHelper
from .throttling import (
    NewsEventsAnonRateThrottle, NewsEventsUserRateThrottle,
    NewsEventsSearchThrottle, NewsEventsWriteThrottle, NewsEventsBurstThrottle
)
from .constants import (
    DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, DEFAULT_RECENT_LIMIT,
    ANALYTICS_DEFAULT_DAYS, ANALYTICS_LAST_24_HOURS, ANALYTICS_LAST_7_DAYS,
    PERCENTAGE_DECIMAL_PLACES
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination configuration for API responses.
    
    Provides consistent pagination across all API endpoints with:
    - Default page size: 20 items
    - Configurable page size via query parameter
    - Maximum page size limit: 100 items
    """
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for news categories.
    
    Provides read-only access to categories with:
    - List and detail views
    - Search by name and description
    - Ordering by sort_order or name
    - Active categories filtering
    
    Endpoints:
    - GET /api/v1/news-events/categories/ - List all active categories
    - GET /api/v1/news-events/categories/{id}/ - Get specific category
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'name']
    permission_classes = [permissions.AllowAny]
    throttle_classes = [NewsEventsAnonRateThrottle, NewsEventsUserRateThrottle, NewsEventsBurstThrottle]
    
    @action(detail=True, methods=['get'])
    def articles(self, request: Request, pk: Optional[str] = None) -> Response:
        """
        Get all published articles in this category.
        
        GET /api/v1/news-events/categories/{id}/articles/
        """
        category = self.get_object()
        articles = NewsArticle.objects.filter(
            category=category,
            status=NewsArticle.Status.PUBLISHED
        ).select_related('author', 'category').order_by('-published_date', '-created_at')
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(articles, request)
        if page is not None:
            serializer = NewsArticleListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = NewsArticleListSerializer(articles, many=True)
        return Response(serializer.data)


class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for news articles.
    
    Provides read-only access to news articles with:
    - List and detail views
    - Filtering by category, status, priority, featured
    - Search by title, content, excerpt
    - Ordering by published_at, created_at, view_count
    - Featured articles endpoint
    - Recent articles endpoint
    - By-category endpoint
    
    Endpoints:
    - GET /api/v1/news-events/articles/ - List all published articles
    - GET /api/v1/news-events/articles/{id}/ - Get specific article
    - GET /api/v1/news-events/articles/featured/ - Get featured articles
    - GET /api/v1/news-events/articles/recent/ - Get recent articles
    - GET /api/v1/news-events/articles/by_category/?category_id=X - Get articles by category
    """
    serializer_class = NewsArticleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status', 'priority', 'is_featured']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_date', 'created_at', 'view_count', 'share_count']
    ordering = ['-published_date', '-created_at']
    permission_classes = [permissions.AllowAny]
    throttle_classes = [NewsEventsAnonRateThrottle, NewsEventsUserRateThrottle, NewsEventsBurstThrottle]
    
    def get_queryset(self) -> QuerySet:
        """Get queryset of published articles."""
        queryset = NewsArticle.objects.filter(
            status=NewsArticle.Status.PUBLISHED
        ).select_related('author', 'category').prefetch_related('comments')
        
        # Allow staff to see all statuses if status filter is provided
        if self.request.user.is_staff:
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = NewsArticle.objects.all().select_related('author', 'category').prefetch_related('comments')
        
        return queryset
    
    def get_serializer_class(self):
        """Use list serializer for list view."""
        if self.action == 'list':
            return NewsArticleListSerializer
        return NewsArticleSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request: Request) -> Response:
        """
        Get featured articles.
        
        GET /api/v1/news-events/articles/featured/
        """
        articles = self.get_queryset().filter(is_featured=True)[:DEFAULT_RECENT_LIMIT]
        serializer = NewsArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request: Request) -> Response:
        """
        Get recent articles (last 10).
        
        GET /api/v1/news-events/articles/recent/
        """
        articles = self.get_queryset()[:DEFAULT_RECENT_LIMIT]
        serializer = NewsArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request: Request) -> Response:
        """
        Get articles by category.
        
        GET /api/v1/news-events/articles/by_category/?category_id=X
        """
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {
                    'error': 'category_id parameter is required',
                    'detail': 'Please provide a category_id query parameter.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate category_id is numeric
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return Response(
                {
                    'error': 'Invalid category_id',
                    'detail': 'category_id must be a valid integer.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            category = Category.objects.get(pk=category_id, is_active=True)
        except Category.DoesNotExist:
            return Response(
                {
                    'error': 'Category not found',
                    'detail': f'Category with id {category_id} does not exist or is inactive.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        articles = self.get_queryset().filter(category=category)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(articles, request)
        if page is not None:
            serializer = NewsArticleListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = NewsArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request: Request, pk: Optional[str] = None) -> Response:
        """
        Increment article view count.
        
        POST /api/v1/news-events/articles/{id}/increment_view/
        """
        try:
            article = self.get_object()
            article.increment_view_count()
            article.last_accessed = timezone.now()
            article.save(update_fields=['view_count', 'last_accessed'])
            return Response({
                'view_count': article.view_count,
                'message': 'View count incremented successfully'
            })
        except Exception as e:
            logger.error(f"Error incrementing view count for article {pk}: {e}", exc_info=True)
            return Response(
                {
                    'error': 'Failed to increment view count',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for events.
    
    Provides read-only access to events with:
    - List and detail views
    - Filtering by event_type, status, featured
    - Search by title, description
    - Ordering by event_date, created_at, view_count
    - Upcoming events endpoint
    - Past events endpoint
    - Featured events endpoint
    
    Endpoints:
    - GET /api/v1/news-events/events/ - List all published events
    - GET /api/v1/news-events/events/{id}/ - Get specific event
    - GET /api/v1/news-events/events/upcoming/ - Get upcoming events
    - GET /api/v1/news-events/events/past/ - Get past events
    - GET /api/v1/news-events/events/featured/ - Get featured events
    """
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'status', 'is_featured', 'is_recurring']
    search_fields = ['title', 'description', 'short_description']
    ordering_fields = ['event_date', 'created_at', 'view_count', 'registration_count']
    ordering = ['event_date']
    permission_classes = [permissions.AllowAny]
    throttle_classes = [NewsEventsAnonRateThrottle, NewsEventsUserRateThrottle, NewsEventsBurstThrottle]
    
    def get_queryset(self) -> QuerySet:
        """Get queryset of published events."""
        queryset = Event.objects.filter(
            status=Event.Status.PUBLISHED
        )
        
        # Allow staff to see all statuses
        if self.request.user.is_staff:
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = Event.objects.all()
        
        return queryset
    
    def get_serializer_class(self):
        """Use list serializer for list view."""
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request: Request) -> Response:
        """
        Get upcoming events.
        
        GET /api/v1/news-events/events/upcoming/
        """
        now = timezone.now()
        events = self.get_queryset().filter(event_date__gte=now).order_by('event_date')[:10]
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def past(self, request: Request) -> Response:
        """
        Get past events.
        
        GET /api/v1/news-events/events/past/
        """
        now = timezone.now()
        events = self.get_queryset().filter(event_date__lt=now).order_by('-event_date')[:DEFAULT_RECENT_LIMIT]
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request: Request) -> Response:
        """
        Get featured events.
        
        GET /api/v1/news-events/events/featured/
        """
        events = self.get_queryset().filter(is_featured=True).order_by('event_date')[:DEFAULT_RECENT_LIMIT]
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request: Request, pk: Optional[str] = None) -> Response:
        """
        Increment event view count.
        
        POST /api/v1/news-events/events/{id}/increment_view/
        """
        event = self.get_object()
        event.view_count += 1
        event.last_accessed = timezone.now()
        event.save(update_fields=['view_count', 'last_accessed'])
        return Response({'view_count': event.view_count})


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for comments.
    
    Provides full CRUD access to comments with:
    - List, create, retrieve, update, delete
    - Filtering by article, is_approved
    - Search by content, author_name
    - Ordering by created_at
    
    Endpoints:
    - GET /api/v1/news-events/comments/ - List all comments
    - POST /api/v1/news-events/comments/ - Create new comment
    - GET /api/v1/news-events/comments/{id}/ - Get specific comment
    - PUT/PATCH /api/v1/news-events/comments/{id}/ - Update comment
    - DELETE /api/v1/news-events/comments/{id}/ - Delete comment
    """
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['article', 'is_approved']
    search_fields = ['content', 'author_name', 'author_email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    permission_classes = [permissions.AllowAny]  # Allow anyone to view, but creation might need auth
    throttle_classes = [NewsEventsAnonRateThrottle, NewsEventsUserRateThrottle, NewsEventsWriteThrottle, NewsEventsBurstThrottle]
    
    def get_queryset(self) -> QuerySet:
        """Get queryset of approved comments (or all for staff)."""
        queryset = Comment.objects.all().select_related('article')
        
        # Only show approved comments to non-staff users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set article when creating comment and validate spam."""
        from .security import SpamProtectionManager
        
        # Check for spam
        content = serializer.validated_data.get('content', '')
        author_email = serializer.validated_data.get('author_email', '')
        
        if SpamProtectionManager.check_spam_indicators(content, author_email):
            logger.warning(f"Spam detected in comment from {author_email}")
            # Still save but mark as not approved
            comment = serializer.save(is_approved=False)
            return comment
        
        serializer.save()


class SubscriberViewSet(viewsets.ModelViewSet):
    """
    API endpoint for newsletter subscribers.
    
    Provides full CRUD access to subscribers.
    Staff-only for security.
    
    Endpoints:
    - GET /api/v1/news-events/subscribers/ - List all subscribers (staff only)
    - POST /api/v1/news-events/subscribers/ - Create new subscriber
    - GET /api/v1/news-events/subscribers/{id}/ - Get specific subscriber
    """
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'is_confirmed']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['subscribed_at', 'last_activity']
    ordering = ['-subscribed_at']
    permission_classes = [permissions.IsAuthenticated]  # Require authentication
    throttle_classes = [NewsEventsAnonRateThrottle, NewsEventsUserRateThrottle, NewsEventsWriteThrottle, NewsEventsBurstThrottle]
    
    def get_permissions(self):
        """Allow public subscription creation, but require staff for other operations."""
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class NewsletterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for newsletters.
    
    Provides read-only access to newsletters.
    Staff-only for security.
    
    Endpoints:
    - GET /api/v1/news-events/newsletters/ - List all newsletters (staff only)
    - GET /api/v1/news-events/newsletters/{id}/ - Get specific newsletter
    """
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'subject', 'content']
    ordering_fields = ['created_at', 'sent_date']
    ordering = ['-created_at']
    permission_classes = [permissions.IsAdminUser]
    throttle_classes = [NewsEventsUserRateThrottle, NewsEventsBurstThrottle]


class ContentAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for content analytics.
    
    Provides read-only access to content analytics.
    Staff-only for security.
    
    Endpoints:
    - GET /api/v1/news-events/analytics/ - List all analytics (staff only)
    - GET /api/v1/news-events/analytics/{id}/ - Get specific analytics
    """
    queryset = ContentAnalytics.objects.all()
    serializer_class = ContentAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['content_type']
    ordering_fields = ['views', 'shares', 'last_accessed']
    ordering = ['-views']
    permission_classes = [permissions.IsAdminUser]
    throttle_classes = [NewsEventsUserRateThrottle, NewsEventsBurstThrottle]


# Analytics API endpoints (function-based views for dashboard)
# SECURITY: All analytics endpoints require staff/admin access
# These endpoints expose sensitive traffic and user data
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])  # Requires user.is_staff == True
def get_real_time_metrics(request: Request) -> Response:
    """
    Get real-time metrics for the analytics dashboard.
    
    Returns current metrics including:
    - Total views, shares, comments
    - Active users (last 24 hours)
    - Recent activity
    """
    from datetime import timedelta
    
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    # Get article metrics
    article_stats = NewsArticle.objects.filter(
        status=NewsArticle.Status.PUBLISHED
    ).aggregate(
        total_views=Sum('view_count'),
        total_shares=Sum('share_count'),
        total_comments=Sum('comment_count'),
        recent_views=Sum('view_count', filter=Q(last_accessed__gte=last_24h)),
    )
    
    # Get event metrics
    event_stats = Event.objects.filter(
        status=Event.Status.PUBLISHED
    ).aggregate(
        total_views=Sum('view_count'),
        total_registrations=Sum('registration_count'),
        recent_views=Sum('view_count', filter=Q(last_accessed__gte=last_24h)),
    )
    
    # Get recent analytics data
    recent_analytics = ContentAnalytics.objects.filter(
        date__gte=(now - timedelta(days=7)).date()
    ).aggregate(
        total_views=Sum('views'),
        total_unique_views=Sum('unique_views'),
        total_shares=Sum('shares'),
        total_comments=Sum('comments'),
    )
    
    return Response({
        'articles': {
            'total_views': article_stats['total_views'] or 0,
            'total_shares': article_stats['total_shares'] or 0,
            'total_comments': article_stats['total_comments'] or 0,
            'views_last_24h': article_stats['recent_views'] or 0,
        },
        'events': {
            'total_views': event_stats['total_views'] or 0,
            'total_registrations': event_stats['total_registrations'] or 0,
            'views_last_24h': event_stats['recent_views'] or 0,
        },
        'analytics_7d': {
            'total_views': recent_analytics['total_views'] or 0,
            'total_unique_views': recent_analytics['total_unique_views'] or 0,
            'total_shares': recent_analytics['total_shares'] or 0,
            'total_comments': recent_analytics['total_comments'] or 0,
        },
        'timestamp': now.isoformat(),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])  # Staff-only: Traffic data is sensitive
def get_traffic_sources(request: Request) -> Response:
    """
    Get traffic source breakdown.
    
    Returns traffic sources from ContentAnalytics:
    - Organic search
    - Social media
    - Direct traffic
    - Referral traffic
    """
    from datetime import timedelta
    
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    traffic = ContentAnalytics.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).aggregate(
        organic=Sum('organic_search'),
        social=Sum('social_media'),
        direct=Sum('direct_traffic'),
        referral=Sum('referral_traffic'),
    )
    
    total = sum([
        traffic['organic'] or 0,
        traffic['social'] or 0,
        traffic['direct'] or 0,
        traffic['referral'] or 0,
    ])
    
    return Response({
        'sources': {
            'organic_search': traffic['organic'] or 0,
            'social_media': traffic['social'] or 0,
            'direct_traffic': traffic['direct'] or 0,
            'referral_traffic': traffic['referral'] or 0,
        },
        'total': total,
        'percentages': {
            'organic_search': round((traffic['organic'] or 0) / total * 100, 2) if total > 0 else 0,
            'social_media': round((traffic['social'] or 0) / total * 100, 2) if total > 0 else 0,
            'direct_traffic': round((traffic['direct'] or 0) / total * 100, 2) if total > 0 else 0,
            'referral_traffic': round((traffic['referral'] or 0) / total * 100, 2) if total > 0 else 0,
        },
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days,
        },
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])  # Staff-only: Content performance data
def get_content_performance(request: Request) -> Response:
    """
    Get content performance metrics.
    
    Returns aggregated performance data for articles and events.
    """
    from datetime import timedelta
    
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Article performance
    article_perf = NewsArticle.objects.filter(
        status=NewsArticle.Status.PUBLISHED,
        published_date__gte=timezone.now() - timedelta(days=days)
    ).aggregate(
        total_articles=Count('id'),
        total_views=Sum('view_count'),
        total_shares=Sum('share_count'),
        total_comments=Sum('comment_count'),
        avg_views=Avg('view_count'),
        avg_shares=Avg('share_count'),
        avg_read_time=Avg('read_time'),
    )
    
    # Event performance
    event_perf = Event.objects.filter(
        status=Event.Status.PUBLISHED,
        created_at__gte=timezone.now() - timedelta(days=days)
    ).aggregate(
        total_events=Count('id'),
        total_views=Sum('view_count'),
        total_registrations=Sum('registration_count'),
        avg_views=Avg('view_count'),
        avg_registrations=Avg('registration_count'),
    )
    
    # Analytics data
    analytics_perf = ContentAnalytics.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).aggregate(
        avg_time_on_page=Avg('time_on_page'),
        total_views=Sum('views'),
        total_unique_views=Sum('unique_views'),
    )
    
    return Response({
        'articles': {
            'total': article_perf['total_articles'] or 0,
            'total_views': article_perf['total_views'] or 0,
            'total_shares': article_perf['total_shares'] or 0,
            'total_comments': article_perf['total_comments'] or 0,
            'avg_views': round(article_perf['avg_views'] or 0, 2),
            'avg_shares': round(article_perf['avg_shares'] or 0, 2),
            'avg_read_time': round(article_perf['avg_read_time'] or 0, 2),
        },
        'events': {
            'total': event_perf['total_events'] or 0,
            'total_views': event_perf['total_views'] or 0,
            'total_registrations': event_perf['total_registrations'] or 0,
            'avg_views': round(event_perf['avg_views'] or 0, 2),
            'avg_registrations': round(event_perf['avg_registrations'] or 0, 2),
        },
        'analytics': {
            'avg_time_on_page': round(analytics_perf['avg_time_on_page'] or 0, 2),
            'total_views': analytics_perf['total_views'] or 0,
            'total_unique_views': analytics_perf['total_unique_views'] or 0,
        },
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days,
        },
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])  # Staff-only: User demographics are sensitive
def get_user_demographics(request: Request) -> Response:
    """
    Get user demographics data.
    
    Note: This is a placeholder implementation. 
    For full demographics, you would need to track user data separately.
    """
    # Basic subscriber demographics
    subscriber_stats = Subscriber.objects.aggregate(
        total_subscribers=Count('id'),
        confirmed_subscribers=Count('id', filter=Q(is_confirmed=True)),
        active_subscribers=Count('id', filter=Q(status=Subscriber.Status.ACTIVE)),
    )
    
    # Comment author demographics (if available)
    comment_stats = Comment.objects.aggregate(
        total_comments=Count('id'),
        approved_comments=Count('id', filter=Q(is_approved=True)),
        unique_authors=Count('author_email', distinct=True),
    )
    
    return Response({
        'subscribers': {
            'total': subscriber_stats['total_subscribers'] or 0,
            'confirmed': subscriber_stats['confirmed_subscribers'] or 0,
            'active': subscriber_stats['active_subscribers'] or 0,
        },
        'engagement': {
            'total_comments': comment_stats['total_comments'] or 0,
            'approved_comments': comment_stats['approved_comments'] or 0,
            'unique_commenters': comment_stats['unique_authors'] or 0,
        },
        'note': 'Full demographics require additional user tracking implementation',
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])  # Staff-only: Device usage data
def get_device_usage(request: Request) -> Response:
    """
    Get device usage statistics.
    
    Note: This is a placeholder implementation.
    For full device tracking, you would need to track user agents separately.
    """
    # Placeholder - would need device tracking in ContentAnalytics or separate model
    return Response({
        'devices': {
            'desktop': 0,
            'mobile': 0,
            'tablet': 0,
        },
        'browsers': {},
        'note': 'Device usage tracking requires additional implementation. Consider adding device fields to ContentAnalytics model.',
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])  # Staff-only: Top content analytics
def get_top_articles(request: Request) -> Response:
    """
    Get top performing articles.
    
    Returns top articles by views, shares, or comments.
    """
    limit = int(request.query_params.get('limit', 10))
    sort_by = request.query_params.get('sort_by', 'view_count')  # view_count, share_count, comment_count
    
    valid_sort_fields = ['view_count', 'share_count', 'comment_count', 'published_date']
    if sort_by not in valid_sort_fields:
        sort_by = 'view_count'
    
    articles = NewsArticle.objects.filter(
        status=NewsArticle.Status.PUBLISHED
    ).order_by(f'-{sort_by}')[:limit]
    
    serializer = NewsArticleListSerializer(articles, many=True)
    return Response({
        'articles': serializer.data,
        'sort_by': sort_by,
        'limit': limit,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])  # Staff-only: Top events analytics
def get_top_events(request: Request) -> Response:
    """
    Get top performing events.
    
    Returns top events by views or registrations.
    """
    limit = int(request.query_params.get('limit', 10))
    sort_by = request.query_params.get('sort_by', 'view_count')  # view_count, registration_count
    
    valid_sort_fields = ['view_count', 'registration_count', 'event_date', 'created_at']
    if sort_by not in valid_sort_fields:
        sort_by = 'view_count'
    
    events = Event.objects.filter(
        status=Event.Status.PUBLISHED
    ).order_by(f'-{sort_by}')[:limit]
    
    serializer = EventListSerializer(events, many=True)
    return Response({
        'events': serializer.data,
        'sort_by': sort_by,
        'limit': limit,
    })


# New ViewSets for News Events App - Advanced Features.
# These ViewSets provide advanced search, notifications, and social media integration.


class AdvancedSearchViewSet(viewsets.ViewSet):
    """
    API endpoint for advanced full-text search.
    
    Provides advanced search capabilities with PostgreSQL full-text search.
    
    Endpoints:
    - POST /api/v1/news-events/search/advanced/ - Perform advanced search
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [NewsEventsSearchThrottle, NewsEventsBurstThrottle]
    
    @action(detail=False, methods=['post'])
    def advanced(self, request: Request) -> Response:
        """
        Perform advanced full-text search.
        
        POST /api/v1/news-events/search/advanced/
        
        Body:
        {
            "query": "search term",
            "content_type": "all|articles|events",
            "filters": {
                "category_id": 1,
                "featured_only": false,
                "event_type": "MEET"
            },
            "limit": DEFAULT_PAGE_SIZE
        }
        """
        from .advanced_search import AdvancedSearchService
        
        query = request.data.get('query', '').strip()
        if not query:
            return Response(
                {'error': 'Query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content_type = request.data.get('content_type', 'all')
        filters = request.data.get('filters', {})
        limit = int(request.data.get('limit', 20))
        
        try:
            results = AdvancedSearchService.advanced_search(
                query=query,
                content_type=content_type,
                filters=filters,
                limit=limit
            )
            
            # Serialize results
            from .serializers import NewsArticleListSerializer, EventListSerializer
            
            serialized_results = {
                'query': results['query'],
                'search_type': results['search_type'],
                'total_results': results['total_results'],
                'articles': NewsArticleListSerializer(results['articles'], many=True).data,
                'events': EventListSerializer(results['events'], many=True).data
            }
            
            return Response(serialized_results)
            
        except Exception as e:
            logger.error(f"Advanced search error: {e}", exc_info=True)
            return Response(
                {'error': 'Search failed', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NotificationViewSet(viewsets.ViewSet):
    """
    API endpoint for notifications.
    
    Provides access to user notifications.
    
    Endpoints:
    - GET /api/v1/news-events/notifications/ - Get user notifications
    - GET /api/v1/news-events/notifications/unread-count/ - Get unread count
    - POST /api/v1/news-events/notifications/{id}/mark-read/ - Mark as read
    - POST /api/v1/news-events/notifications/mark-all-read/ - Mark all as read
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [NewsEventsUserRateThrottle, NewsEventsBurstThrottle]
    
    def list(self, request: Request) -> Response:
        """Get user notifications."""
        from .notifications import NotificationService
        
        limit = int(request.query_params.get('limit', 20))
        notifications = NotificationService.get_user_notifications(request.user, limit)
        
        return Response({
            'count': len(notifications),
            'notifications': notifications
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request: Request) -> Response:
        """Get unread notification count."""
        from .notifications import NotificationService
        
        count = NotificationService.get_unread_count(request.user)
        return Response({'unread_count': count})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request: Request, pk: str = None) -> Response:
        """Mark notification as read."""
        from .notifications import NotificationService
        
        success = NotificationService.mark_as_read(request.user, pk)
        if success:
            return Response({'message': 'Notification marked as read'})
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request: Request) -> Response:
        """Mark all notifications as read."""
        from .notifications import NotificationService
        
        NotificationService.mark_all_as_read(request.user)
        return Response({'message': 'All notifications marked as read'})


class SocialMediaViewSet(viewsets.ViewSet):
    """
    API endpoint for social media sharing.
    
    Provides social media share URLs and tracking.
    
    Endpoints:
    - GET /api/v1/news-events/social/article/{id}/share-urls/ - Get article share URLs
    - GET /api/v1/news-events/social/event/{id}/share-urls/ - Get event share URLs
    - POST /api/v1/news-events/social/track-share/ - Track social share
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [NewsEventsAnonRateThrottle, NewsEventsUserRateThrottle, NewsEventsWriteThrottle, NewsEventsBurstThrottle]
    
    @action(detail=False, methods=['get'], url_path='article/(?P<article_id>[^/.]+)/share-urls')
    def article_share_urls(self, request: Request, article_id: int = None) -> Response:
        """Get social media share URLs for an article."""
        from .social_media import SocialMediaService
        
        try:
            article = NewsArticle.objects.get(pk=article_id, status=NewsArticle.Status.PUBLISHED)
            share_urls = SocialMediaService.get_article_share_urls(article)
            og_meta = SocialMediaService.get_open_graph_meta(article=article)
            
            return Response({
                'share_urls': share_urls,
                'open_graph': og_meta
            })
        except NewsArticle.DoesNotExist:
            return Response(
                {'error': 'Article not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='event/(?P<event_id>[^/.]+)/share-urls')
    def event_share_urls(self, request: Request, event_id: int = None) -> Response:
        """Get social media share URLs for an event."""
        from .social_media import SocialMediaService
        
        try:
            event = Event.objects.get(pk=event_id, status=Event.Status.PUBLISHED)
            share_urls = SocialMediaService.get_event_share_urls(event)
            og_meta = SocialMediaService.get_open_graph_meta(event=event)
            
            return Response({
                'share_urls': share_urls,
                'open_graph': og_meta
            })
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def track_share(self, request: Request) -> Response:
        """Track social media share."""
        from .social_media import SocialMediaService
        
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')
        platform = request.data.get('platform')
        
        if not all([content_type, content_id, platform]):
            return Response(
                {'error': 'content_type, content_id, and platform are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = SocialMediaService.track_social_share(
            content_type=content_type,
            content_id=content_id,
            platform=platform,
            request=request
        )
        
        if success:
            return Response({'message': 'Share tracked successfully'})
        return Response(
            {'error': 'Failed to track share'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

