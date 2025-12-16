import logging
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from typing import Dict, Any, List

from .models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Committee, Staff
)

logger = logging.getLogger(__name__)

class AboutService:
    """
    Service Layer for the About App.
    Handles data fetching and business logic for 'About Us' pages.
    """

    @staticmethod
    def get_about_home_data(is_staff: bool = False) -> Dict[str, Any]:
        """
        Retrieves data for the main About page.
        """
        cache_key = f'about_home_data_{is_staff}'
        cached_data = cache.get(cache_key)
        
        if cached_data and not is_staff:
            return cached_data

        try:
            info = CooperativeInfo.objects.active().first()
            timeline = list(CooperativeTimeline.objects.featured()[:6])
            achievements = list(CooperativeAchievement.objects.featured()[:6])
            stats = list(CooperativeStatistic.objects.active().order_by('order'))
            affiliations = list(CooperativeAffiliation.objects.featured())
            messages = list(LeadershipMessage.objects.active().order_by('order'))
            
            # Counts
            total_committees = Committee.objects.filter(is_active=True).count()
            total_staff = Staff.objects.filter(is_active=True).count()

            context = {
                'cooperative_info': info,
                'timeline_events': timeline,
                'achievements': achievements,
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
        return CooperativeTimeline.objects.active().order_by('-event_date')

    @staticmethod
    def get_achievements():
        return CooperativeAchievement.objects.active().order_by('-received_date')

    @staticmethod
    def get_affiliations():
        return CooperativeAffiliation.objects.active().order_by('order')

    @staticmethod
    def get_leadership_messages():
        return LeadershipMessage.objects.active().order_by('order')

    @staticmethod
    def get_active_team():
        committees = Committee.objects.filter(is_active=True).prefetch_related('memberships__person')
        staff = Staff.objects.filter(is_active=True).select_related('person')
        return committees, staff

    @staticmethod
    def get_past_committees():
        return Committee.objects.filter(is_active=False).order_by('-tenure_bs').prefetch_related('memberships__person')

    @staticmethod
    def send_contact_emails(data: Dict[str, Any]) -> bool:
        """Sends contact form emails (Admin Notification + User Confirmation)"""
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
        """Sends welcome email for newsletter"""
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
        """Sends feedback email to admin"""
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
