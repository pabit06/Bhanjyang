"""
Register gallery models with the custom admin site
"""
from django.apps import AppConfig
from apps.core.admin_site import admin_site
from .models import GalleryImage, GalleryAlbum
from .admin import GalleryImageAdmin, GalleryAlbumAdmin


class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'
    
    def ready(self):
        """Register models with custom admin site when app is ready"""
        # Unregister from default admin site
        from django.contrib import admin
        admin.site.unregister(GalleryImage)
        admin.site.unregister(GalleryAlbum)
        
        # Register with custom admin site
        admin_site.register(GalleryImage, GalleryImageAdmin)
        admin_site.register(GalleryAlbum, GalleryAlbumAdmin)
