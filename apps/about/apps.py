from django.apps import AppConfig


class AboutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.about'
    verbose_name = 'About Us'
    
    def ready(self):
        """App initialization when Django starts."""
        # Signal handlers can be imported here if needed in the future
        pass
