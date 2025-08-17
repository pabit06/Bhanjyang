from django.contrib import admin
from django.urls import path, include
# These two imports are necessary for serving media files during development
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contact/', include('contact.urls')),
    path('updates/', include('updates.urls')),
    path('team/', include('team.urls')),
    path('downloads/', include('downloads.urls')),
    path('services/', include('services.urls')),
    path('', include('main.urls')), # This should be the last one
]

# This is the crucial part for showing images in development mode.
# It tells Django to serve files from your MEDIA_ROOT when in DEBUG mode.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
