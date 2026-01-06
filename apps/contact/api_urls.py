"""
Contact App API URLs

URL configuration for Contact REST API.

Author: Bhanjyang Tech Team
Created: 2026-01-06
"""

from rest_framework.routers import DefaultRouter
from .api_views import ContactViewSet

# Router setup
router = DefaultRouter()
router.register(r'', ContactViewSet, basename='contact')

app_name = 'contact_api'
urlpatterns = router.urls

# Available endpoints:
# POST   /api/v1/contact/submit/       - Submit contact form
# GET    /api/v1/contact/officer/      - Get RTI officer info
# GET    /api/v1/contact/privacy/      - Get privacy policy
# GET    /api/v1/contact/stats/        - Get statistics (admin only)
