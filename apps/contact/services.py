"""
Business logic services for the Contact app.

This module contains service classes that handle business logic
separate from views, making the code more maintainable and testable.
"""
import logging
from django.utils import timezone
from django.db import connection
import time

from .models import ContactSubmission, KYMSubmission
from .tasks import send_contact_email, send_auto_response_email

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
    def get_contact_page_context():
        """
        Get context data for the contact page.
        
        Returns:
            dict: Context dictionary with form, breadcrumbs, cooperative info, and information officer
        """
        from .forms import ContactForm
        from apps.about.models import CooperativeInfo, Staff
        
        # Fetch cooperative info
        cooperative_info = None
        try:
            cooperative_info = CooperativeInfo.objects.active().first()
        except Exception as e:
            logger.warning(f"Could not fetch cooperative info: {e}")
        
        # Fetch Information Officer from Staff (RTI Act 2064)
        information_officer = None
        try:
            information_officer = Staff.get_information_officer()
        except Exception as e:
            logger.warning(f"Could not fetch information officer: {e}")
        
        return {
            'form': ContactForm(),
            'cooperative_info': cooperative_info,
            'information_officer': information_officer,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Contact', 'url': '/contact/'}
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
        ip_address = request_meta.get('REMOTE_ADDR', '')
        user_agent = request_meta.get('HTTP_USER_AGENT', '')
        
        # Generate subject from message if not provided
        message_body = form_data['message']
        if 'subject' in form_data and form_data['subject']:
            subject = form_data['subject']
        else:
            subject = message_body[:50].strip() if message_body else "Contact Form Inquiry"
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
        
        logger.info(f"Contact submission saved with ID: {submission.id}")
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
        attachment_info = ""
        if submission.has_attachment():
            attachment_info = f"Attachment: {submission.get_attachment_filename()} ({submission.get_attachment_size_display()})"
        
        full_message = f"""
New message from Bhanjyang Cooperative website:

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
    
    @staticmethod
    def get_performance_metrics(start_time, db_queries_start):
        """
        Calculate performance metrics.
        
        Args:
            start_time: Start time from time.time()
            db_queries_start: Initial number of DB queries
            
        Returns:
            tuple: (processing_time, db_queries_count)
        """
        processing_time = time.time() - start_time
        db_queries_count = len(connection.queries) - db_queries_start
        return processing_time, db_queries_count


class KYMService:
    """
    Service class for handling KYM (Know Your Member) form submissions.
    
    KYM forms are used for member registration and verification. This service
    handles the creation and processing of KYM submissions including document
    uploads and personal information.
    
    Usage:
        submission = KYMService.create_kym_submission(form_data, files, request.META)
    """
    
    @staticmethod
    def get_kym_page_context():
        """
        Get context data for the KYM form page.
        
        Returns:
            dict: Context dictionary with form and breadcrumbs
        """
        from .forms import KYMForm
        
        return {
            'form': KYMForm(),
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'KYM Form', 'url': '/contact/kym-form/'}
            ]
        }
    
    @staticmethod
    def create_kym_submission(form_data, files, request_meta):
        """
        Create a KYM submission from form data.
        
        Args:
            form_data: Cleaned form data dictionary
            files: Request.FILES dictionary
            request_meta: Request.META dictionary for IP and user agent
            
        Returns:
            KYMSubmission: Created submission instance
        """
        ip_address = request_meta.get('REMOTE_ADDR', '')
        user_agent = request_meta.get('HTTP_USER_AGENT', '')
        
        kym_submission = KYMSubmission.objects.create(
            full_name=form_data['full_name'],
            dob=form_data['dob'],
            gender=form_data['gender'],
            marital_status=form_data['marital_status'],
            nationality=form_data.get('nationality', 'Nepali'),
            phone=form_data['phone'],
            email=form_data['email'],
            permanent_address=form_data['permanent_address'],
            district=form_data.get('district', 'Kaski'),
            province=form_data.get('province', 'Gandaki Province'),
            father_name=form_data['father_name'],
            mother_name=form_data['mother_name'],
            spouse_name=form_data.get('spouse_name', ''),
            grand_father_name=form_data['grand_father_name'],
            nominee_name=form_data.get('nominee_name', ''),
            occupation=form_data['occupation'],
            income_source=form_data['income_source'],
            estimated_income=form_data.get('estimated_income'),
            citizenship_front=form_data['citizenship_front'],
            citizenship_back=form_data['citizenship_back'],
            passport_photo=form_data['passport_photo_upload'],
            address_proof=form_data['address_proof_upload'],
            income_proof=form_data.get('income_proof_upload'),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"KYM submission saved with ID: {kym_submission.id}")
        return kym_submission


class ContactAnalyticsService:
    """
    Service class for contact analytics and statistics.
    
    Provides methods to retrieve statistics about contact submissions and
    KYM submissions for dashboard and reporting purposes.
    
    Usage:
        stats = ContactAnalyticsService.get_submission_stats()
        kym_stats = ContactAnalyticsService.get_kym_stats()
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
    
    @staticmethod
    def get_kym_stats():
        """
        Get statistics about KYM submissions.
        
        Returns:
            dict: Dictionary with various statistics
        """
        total_kym = KYMSubmission.objects.count()
        pending_kym = KYMSubmission.objects.filter(status='pending').count()
        approved_kym = KYMSubmission.objects.filter(status='approved').count()
        rejected_kym = KYMSubmission.objects.filter(status='rejected').count()
        
        return {
            'total_kym': total_kym,
            'pending_kym': pending_kym,
            'approved_kym': approved_kym,
            'rejected_kym': rejected_kym,
        }

