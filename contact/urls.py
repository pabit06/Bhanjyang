from django.urls import path
from . import views

app_name = 'contact'  # This defines a namespace for the app's URLs

urlpatterns = [
    path('', views.contact_view, name='contact_view'),
]
