"""
Background tasks for the News Events app.

This module contains Celery tasks for sending newsletters asynchronously.
This prevents blocking the request/response cycle when sending to many subscribers.
"""
import logging
from typing import List, Dict, Any
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from .models import Newsletter, Subscriber

logger = logging.getLogger(__name__)

# Celery configuration - check if Celery is available
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create a no-op decorator when Celery is not available
    def shared_task(*args, **kwargs):
        """No-op decorator when Celery is not installed"""
        def decorator(func):
            return func
        return decorator


@shared_task(bind=True, max_retries=3)
def send_newsletter_email(self, newsletter_id: int, subscriber_id: int):
    """
    Send newsletter email to a single subscriber.
    This task is called for each subscriber to enable parallel processing.
    
    Args:
        newsletter_id: ID of the Newsletter object
        subscriber_id: ID of the Subscriber object
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        newsletter = Newsletter.objects.get(pk=newsletter_id)
        subscriber = Subscriber.objects.get(pk=subscriber_id)
        
        # Check if subscriber is active
        if subscriber.status != Subscriber.Status.ACTIVE:
            logger.info(f"Skipping inactive subscriber: {subscriber.email}")
            return False
        
        # Check if subscriber is confirmed
        if not subscriber.is_confirmed:
            logger.info(f"Skipping unconfirmed subscriber: {subscriber.email}")
            return False
        
        # Prepare email
        subject = newsletter.subject
        html_content = newsletter.content
        
        # Create plain text version from HTML
        text_content = strip_tags(html_content)
        
        # Send email
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            # Update subscriber analytics
            subscriber.open_count = 0  # Reset for new newsletter
            subscriber.last_activity = timezone.now()
            subscriber.save(update_fields=['last_activity', 'open_count'])
            
            logger.info(f"Newsletter sent successfully to {subscriber.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send newsletter to {subscriber.email}: {e}")
            # Mark subscriber as bounced if email fails
            subscriber.status = Subscriber.Status.BOUNCED
            subscriber.save(update_fields=['status'])
            raise
            
    except Newsletter.DoesNotExist:
        logger.error(f"Newsletter {newsletter_id} not found")
        return False
    except Subscriber.DoesNotExist:
        logger.error(f"Subscriber {subscriber_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending newsletter email: {e}", exc_info=True)
        # Retry the task
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True)
def send_newsletter_batch(self, newsletter_id: int, subscriber_ids: List[int]):
    """
    Send newsletter to a batch of subscribers.
    This task processes multiple subscribers in parallel.
    
    Args:
        newsletter_id: ID of the Newsletter object
        subscriber_ids: List of Subscriber IDs
    
    Returns:
        Dict with success/failure counts
    """
    try:
        newsletter = Newsletter.objects.get(pk=newsletter_id)
        
        # Update newsletter status
        newsletter.status = Newsletter.Status.SENDING
        newsletter.save(update_fields=['status'])
        
        success_count = 0
        failure_count = 0
        
        # Process subscribers in batches
        batch_size = 50  # Process 50 at a time to avoid overwhelming the email server
        
        for i in range(0, len(subscriber_ids), batch_size):
            batch = subscriber_ids[i:i + batch_size]
            
            # Send emails in parallel using group
            from celery import group
            job = group(
                send_newsletter_email.s(newsletter_id, sub_id) 
                for sub_id in batch
            )
            result = job.apply_async()
            
            # Wait for batch to complete and count results
            for task_result in result.get():
                if task_result:
                    success_count += 1
                else:
                    failure_count += 1
        
        # Update newsletter statistics
        newsletter.total_sent = success_count
        newsletter.status = Newsletter.Status.SENT
        newsletter.sent_date = timezone.now()
        newsletter.save(update_fields=['status', 'total_sent', 'sent_date'])
        
        logger.info(
            f"Newsletter {newsletter_id} sent: {success_count} successful, "
            f"{failure_count} failed"
        )
        
        return {
            'success': success_count,
            'failed': failure_count,
            'total': len(subscriber_ids)
        }
        
    except Newsletter.DoesNotExist:
        logger.error(f"Newsletter {newsletter_id} not found")
        return {'success': 0, 'failed': 0, 'total': 0}
    except Exception as e:
        logger.error(f"Error sending newsletter batch: {e}", exc_info=True)
        # Update newsletter status to failed
        try:
            newsletter = Newsletter.objects.get(pk=newsletter_id)
            newsletter.status = Newsletter.Status.FAILED
            newsletter.save(update_fields=['status'])
        except:
            pass
        raise


@shared_task
def send_newsletter_to_all(newsletter_id: int):
    """
    Send newsletter to all active subscribers.
    This is the main task called from admin or views.
    
    Args:
        newsletter_id: ID of the Newsletter object
    
    Returns:
        Dict with task information
    """
    try:
        newsletter = Newsletter.objects.get(pk=newsletter_id)
        
        # Get all active, confirmed subscribers
        if newsletter.send_to_all:
            subscribers = Subscriber.objects.filter(
                status=Subscriber.Status.ACTIVE,
                is_confirmed=True
            )
        else:
            # Send only to subscribers with matching categories
            subscribers = Subscriber.objects.filter(
                status=Subscriber.Status.ACTIVE,
                is_confirmed=True,
                categories__in=newsletter.categories.all()
            ).distinct()
        
        subscriber_ids = list(subscribers.values_list('id', flat=True))
        
        if not subscriber_ids:
            logger.warning(f"No active subscribers found for newsletter {newsletter_id}")
            newsletter.status = Newsletter.Status.FAILED
            newsletter.save(update_fields=['status'])
            return {'message': 'No active subscribers found', 'total': 0}
        
        # Start batch sending task
        task = send_newsletter_batch.delay(newsletter_id, subscriber_ids)
        
        logger.info(
            f"Started newsletter dispatch task {task.id} for {len(subscriber_ids)} subscribers"
        )
        
        return {
            'task_id': task.id,
            'total_subscribers': len(subscriber_ids),
            'message': 'Newsletter dispatch started'
        }
        
    except Newsletter.DoesNotExist:
        logger.error(f"Newsletter {newsletter_id} not found")
        return {'error': 'Newsletter not found', 'total': 0}
    except Exception as e:
        logger.error(f"Error starting newsletter dispatch: {e}", exc_info=True)
        return {'error': str(e), 'total': 0}

