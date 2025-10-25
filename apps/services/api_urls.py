"""
API URL configuration for the Bhanjyang Cooperative services.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
# from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView  # Commented out until installed

from .api_views import (
    SavingsAccountViewSet, FixedDepositViewSet, LoanTypeViewSet,
    RemittanceServiceViewSet, MemberReliefViewSet, ServiceApplicationViewSet,
    ServiceAnalyticsViewSet, ServiceRecommendationViewSet, ServiceSearchViewSet
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'savings-accounts', SavingsAccountViewSet, basename='savings-accounts')
router.register(r'fixed-deposits', FixedDepositViewSet, basename='fixed-deposits')
router.register(r'loan-types', LoanTypeViewSet, basename='loan-types')
router.register(r'remittance-services', RemittanceServiceViewSet, basename='remittance-services')
router.register(r'member-relief', MemberReliefViewSet, basename='member-relief')
router.register(r'applications', ServiceApplicationViewSet, basename='applications')
router.register(r'analytics', ServiceAnalyticsViewSet, basename='analytics')
router.register(r'recommendations', ServiceRecommendationViewSet, basename='recommendations')
router.register(r'search', ServiceSearchViewSet, basename='search')

app_name = 'services_api'

urlpatterns = [
    # API routes
    path('', include(router.urls)),
    
    # API documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='services_api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='services_api:schema'), name='redoc'),
    
    # Health check endpoints
    path('health/', include('apps.core.urls')),
]
