from django.apps import AppConfig


class AboutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.about'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.about.signals  # noqa
    verbose_name = 'About Us'
    
    def ready(self):
        """App initialization when Django starts."""
        # Signal handlers can be imported here if needed in the future
        pass
