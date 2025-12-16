from django.urls import path
from django.views.decorators.cache import cache_page
from . import views

app_name = 'gallery'

# Cache settings
CACHE_TIMEOUTS = {
    'gallery': 900,   # 15 minutes
    'album_detail': 900,
}

urlpatterns = [
    # Pages
    path('', cache_page(CACHE_TIMEOUTS['gallery'])(views.GalleryHomeView.as_view()), name='gallery'),
    path('vr/', views.VRGalleryView.as_view(), name='vr_gallery'),
    path('analytics/', views.GalleryAnalyticsRawView.as_view(), name='analytics'),
    
    path('smart-collections/', views.SmartCollectionsView.as_view(), name='smart_collections'),
    path('smart-collections/<int:collection_id>/', views.SmartCollectionDetailView.as_view(), name='smart_collection_detail'),
    path('auto-categorization/', views.AutoCategorizationView.as_view(), name='auto_categorization'),
    
    path('album/<int:album_id>/', cache_page(CACHE_TIMEOUTS['album_detail'])(views.AlbumDetailView.as_view()), name='album_detail'),

    # APIs
    path('api/search/', views.GallerySearchAPI.as_view(), name='gallery_search_api'),
    path('api/stats/', views.GalleryStatsAPI.as_view(), name='gallery_stats_api'),
    path('api/interact/', views.GalleryInteractionAPI.as_view(), name='gallery_interaction_api'),
    
    path('api/smart-collections/<int:collection_id>/update/', views.UpdateSmartCollectionAPI.as_view(), name='update_smart_collection_api'),
    path('api/auto-categorization/apply/', views.ApplyAutoCategorizationAPI.as_view(), name='apply_auto_categorization_api'),
]
