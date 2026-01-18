"""
Celery tasks for home app.
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging

from .models import HomePageContent, Testimonial, Statistic, Announcement

logger = logging.getLogger(__name__)


@shared_task
def publish_scheduled_content():
    """
    Publish content that has reached its scheduled_date.
    Runs every 5 minutes via Celery Beat.
    """
    now = timezone.now()
    published_count = 0
    
    try:
        with transaction.atomic():
            # HomePageContent
            homepage_content = HomePageContent.objects.filter(
                status=HomePageContent.Status.SCHEDULED,
                scheduled_date__lte=now
            )
            count = homepage_content.update(
                status=HomePageContent.Status.PUBLISHED,
                published_date=now,
                published_by=None  # System published (automated)
            )
            published_count += count
            if count > 0:
                logger.info(f"Published {count} HomePageContent item(s)")
            
            # Testimonial
            testimonials = Testimonial.objects.filter(
                status=Testimonial.Status.SCHEDULED,
                scheduled_date__lte=now
            )
            count = testimonials.update(
                status=Testimonial.Status.PUBLISHED,
                published_date=now,
                published_by=None  # System published (automated)
            )
            published_count += count
            if count > 0:
                logger.info(f"Published {count} Testimonial(s)")
            
            # Statistic
            statistics = Statistic.objects.filter(
                status=Statistic.Status.SCHEDULED,
                scheduled_date__lte=now
            )
            count = statistics.update(
                status=Statistic.Status.PUBLISHED,
                published_date=now,
                published_by=None  # System published (automated)
            )
            published_count += count
            if count > 0:
                logger.info(f"Published {count} Statistic(s)")
            
            # Announcement
            announcements = Announcement.objects.filter(
                status=Announcement.Status.SCHEDULED,
                scheduled_date__lte=now
            )
            count = announcements.update(
                status=Announcement.Status.PUBLISHED,
                published_date=now,
                published_by=None  # System published (automated)
            )
            published_count += count
            if count > 0:
                logger.info(f"Published {count} Announcement(s)")
        
        if published_count > 0:
            logger.info(f"Total published: {published_count} item(s)")
            # Clear cache after publishing
            from django.core.cache import cache
            cache.clear()
        
        return published_count
        
    except Exception as e:
        logger.error(f"Error publishing scheduled content: {e}", exc_info=True)
        raise


@shared_task
def expire_content():
    """
    Archive content that has reached its expiry_date.
    Runs every 5 minutes via Celery Beat (same schedule as publish).
    """
    now = timezone.now()
    expired_count = 0
    
    try:
        with transaction.atomic():
            # Announcements with auto_expire enabled
            expired_announcements = Announcement.objects.filter(
                status=Announcement.Status.PUBLISHED,
                auto_expire=True,
                expiry_date__isnull=False,
                expiry_date__lte=now
            )
            count = expired_announcements.update(
                status=Announcement.Status.ARCHIVED
            )
            expired_count += count
            if count > 0:
                logger.info(f"Expired {count} Announcement(s)")
        
        if expired_count > 0:
            logger.info(f"Total expired: {expired_count} item(s)")
            # Clear cache after expiring
            from django.core.cache import cache
            cache.clear()
        
        return expired_count
        
    except Exception as e:
        logger.error(f"Error expiring content: {e}", exc_info=True)
        raise
