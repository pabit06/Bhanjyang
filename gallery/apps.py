from django.apps import AppConfig


class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'
    
    def ready(self):
        """Import admin registration when app is ready"""
        try:
            import gallery.admin_registration
        except ImportError:
            pass