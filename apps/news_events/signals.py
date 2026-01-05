"""
Signals for News Events App.

Handles notifications and other post-save/post-delete actions.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import NewsArticle, Event, Comment
from .notifications import NotificationService, NotificationType

logger = logging.getLogger(__name__)


@receiver(post_save, sender=NewsArticle)
def notify_new_article(sender, instance, created, **kwargs):
    """Send notification when new article is published."""
    if created and instance.status == NewsArticle.Status.PUBLISHED:
        try:
            NotificationService.notify_new_article(instance)
            logger.info(f"Notification created for new article: {instance.title}")
        except Exception as e:
            logger.error(f"Error creating notification for article {instance.id}: {e}")


@receiver(post_save, sender=Event)
def notify_new_event(sender, instance, created, **kwargs):
    """Send notification when new event is published."""
    if created and instance.status == Event.Status.PUBLISHED:
        try:
            NotificationService.notify_new_event(instance)
            logger.info(f"Notification created for new event: {instance.title}")
        except Exception as e:
            logger.error(f"Error creating notification for event {instance.id}: {e}")


@receiver(post_save, sender=Comment)
def notify_new_comment(sender, instance, created, **kwargs):
    """Send notification when new comment is approved."""
    if created and instance.is_approved and instance.article:
        try:
            NotificationService.notify_new_comment(instance, instance.article)
            logger.info(f"Notification created for new comment on article {instance.article.id}")
        except Exception as e:
            logger.error(f"Error creating notification for comment {instance.id}: {e}")

