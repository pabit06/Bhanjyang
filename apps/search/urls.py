from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.AdvancedSearchView.as_view(), name='advanced_search'),
    path('api/', views.search_api, name='search_api'),
]
