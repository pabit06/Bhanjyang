"""
Business logic services for the Contact app.

This module contains service classes that handle business logic
separate from views, making the code more maintainable and testable.
"""
import logging
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import connection
from django.core.cache import cache
import time

import hashlib
import uuid
from django.template.loader import get_template
from django.conf import settings
from io import BytesIO
from xhtml2pdf import pisa

from .models import ContactSubmission
from .tasks import send_contact_email, send_auto_response_email
from .utils.helpers import get_client_ip, get_attachment_filename, format_file_size_display
from .utils.constants import (
    CACHE_TIMEOUT_FAQS, 
    CACHE_TIMEOUT_OFFICE_LOCATIONS,
    CACHE_TIMEOUT_COOPERATIVE_INFO,
    CACHE_TIMEOUT_INFORMATION_OFFICER
)
from .utils.performance import (
    track_performance,
    track_form_submission_performance,
    track_pdf_generation_time
)
from .utils.error_codes import ContactErrorCodes

logger = logging.getLogger(__name__)


class ContactService:
    """
    Service class for handling contact form submissions and related operations.
    
    Provides methods for creating contact submissions, sending notification emails,
    and managing contact form data. Handles file attachments and tracks submission
    metadata (IP address, user agent) for security and analytics.
    
    Usage:
        submission = ContactService.create_contact_submission(form_data, files, request.META)
        ContactService.send_contact_notification_emails(submission)
    """
    
    @staticmethod
    def get_contact_page_context(is_staff=False):
        """
        Get context data for the contact page with caching support.
        
        Args:
            is_staff: If True, bypasses cache to show real-time data for staff users
        
        Returns:
            dict: Context dictionary with form, breadcrumbs, cooperative info, information officer,
                  FAQs, and office locations
        """
        from .forms import ContactForm
        from apps.about.models import CooperativeInfo, Staff
        from apps.core.models import PageSEO
        
        # Fetch cooperative info with caching
        cooperative_info = None
        if not is_staff:
            cache_key_coop_info = 'contact_cooperative_info_active'
            cached_coop_info = cache.get(cache_key_coop_info)
            if cached_coop_info is not None:
                cooperative_info = cached_coop_info
            else:
                try:
                    cooperative_info = CooperativeInfo.objects.active().first()
                    if cooperative_info:
                        cache.set(cache_key_coop_info, cooperative_info, CACHE_TIMEOUT_COOPERATIVE_INFO)
                except Exception as e:
                    logger.warning(f"Could not fetch cooperative info: {e}")
        else:
            # Staff users get real-time data
            try:
                cooperative_info = CooperativeInfo.objects.active().first()
            except Exception as e:
                logger.warning(f"Could not fetch cooperative info: {e}")
        
        # Fetch FAQs with caching
        faqs = []
        if not is_staff:
            cache_key_faqs = 'contact_faqs_active'
            cached_faqs = cache.get(cache_key_faqs)
            if cached_faqs is not None:
                faqs = cached_faqs
            else:
                try:
                    from .models import FAQ
                    faqs = list(FAQ.objects.filter(is_active=True).order_by('order', 'created_at'))
                    cache.set(cache_key_faqs, faqs, CACHE_TIMEOUT_FAQS)
                except Exception as e:
                    logger.warning(f"Could not fetch FAQs: {e}")
        else:
            # Staff users get real-time data
            try:
                from .models import FAQ
                faqs = list(FAQ.objects.filter(is_active=True).order_by('order', 'created_at'))
            except Exception as e:
                logger.warning(f"Could not fetch FAQs: {e}")
        
        # Fetch office locations with caching
        office_locations = []
        if not is_staff:
            cache_key_locations = 'contact_office_locations_active'
            cached_locations = cache.get(cache_key_locations)
            if cached_locations is not None:
                office_locations = cached_locations
            else:
                try:
                    from .models import OfficeLocation
                    office_locations = list(OfficeLocation.objects.filter(is_active=True).order_by('order'))
                    cache.set(cache_key_locations, office_locations, CACHE_TIMEOUT_OFFICE_LOCATIONS)
                except Exception as e:
                    logger.warning(f"Could not fetch office locations: {e}")
        else:
            # Staff users get real-time data
            try:
                from .models import OfficeLocation
                office_locations = list(OfficeLocation.objects.filter(is_active=True).order_by('order'))
            except Exception as e:
                logger.warning(f"Could not fetch office locations: {e}")
        
        # Fetch Information Officer from Staff (RTI Act 2064) with caching
        information_officer = None
        if not is_staff:
            cache_key_info_officer = 'contact_information_officer_active'
            cached_info_officer = cache.get(cache_key_info_officer)
            if cached_info_officer is not None:
                information_officer = cached_info_officer
            else:
                try:
                    information_officer = Staff.get_information_officer()
                    if information_officer:
                        cache.set(cache_key_info_officer, information_officer, CACHE_TIMEOUT_INFORMATION_OFFICER)
                except Exception as e:
                    logger.warning(f"Could not fetch information officer: {e}")
        else:
            # Staff users get real-time data
            try:
                information_officer = Staff.get_information_officer()
            except Exception as e:
                logger.warning(f"Could not fetch information officer: {e}")
        
        # Get page-specific SEO settings
        page_seo = None
        try:
            page_seo = PageSEO.objects.filter(page='contact', is_active=True).first()
        except Exception as e:
            logger.warning(f"Could not fetch page SEO for contact: {e}")
        
        return {
            'form': ContactForm(),
            'cooperative_info': cooperative_info,
            'faqs': faqs,
            'information_officer': information_officer,
            'office_locations': office_locations,
            'page_seo': page_seo,
            'breadcrumbs': [
                {'name': _('Home'), 'url': '/'},
                {'name': _('Contact'), 'url': '/contact/'}
            ]
        }
    
    @staticmethod
    def create_contact_submission(form_data, files, request_meta):
        """
        Create a contact submission from form data.
        
        Args:
            form_data: Cleaned form data dictionary
            files: Request.FILES dictionary
            request_meta: Request.META dictionary for IP and user agent
            
        Returns:
            ContactSubmission: Created submission instance
        """
        attachment = files.get('attachment')
        ip_address = get_client_ip(request_meta)
        user_agent = request_meta.get('HTTP_USER_AGENT', '')
        
        # Generate a unique tracking hash for this submission
        submission_hash = hashlib.md5(f"{uuid.uuid4()}-{time.time()}".encode()).hexdigest()[:12]
        
        # Generate subject from message if not provided
        message_body = form_data.get('message', '')
        if 'subject' in form_data and form_data['subject']:
            subject = form_data['subject']
        else:
            subject = message_body[:50].strip() if message_body else _("Contact Form Inquiry")
            if len(message_body) > 50:
                subject += "..."
        
        submission = ContactSubmission.objects.create(
            name=form_data['name'],
            email=form_data['email'],
            phone=form_data.get('phone', ''),
            subject=subject,
            message=message_body,
            attachment=attachment,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"[SUBMISSION:{submission_hash}] Contact submission saved with ID: {submission.id} for {submission.email}")
        setattr(submission, 'tracking_hash', submission_hash) # Temporary attribute for email
        return submission
    
    @staticmethod
    def send_contact_notification_emails(submission):
        """
        Send notification emails for a contact submission.
        
        Args:
            submission: ContactSubmission instance
        """
        # Prepare email content
        full_subject = f"Website Contact: {submission.subject}"
        tracking_hash = getattr(submission, 'tracking_hash', 'N/A')
        
        attachment_info = ""
        if submission.has_attachment():
            filename = get_attachment_filename(submission.attachment)
            size_display = format_file_size_display(submission.attachment.size)
            attachment_info = f"Attachment: {filename} ({size_display})"
        
        full_message = f"""
New message from Bhanjyang Cooperative website:

Tracking Hash: {tracking_hash}
Name: {submission.name}
Email: {submission.email}
Phone: {submission.phone if submission.phone else 'Not provided'}
Submission ID: {submission.id}
IP Address: {submission.ip_address}
Date: {submission.created_at.strftime('%Y-%m-%d %H:%M:%S')}
{attachment_info}
--------------------------------------------------

Message:
{submission.message}

---
This submission has been automatically saved to the database.
You can manage it through the admin interface.
        """
        
        email_data = {
            'subject': full_subject,
            'message': full_message,
            'submission_id': submission.id
        }
        
        # Try to use celery if available, otherwise send synchronously
        try:
            send_contact_email.delay(email_data)
            send_auto_response_email.delay(
                submission.email,
                submission.name,
                submission.subject,
                submission.id
            )
        except (AttributeError, Exception) as e:
            # Celery not installed or broker not available, send synchronously
            # Catch all exceptions to handle connection errors gracefully
            logger.warning(f"Celery unavailable, sending emails synchronously: {e}")
            send_contact_email(email_data)
            send_auto_response_email(
                submission.email,
                submission.name,
                submission.subject,
                submission.id
            )
        
        logger.info(f"Email tasks queued for submission {submission.id}")
    



class ContactAnalyticsService:
    """
    Service class for contact analytics and statistics.
    
    Provides methods to retrieve statistics about contact submissions.
    
    Usage:
        stats = ContactAnalyticsService.get_submission_stats()
    """
    
    @staticmethod
    def get_submission_stats():
        """
        Get statistics about contact submissions.
        
        Returns:
            dict: Dictionary with various statistics
        """
        total_submissions = ContactSubmission.objects.count()
        new_submissions = ContactSubmission.objects.filter(status='new').count()
        resolved_submissions = ContactSubmission.objects.filter(status='resolved').count()
        spam_submissions = ContactSubmission.objects.filter(status='spam').count()
        
        # Recent submissions (last 24 hours)
        recent_threshold = timezone.now() - timezone.timedelta(hours=24)
        recent_submissions = ContactSubmission.objects.filter(
            created_at__gte=recent_threshold
        ).count()
        
        return {
            'total_submissions': total_submissions,
            'new_submissions': new_submissions,
            'resolved_submissions': resolved_submissions,
            'spam_submissions': spam_submissions,
            'recent_submissions': recent_submissions,
        }

