# downloads/urls.py

from django.urls import path
from . import views

app_name = 'downloads' # Namespace for this app's URLs

urlpatterns = [
    path('', views.download_center_view, name='download_center'),
]