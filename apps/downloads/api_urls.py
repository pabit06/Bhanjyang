"""
API URL Configuration for Downloads App
========================================

Defines REST API endpoints for the downloads app.

Author: Prem Bhandari
Date: January 6, 2026
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import DownloadableFileViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'files', DownloadableFileViewSet, basename='file')

app_name = 'downloads_api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
]

"""
Generated URLs:

GET    /api/downloads/files/                      - List files
POST   /api/downloads/files/                      - Create file (admin)
GET    /api/downloads/files/{id}/                 - File details
PUT    /api/downloads/files/{id}/                 - Update file (admin)
PATCH  /api/downloads/files/{id}/                 - Partial update (admin)
DELETE /api/downloads/files/{id}/                 - Delete file (admin)

POST   /api/downloads/files/{id}/download/        - Download file
POST   /api/downloads/files/{id}/increment_view/  - Increment view
GET    /api/downloads/files/featured/             - Featured files
GET   /api/downloads/files/categories/           - Categories list
GET    /api/downloads/files/priorities/           - Priorities list
GET    /api/downloads/files/stats/                - Statistics (admin)
"""
