from django.urls import path
from . import views

app_name = 'downloads'

urlpatterns = [
    path('', views.DownloadCenterView.as_view(), name='download_center'),
    path('<int:pk>/', views.FileDetailView.as_view(), name='file_detail'),
    path('<int:pk>/download/', views.DownloadFileView.as_view(), name='download_file'),
    path('<int:pk>/preview/', views.FilePreviewView.as_view(), name='file_preview'),
    path('bulk-download/', views.BulkDownloadView.as_view(), name='bulk_download'),
    path('history/', views.DownloadHistoryView.as_view(), name='download_history'),
]