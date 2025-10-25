from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'home'

# Cache settings
CACHE_TIMEOUTS = {
    'homepage': 300,  # 5 minutes
    'about': 600,     # 10 minutes
    'gallery': 900,   # 15 minutes
    'remittance': 1800,  # 30 minutes
}

urlpatterns = [
    # Main pages with caching
    path('', cache_page(CACHE_TIMEOUTS['homepage'])(views.index), name='index'),
    path('about/', cache_page(CACHE_TIMEOUTS['about'])(views.about_view), name='about'),
    path('remittance/', cache_page(CACHE_TIMEOUTS['remittance'])(views.remittance_view), name='remittance'),
    
    # Form handling with security
    path('contact/submit/', 
         require_http_methods(["POST"])(views.contact_submit), 
         name='contact_submit'),
    path('newsletter/signup/', 
         require_http_methods(["POST"])(csrf_exempt(views.newsletter_signup)), 
         name='newsletter_signup'),
    
    # API endpoints with caching
    path('api/statistics/', 
         cache_page(180)(views.api_statistics), 
         name='api_statistics'),
    path('api/testimonials/', 
         cache_page(180)(views.api_testimonials), 
         name='api_testimonials'),
]
