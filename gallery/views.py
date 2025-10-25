from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q, Count
import json
import logging
import uuid
import time

# Set up logging
logger = logging.getLogger(__name__)

from .models import GalleryImage, GalleryAlbum


def track_page_view(request, page_url, page_title=""):
    """Track page views for analytics with error handling"""
    try:
        # Sanitize inputs
        page_url = page_url[:500] if page_url else ""
        page_title = page_title[:200] if page_title else ""
        user_ip = request.META.get('REMOTE_ADDR', '')[:45]  # IPv6 max length
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        referrer = request.META.get('HTTP_REFERER', '')[:500]
        session_id = request.session.session_key or str(uuid.uuid4())
        
        # Import PageView from home app
        from apps.home.models import PageView
        PageView.objects.create(
            page_url=page_url,
            page_title=page_title,
            user_ip=user_ip,
            user_agent=user_agent,
            referrer=referrer,
            session_id=session_id[:100]
        )
    except Exception as e:
        logger.error(f"Error tracking page view: {e}", exc_info=True)


# @cache_page(900)  # Cache for 15 minutes - temporarily disabled for testing
def gallery_view(request):
    """
    Enhanced gallery view with dynamic images and album support
    """
    track_page_view(request, request.build_absolute_uri(), "Gallery - Bhanjyang Cooperative")
    
    # Temporarily disable caching for testing
    # cache_key = f'gallery_data_{request.user.is_staff}'
    # cached_data = cache.get(cache_key)
    # 
    # if cached_data and not request.user.is_staff:
    #     return render(request, 'gallery/gallery.html', cached_data)
    
    try:
        # Get all active gallery images
        gallery_images = GalleryImage.objects.filter(
            is_active=True
        ).select_related('album').order_by('order', '-created_at')
        
        # Get all active albums
        albums = GalleryAlbum.objects.filter(
            is_active=True
        ).prefetch_related('images', 'sub_albums').order_by('order', '-created_at')
        
        # Group images by category (for backward compatibility)
        categories = {}
        for image in gallery_images:
            if image.category not in categories:
                categories[image.category] = []
            categories[image.category].append(image)
        
        # Group images by album
        album_images = {}
        for album in albums:
            album_images[album.id] = album.images.filter(is_active=True).order_by('order', '-created_at')
        
        # Get root albums (no parent)
        root_albums = albums.filter(parent_album__isnull=True)
        
    except Exception as e:
        logger.error(f"Error fetching gallery data: {e}", exc_info=True)
        categories = {}
        albums = []
        album_images = {}
        root_albums = []
        gallery_images = []
    
    context = {
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Gallery', 'url': reverse('gallery:gallery')}
        ],
        'categories': categories,
        'albums': albums,
        'root_albums': root_albums,
        'album_images': album_images,
        'gallery_images': gallery_images,
        'timestamp': int(time.time()),
    }
    
    # Temporarily disable caching for testing
    # cache.set(cache_key, context, 900)
    
    return render(request, 'gallery/gallery.html', context)


def vr_gallery_view(request):
    """Virtual Reality Gallery View"""
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by('-created_at')
    albums = GalleryAlbum.objects.filter(is_active=True).order_by('order')
    
    # Group images by category
    categories = {}
    for image in gallery_images:
        category_key = image.category
        if category_key not in categories:
            categories[category_key] = []
        categories[category_key].append(image)
    
    context = {
        'gallery_images': gallery_images,
        'albums': albums,
        'categories': categories,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Gallery', 'url': reverse('gallery:gallery')},
            {'name': 'VR Gallery', 'url': reverse('gallery:vr_gallery')}
        ],
    }
    
    return render(request, 'gallery/vr_gallery.html', context)


