from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/', views.dashboard_api, name='api'),
    path('track/page-view/', views.track_page_view, name='track_page_view'),
    path('track/error/', views.track_error, name='track_error'),
    path('track/image-load/', views.track_page_view, name='track_image_load'),
    path('track/search/', views.track_page_view, name='track_search'),
    path('track/form-submit/', views.track_page_view, name='track_form_submit'),
    path('track/custom-metric/', views.track_page_view, name='track_custom_metric'),
    path('track/session-health/', views.track_page_view, name='track_session_health'),
    path('track/session-end/', views.track_page_view, name='track_session_end'),
    path('track/visibility/', views.track_page_view, name='track_visibility'),
    path('report/generate/', views.generate_dashboard_report, name='generate_report'),
    path('alerts/', views.get_alerts, name='get_alerts'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('export/', views.export_dashboard_data, name='export_data'),
    path('widgets/', views.dashboard_widgets, name='dashboard_widgets'),
    path('preferences/', views.update_user_preferences, name='update_preferences'),
]
