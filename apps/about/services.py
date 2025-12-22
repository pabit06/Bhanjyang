import logging
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from typing import Dict, Any, List

from .models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Committee, Staff
)

logger = logging.getLogger(__name__)

class AboutService:
    """
    Service Layer for the About App.
    
    Handles data fetching, caching, and business logic for 'About Us' related pages
    including cooperative information, timeline, affiliations, and team data.
    Implements caching strategies to improve performance.
    
    Usage:
        context = AboutService.get_about_home_data(is_staff=False)
        timeline = AboutService.get_timeline_events()
    """

    @staticmethod
    def get_about_home_data(is_staff: bool = False) -> Dict[str, Any]:
        """
        Retrieve all data required for the main About Us page.
        
        Fetches cooperative information, featured timeline events,
        statistics, affiliations, leadership messages, and team counts. Results
        are cached for 10 minutes for non-staff users to improve performance.
        
        Args:
            is_staff: If True, bypasses cache and shows all content including inactive items
            
        Returns:
            Dictionary containing:
                - cooperative_info: CooperativeInfo instance
                - timeline_events: List of featured timeline events (max 6)
                - statistics: List of active statistics ordered by order field
                - affiliations: List of featured affiliations
                - leadership_messages: List of active leadership messages
                - total_committees: Count of active committees
                - total_staff: Count of active staff members
                - breadcrumbs: Navigation breadcrumbs
                
        Example:
            >>> context = AboutService.get_about_home_data()
            >>> len(context['timeline_events'])
            6
            >>> context['cooperative_info'].cooperative_name
            'Bhanjyang Cooperative'
        """
        cache_key = f'about_home_data_{is_staff}'
        cached_data = cache.get(cache_key)
        
        if cached_data and not is_staff:
            return cached_data

        try:
            info = CooperativeInfo.objects.active().first()
            timeline = list(CooperativeTimeline.objects.featured()[:6])
            stats = list(CooperativeStatistic.objects.active().order_by('order'))
            affiliations = list(CooperativeAffiliation.objects.featured())
            messages = list(LeadershipMessage.objects.active().order_by('order'))
            
            # Counts
            total_committees = Committee.objects.filter(is_active=True).count()
            total_staff = Staff.objects.filter(is_active=True).count()

            context = {
                'cooperative_info': info,
                'timeline_events': timeline,
                'statistics': stats,
                'affiliations': affiliations,
                'leadership_messages': messages,
                'total_committees': total_committees,
                'total_staff': total_staff,
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'About Us', 'url': '/about/'}
                ]
            }

            if not is_staff:
                try:
                    cache.set(cache_key, context, 600)
                except Exception as e:
                    logger.warning(f"Failed to cache about data: {e}")
            
            return context

        except Exception as e:
            logger.error(f"Error fetching about home data: {e}", exc_info=True)
            return {'error': 'Unable to load content'}

    @staticmethod
    def get_timeline_events():
        """
        Retrieve all active timeline events ordered by date (newest first).
        
        Returns:
            QuerySet of CooperativeTimeline objects ordered by event_date descending
        """
        return CooperativeTimeline.objects.active().order_by('-event_date')

    # Removed: get_achievements() method - CooperativeAchievement model no longer exists

    @staticmethod
    def get_affiliations():
        """
        Retrieve all active affiliations ordered by display order.
        
        Returns:
            QuerySet of CooperativeAffiliation objects ordered by order field
        """
        return CooperativeAffiliation.objects.active().order_by('order')

    @staticmethod
    def get_leadership_messages():
        """
        Retrieve all active leadership messages ordered by display order.
        
        Returns:
            QuerySet of LeadershipMessage objects ordered by order field
        """
        return LeadershipMessage.objects.active().order_by('order')

    @staticmethod
    def get_active_team() -> tuple:
        """
        Retrieve active committees and staff members with optimized queries.
        
        Uses prefetch_related and select_related to avoid N+1 queries.
        
        Returns:
            Tuple of (committees QuerySet, staff QuerySet):
                - committees: Active committees with prefetched memberships and persons
                - staff: Active staff members with related person data
                
        Example:
            >>> committees, staff = AboutService.get_active_team()
            >>> len(list(committees))
            3
            >>> len(list(staff))
            5
        """
        committees = Committee.objects.filter(is_active=True).prefetch_related('memberships__person')
        staff = Staff.objects.filter(is_active=True).select_related('person')
        return committees, staff

    @staticmethod
    def get_past_committees():
        """
        Retrieve inactive (past) committees ordered by tenure.
        
        Returns:
            QuerySet of inactive Committee objects ordered by tenure_bs descending,
            with prefetched memberships and persons to avoid N+1 queries
        """
        return Committee.objects.filter(is_active=False).order_by('-tenure_bs').prefetch_related('memberships__person')

    @staticmethod
    def send_contact_emails(data: Dict[str, Any]) -> bool:
        """
        Send contact form notification emails.
        
        Sends an email notification to administrators when a contact form is submitted.
        Respects SEND_REAL_EMAILS setting - if False, only logs the action.
        
        Args:
            data: Dictionary containing contact form data:
                - name: Submitter's name
                - email: Submitter's email
                - subject: Email subject
                - message: Email message content
                
        Returns:
            True if email sent successfully (or mocked), False on error
            
        Note:
            Email sending respects SEND_REAL_EMAILS setting in Django settings.
            If False, the method logs the action but doesn't send actual emails.
        """
        try:
            if not getattr(settings, 'SEND_REAL_EMAILS', False):
                logger.info(f"Mocking contact email for {data.get('email')}")
                return True

            # Admin Notification
            send_mail(
                subject=f"New Contact Form Submission: {data.get('subject')}",
                message=f"Name: {data.get('name')}\nEmail: {data.get('email')}\nMessage: {data.get('message')}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL] if hasattr(settings, 'CONTACT_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Error sending contact emails: {e}", exc_info=True)
            return False

    @staticmethod
    def send_newsletter_welcome_email(data: Dict[str, Any]) -> bool:
        """
        Send welcome email to new newsletter subscribers.
        
        Sends a welcome email when someone subscribes to the newsletter.
        Respects SEND_REAL_EMAILS setting.
        
        Args:
            data: Dictionary containing subscriber data:
                - name: Subscriber's name
                - email: Subscriber's email address
                
        Returns:
            True if email sent successfully (or mocked), False on error
        """
        try:
            if not getattr(settings, 'SEND_REAL_EMAILS', False):
                return True
                
            send_mail(
                subject="Welcome to Bhanjyang Cooperative Newsletter",
                message=f"Hello {data.get('name')},\n\nThank you for subscribing!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[data.get('email')],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Error sending newsletter email: {e}", exc_info=True)
            return False

    @staticmethod
    def send_feedback_email(data: Dict[str, Any]) -> bool:
        """
        Send feedback notification email to administrators.
        
        Sends an email to administrators when user feedback is submitted.
        Respects SEND_REAL_EMAILS setting.
        
        Args:
            data: Dictionary containing feedback data:
                - feedback_type: Type of feedback
                - rating: User's rating (if applicable)
                - comments: Feedback comments
                - email: Submitter's email
                
        Returns:
            True if email sent successfully (or mocked), False on error
        """
        try:
            if not getattr(settings, 'SEND_REAL_EMAILS', False):
                return True
                
            send_mail(
                subject=f"New Feedback: {data.get('feedback_type')}",
                message=f"Rating: {data.get('rating')}\nComments: {data.get('comments')}\nFrom: {data.get('email')}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL] if hasattr(settings, 'CONTACT_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Error sending feedback email: {e}", exc_info=True)
            return False
