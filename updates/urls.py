from django.urls import path
from . import views

# Defines a namespace for this app's URLs.
# This is important for using names like 'updates:list' in templates.
app_name = 'updates'

# The list of URL patterns for the 'updates' app.
urlpatterns = [
    # Example: /updates/
    path('', views.news_list_view, name='list'),
    
    # Example: /updates/events/
    path('events/', views.event_list_view, name='event-list'),
    
    # Example: /updates/events/past/
    path('events/past/', views.past_event_list_view, name='past-event-list'),
    
    # Example: /updates/subscribe/ (for the newsletter form)
    path('subscribe/', views.subscribe_view, name='subscribe'),
    
    # Example: /updates/all-news/
    path('all-news/', views.all_news_list_view, name='news-all-list'),
    
    # Example: /updates/category/general-notice/
    path('category/<slug:category_slug>/', views.article_by_category_view, name='article-by-category'),
    
    # Example: /updates/my-first-article/ (This must be last)
    path('<slug:slug>/', views.news_detail_view, name='detail'),
]
