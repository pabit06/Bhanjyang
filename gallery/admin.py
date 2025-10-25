from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
import os
from PIL import Image
from .models import (
    GalleryImage, GalleryAlbum, GalleryImageLike, GalleryImageComment, 
    GalleryImageShare, GalleryImageDownload, SmartCollection, 
    SmartCollectionImage, AutoCategorizationRule, ImageAnalysisJob
)


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_path', 'get_image_count', 'get_sub_album_count', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active', 'created_at', 'parent_album']
    search_fields = ['name', 'description']
    list_editable = ['is_featured', 'is_active']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Album Information', {
            'fields': ('name', 'description', 'cover_image', 'parent_album')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )
    
    def get_path(self, obj):
        return obj.get_path()
    get_path.short_description = "Path"
    
    def get_image_count(self, obj):
        return obj.get_image_count()
    get_image_count.short_description = "Images"
    
    def get_sub_album_count(self, obj):
        return obj.get_sub_album_count()
    get_sub_album_count.short_description = "Sub-albums"


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'category', 'image_preview', 'file_size', 'dimensions', 'is_featured', 'is_active']
    list_filter = ['album', 'category', 'is_featured', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_featured', 'is_active']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('title', 'description', 'image', 'album', 'category')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )
    
    actions = [
        'bulk_upload_images', 'mark_as_featured', 'mark_as_unfeatured', 
        'mark_as_active', 'mark_as_inactive', 'optimize_images', 'optimize_for_mobile',
        'generate_thumbnails', 'assign_to_album'
    ]
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['bulk_upload_url'] = reverse('admin:gallery_bulk_upload')
        extra_context['drag_drop_url'] = reverse('admin:gallery_drag_drop_upload')
        extra_context['batch_operations_url'] = reverse('admin:gallery_batch_operations')
        extra_context['show_bulk_upload'] = True
        return super().changelist_view(request, extra_context)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = "Preview"
    
    def file_size(self, obj):
        size_mb = obj.get_file_size_mb()
        return f"{size_mb:.2f} MB"
    file_size.short_description = "File Size"
    
    def dimensions(self, obj):
        width, height = obj.get_image_dimensions()
        return f"{width} x {height}"
    dimensions.short_description = "Dimensions"
    
    def bulk_upload_images(self, request, queryset):
        """Redirect to bulk upload page"""
        return redirect('admin:gallery_bulk_upload')
    bulk_upload_images.short_description = "Bulk Upload Images"
    bulk_upload_images.allowed_permissions = ('add',)
    bulk_upload_images.requires_model_perms = False
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} images marked as featured.")
    mark_as_featured.short_description = "Mark selected images as featured"
    
    def mark_as_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} images marked as unfeatured.")
    mark_as_unfeatured.short_description = "Mark selected images as unfeatured"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} images marked as active.")
    mark_as_active.short_description = "Mark selected images as active"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} images marked as inactive.")
    mark_as_inactive.short_description = "Mark selected images as inactive"
    
    def optimize_images(self, request, queryset):
        """Optimize selected images"""
        optimized_count = 0
        for image_obj in queryset:
            if image_obj.image:
                try:
                    # Open and optimize the image
                    img_path = image_obj.image.path
                    with Image.open(img_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        
                        # Save with optimization
                        img.save(img_path, 'JPEG', quality=85, optimize=True)
                        optimized_count += 1
                except Exception as e:
                    self.message_user(request, f"Error optimizing {image_obj.title}: {str(e)}", level=messages.ERROR)
        
        self.message_user(request, f"{optimized_count} images optimized successfully.")
    optimize_images.short_description = "Optimize selected images"
    
    def optimize_for_mobile(self, request, queryset):
        """Optimize selected images specifically for mobile devices"""
        optimized_count = 0
        for image_obj in queryset:
            try:
                mobile_path = image_obj.optimize_image_for_mobile()
                if mobile_path:
                    optimized_count += 1
            except Exception as e:
                self.message_user(request, f"Error optimizing {image_obj.title} for mobile: {str(e)}", level=messages.ERROR)
        
        if optimized_count > 0:
            self.message_user(request, f"Successfully optimized {optimized_count} images for mobile devices.")
        else:
            self.message_user(request, "No images were optimized for mobile.", level=messages.WARNING)
    optimize_for_mobile.short_description = "Optimize for Mobile"
    
    def generate_thumbnails(self, request, queryset):
        """Generate thumbnails for selected images"""
        thumbnail_count = 0
        for image_obj in queryset:
            try:
                thumbnail_url = image_obj.get_thumbnail_url()
                if thumbnail_url:
                    thumbnail_count += 1
            except Exception as e:
                self.message_user(request, f"Error generating thumbnail for {image_obj.title}: {str(e)}", level=messages.ERROR)
        
        if thumbnail_count > 0:
            self.message_user(request, f"Successfully generated {thumbnail_count} thumbnails.")
        else:
            self.message_user(request, "No thumbnails were generated.", level=messages.WARNING)
    generate_thumbnails.short_description = "Generate Thumbnails"
    
    def assign_to_album(self, request, queryset):
        """Assign selected images to an album"""
        if request.POST.get('album_id'):
            album_id = request.POST.get('album_id')
            album = GalleryAlbum.objects.get(id=album_id)
            queryset.update(album=album)
            self.message_user(request, f"{queryset.count()} images assigned to album '{album.name}'.")
        else:
            # Show album selection form
            albums = GalleryAlbum.objects.filter(is_active=True)
            return render(request, 'admin/gallery/assign_album.html', {
                'albums': albums,
                'selected_images': queryset,
                'title': 'Assign Images to Album'
            })
    assign_to_album.short_description = "Assign to album"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='gallery_bulk_upload'),
            path('drag-drop-upload/', self.admin_site.admin_view(self.drag_drop_upload), name='gallery_drag_drop_upload'),
            path('batch-operations/', self.admin_site.admin_view(self.batch_operations_view), name='gallery_batch_operations'),
        ]
        return custom_urls + urls
    
    def bulk_upload_view(self, request):
        """Bulk upload view with drag-and-drop interface"""
        if request.method == 'POST':
            return self.handle_bulk_upload(request)
        
        albums = GalleryAlbum.objects.filter(is_active=True)
        return render(request, 'admin/gallery/bulk_upload.html', {
            'albums': albums,
            'title': 'Bulk Upload Gallery Images'
        })
    
    def handle_bulk_upload(self, request):
        """Handle bulk upload of images"""
        try:
            uploaded_files = request.FILES.getlist('images')
            album_id = request.POST.get('album')
            category = request.POST.get('category', 'events')
            is_featured = request.POST.get('is_featured') == 'on'
            
            album = None
            if album_id:
                album = GalleryAlbum.objects.get(id=album_id)
            
            created_count = 0
            with transaction.atomic():
                for i, file in enumerate(uploaded_files):
                    # Generate title from filename
                    title = os.path.splitext(file.name)[0].replace('_', ' ').title()
                    
                    # Create GalleryImage instance
                    gallery_image = GalleryImage.objects.create(
                        title=title,
                        image=file,
                        album=album,
                        category=category,
                        is_featured=is_featured,
                        order=i
                    )
                    created_count += 1
            
            messages.success(request, f"Successfully uploaded {created_count} images.")
            return redirect('admin:gallery_galleryimage_changelist')
            
        except Exception as e:
            messages.error(request, f"Error uploading images: {str(e)}")
            return redirect('admin:gallery_bulk_upload')
    
    @method_decorator(csrf_exempt)
    def drag_drop_upload(self, request):
        """Handle drag-and-drop upload via AJAX"""
        if request.method == 'POST':
            try:
                files = request.FILES.getlist('files')
                album_id = request.POST.get('album_id')
                category = request.POST.get('category', 'events')
                
                album = None
                if album_id:
                    album = GalleryAlbum.objects.get(id=album_id)
                
                uploaded_images = []
                with transaction.atomic():
                    for i, file in enumerate(files):
                        title = os.path.splitext(file.name)[0].replace('_', ' ').title()
                        
                        gallery_image = GalleryImage.objects.create(
                            title=title,
                            image=file,
                            album=album,
                            category=category,
                            order=i
                        )
                        uploaded_images.append({
                            'id': gallery_image.id,
                            'title': gallery_image.title,
                            'url': gallery_image.image.url,
                            'thumbnail': gallery_image.image.url
                        })
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully uploaded {len(files)} images',
                    'images': uploaded_images
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error uploading images: {str(e)}'
                })
        
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    def batch_operations_view(self, request):
        """Batch operations view for existing images"""
        if request.method == 'POST':
            return self.handle_batch_operations(request)
        
        images = GalleryImage.objects.all()
        albums = GalleryAlbum.objects.filter(is_active=True)
        return render(request, 'admin/gallery/batch_operations.html', {
            'images': images,
            'albums': albums,
            'title': 'Batch Operations'
        })
    
    def handle_batch_operations(self, request):
        """Handle batch operations on images"""
        try:
            operation = request.POST.get('operation')
            image_ids = request.POST.getlist('image_ids')
            queryset = GalleryImage.objects.filter(id__in=image_ids)
            
            if operation == 'assign_album':
                album_id = request.POST.get('album_id')
                if album_id:
                    album = GalleryAlbum.objects.get(id=album_id)
                    queryset.update(album=album)
                    messages.success(request, f"Assigned {queryset.count()} images to album '{album.name}'.")
            
            elif operation == 'change_category':
                category = request.POST.get('category')
                queryset.update(category=category)
                messages.success(request, f"Updated category for {queryset.count()} images.")
            
            elif operation == 'toggle_featured':
                featured_status = request.POST.get('featured_status') == 'true'
                queryset.update(is_featured=featured_status)
                status_text = "featured" if featured_status else "unfeatured"
                messages.success(request, f"Marked {queryset.count()} images as {status_text}.")
            
            elif operation == 'toggle_active':
                active_status = request.POST.get('active_status') == 'true'
                queryset.update(is_active=active_status)
                status_text = "active" if active_status else "inactive"
                messages.success(request, f"Marked {queryset.count()} images as {status_text}.")
            
            elif operation == 'optimize':
                optimized_count = 0
                for image_obj in queryset:
                    if image_obj.image:
                        try:
                            img_path = image_obj.image.path
                            with Image.open(img_path) as img:
                                if img.mode in ('RGBA', 'LA', 'P'):
                                    img = img.convert('RGB')
                                img.save(img_path, 'JPEG', quality=85, optimize=True)
                                optimized_count += 1
                        except Exception as e:
                            messages.error(request, f"Error optimizing {image_obj.title}: {str(e)}")
                
                messages.success(request, f"Optimized {optimized_count} images.")
            
            elif operation == 'delete':
                count = queryset.count()
                queryset.delete()
                messages.success(request, f"Deleted {count} images.")
            
            return redirect('admin:gallery_batch_operations')
            
        except Exception as e:
            messages.error(request, f"Error performing batch operation: {str(e)}")
            return redirect('admin:gallery_batch_operations')


