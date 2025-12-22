from django.apps import AppConfig


class AboutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.about'
    verbose_name = 'About Us'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        # Import signals if needed
        try:
            from . import signals  # noqa: F401
        except ImportError:
            pass
