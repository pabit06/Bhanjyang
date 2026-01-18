"""
Celery tasks for the About app.

Handles scheduled publishing and content expiration.
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging

from .models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage
)

logger = logging.getLogger(__name__)


@shared_task
def publish_scheduled_content():
    """
    Publish scheduled content that has reached its scheduled_date.
    
    Runs every 5 minutes via Celery Beat.
    Sets published_by to None for automated tasks.
    """
    now = timezone.now()
    published_count = 0
    
    try:
        with transaction.atomic():
            # CooperativeInfo
            cooperative_info = CooperativeInfo.objects.filter(
                status=CooperativeInfo.Status.SCHEDULED,
                scheduled_date__lte=now
            )
            count = cooperative_info.update(
                status=CooperativeInfo.Status.PUBLISHED,
                published_date=now,
                published_by=None  # System published (automated)
            )
            published_count += count
            if count > 0:
                logger.info(f"Published {count} CooperativeInfo item(s)")
            
            # CooperativeTimeline
            timeline_events = CooperativeTimeline.objects.filter(
                status=CooperativeTimeline.Status.SCHEDULED,
                scheduled_date__lte=now
            )
            count = timeline_events.update(
                status=CooperativeTimeline.Status.PUBLISHED,
                published_date=now,
                published_by=None  # System published (automated)
            )
            published_count += count
            if count > 0:
                logger.info(f"Published {count} CooperativeTimeline event(s)")
            
            # CooperativeStatistic
            statistics = CooperativeStatistic.objects.filter(
                status=CooperativeStatistic.Status.SCHEDULED,
                scheduled_date__lte=now
            )
            count = statistics.update(
                status=CooperativeStatistic.Status.PUBLISHED,
                published_date=now,
                published_by=None  # System published (automated)
            )
            published_count += count
            if count > 0:
                logger.info(f"Published {count} CooperativeStatistic item(s)")
            
            # CooperativeAffiliation
            affiliations = CooperativeAffiliation.objects.filter(
                status=CooperativeAffiliation.Status.SCHEDULED,
                scheduled_date__lte=now
            )
            count = affiliations.update(
                status=CooperativeAffiliation.Status.PUBLISHED,
                published_date=now,
                published_by=None  # System published (automated)
            )
            published_count += count
            if count > 0:
                logger.info(f"Published {count} CooperativeAffiliation item(s)")
            
            # LeadershipMessage
            messages = LeadershipMessage.objects.filter(
                status=LeadershipMessage.Status.SCHEDULED,
                scheduled_date__lte=now
            )
            count = messages.update(
                status=LeadershipMessage.Status.PUBLISHED,
                published_date=now,
                published_by=None  # System published (automated)
            )
            published_count += count
            if count > 0:
                logger.info(f"Published {count} LeadershipMessage item(s)")
        
        if published_count > 0:
            logger.info(f"Total published: {published_count} item(s)")
            # Clear cache
            from django.core.cache import cache
            cache.clear()
        
        return published_count
    
    except Exception as e:
        logger.error(f"Error publishing scheduled content: {e}", exc_info=True)
        raise
