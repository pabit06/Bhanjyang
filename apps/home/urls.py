from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    # Main pages
    path('', views.IndexView.as_view(), name='index'),
    path('remittance/', views.RemittanceView.as_view(), name='remittance'),
    path('offline/', views.OfflineView.as_view(), name='offline'),
    
    # Form processing (AJAX) - Renamed paths to avoid conflicts
    path('ajax/contact/submit/', views.ContactSubmissionView.as_view(), name='contact_submit'),
    path('ajax/newsletter/signup/', views.NewsletterSignupView.as_view(), name='newsletter_signup'),
    
    # API endpoints
    path('api/statistics/', views.StatisticsAPI.as_view(), name='api_statistics'),
    path('api/testimonials/', views.TestimonialsAPI.as_view(), name='api_testimonials'),
    
    # Preview (with token for security)
    path('preview/<str:model_name>/<int:pk>/<str:token>/', views.PreviewContentView.as_view(), name='preview_content'),
]
