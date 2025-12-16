from django.db import models
from django.utils import timezone
from django.db.models import Q

class ArticleManager(models.Manager):
    """Custom manager for NewsArticle"""
    
    def published(self):
        """Return published articles"""
        from .models import NewsArticle  # Avoid circular import
        return self.filter(status=NewsArticle.Status.PUBLISHED, published_date__lte=timezone.now())
    
    def featured(self):
        """Return featured published articles"""
        return self.published().filter(is_featured=True)
    
    def recent(self):
        """Return recent published articles"""
        return self.published().order_by('-published_date')

class EventManager(models.Manager):
    """Custom manager for Event"""
    
    def published(self):
        """Return published events"""
        from .models import Event  # Avoid circular import
        return self.filter(status=Event.Status.PUBLISHED)
    
    def upcoming(self):
        """Return upcoming published events"""
        return self.published().filter(event_date__gt=timezone.now()).order_by('event_date')
    
    def past(self):
        """Return past published events"""
        return self.published().filter(event_date__lte=timezone.now()).order_by('-event_date')
    
    def featured(self):
        """Return featured published upcoming events"""
        return self.upcoming().filter(is_featured=True)
