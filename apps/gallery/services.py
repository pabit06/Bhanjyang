from typing import List, Dict, Any, Optional
from django.db import transaction
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from .models import (
    GalleryImage, GalleryAlbum, GalleryImageDownload, GalleryImageLike,
    GalleryImageShare, SmartCollection, AutoCategorizationRule
)
from apps.dashboard.services import DashboardAnalyticsService

class GalleryService:
    """
    Handles all business logic for the Gallery application.
    Follows strict Service Layer pattern.
    """
    
    @staticmethod
    def get_gallery_home_data() -> Dict[str, Any]:
        """
        Fetches data for the main gallery page with optimization.
        """
        # 1. Fetch Data
        images = GalleryImage.objects.filter(is_active=True).select_related('album').order_by('order', '-created_at')
        albums = GalleryAlbum.objects.filter(is_active=True).prefetch_related('sub_albums').order_by('order', '-created_at')
        
        # 2. Process Data
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
    def get_vr_gallery_data() -> Dict[str, Any]:
        """Get data specific for VR view"""
        gallery_images = GalleryImage.objects.filter(is_active=True).order_by('-created_at')
        albums = GalleryAlbum.objects.filter(is_active=True).order_by('order')
        
        categories = {}
        for image in gallery_images:
            if image.category not in categories:
                categories[image.category] = []
            categories[image.category].append(image)
            
        return {
            'gallery_images': gallery_images,
            'albums': albums,
            'categories': categories
        }

    @staticmethod
    def get_album_detail(album_id: int) -> Dict[str, Any]:
        """Get details for a specific album"""
        album = get_object_or_404(GalleryAlbum, id=album_id, is_active=True)
        images = album.images.filter(is_active=True).order_by('order', '-created_at')
        return {'album': album, 'images': images}

    @staticmethod
    def get_analytics_data(time_range: str = '30d') -> Dict[str, Any]:
        """Calculates analytics metrics for dashboard"""
        now = timezone.now()
        days_map = {'7d': 7, '30d': 30, '90d': 90, '1y': 365}
        days = days_map.get(time_range, 30)
        start_date = now - timedelta(days=days)
        
        qs = GalleryImage.objects.filter(is_active=True, created_at__gte=start_date)
            
        # Stats
        total_downloads = GalleryImageDownload.objects.filter(image__in=qs).count()
        category_stats = qs.values('category').annotate(
            count=Count('id'),
            total_views=Sum('views_count'),
            avg_quality=Avg('ai_quality_score')
        ).order_by('-count')
        
        top_images_qs = qs.annotate(
            engagement=Sum('likes_count') + Sum('shares_count') + Count('comments')
        ).order_by('-views_count')[:10]
        
        # Serialize top_images manually for API stats
        top_images = [{
            'id': img.id,
            'title': img.title,
            'image': img.image.name if img.image else None,
            'views_count': img.views_count,
            'likes_count': img.likes_count,
            'shares_count': img.shares_count,
            'engagement': img.engagement
        } for img in top_images_qs]
        
        recent_activity = [{
            'id': img.id,
            'title': img.title,
            'created_at': img.created_at
        } for img in qs.order_by('-created_at')[:5]]

        # Aggregates
        aggs = qs.aggregate(
            views=Sum('views_count'),
            likes=Sum('likes_count'),
            shares=Sum('shares_count')
        )
        
        # Traffic Data from Dashboard
        try:
            views_chart = DashboardAnalyticsService.get_chart_data('traffic', days, {'page_url': '/gallery/'})
        except Exception:
            views_chart = {'labels': [], 'data': []}

        return {
            'total_views': aggs['views'] or 0,
            'total_likes': aggs['likes'] or 0,
            'total_shares': aggs['shares'] or 0,
            'total_downloads': total_downloads,
            'category_stats': category_stats,
            'top_images': top_images,
            'recent_activity': recent_activity,
            'views_chart': views_chart,
        }

    @staticmethod
    def search_images(query: str) -> List[Dict]:
        """Search images by title, description or AI tags"""
        if not query: return []
        
        images = GalleryImage.objects.filter(is_active=True).filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(ai_tags__icontains=query)
        ).select_related('album')[:20]
        
        return [{
            'id': img.id,
            'title': img.title,
            'description': img.description,
            'image_url': img.image.url,
            'thumbnail_url': img.get_thumbnail_url() if hasattr(img, 'get_thumbnail_url') else img.image.url,
            'album_name': img.album.name if img.album else 'Uncategorized',
            'category_name': img.get_category_display(),
            'ai_tags': img.ai_tags or []
        } for img in images]

    @staticmethod
    def record_interaction(image_id: int, action: str, request_meta: Dict) -> Dict:
        """Record user interaction (view, like, share, download)"""
        image = get_object_or_404(GalleryImage, id=image_id)
        user_ip = (request_meta.get('ip') or '')[:45]
        user_agent = (request_meta.get('ua') or '')[:500]
        session_id = request_meta.get('session_id') or ''

        with transaction.atomic():
            message = ""
            if action == 'view':
                image.views_count = F('views_count') + 1
                image.save(update_fields=['views_count'])
                message = 'View recorded.'
            
            elif action == 'download':
                GalleryImageDownload.objects.create(
                    image=image, user_ip=user_ip, user_agent=user_agent, session_id=session_id
                )
                message = 'Download recorded.'
            
            elif action == 'share':
                image.shares_count = F('shares_count') + 1
                image.save(update_fields=['shares_count'])
                GalleryImageShare.objects.create(
                    image=image, platform=request_meta.get('platform', 'unknown'),
                    user_ip=user_ip, user_agent=user_agent, session_id=session_id
                )
                message = 'Share recorded.'
            
            elif action == 'like':
                like_obj, created = GalleryImageLike.objects.get_or_create(
                    image=image, user_ip=user_ip,
                    defaults={'user_agent': user_agent, 'session_id': session_id}
                )
                if created:
                    image.likes_count = F('likes_count') + 1
                    message = 'Image liked.'
                else:
                    like_obj.delete()
                    image.likes_count = F('likes_count') - 1
                    message = 'Image unliked.'
                image.save(update_fields=['likes_count'])

        image.refresh_from_db()
        return {
            'success': True, 'message': message,
            'view_count': image.views_count,
            'like_count': image.likes_count, 'share_count': image.shares_count
        }

    # --- Smart Collections & Auto-Tagging ---

    @staticmethod
    def get_smart_collections() -> Dict[str, Any]:
        collections = SmartCollection.objects.filter(is_active=True).order_by('-is_featured', 'name')
        data = []
        for c in collections:
            data.append({
                'collection': c,
                'image_count': c.get_image_count(),
                'images': c.get_images()[:6]
            })
        return {'collections': data, 'featured': collections.filter(is_featured=True)[:3]}

    @staticmethod
    def update_smart_collection(collection_id: int, user) -> int:
        if not user.is_staff: raise PermissionError("Staff access required")
        collection = get_object_or_404(SmartCollection, id=collection_id)
        return collection.update_collection()

    @staticmethod
    def apply_auto_categorization(user) -> int:
        if not user.is_staff: raise PermissionError("Staff access required")
        
        rules = AutoCategorizationRule.objects.filter(is_active=True, auto_apply=True).order_by('-priority')
        images = GalleryImage.objects.filter(is_active=True)
        count = 0
        
        with transaction.atomic():
            for rule in rules:
                for image in images:
                    if rule.apply_to_image(image):
                        count += 1
        return count
