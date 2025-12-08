from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Specialized Dashboard Sections
    path('performance/', views.PerformanceDashboardView.as_view(), name='performance'),
    path('analytics/', views.AnalyticsDashboardView.as_view(), name='analytics'),
    path('errors/', views.ErrorDashboardView.as_view(), name='errors'),
    path('reports/', views.ReportsDashboardView.as_view(), name='reports'),
    
    # API Endpoints
    path('api/', views.DashboardDataView.as_view(), name='api'),
    path('api/performance/', views.PerformanceDataView.as_view(), name='performance_api'),
    path('api/analytics/', views.AnalyticsDataView.as_view(), name='analytics_api'),
    path('api/errors/', views.ErrorsDataView.as_view(), name='errors_api'),
    
    # Tracking Endpoints
    path('track/page-view/', views.TrackPageView.as_view(), name='track_page_view'),
    path('track/error/', views.TrackErrorView.as_view(), name='track_error'),
    # Pointing other tracking to TrackPageView for compatibility with previous generic implementation
    path('track/image-load/', views.TrackPageView.as_view(), name='track_image_load'),
    path('track/search/', views.TrackPageView.as_view(), name='track_search'),
    path('track/form-submit/', views.TrackPageView.as_view(), name='track_form_submit'),
    path('track/custom-metric/', views.TrackPageView.as_view(), name='track_custom_metric'),
    path('track/session-health/', views.TrackPageView.as_view(), name='track_session_health'),
    path('track/session-end/', views.TrackPageView.as_view(), name='track_session_end'),
    path('track/visibility/', views.TrackPageView.as_view(), name='track_visibility'),
    
    # Management Endpoints
    path('report/generate/', views.DashboardReportView.as_view(), name='generate_report'),
    path('alerts/', views.AlertsView.as_view(), name='get_alerts'),
    path('alerts/<int:alert_id>/resolve/', views.ResolveAlertView.as_view(), name='resolve_alert'),
    path('export/', views.ExportDashboardDataView.as_view(), name='export_data'),
    path('widgets/', views.DashboardWidgetsView.as_view(), name='dashboard_widgets'),
    path('preferences/', views.UserPreferenceView.as_view(), name='update_preferences'),
]
