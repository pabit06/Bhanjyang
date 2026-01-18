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
                published_date=now
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
                published_date=now
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
                published_date=now
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
                published_date=now
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
