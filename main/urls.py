from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    # Add this line to create the URL for the about page
    path('about/', views.about_view, name='about'), 
]