# Smart Collections Admin
@admin.register(SmartCollection)
class SmartCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_image_count', 'is_featured', 'is_active', 'auto_update', 'last_updated']
    list_filter = ['is_featured', 'is_active', 'auto_update', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_featured', 'is_active', 'auto_update']
    ordering = ['-is_featured', 'name']
    
    fieldsets = (
        ('Collection Information', {
            'fields': ('name', 'description')
        }),
        ('AI Criteria', {
            'fields': ('ai_tags', 'ai_objects', 'ai_scene_type', 'ai_sentiment', 'ai_color_palette', 'min_quality_score'),
            'classes': ('collapse',)
        }),
        ('Collection Settings', {
            'fields': ('is_featured', 'is_active', 'auto_update', 'max_images')
        }),
        ('Statistics', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['update_collections', 'mark_as_featured', 'mark_as_unfeatured']
    
    def get_image_count(self, obj):
        return obj.get_image_count()
    get_image_count.short_description = "Images"
    
    def update_collections(self, request, queryset):
        """Update selected smart collections"""
        updated_count = 0
        for collection in queryset:
            try:
                count = collection.update_collection()
                updated_count += count
            except Exception as e:
                self.message_user(request, f"Error updating {collection.name}: {str(e)}", level=messages.ERROR)
        
        if updated_count > 0:
            self.message_user(request, f"Successfully updated {updated_count} images across {queryset.count()} collections.")
        else:
            self.message_user(request, "No collections were updated.", level=messages.WARNING)
    update_collections.short_description = "Update Collections"
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} collections marked as featured.")
    mark_as_featured.short_description = "Mark as Featured"
    
    def mark_as_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} collections marked as unfeatured.")
    mark_as_unfeatured.short_description = "Mark as Unfeatured"


@admin.register(SmartCollectionImage)
class SmartCollectionImageAdmin(admin.ModelAdmin):
    list_display = ['collection', 'image', 'match_score', 'added_at']
    list_filter = ['collection', 'added_at']
    search_fields = ['collection__name', 'image__title']
    ordering = ['-match_score', '-added_at']
    readonly_fields = ['added_at']


@admin.register(AutoCategorizationRule)
class AutoCategorizationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_category', 'priority', 'is_active', 'times_applied', 'last_applied']
    list_filter = ['target_category', 'is_active', 'auto_apply', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['priority', 'is_active']
    ordering = ['-priority', 'name']
    
    fieldsets = (
        ('Rule Information', {
            'fields': ('name', 'description', 'priority')
        }),
        ('Conditions', {
            'fields': ('ai_tags', 'ai_objects', 'ai_scene_type', 'ai_sentiment', 'min_quality_score'),
            'classes': ('collapse',)
        }),
        ('Actions', {
            'fields': ('target_category', 'target_album', 'mark_featured')
        }),
        ('Settings', {
            'fields': ('is_active', 'auto_apply')
        }),
        ('Statistics', {
            'fields': ('times_applied', 'last_applied'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['apply_to_all_images', 'mark_as_active', 'mark_as_inactive']
    
    def apply_to_all_images(self, request, queryset):
        """Apply selected rules to all images"""
        applied_count = 0
        for rule in queryset:
            if not rule.is_active:
                continue
            
            images = GalleryImage.objects.filter(is_active=True)
            for image in images:
                if rule.apply_to_image(image):
                    applied_count += 1
        
        if applied_count > 0:
            self.message_user(request, f"Successfully applied rules to {applied_count} images.")
        else:
            self.message_user(request, "No rules were applied.", level=messages.WARNING)
    apply_to_all_images.short_description = "Apply to All Images"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} rules marked as active.")
    mark_as_active.short_description = "Mark as Active"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} rules marked as inactive.")
    mark_as_inactive.short_description = "Mark as Inactive"


@admin.register(ImageAnalysisJob)
class ImageAnalysisJobAdmin(admin.ModelAdmin):
    list_display = ['image', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['image__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('image', 'status', 'error_message')
        }),
        ('Analysis Data', {
            'fields': ('analysis_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['retry_failed_jobs', 'mark_as_completed']
    
    def retry_failed_jobs(self, request, queryset):
        """Retry failed analysis jobs"""
        failed_jobs = queryset.filter(status='failed')
        failed_jobs.update(status='pending', error_message='')
        self.message_user(request, f"{failed_jobs.count()} jobs marked for retry.")
    retry_failed_jobs.short_description = "Retry Failed Jobs"
    
    def mark_as_completed(self, request, queryset):
        """Mark jobs as completed"""
        from django.utils import timezone
        queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} jobs marked as completed.")
    mark_as_completed.short_description = "Mark as Completed"


# Custom admin site configuration
admin.site.site_header = "Bhanjyang Cooperative Admin"
admin.site.site_title = "Bhanjyang Admin"
admin.site.index_title = "Welcome to Bhanjyang Cooperative Administration"