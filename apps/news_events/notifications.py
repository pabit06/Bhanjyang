"""
Real-time Notifications for News Events App.

Provides notification system for new articles, events, and comments.
"""
from typing import Dict, Any, List, Optional
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
import logging
import json

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationType(models.TextChoices):
    """Notification type choices."""
    NEW_ARTICLE = 'NEW_ARTICLE', 'New Article Published'
    NEW_EVENT = 'NEW_EVENT', 'New Event Published'
    NEW_COMMENT = 'NEW_COMMENT', 'New Comment'
    COMMENT_REPLY = 'COMMENT_REPLY', 'Comment Reply'
    NEWSLETTER = 'NEWSLETTER', 'Newsletter Sent'
    EVENT_REMINDER = 'EVENT_REMINDER', 'Event Reminder'


class NotificationService:
    """Service for managing notifications."""
    
    @staticmethod
    def create_notification(
        notification_type: str,
        title: str,
        message: str,
        url: Optional[str] = None,
        user: Optional[User] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a notification.
        
        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            url: Optional URL to related content
            user: Optional specific user to notify
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with notification data
        """
        notification = {
            'id': f"{notification_type}_{timezone.now().timestamp()}",
            'type': notification_type,
            'title': title,
            'message': message,
            'url': url,
            'timestamp': timezone.now().isoformat(),
            'read': False,
            'metadata': metadata or {}
        }
        
        # Store in cache for real-time delivery
        if user:
            cache_key = f"notifications_user_{user.id}"
            notifications = cache.get(cache_key, [])
            notifications.append(notification)
            # Keep only last 50 notifications
            notifications = notifications[-50:]
            cache.set(cache_key, notifications, timeout=86400)  # 24 hours
        
        # Also store globally for broadcast
        cache_key_global = f"notifications_global_{notification_type}"
        global_notifications = cache.get(cache_key_global, [])
        global_notifications.append(notification)
        global_notifications = global_notifications[-20:]
        cache.set(cache_key_global, global_notifications, timeout=3600)  # 1 hour
        
        logger.info(f"Notification created: {notification_type} - {title}")
        return notification
    
    @staticmethod
    def notify_new_article(article) -> Dict[str, Any]:
        """
        Create notification for new article.
        
        Args:
            article: NewsArticle instance
            
        Returns:
            Notification dictionary
        """
        from django.urls import reverse
        
        url = reverse('news_events:article-detail', kwargs={'slug': article.slug})
        
        return NotificationService.create_notification(
            notification_type=NotificationType.NEW_ARTICLE,
            title='New Article Published',
            message=f"{article.title} has been published",
            url=url,
            metadata={
                'article_id': article.id,
                'article_slug': article.slug,
                'category': article.category.name if article.category else None
            }
        )
    
    @staticmethod
    def notify_new_event(event) -> Dict[str, Any]:
        """
        Create notification for new event.
        
        Args:
            event: Event instance
            
        Returns:
            Notification dictionary
        """
        from django.urls import reverse
        
        url = reverse('news_events:event-detail', kwargs={'slug': event.slug})
        
        return NotificationService.create_notification(
            notification_type=NotificationType.NEW_EVENT,
            title='New Event Published',
            message=f"{event.title} - {event.event_date.strftime('%B %d, %Y')}",
            url=url,
            metadata={
                'event_id': event.id,
                'event_slug': event.slug,
                'event_date': event.event_date.isoformat()
            }
        )
    
    @staticmethod
    def notify_new_comment(comment, article) -> Dict[str, Any]:
        """
        Create notification for new comment.
        
        Args:
            comment: Comment instance
            article: NewsArticle instance
            
        Returns:
            Notification dictionary
        """
        from django.urls import reverse
        
        url = reverse('news_events:article-detail', kwargs={'slug': article.slug})
        
        return NotificationService.create_notification(
            notification_type=NotificationType.NEW_COMMENT,
            title='New Comment',
            message=f"{comment.author_name} commented on {article.title}",
            url=url,
            metadata={
                'comment_id': comment.id,
                'article_id': article.id,
                'author_name': comment.author_name
            }
        )
    
    @staticmethod
    def get_user_notifications(user: User, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.
        
        Args:
            user: User instance
            limit: Maximum number of notifications
            
        Returns:
            List of notification dictionaries
        """
        cache_key = f"notifications_user_{user.id}"
        notifications = cache.get(cache_key, [])
        return notifications[-limit:]
    
    @staticmethod
    def get_unread_count(user: User) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user: User instance
            
        Returns:
            Number of unread notifications
        """
        notifications = NotificationService.get_user_notifications(user)
        return sum(1 for n in notifications if not n.get('read', False))
    
    @staticmethod
    def mark_as_read(user: User, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            user: User instance
            notification_id: Notification ID
            
        Returns:
            True if marked successfully
        """
        cache_key = f"notifications_user_{user.id}"
        notifications = cache.get(cache_key, [])
        
        for notification in notifications:
            if notification.get('id') == notification_id:
                notification['read'] = True
                cache.set(cache_key, notifications, timeout=86400)
                return True
        
        return False
    
    @staticmethod
    def mark_all_as_read(user: User) -> bool:
        """
        Mark all notifications as read for a user.
        
        Args:
            user: User instance
            
        Returns:
            True if marked successfully
        """
        cache_key = f"notifications_user_{user.id}"
        notifications = cache.get(cache_key, [])
        
        for notification in notifications:
            notification['read'] = True
        
        cache.set(cache_key, notifications, timeout=86400)
        return True
    
    @staticmethod
    def get_global_notifications(notification_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get global notifications (for all users).
        
        Args:
            notification_type: Optional filter by type
            limit: Maximum number of notifications
            
        Returns:
            List of notification dictionaries
        """
        if notification_type:
            cache_key = f"notifications_global_{notification_type}"
            notifications = cache.get(cache_key, [])
            return notifications[-limit:]
        else:
            # Get from all types
            all_notifications = []
            for ntype in NotificationType.values:
                cache_key = f"notifications_global_{ntype}"
                notifications = cache.get(cache_key, [])
                all_notifications.extend(notifications)
            
            # Sort by timestamp and return latest
            all_notifications.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return all_notifications[:limit]

