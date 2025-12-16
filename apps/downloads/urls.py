# downloads/urls.py

from django.urls import path
from . import views

app_name = 'downloads'  # Namespace for this app's URLs

urlpatterns = [
    path('', views.download_center_view, name='download_center'),
    path('<int:pk>/', views.file_detail_view, name='file_detail'),
    path('<int:pk>/download/', views.download_file_view, name='download_file'),
    path('<int:pk>/preview/', views.file_preview_view, name='file_preview'),
    path('bulk-download/', views.bulk_download_view, name='bulk_download'),
    path('history/', views.download_history_view, name='download_history'),
]