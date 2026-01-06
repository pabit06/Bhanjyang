# news_events/urls.py

from django.urls import path
from . import views
from . import api_views

app_name = 'news_events'

urlpatterns = [
    # Main pages
    path('', views.NewsHomeView.as_view(), name='home'),
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('events/', views.EventListView.as_view(), name='event-list'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Article detail
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    
    # Event detail
    path('event/<slug:slug>/', views.EventDetailView.as_view(), name='event-detail'),
    
    # Category pages
    path('category/<slug:category_slug>/', views.ArticleListView.as_view(), name='article-by-category'),
    
    # User actions
    path('subscribe/', views.SubscriptionView.as_view(), name='subscribe'),
    path('confirm-subscription/<str:token>/', views.SubscriptionConfirmationView.as_view(), name='confirm-subscription'),
    path('unsubscribe/<str:token>/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    
    # Comments
    path('article/<slug:article_slug>/comment/', views.CommentSubmissionView.as_view(), name='comment-submit'),
    
    # Sharing
    path('article/<slug:article_slug>/share/', views.ArticleShareView.as_view(), name='share-article'),
    
    # RSS Feed
    path('rss/', views.RSSFeedView.as_view(), name='rss-feed'),
    path('analytics/', views.AnalyticsDashboardView.as_view(), name='analytics-dashboard'),
    
    # Analytics API endpoints
    path('analytics/api/real-time-metrics/', api_views.get_real_time_metrics, name='api-real-time-metrics'),
    path('analytics/api/traffic-sources/', api_views.get_traffic_sources, name='api-traffic-sources'),
    path('analytics/api/content-performance/', api_views.get_content_performance, name='api-content-performance'),
    path('analytics/api/user-demographics/', api_views.get_user_demographics, name='api-user-demographics'),
    path('analytics/api/device-usage/', api_views.get_device_usage, name='api-device-usage'),
    path('analytics/api/top-articles/', api_views.get_top_articles, name='api-top-articles'),
    path('analytics/api/top-events/', api_views.get_top_events, name='api-top-events'),
]
