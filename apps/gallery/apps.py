from django.apps import AppConfig


class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gallery'
    
    def ready(self):
        """Register gallery admin models with custom admin site"""
        try:
            from apps.admin.admin_site import register_gallery_models
            register_gallery_models()
        except Exception:
            # Registration will be handled at startup
            pass