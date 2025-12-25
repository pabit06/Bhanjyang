import logging
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from typing import Dict, Any, List, Optional

from .models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Committee, Staff, Person
)
from .constants import CACHE_TIMEOUT_MEDIUM, ERROR_UNABLE_TO_LOAD

logger = logging.getLogger(__name__)

class AboutService:
    """
    Service Layer for the About App.
    
    Handles data fetching, caching, and business logic for 'About Us' related pages
    including cooperative information, timeline, affiliations, and team data.
    Implements caching strategies to improve performance.
    """

    @staticmethod
    def get_about_home_data(is_staff: bool = False) -> Dict[str, Any]:
        """
        Retrieve all data required for the main About Us page.
        
        Args:
            is_staff: If True, bypasses cache and shows all content including inactive items
            
        Returns:
            Dictionary containing cooperative info, timeline, stats, etc.
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
                    cache.set(cache_key, context, CACHE_TIMEOUT_MEDIUM)
                except Exception as e:
                    logger.warning(f"Failed to cache about data: {e}")
            
            return context

        except Exception as e:
            logger.error(f"Error fetching about home data: {e}", exc_info=True)
            return {'error': str(ERROR_UNABLE_TO_LOAD)}

    @staticmethod
    def get_timeline_events():
        """Retrieve all active timeline events ordered by date (newest first)."""
        return CooperativeTimeline.objects.active().order_by('-event_date')

    @staticmethod
    def get_affiliations():
        """Retrieve all active affiliations ordered by display order."""
        return CooperativeAffiliation.objects.active().order_by('order')

    @staticmethod
    def get_leadership_messages():
        """Retrieve all active leadership messages ordered by display order."""
        return LeadershipMessage.objects.active().order_by('order')

    @staticmethod
    def get_active_team() -> tuple:
        """
        Retrieve active committees and staff members with optimized queries.
        Uses prefetch_related and select_related to avoid N+1 queries.
        """
        committees = Committee.objects.filter(is_active=True).prefetch_related('memberships__person')
        staff = Staff.objects.filter(is_active=True).select_related('person')
        return committees, staff

    @staticmethod
    def get_past_committees():
        """Retrieve inactive (past) committees ordered by tenure."""
        return Committee.objects.filter(is_active=False).order_by('-tenure_bs').prefetch_related('memberships__person')

    @staticmethod
    def get_search_results(query: str) -> Dict[str, Any]:
        """
        Perform a global search across about app models.
        """
        results = {
            'query': query,
            'cooperative_info': list(CooperativeInfo.objects.active().filter(
                Q(cooperative_name__icontains=query) |
                Q(description__icontains=query) |
                Q(mission__icontains=query) |
                Q(vision__icontains=query)
            )[:5]),
            'timeline': list(CooperativeTimeline.objects.active().filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )[:5]),
            'affiliations': list(CooperativeAffiliation.objects.active().filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:5]),
            'leadership': list(LeadershipMessage.objects.active().filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author_name__icontains=query)
            )[:5]),
            'team': list(Person.objects.filter(is_active=True).filter(
                Q(full_name__icontains=query) |
                Q(bio__icontains=query) |
                Q(position_general__icontains=query)
            )[:5])
        }
        return results

    @staticmethod
    def get_site_statistics() -> Dict[str, Any]:
        """
        Get aggregated site statistics.
        """
        return {
            'cooperative_info_count': CooperativeInfo.objects.active().count(),
            'timeline_events_count': CooperativeTimeline.objects.active().count(),
            'affiliations_count': CooperativeAffiliation.objects.active().count(),
            'leadership_messages_count': LeadershipMessage.objects.active().count(),
            'team_members_count': Person.objects.filter(is_active=True).count(),
            'committees_count': Committee.objects.filter(is_active=True).count(),
            'staff_count': Staff.objects.filter(is_active=True).count(),
            'last_updated': timezone.now().isoformat()
        }

    @staticmethod
    def _send_email_safe(subject: str, message: str, recipient_list: List[str], from_email: Optional[str] = None) -> bool:
        """
        Helper method to send emails safely with error handling and environment checks.
        """
        try:
            if not getattr(settings, 'SEND_REAL_EMAILS', False):
                logger.info(f"Mocking email: {subject} to {recipient_list}")
                return True

            send_mail(
                subject=subject,
                message=message,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Error sending email ({subject}): {e}", exc_info=True)
            return False

    @classmethod
    def send_contact_emails(cls, data: Dict[str, Any]) -> bool:
        """
        Send contact form notification emails.
        """
        recipient_list = [settings.CONTACT_EMAIL] if hasattr(settings, 'CONTACT_EMAIL') else [settings.DEFAULT_FROM_EMAIL]
        subject = f"New Contact Form Submission: {data.get('subject')}"
        message = f"Name: {data.get('name')}\nEmail: {data.get('email')}\nMessage: {data.get('message')}"
        
        return cls._send_email_safe(subject, message, recipient_list)

    @classmethod
    def send_newsletter_welcome_email(cls, data: Dict[str, Any]) -> bool:
        """
        Send welcome email to new newsletter subscribers.
        """
        recipient_list = [data.get('email')]
        subject = "Welcome to Bhanjyang Cooperative Newsletter"
        message = f"Hello {data.get('name')},\n\nThank you for subscribing!"
        
        return cls._send_email_safe(subject, message, recipient_list)

    @classmethod
    def send_feedback_email(cls, data: Dict[str, Any]) -> bool:
        """
        Send feedback notification email to administrators.
        """
        recipient_list = [settings.CONTACT_EMAIL] if hasattr(settings, 'CONTACT_EMAIL') else [settings.DEFAULT_FROM_EMAIL]
        subject = f"New Feedback: {data.get('feedback_type')}"
        message = f"Rating: {data.get('rating')}\nComments: {data.get('comments')}\nFrom: {data.get('email')}"
        
        return cls._send_email_safe(subject, message, recipient_list)
