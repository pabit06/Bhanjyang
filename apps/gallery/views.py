from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
import json
import logging
import time

# Set up logging
logger = logging.getLogger(__name__)

from .models import (
    GalleryImage, GalleryAlbum, GalleryImageLike, GalleryImageComment,
    GalleryImageShare, GalleryImageDownload, SmartCollection, 
    SmartCollectionImage, AutoCategorizationRule, ImageAnalysisJob
)

from .services import GalleryService


def track_page_view(request, page_url, page_title=""):
    """Track page views for analytics with error handling"""
    try:
        # Sanitize inputs
        page_url = page_url[:500] if page_url else ""
        page_title = page_title[:200] if page_title else ""
        user_ip = request.META.get('REMOTE_ADDR', '')[:45]  # IPv6 max length
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        referrer = request.META.get('HTTP_REFERER', '')[:500]
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
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
    [OPTIMIZED] Enhanced gallery view with optimized data fetching to avoid N+1 queries
    """
    track_page_view(request, request.build_absolute_uri(), "Gallery - Bhanjyang Cooperative")
    
    try:
        # All complex logic is handled by the Service
        data = GalleryService.get_optimized_gallery_data()
        
        context = {
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Gallery', 'url': reverse('gallery:gallery')}
            ],
            **data, # Unpack the data from service
            'timestamp': int(time.time()),
        }
        
    except Exception as e:
        logger.error(f"Error fetching gallery data: {e}", exc_info=True)
        # Fallback empty context
        context = {
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Gallery', 'url': reverse('gallery:gallery')}
            ],
            'categories': {},
            'albums': [],
            'root_albums': [],
            'album_images': {},
            'gallery_images': [],
            'timestamp': int(time.time()),
        }
    
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
    try:
        # Get time range filter
        time_range = request.GET.get('time_range', '30d')
        
        # Get analytics data from service
        data = GalleryService.get_analytics_data(time_range)
        
        context = {
            **data,
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
        logger.error(f"Error in analytics view: {e}", exc_info=True)
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


@require_GET
def gallery_search_api(request):
    """
    [UPDATED] API endpoint for gallery search - changed to GET method
    """
    try:
        query = request.GET.get('query', '').strip()
        
        if not query:
            return JsonResponse({'success': True, 'images': []})
        
        images = GalleryImage.objects.filter(
            is_active=True
        ).filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(ai_tags__icontains=query)  # Also search AI tags
        ).select_related('album')[:20]
        
        results = [{
            'id': img.id,
            'title': img.title,
            'description': img.description,
            'image_url': img.image.url,
            'thumbnail_url': img.get_thumbnail_url() if hasattr(img, 'get_thumbnail_url') else img.image.url,
            'album_name': img.album.name if img.album else 'Uncategorized',
            'album_id': img.album.id if img.album else None,
            'category': img.category,
            'category_name': img.get_category_display(),
            'ai_tags': img.ai_tags or [],
            'created_at': img.created_at.isoformat(),
        } for img in images]
        
        return JsonResponse({'success': True, 'images': results})
        
    except Exception as e:
        logger.error(f"Error in gallery search: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Search failed'}, status=500)


@require_GET
def gallery_categories_api(request):
    """
    API endpoint for getting gallery categories with counts
    """
    try:
        categories = GalleryImage.objects.filter(is_active=True).values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        # Get category display names
        category_choices = dict(GalleryImage._meta.get_field('category').choices)
        
        results = []
        for cat in categories:
            if cat['category']:  # Ensure category is not None
                category_name = category_choices.get(cat['category'], cat['category'])
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
            image_count=Count('images', filter=Q(images__is_active=True)),
            sub_album_count=Count('sub_albums', filter=Q(sub_albums__is_active=True))
        ).select_related('parent_album').order_by('order', '-created_at')
        
        results = [{
            'id': album.id,
            'name': album.name,
            'description': album.description,
            'cover_image': album.cover_image.url if album.cover_image else None,
            'image_count': album.image_count,
            'sub_album_count': album.sub_album_count,
            'parent_album': album.parent_album.id if album.parent_album else None,
            'is_featured': album.is_featured,
            'created_at': album.created_at.isoformat(),
            'updated_at': album.updated_at.isoformat(),
        } for album in albums]
        
        return JsonResponse({'success': True, 'albums': results})
        
    except Exception as e:
        logger.error(f"Error in gallery albums API: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'An error occurred.'}, status=500)


@require_POST
def gallery_image_analytics(request):
    """
    [UPDATED] API endpoint for tracking image views and interactions with atomic updates
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        action = data.get('action')  # 'view', 'download', 'share', 'like'
        
        if not image_id or not action:
            return JsonResponse({'success': False, 'message': 'Missing required parameters.'}, status=400)
        
        # Validate action
        allowed_actions = ['view', 'download', 'share', 'like']
        if action not in allowed_actions:
            return JsonResponse({'success': False, 'message': 'Invalid action.'}, status=400)
        
        # Get the image object
        image = get_object_or_404(GalleryImage, id=image_id)
        
        # Get user/session identifiers
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        user_ip = request.META.get('REMOTE_ADDR', '')[:45]
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        with transaction.atomic():
            if action == 'view':
                # Atomically increment view count
                image.views_count = F('views_count') + 1
                image.save(update_fields=['views_count'])
                message = 'View recorded.'
            
            elif action == 'download':
                # Create a download record
                GalleryImageDownload.objects.create(
                    image=image,
                    user_ip=user_ip,
                    user_agent=user_agent,
                    session_id=session_id
                )
                message = 'Download recorded.'
            
            elif action == 'share':
                # Atomically increment share count
                image.shares_count = F('shares_count') + 1
                image.save(update_fields=['shares_count'])
                # Create a share record
                platform = data.get('platform', 'unknown')
                GalleryImageShare.objects.create(
                    image=image,
                    platform=platform,
                    user_ip=user_ip,
                    user_agent=user_agent,
                    session_id=session_id
                )
                message = 'Share recorded.'
            
            elif action == 'like':
                # Toggle: Create a like or delete it
                like_obj, created = GalleryImageLike.objects.get_or_create(
                    image=image,
                    user_ip=user_ip,
                    defaults={
                        'user_agent': user_agent,
                        'session_id': session_id
                    }
                )
                
                if created:
                    # New like - atomically increment
                    image.likes_count = F('likes_count') + 1
                    message = 'Image liked.'
                else:
                    # Already liked, so unlike
                    like_obj.delete()
                    image.likes_count = F('likes_count') - 1
                    message = 'Image unliked.'
                
                image.save(update_fields=['likes_count'])

        # Refresh from DB to get the updated counts
        image.refresh_from_db()
        
        return JsonResponse({
            'success': True, 
            'message': message,
            'view_count': image.views_count,
            'like_count': image.likes_count,
            'share_count': image.shares_count,
        })
        
    except GalleryImage.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Image not found.'}, status=404)
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


@require_POST
def update_smart_collection_api(request, collection_id):
    """API to update a smart collection - requires staff permissions"""
    # Require admin/staff access for security
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
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


@require_POST
def apply_auto_categorization_api(request):
    """API to apply auto-categorization rules to all images - requires staff permissions"""
    # Require admin/staff access for security
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        rules = AutoCategorizationRule.objects.filter(is_active=True, auto_apply=True).order_by('-priority')
        applied_count = 0
        
        # Get all images once
        images = GalleryImage.objects.filter(is_active=True)
        
        with transaction.atomic():  # Run all rule applications in a single transaction
            for rule in rules:
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