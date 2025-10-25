# news_events/apps.py

from django.apps import AppConfig

class NewsEventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.news_events'
    verbose_name = 'News & Events'
    
    def ready(self):
        """Initialize app when ready"""
        # Import signal handlers
        try:
            import apps.news_events.signals
        except ImportError:
            pass
