from django.urls import path
from . import views

app_name = 'about'

urlpatterns = [
    # Main about page - redirect to introduction
    path('', views.AboutHomeView.as_view(), name='home'),
    
    # Sub-pages
    path('introduction/', views.IntroductionView.as_view(), name='introduction'),
    path('timeline/', views.TimelineView.as_view(), name='timeline'),
    path('affiliations/', views.AffiliationsView.as_view(), name='affiliations'),
    path('chairperson-message/', views.ChairpersonMessageView.as_view(), name='chairperson_message'),
    path('manager-commitment/', views.ManagerCommitmentView.as_view(), name='manager_commitment'),
    
    # Team pages
    path('board-of-directors/', views.BoardOfDirectorsView.as_view(), name='board_of_directors'),
    path('management/', views.ManagementView.as_view(), name='management'),
    
    # Testimonials
    path('member-testimonials/', views.MemberTestimonialsView.as_view(), name='member_testimonials'),
    
    # Form handling
    path('contact/', views.ContactView.as_view(), name='contact'),  # Redirects to main contact app
    # Newsletter and Feedback forms removed - no longer needed
    
    # Cooperative detail
    path('cooperative/<slug:slug>/', views.CooperativeDetailView.as_view(), name='cooperative_detail'),
    
    # Preview (with token for security)
    path('preview/<str:model_name>/<int:pk>/', views.PreviewContentView.as_view(), name='preview_content'),
    path('preview/<str:model_name>/<int:pk>/<str:token>/', views.PreviewContentView.as_view(), name='preview_content_token'),
]