def analytics_view(request):
    """Advanced Analytics Dashboard View"""
    from django.db.models import Count, Sum, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        # Get time range filter
        time_range = request.GET.get('time_range', '30d')
        
        # Calculate date filter
        now = timezone.now()
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
        
        # Base queryset
        images_queryset = GalleryImage.objects.filter(is_active=True)
        if start_date:
            images_queryset = images_queryset.filter(created_at__gte=start_date)
        
        # Calculate metrics with error handling
        total_views = images_queryset.aggregate(total=Sum('views_count'))['total'] or 0
        total_likes = images_queryset.aggregate(total=Sum('likes_count'))['total'] or 0
        total_shares = images_queryset.aggregate(total=Sum('shares_count'))['total'] or 0
        
        # Count downloads from related model
        try:
            total_downloads = images_queryset.aggregate(total=Count('downloads'))['total'] or 0
        except Exception:
            total_downloads = 0
        
        # Category distribution
        category_stats = images_queryset.values('category').annotate(
            count=Count('id'),
            total_views=Sum('views_count'),
            avg_quality=Avg('ai_quality_score')
        ).order_by('-count')
        
        # Top performing images
        top_images = images_queryset.annotate(
            engagement_rate=Sum('likes_count') + Sum('shares_count') + Sum('comments_count')
        ).order_by('-views_count')[:10]
        
        # Recent activity
        recent_activity = images_queryset.order_by('-created_at')[:5]
        
        context = {
            'total_views': total_views,
            'total_likes': total_likes,
            'total_shares': total_shares,
            'total_downloads': total_downloads,
            'category_stats': category_stats,
            'top_images': top_images,
            'recent_activity': recent_activity,
            'time_range': time_range,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Gallery', 'url': reverse('gallery:gallery')},
                {'name': 'Analytics', 'url': reverse('gallery:analytics')}
            ],
        }
        
        return render(request, 'gallery/analytics.html', context)
        
    except Exception as e:
        # Fallback context in case of any errors
        context = {
            'total_views': 0,
            'total_likes': 0,
            'total_shares': 0,
            'total_downloads': 0,
            'category_stats': [],
            'top_images': [],
            'recent_activity': [],
            'time_range': '30d',
            'error': str(e),
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Gallery', 'url': reverse('gallery:gallery')},
                {'name': 'Analytics', 'url': reverse('gallery:analytics')}
            ],
        }
        
        return render(request, 'gallery/analytics.html', context)


def album_detail_view(request, album_id):
    """
    Detailed view for a specific album
    """
    try:
        album = GalleryAlbum.objects.get(id=album_id, is_active=True)
        images = album.images.filter(is_active=True).order_by('order', '-created_at')
        
        context = {
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Gallery', 'url': reverse('gallery:gallery')},
                {'name': album.name, 'url': reverse('gallery:album_detail', args=[album_id])}
            ],
            'album': album,
            'images': images,
        }
        
        return render(request, 'gallery/album_detail.html', context)
        
    except GalleryAlbum.DoesNotExist:
        return render(request, 'gallery/404.html', status=404)


