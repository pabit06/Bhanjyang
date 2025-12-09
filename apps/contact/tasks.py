# from celery import shared_task  # Commented out until celery is installed
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# @shared_task(bind=True, max_retries=3)  # Commented out until celery is installed
def send_contact_email(submission_data):
    """
    Send contact form email to admin asynchronously
    Note: When celery is installed, uncomment @shared_task decorator and add 'self' parameter
    """
    try:
        send_mail(
            subject=submission_data['subject'],
            message=submission_data['message'],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['admin@bhanjyang.coop.np'],
            fail_silently=False,
        )
        logger.info(f"Contact email sent successfully for submission {submission_data.get('submission_id', 'unknown')}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send contact email: {exc}")
        # When celery is installed, uncomment the retry line below
        # raise self.retry(exc=exc, countdown=60, max_retries=3)
        return False

# @shared_task(bind=True, max_retries=3)  # Commented out until celery is installed
def send_auto_response_email(user_email, user_name, subject, submission_id):
    """
    Send auto-response email to user asynchronously
    Note: When celery is installed, uncomment @shared_task decorator and add 'self' parameter
    """
    try:
        auto_response_subject = "Thank you for contacting Bhanjyang Cooperative"
        auto_response_message = f"""
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
        
        send_mail(
            subject=auto_response_subject,
            message=auto_response_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=True,  # Don't fail if auto-response fails
        )
        logger.info(f"Auto-response sent to {user_email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send auto-response email: {exc}")
        # When celery is installed, uncomment the retry line below
        # raise self.retry(exc=exc, countdown=60, max_retries=3)
        return False

# @shared_task  # Commented out until celery is installed
def cleanup_old_contact_submissions():
    """
    Clean up old contact submissions (older than 1 year)
    """
    from apps.contact.models import ContactSubmission
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        cutoff_date = timezone.now() - timedelta(days=365)
        old_submissions = ContactSubmission.objects.filter(
            created_at__lt=cutoff_date,
            status='resolved'
        )
        
        count = old_submissions.count()
        old_submissions.delete()
        
        logger.info(f"Cleaned up {count} old contact submissions")
        return count
    except Exception as exc:
        logger.error(f"Failed to cleanup old submissions: {exc}")
        return 0
