"""
Django signals for the About app.

Handles cache invalidation when content is published or updated.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage
)


def clear_about_cache():
    """Clear all about app related caches"""
    try:
        # Clear specific cache keys
        cache.delete_pattern('about_*')
        # Also clear general cache as fallback
        cache.clear()
    except Exception:
        # If cache backend doesn't support delete_pattern, just clear all
        cache.clear()


@receiver(post_save, sender=CooperativeInfo)
@receiver(post_save, sender=CooperativeTimeline)
@receiver(post_save, sender=CooperativeStatistic)
@receiver(post_save, sender=CooperativeAffiliation)
@receiver(post_save, sender=LeadershipMessage)
def invalidate_about_cache_on_save(sender, instance, **kwargs):
    """Clear cache when content is saved"""
    clear_about_cache()


@receiver(post_delete, sender=CooperativeInfo)
@receiver(post_delete, sender=CooperativeTimeline)
@receiver(post_delete, sender=CooperativeStatistic)
@receiver(post_delete, sender=CooperativeAffiliation)
@receiver(post_delete, sender=LeadershipMessage)
def invalidate_about_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when content is deleted"""
    clear_about_cache()
