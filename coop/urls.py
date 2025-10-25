from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
# These two imports are necessary for serving media files during development
from django.conf import settings
from django.conf.urls.static import static
from apps.core.admin_site import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('about/', include('apps.about.urls')),
    path('search/', include('apps.search.urls')),
    path('contact/', include('apps.contact.urls')),
    path('news-events/', include('apps.news_events.urls')),
    path('downloads/', include('apps.downloads.urls')),
    path('services/', include('apps.services.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Gallery app
    path('gallery/', include('gallery.urls')),
    
    # Member management system
    path('members/', include('members.urls')),
    
    # API URLs (commented out until dependencies are installed)
    # path('api/v1/', include('apps.services.api_urls')),
    # path('api/v1/about/', include('apps.about.api_urls')),
    # path('api/v1/news-events/', include('apps.news_events.api_urls')),
    # path('api/v1/contact/', include('apps.contact.api_urls')),
    # path('api/v1/downloads/', include('apps.downloads.api_urls')),
    
    # Health check endpoints
    path('health/', include('apps.core.urls')),
    
    # API Documentation (commented out until drf_spectacular is installed)
    # path('api/docs/', include('drf_spectacular.urls')),
    
    path('', include('apps.home.urls')), # This should be the last one
]

# This is the crucial part for showing images in development mode.
# It tells Django to serve files from your MEDIA_ROOT when in DEBUG mode.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
