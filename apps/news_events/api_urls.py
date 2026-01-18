"""
API URL configuration for the News Events app.

Provides REST API endpoints using Django REST Framework with versioning support.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .versioning import NewsEventsAPIVersioning

from .api_views import (
    CategoryViewSet, NewsArticleViewSet, EventViewSet,
    CommentViewSet, SubscriberViewSet, NewsletterViewSet,
    ContentAnalyticsViewSet, AdvancedSearchViewSet,
    NotificationViewSet, SocialMediaViewSet
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'articles', NewsArticleViewSet, basename='article')
router.register(r'events', EventViewSet, basename='event')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'subscribers', SubscriberViewSet, basename='subscriber')
router.register(r'newsletters', NewsletterViewSet, basename='newsletter')
router.register(r'analytics', ContentAnalyticsViewSet, basename='analytics')
router.register(r'search', AdvancedSearchViewSet, basename='search')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'social', SocialMediaViewSet, basename='social')

app_name = 'news_events_api'

urlpatterns = [
    # Explicit version support (v1)
    path('v1/', include(router.urls)),
    
    # Default API routes (maps to v1)
    path('', include(router.urls)),
    
    # API documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='news_events_api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='news_events_api:schema'), name='redoc'),
]

