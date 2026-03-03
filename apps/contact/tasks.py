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

    # No-op decorator when Celery is not installed.
    # Handles both: @shared_task (no parens → first arg is the function) and @shared_task(...) (options).
    def shared_task(*args, **kwargs):
        # @shared_task without parentheses: shared_task(cleanup_old_contact_submissions)
        if len(args) == 1 and not kwargs and callable(args[0]):
            func = args[0]
            def wrapper_no_options(*wargs, **wkwargs):
                return func(*wargs, **wkwargs)
            wrapper_no_options.delay = wrapper_no_options
            return wrapper_no_options

        # @shared_task(bind=True, max_retries=3) etc.: return a decorator
        bind = kwargs.get('bind', False)

        def decorator(func):
            def wrapper(*wargs, **wkwargs):
                if bind:
                    class DummySelf:
                        def retry(self, *a, **kw):
                            logger.warning("Retry called without Celery. Task failed permanently.")
                            raise kw.get('exc', Exception("Task failed and Celery is not available for retry."))
                    return func(DummySelf(), *wargs, **wkwargs)
                return func(*wargs, **wkwargs)
            wrapper.delay = wrapper
            return wrapper
        return decorator

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


@shared_task(bind=True, max_retries=3)
def send_contact_email(self, submission_data):
    """
    Send contact form email to admin.
    Will retry up to 3 times if email sending fails (when Celery is active).
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
        if CELERY_AVAILABLE:
            logger.info(f"Retrying email task for submission {submission_id}...")
            raise self.retry(exc=exc, countdown=60)
        return False


@shared_task(bind=True, max_retries=3)
def send_auto_response_email(self, user_email, user_name, subject, submission_id):
    """
    Send auto-response confirmation email to user.
    Will retry up to 3 times if email sending fails (when Celery is active).
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
            fail_silently=False,  # False so we can catch the exception and retry
        )
        logger.info(f"Auto-response sent to {user_email} for submission {submission_id}")
        return True

    except Exception as exc:
        logger.error(f"Failed to send auto-response email to {user_email}: {exc}")
        if CELERY_AVAILABLE:
            logger.info(f"Retrying auto-response task for {user_email}...")
            raise self.retry(exc=exc, countdown=60)
        return False


@shared_task
def cleanup_old_contact_submissions():
    """
    Clean up old resolved contact submissions.
    """
    from .models import ContactSubmission

    try:
        cutoff_date = timezone.now() - timedelta(days=SUBMISSION_CLEANUP_DAYS)

        deleted_count, _ = ContactSubmission.objects.filter(
            created_at__lt=cutoff_date,
            status='resolved'
        ).delete()

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old contact submissions older than {SUBMISSION_CLEANUP_DAYS} days")
        else:
            logger.info("No old contact submissions to clean up")

        return deleted_count

    except Exception as exc:
        logger.error(f"Failed to cleanup old submissions: {exc}")
        return 0
