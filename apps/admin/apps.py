from django.apps import AppConfig


class AdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin'
    label = 'bhanjyang_admin'  # Custom label to avoid conflict with django.contrib.admin
    verbose_name = 'Admin Customization'
    
    def ready(self):
        """Called when Django starts"""
        # Register gallery models with custom admin site
        from .admin_site import register_gallery_models
        register_gallery_models()

