from django.urls import path
from . import views
from . import map_views

app_name = 'contact'  # This defines a namespace for the app's URLs

urlpatterns = [
    path('', views.contact_view, name='contact_view'),
    path('kym-form/', views.kym_form_view, name='kym_form'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    
    # Interactive Map
    path('map/', map_views.interactive_map_view, name='interactive_map'),
    path('map/api/', map_views.map_locations_api, name='map_locations_api'),
    path('map/directions/', map_views.map_directions_api, name='map_directions_api'),
    path('map/analytics/', map_views.map_analytics, name='map_analytics'),
]
