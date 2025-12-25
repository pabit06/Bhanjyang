"""
Background tasks for the Contact app.

This module contains task functions for sending emails and cleanup operations.
These can be used with Celery when installed, or run synchronously.
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .utils.constants import SUBMISSION_CLEANUP_DAYS

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

# Note: When Celery is available, functions decorated with @shared_task(bind=True)
# will receive 'self' as first argument. When not available, they work normally.
# The services.py handles calling .delay() vs direct call based on availability.

# Admin email recipient
ADMIN_EMAIL = 'admin@bhanjyang.coop.np'

# Auto-response email template
AUTO_RESPONSE_TEMPLATE = """
Dear {user_name},

Thank you for contacting Bhanjyang Saving & Credit Cooperative Society Ltd.

We have received your message regarding "{subject}" and will respond to you within 24-48 hours.

Your submission ID is: {submission_id}

If you have any urgent inquiries, please call us at:
- Main Office: +977-9856083101
- Service Center: +977-9846242424

Best regards,
Bhanjyang Cooperative Team
"""


@shared_task(max_retries=3)
def send_contact_email(submission_data):
    """
    Send contact form email to admin.
    
    Args:
        submission_data: Dictionary containing 'subject', 'message', and 'submission_id'
        
    Returns:
        bool: True if email sent successfully, False otherwise
        
    Note:
        When Celery is available, this function can be called with .delay() for async execution.
        For retry functionality, change decorator to @shared_task(bind=True, max_retries=3)
        and add 'self' as first parameter, then use self.retry() in exception handling.
    """
    submission_id = submission_data.get('submission_id', 'unknown')
    
    try:
        send_mail(
            subject=submission_data['subject'],
            message=submission_data['message'],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ADMIN_EMAIL],
            fail_silently=False,
        )
        logger.info(f"Contact email sent successfully for submission {submission_id}")
        return True
        
    except Exception as exc:
        logger.error(f"Failed to send contact email for submission {submission_id}: {exc}")
        # Note: For retry functionality, use @shared_task(bind=True) and self.retry()
        return False


@shared_task(max_retries=3)
def send_auto_response_email(user_email, user_name, subject, submission_id):
    """
    Send auto-response confirmation email to user.
    
    Args:
        user_email: Recipient email address
        user_name: User's name for personalization
        subject: Original inquiry subject
        submission_id: Submission reference ID
        
    Returns:
        bool: True if email sent successfully, False otherwise
        
    Note:
        When Celery is available, this function can be called with .delay() for async execution.
        For retry functionality, change decorator to @shared_task(bind=True, max_retries=3)
        and add 'self' as first parameter, then use self.retry() in exception handling.
    """
    try:
        message = AUTO_RESPONSE_TEMPLATE.format(
            user_name=user_name,
            subject=subject,
            submission_id=submission_id
        )
        
        send_mail(
            subject="Thank you for contacting Bhanjyang Cooperative",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=True,  # Don't fail if auto-response fails
        )
        logger.info(f"Auto-response sent to {user_email} for submission {submission_id}")
        return True
        
    except Exception as exc:
        logger.error(f"Failed to send auto-response email to {user_email}: {exc}")
        # Note: For retry functionality, use @shared_task(bind=True) and self.retry()
        return False


@shared_task
def cleanup_old_contact_submissions():
    """
    Clean up old resolved contact submissions.
    
    Deletes contact submissions that are:
    - Older than SUBMISSION_CLEANUP_DAYS (default: 1 year)
    - Have 'resolved' status
    
    Returns:
        int: Number of deleted submissions
    """
    # Import here to avoid circular imports
    from .models import ContactSubmission
    
    try:
        cutoff_date = timezone.now() - timedelta(days=SUBMISSION_CLEANUP_DAYS)
        old_submissions = ContactSubmission.objects.filter(
            created_at__lt=cutoff_date,
            status='resolved'
        )
        
        count = old_submissions.count()
        if count > 0:
            old_submissions.delete()
            logger.info(f"Cleaned up {count} old contact submissions older than {SUBMISSION_CLEANUP_DAYS} days")
        else:
            logger.info("No old contact submissions to clean up")
            
        return count
        
    except Exception as exc:
        logger.error(f"Failed to cleanup old submissions: {exc}")
        return 0
