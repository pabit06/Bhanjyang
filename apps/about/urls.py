from django.urls import path
from . import views
from . import map_views

app_name = 'about'

urlpatterns = [
    # Main about page
    path('', views.about_home_view, name='home'),
    
    # Sub-pages
    path('timeline/', views.timeline_view, name='timeline'),
    path('achievements/', views.achievements_view, name='achievements'),
    path('affiliations/', views.affiliations_view, name='affiliations'),
    path('leadership/', views.leadership_view, name='leadership'),
    
    # Team pages
    path('team/', views.team_view, name='team'),
    path('team/past/', views.past_team_view, name='past_team'),
    
    # Gallery
    path('gallery/', views.gallery_view, name='gallery'),
    
    # Interactive Map
    path('map/', map_views.interactive_map_view, name='interactive_map'),
    path('map/api/', map_views.map_locations_api, name='map_locations_api'),
    path('map/directions/', map_views.map_directions_api, name='map_directions_api'),
    
    # Form handling
    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.contact_success_view, name='contact_success'),
    path('api/newsletter-signup/', views.newsletter_signup_view, name='newsletter_signup'),
    path('api/feedback/', views.feedback_view, name='feedback'),
    
    # Cooperative detail (if multiple cooperatives)
    path('cooperative/<slug:slug>/', views.CooperativeDetailView.as_view(), name='cooperative_detail'),
]
