from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .services import GalleryService
from .models import GalleryAlbum, SmartCollection

# --- Class-Based Views (CBVs) for Pages ---

class GalleryHomeView(TemplateView):
    """Main Gallery Page displaying optimized grid"""
    template_name = 'gallery/gallery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(GalleryService.get_gallery_home_data())
        return context

class VRGalleryView(TemplateView):
    """Virtual Reality Gallery Experience"""
    template_name = 'gallery/vr_gallery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(GalleryService.get_vr_gallery_data())
        return context

class AlbumDetailView(DetailView):
    model = GalleryAlbum
    template_name = 'gallery/album_detail.html'
    context_object_name = 'album'
    pk_url_kwarg = 'album_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_data = GalleryService.get_album_detail(self.object.id)
        context['images'] = service_data['images']
        return context

class GalleryAnalyticsRawView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Standard Django Template View for internal Staff Analytics"""
    template_name = 'gallery/analytics.html'

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(GalleryService.get_analytics_data())
        return context

class SmartCollectionsView(TemplateView):
    template_name = 'gallery/smart_collections.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(GalleryService.get_smart_collections())
        return context

class SmartCollectionDetailView(DetailView):
    model = SmartCollection
    template_name = 'gallery/smart_collection_detail.html'
    context_object_name = 'collection'
    pk_url_kwarg = 'collection_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.get_images()
        return context

class AutoCategorizationView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'gallery/auto_categorization.html'
    
    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


# --- API Views (Using DRF for consistency) ---

class GallerySearchAPI(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        parameters=[OpenApiParameter(name='q', type=str, description='Search Query')],
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request):
        query = request.GET.get('q', '').strip()
        results = GalleryService.search_images(query)
        return Response({'results': results, 'count': len(results)})

class GalleryStatsAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        time_range = request.GET.get('time_range', '30d')
        return Response(GalleryService.get_analytics_data(time_range))

class GalleryInteractionAPI(APIView):
    """API to record likes, shares, downloads"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        image_id = request.data.get('image_id')
        action = request.data.get('action')
        
        if not image_id or not action:
            return Response({'error': 'Missing parameters'}, status=400)
            
        meta = {
            'ip': request.META.get('REMOTE_ADDR') or '',
            'ua': request.META.get('HTTP_USER_AGENT') or '',
            'session_id': request.session.session_key or '',
            'platform': request.data.get('platform', 'web')
        }
        
        try:
            result = GalleryService.record_interaction(image_id, action, meta)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class UpdateSmartCollectionAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, collection_id):
        try:
            count = GalleryService.update_smart_collection(collection_id, request.user)
            return Response({'success': True, 'updated_count': count})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class ApplyAutoCategorizationAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            count = GalleryService.apply_auto_categorization(request.user)
            return Response({'success': True, 'processed': count})
        except Exception as e:
            return Response({'error': str(e)}, status=500)