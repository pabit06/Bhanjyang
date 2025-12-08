from typing import List, Dict, Any, Optional
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import GalleryImage, GalleryAlbum, GalleryImageDownload

class GalleryService:
    """
    Handles complex business logic for Gallery.
    Future-proof by using Type Hinting and Logic Separation.
    """
    
    @staticmethod
    def get_optimized_gallery_data() -> Dict[str, Any]:
        """
        Fetches gallery data efficiently avoiding N+1 queries.
        Returns a dictionary ready for the template or API.
        """
        # 1. Fetch Data
        images = GalleryImage.objects.filter(is_active=True).select_related('album').order_by('order', '-created_at')
        albums = GalleryAlbum.objects.filter(is_active=True).prefetch_related('sub_albums').order_by('order', '-created_at')
        
        # 2. Process Data (Grouping logic moved from View)
        categories: Dict[str, List[GalleryImage]] = {}
        album_images: Dict[int, List[GalleryImage]] = {album.id: [] for album in albums}
        
        for image in images:
            # Group by category
            if image.category not in categories:
                categories[image.category] = []
            categories[image.category].append(image)
            
            # Group by album
            if image.album_id in album_images:
                album_images[image.album_id].append(image)
                
        root_albums = [album for album in albums if album.parent_album_id is None]
        
        return {
            'categories': categories,
            'albums': albums,
            'root_albums': root_albums,
            'album_images': album_images,
            'gallery_images': images,
        }

    @staticmethod
    def get_analytics_data(time_range: str = '30d') -> Dict[str, Any]:
        """
        Calculates analytics metrics.
        """
        now = timezone.now()
        start_date = None
        
        if time_range == '7d':
            start_date = now - timedelta(days=7)
        elif time_range == '30d':
            start_date = now - timedelta(days=30)
        elif time_range == '90d':
            start_date = now - timedelta(days=90)
        elif time_range == '1y':
            start_date = now - timedelta(days=365)
        else:
            start_date = None
        
        qs = GalleryImage.objects.filter(is_active=True)
        if start_date:
            qs = qs.filter(created_at__gte=start_date)
            
        # Count downloads from related model
        total_downloads = GalleryImageDownload.objects.filter(
            image__in=qs
        ).count()

        # Category distribution
        category_stats = qs.values('category').annotate(
            count=Count('id'),
            total_views=Sum('views_count'),
            avg_quality=Avg('ai_quality_score')
        ).order_by('-count')
        
        # Top performing images
        top_images = qs.annotate(
            engagement_rate=Sum('likes_count') + Sum('shares_count') + Count('comments')
        ).order_by('-views_count')[:10]
        
        # Recent activity
        recent_activity = qs.order_by('-created_at')[:5]

        return {
            'total_views': qs.aggregate(total=Sum('views_count'))['total'] or 0,
            'total_likes': qs.aggregate(total=Sum('likes_count'))['total'] or 0,
            'total_shares': qs.aggregate(total=Sum('shares_count'))['total'] or 0,
            'total_downloads': total_downloads,
            'category_stats': category_stats,
            'top_images': top_images,
            'recent_activity': recent_activity,
        }

