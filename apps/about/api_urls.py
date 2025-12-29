from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    CooperativeInfoViewSet, CooperativeTimelineViewSet,
    CooperativeAffiliationViewSet, LeadershipMessageViewSet,
    PersonViewSet, CommitteeViewSet, StaffViewSet,
    SearchAPIView, StatisticsAPIView
    # NewsletterAPIView removed - no longer needed
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'cooperative-info', CooperativeInfoViewSet, basename='cooperative-info')
router.register(r'timeline', CooperativeTimelineViewSet, basename='timeline')
router.register(r'affiliations', CooperativeAffiliationViewSet, basename='affiliations')
router.register(r'leadership', LeadershipMessageViewSet, basename='leadership')
router.register(r'team', PersonViewSet, basename='team')
router.register(r'committees', CommitteeViewSet, basename='committees')
router.register(r'staff', StaffViewSet, basename='staff')

app_name = 'about_api'

urlpatterns = [
    # API router URLs
    path('', include(router.urls)),
    
    # Additional API endpoints
    path('search/', SearchAPIView.as_view(), name='search'),
    path('statistics/', StatisticsAPIView.as_view(), name='statistics'),
    # Note: Contact API endpoint removed - use contact app's API instead
    # Newsletter API endpoint removed - no longer needed
]
