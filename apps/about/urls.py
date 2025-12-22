from django.urls import path
from . import views

app_name = 'about'

urlpatterns = [
    # Main about page
    path('', views.AboutHomeView.as_view(), name='home'),
    
    # Sub-pages
    path('timeline/', views.TimelineView.as_view(), name='timeline'),
    path('affiliations/', views.AffiliationsView.as_view(), name='affiliations'),
    path('leadership/', views.LeadershipView.as_view(), name='leadership'),
    
    # Team pages
    path('team/', views.TeamView.as_view(), name='team'),
    path('team/past/', views.PastTeamView.as_view(), name='past_team'),
    
    # Gallery
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    
    # Form handling
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact_success'),
    path('api/newsletter-signup/', views.NewsletterSignupView.as_view(), name='newsletter_signup'),
    path('api/feedback/', views.FeedbackView.as_view(), name='feedback'),
    
    # Cooperative detail
    path('cooperative/<slug:slug>/', views.CooperativeDetailView.as_view(), name='cooperative_detail'),
]
