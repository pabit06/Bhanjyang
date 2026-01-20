from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.views.i18n import set_language
# These two imports are necessary for serving media files during development
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from apps.admin.admin_site import admin_site
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from two_factor.urls import urlpatterns as tf_urls
from apps.core.sitemaps import (
    StaticPagesSitemap, NewsArticleSitemap, EventSitemap,
    SavingsAccountSitemap, LoanTypeSitemap, FixedDepositSitemap,
    RemittanceServiceSitemap, DigitalServiceSitemap, MemberReliefSitemap,
    GalleryAlbumSitemap, DocumentSitemap
)

urlpatterns = [
    # Favicon redirect
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon/favicon.ico'), permanent=True)),
    
    # Language switching
    path('i18n/setlang/', set_language, name='set_language'),
    
    path('', include(tf_urls)),
    path('admin/', admin_site.urls),
    path('about/', include('apps.about.urls')),
    path('search/', include('apps.search.urls')),
    path('contact/', include('apps.contact.urls')),
    path('news-events/', include('apps.news_events.urls')),
    path('downloads/', include('apps.downloads.urls')),
    path('services/', include('apps.services.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Gallery app
    path('gallery/', include('apps.gallery.urls')),
    
    
    # API URLs
    path('api/v1/', include('apps.services.api_urls')),
    path('api/v1/about/', include('apps.about.api_urls')),
    path('api/v1/news-events/', include('apps.news_events.api_urls')),
    path('api/v1/downloads/', include('apps.downloads.api_urls')),  # Downloads API
    
    
    # Health check endpoints
    path('health/', include('apps.core.urls')),
    
    # Dynamic Sitemap
    path('sitemap.xml', sitemap, {
        'sitemaps': {
            'static': StaticPagesSitemap,
            'news': NewsArticleSitemap,
            'events': EventSitemap,
            'savings': SavingsAccountSitemap,
            'loans': LoanTypeSitemap,
            'fixed_deposits': FixedDepositSitemap,
            'remittance': RemittanceServiceSitemap,
            'digital': DigitalServiceSitemap,
            'relief': MemberReliefSitemap,
            'gallery': GalleryAlbumSitemap,
            'documents': DocumentSitemap,
        }
    }, name='django.contrib.sitemaps.views.sitemap'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('', include('apps.home.urls')), # This should be the last one
]

# This is the crucial part for showing images in development mode.
# It tells Django to serve files from your MEDIA_ROOT when in DEBUG mode.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]

