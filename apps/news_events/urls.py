# news_events/urls.py

from django.urls import path
from . import views

app_name = 'news_events'

urlpatterns = [
    # Main pages
    path('', views.news_events_home_view, name='home'),
    path('articles/', views.article_list_view, name='article-list'),
    path('events/', views.event_list_view, name='event-list'),
    path('search/', views.search_view, name='search'),
    
    # Article detail
    path('article/<slug:slug>/', views.article_detail_view, name='article-detail'),
    
    # Event detail
    path('event/<slug:slug>/', views.event_detail_view, name='event-detail'),
    
    # Category pages
    path('category/<slug:category_slug>/', views.article_list_view, name='article-by-category'),
    
    # User actions
    path('subscribe/', views.subscribe_view, name='subscribe'),
    path('confirm-subscription/<str:token>/', views.confirm_subscription_view, name='confirm-subscription'),
    path('unsubscribe/<str:token>/', views.unsubscribe_view, name='unsubscribe'),
    
    # Comments
    path('article/<slug:article_slug>/comment/', views.comment_submit_view, name='comment-submit'),
    
    # Sharing
    path('article/<slug:article_slug>/share/', views.share_article_view, name='share-article'),
    
    # RSS Feed
    path('rss/', views.rss_feed_view, name='rss-feed'),
    path('analytics/', views.analytics_dashboard_view, name='analytics-dashboard'),
]
