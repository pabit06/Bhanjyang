from django.urls import path, include
from django.contrib import admin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def api_documentation(request):
    """API Documentation view"""
    api_endpoints = {
        'dashboard': {
            'base_url': '/dashboard/api/',
            'endpoints': {
                'GET /dashboard/api/?type=page_load&days=7': 'Get page load performance data',
                'GET /dashboard/api/?type=errors&days=7': 'Get error statistics',
                'POST /dashboard/track/page-view/': 'Track page view performance',
                'POST /dashboard/track/error/': 'Track application errors',
                'POST /dashboard/track/image-load/': 'Track image load times',
            }
        },
        'updates': {
            'base_url': '/updates/',
            'endpoints': {
                'GET /updates/': 'Get news and events list',
                'GET /updates/<slug>/': 'Get specific news article',
                'GET /updates/category/<slug>/': 'Get articles by category',
                'POST /updates/subscribe/': 'Subscribe to newsletter',
            }
        },
        'search': {
            'base_url': '/search/',
            'endpoints': {
                'GET /search/?q=<query>': 'Search across all content',
                'GET /search/?q=<query>&type=<content_type>': 'Search specific content type',
            }
        },
        'contact': {
            'base_url': '/contact/',
            'endpoints': {
                'GET /contact/': 'Get contact form',
                'POST /contact/': 'Submit contact form',
            }
        }
    }
    
    return render(request, 'api/documentation.html', {
        'api_endpoints': api_endpoints,
        'title': 'API Documentation'
    })

@csrf_exempt
@require_http_methods(["GET"])
def api_status(request):
    """API Status endpoint"""
    return JsonResponse({
        'status': 'active',
        'version': '1.0.0',
        'timestamp': request.META.get('HTTP_DATE', ''),
        'endpoints': {
            'dashboard': '/dashboard/api/',
            'updates': '/updates/',
            'search': '/search/',
            'contact': '/contact/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_status, name='api-status'),
    path('api/docs/', api_documentation, name='api-docs'),
    path('search/', include('apps.search.urls')),
    path('contact/', include('apps.contact.urls')),
    path('news-events/', include('apps.news_events.urls')),
    path('downloads/', include('apps.downloads.urls')),
    path('services/', include('apps.services.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('', include('apps.home.urls')), # This should be the last one
]
