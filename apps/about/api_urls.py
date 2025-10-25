from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    CooperativeInfoViewSet, CooperativeTimelineViewSet,
    CooperativeAchievementViewSet, CooperativeStatisticSerializer,
    CooperativeAffiliationViewSet, LeadershipMessageViewSet,
    PersonViewSet, CommitteeViewSet, StaffViewSet,
    SearchAPIView, StatisticsAPIView, ContactAPIView, NewsletterAPIView
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'cooperative-info', CooperativeInfoViewSet, basename='cooperative-info')
router.register(r'timeline', CooperativeTimelineViewSet, basename='timeline')
router.register(r'achievements', CooperativeAchievementViewSet, basename='achievements')
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
    path('contact/', ContactAPIView.as_view(), name='contact'),
    path('newsletter/', NewsletterAPIView.as_view(), name='newsletter'),
]
