from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    # URL for the current team page, e.g., /team/
    path('', views.team_list_view, name='list'),
    
    # URL for the past committees page, e.g., /team/archive/
    path('archive/', views.past_team_list_view, name='archive'),
]
