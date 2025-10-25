from django.urls import path
from django.views.decorators.cache import cache_page
from . import views

app_name = 'gallery'

# Cache settings for gallery views
CACHE_TIMEOUTS = {
    'gallery': 900,   # 15 minutes
    'album_detail': 900, # 15 minutes
}

urlpatterns = [
    # Main gallery views
    path('', cache_page(CACHE_TIMEOUTS['gallery'])(views.gallery_view), name='gallery'),
    path('vr/', views.vr_gallery_view, name='vr_gallery'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('smart-collections/', views.smart_collections_view, name='smart_collections'),
    path('smart-collections/<int:collection_id>/', views.smart_collection_detail_view, name='smart_collection_detail'),
    path('auto-categorization/', views.auto_categorization_view, name='auto_categorization'),
    
    # API endpoints
    path('api/smart-collections/<int:collection_id>/update/', views.update_smart_collection_api, name='update_smart_collection_api'),
    path('api/auto-categorization/apply/', views.apply_auto_categorization_api, name='apply_auto_categorization_api'),
    path('album/<int:album_id>/', cache_page(CACHE_TIMEOUTS['album_detail'])(views.album_detail_view), name='album_detail'),
    
    # API endpoints
    path('api/search/', views.gallery_search_api, name='gallery_search_api'),
    path('api/categories/', views.gallery_categories_api, name='gallery_categories_api'),
    path('api/albums/', views.gallery_albums_api, name='gallery_albums_api'),
    path('api/analytics/', views.gallery_image_analytics, name='gallery_image_analytics'),
    path('api/stats/', views.gallery_stats_api, name='gallery_stats_api'),
]