@csrf_exempt
@require_POST
def gallery_search_api(request):
    """
    API endpoint for gallery search
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({'images': []})
        
        images = GalleryImage.objects.filter(
            is_active=True
        ).filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        ).select_related('album')[:20]
        
        results = []
        for image in images:
            results.append({
                'id': image.id,
                'title': image.title,
                'description': image.description,
                'image_url': image.image.url,
                'album_name': image.get_album_path(),
                'category': image.get_category_display(),
            })
        
        return JsonResponse({'images': results})
        
    except Exception as e:
        logger.error(f"Error in gallery search: {e}", exc_info=True)
        return JsonResponse({'error': 'Search failed'}, status=500)


@require_GET
def gallery_categories_api(request):
    """
    API endpoint for getting gallery categories with counts
    """
    try:
        categories = GalleryImage.objects.filter(is_active=True).values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        results = []
        for cat in categories:
            category_name = dict(GalleryImage._meta.get_field('category').choices)[cat['category']]
            results.append({
                'key': cat['category'],
                'name': category_name,
                'count': cat['count']
            })
        
        return JsonResponse({'success': True, 'categories': results})
        
    except Exception as e:
        logger.error(f"Error in gallery categories API: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'An error occurred.'}, status=500)


@require_GET
def gallery_albums_api(request):
    """
    API endpoint for getting gallery albums with metadata
    """
    try:
        albums = GalleryAlbum.objects.filter(is_active=True).annotate(
            image_count=Count('images', filter=Q(images__is_active=True))
        ).order_by('order', '-created_at')
        
        results = [{
            'id': album.id,
            'name': album.name,
            'description': album.description,
            'cover_image': album.cover_image.url if album.cover_image else None,
            'image_count': album.image_count,
            'sub_album_count': album.sub_albums.filter(is_active=True).count(),
            'parent_album': album.parent_album.id if album.parent_album else None,
            'is_featured': album.is_featured,
            'created_at': album.created_at.isoformat(),
            'updated_at': album.updated_at.isoformat(),
        } for album in albums]
        
        return JsonResponse({'success': True, 'albums': results})
        
    except Exception as e:
        logger.error(f"Error in gallery albums API: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'An error occurred.'}, status=500)


@csrf_exempt
@require_POST
def gallery_image_analytics(request):
    """
    API endpoint for tracking image views and interactions
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        action = data.get('action')  # 'view', 'download', 'share', 'favorite'
        
        if not image_id or not action:
            return JsonResponse({'success': False, 'message': 'Missing required parameters.'}, status=400)
        
        # Here you would typically save analytics data to a database
        # For now, we'll just log it
        logger.info(f"Image analytics: {action} for image {image_id}")
        
        return JsonResponse({'success': True, 'message': 'Analytics recorded.'})
        
    except Exception as e:
        logger.error(f"Error in gallery analytics API: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'An error occurred.'}, status=500)


@require_GET
def gallery_stats_api(request):
    """
    API endpoint for getting gallery statistics
    """
    try:
        stats = {
            'total_images': GalleryImage.objects.filter(is_active=True).count(),
            'total_albums': GalleryAlbum.objects.filter(is_active=True).count(),
            'featured_images': GalleryImage.objects.filter(is_active=True, is_featured=True).count(),
            'featured_albums': GalleryAlbum.objects.filter(is_active=True, is_featured=True).count(),
            'categories': GalleryImage.objects.filter(is_active=True).values('category').distinct().count(),
            'recent_images': GalleryImage.objects.filter(is_active=True).order_by('-created_at')[:5].count(),
        }
        
        return JsonResponse({'success': True, 'stats': stats})
        
    except Exception as e:
        logger.error(f"Error in gallery stats API: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'An error occurred.'}, status=500)


def smart_collections_view(request):
    """Smart Collections View"""
    collections = SmartCollection.objects.filter(is_active=True).order_by('-is_featured', 'name')
    
    # Get featured collections
    featured_collections = collections.filter(is_featured=True)[:3]
    
    # Get all collections with image counts
    collections_with_counts = []
    for collection in collections:
        collections_with_counts.append({
            'collection': collection,
            'image_count': collection.get_image_count(),
            'images': collection.get_images()[:6]  # Preview images
        })
    
    context = {
        'featured_collections': featured_collections,
        'collections': collections_with_counts,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Gallery', 'url': reverse('gallery:gallery')},
            {'name': 'Smart Collections', 'url': reverse('gallery:smart_collections')}
        ],
    }
    
    return render(request, 'gallery/smart_collections.html', context)


def smart_collection_detail_view(request, collection_id):
    """Smart Collection Detail View"""
    collection = get_object_or_404(SmartCollection, id=collection_id, is_active=True)
    
    # Get images in this collection
    collection_images = collection.get_images()
    
    # Pagination
    paginator = Paginator(collection_images, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'collection': collection,
        'page_obj': page_obj,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Gallery', 'url': reverse('gallery:gallery')},
            {'name': 'Smart Collections', 'url': reverse('gallery:smart_collections')},
            {'name': collection.name, 'url': reverse('gallery:smart_collection_detail', args=[collection.id])}
        ],
    }
    
    return render(request, 'gallery/smart_collection_detail.html', context)


@csrf_exempt
@require_POST
def update_smart_collection_api(request, collection_id):
    """API to update a smart collection"""
    try:
        collection = get_object_or_404(SmartCollection, id=collection_id)
        
        # Update the collection
        updated_count = collection.update_collection()
        
        return JsonResponse({
            'success': True,
            'message': f'Collection updated with {updated_count} images',
            'image_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error updating smart collection: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Error updating collection'
        }, status=500)


@csrf_exempt
@require_POST
def apply_auto_categorization_api(request):
    """API to apply auto-categorization rules to all images"""
    try:
        rules = AutoCategorizationRule.objects.filter(is_active=True, auto_apply=True).order_by('-priority')
        applied_count = 0
        
        for rule in rules:
            images = GalleryImage.objects.filter(is_active=True)
            for image in images:
                if rule.apply_to_image(image):
                    applied_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Applied {applied_count} categorizations',
            'applied_count': applied_count
        })
        
    except Exception as e:
        logger.error(f"Error applying auto-categorization: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Error applying categorization rules'
        }, status=500)


def auto_categorization_view(request):
    """Auto Categorization Management View"""
    rules = AutoCategorizationRule.objects.all().order_by('-priority', 'name')
    
    # Get statistics
    total_rules = rules.count()
    active_rules = rules.filter(is_active=True).count()
    total_applied = sum(rule.times_applied for rule in rules)
    
    context = {
        'rules': rules,
        'total_rules': total_rules,
        'active_rules': active_rules,
        'total_applied': total_applied,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Gallery', 'url': reverse('gallery:gallery')},
            {'name': 'Auto Categorization', 'url': reverse('gallery:auto_categorization')}
        ],
    }
    
    return render(request, 'gallery/auto_categorization.html', context)