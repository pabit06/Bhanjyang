"""
Django signals for home app.
Handles cache invalidation and audit logging.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
import logging

from .models import HomePageContent, Testimonial, Statistic, Announcement

logger = logging.getLogger(__name__)


def clear_home_cache():
    """Clear all home page related cache"""
    try:
        # Clear homepage cache
        cache.delete('home_context')
        cache.delete('homepage_content')
        cache.delete('featured_testimonials')
        cache.delete('featured_statistics')
        cache.delete('featured_announcements')
        
        # Clear API cache
        cache.delete('api_statistics')
        cache.delete('api_testimonials')
        
        # Clear pattern-based cache (if using redis)
        try:
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern('home:*')
                cache.delete_pattern('api:*')
        except AttributeError:
            # delete_pattern not available (not using redis)
            pass
        
        logger.info("Home page cache cleared")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")


@receiver(post_save, sender=HomePageContent)
def homepage_content_saved(sender, instance, created, **kwargs):
    """Clear cache when homepage content is saved"""
    if instance.status == HomePageContent.Status.PUBLISHED:
        clear_home_cache()
        logger.info(f"Cache cleared after HomePageContent {instance.pk} was published")


@receiver(post_save, sender=Testimonial)
def testimonial_saved(sender, instance, created, **kwargs):
    """Clear cache when testimonial is saved"""
    if instance.status == Testimonial.Status.PUBLISHED:
        clear_home_cache()
        logger.info(f"Cache cleared after Testimonial {instance.pk} was published")


@receiver(post_save, sender=Statistic)
def statistic_saved(sender, instance, created, **kwargs):
    """Clear cache when statistic is saved"""
    if instance.status == Statistic.Status.PUBLISHED:
        clear_home_cache()
        logger.info(f"Cache cleared after Statistic {instance.pk} was published")


@receiver(post_save, sender=Announcement)
def announcement_saved(sender, instance, created, **kwargs):
    """Clear cache when announcement is saved"""
    if instance.status == Announcement.Status.PUBLISHED:
        clear_home_cache()
        logger.info(f"Cache cleared after Announcement {instance.pk} was published")


@receiver(post_delete, sender=HomePageContent)
def homepage_content_deleted(sender, instance, **kwargs):
    """Clear cache when homepage content is deleted"""
    clear_home_cache()
    logger.info(f"Cache cleared after HomePageContent {instance.pk} was deleted")


@receiver(post_delete, sender=Testimonial)
def testimonial_deleted(sender, instance, **kwargs):
    """Clear cache when testimonial is deleted"""
    clear_home_cache()
    logger.info(f"Cache cleared after Testimonial {instance.pk} was deleted")


@receiver(post_delete, sender=Statistic)
def statistic_deleted(sender, instance, **kwargs):
    """Clear cache when statistic is deleted"""
    clear_home_cache()
    logger.info(f"Cache cleared after Statistic {instance.pk} was deleted")


@receiver(post_delete, sender=Announcement)
def announcement_deleted(sender, instance, **kwargs):
    """Clear cache when announcement is deleted"""
    clear_home_cache()
    logger.info(f"Cache cleared after Announcement {instance.pk} was deleted")
