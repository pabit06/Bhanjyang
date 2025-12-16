from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from typing import Dict, Any, List

from .models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    ServiceHighlight, NewsletterSubscriber, ContactInquiry
)
from apps.gallery.models import GalleryImage
from apps.dashboard.services import DashboardAnalyticsService
import logging

logger = logging.getLogger(__name__)

class HomeService:
    """
    Service Layer for the Home App.
    Handles data fetching, caching, and business logic for the homepage.
    """

    @staticmethod
    def get_home_context(is_staff: bool = False) -> Dict[str, Any]:
        """
        Retrieves all data required for the homepage with caching strategy.
        """
        cache_key = f'homepage_data_{is_staff}'
        cached_data = cache.get(cache_key)

        if cached_data and not is_staff:
            return cached_data

        try:
            # 1. Page Content
            content = HomePageContent.objects.filter(is_active=True).order_by('order').first()

            # 2. Featured Testimonials
            testimonials = list(Testimonial.objects.filter(
                is_featured=True, is_active=True
            ).order_by('order')[:3])

            # 3. Statistics
            stats = list(Statistic.objects.filter(
                is_featured=True, is_active=True
            ).order_by('order')[:4])

            # 4. Announcements (Active & Not Expired)
            announcements = list(Announcement.objects.filter(
                is_featured=True, is_active=True
            ).exclude(
                Q(expiry_date__isnull=False) & Q(expiry_date__lt=timezone.now())
            ).order_by('-priority', '-publish_date')[:3])

            # 5. Services
            services = list(ServiceHighlight.objects.filter(
                is_featured=True, is_active=True
            ).order_by('order')[:3])

            # 6. Gallery (Featured)
            gallery_images = list(GalleryImage.objects.filter(
                is_featured=True, is_active=True
            ).order_by('order')[:6])

            context = {
                'homepage_content': content,
                'featured_testimonials': testimonials,
                'featured_statistics': stats,
                'featured_announcements': announcements,
                'featured_services': services,
                'featured_gallery': gallery_images,
                'breadcrumbs': [{'name': 'Home', 'url': '/'}]
            }

            # Cache for 5 minutes if not staff
            if not is_staff:
                try:
                    cache.set(cache_key, context, 300)
                except Exception as e:
                    logger.warning(f"Failed to cache homepage data: {e}")
            
            return context

        except Exception as e:
            logger.error(f"Error fetching homepage data: {e}", exc_info=True)
            return {
                'homepage_content': None,
                'featured_testimonials': [],
                'featured_statistics': [],
                'featured_announcements': [],
                'featured_services': [],
                'featured_gallery': [],
                'error': "Unable to load content."
            }

    @staticmethod
    def track_view(request, title="Home"):
        """Delegate tracking to DashboardAnalyticsService"""
        try:
            # Prepare data compatible with record_page_view
            data = {
                'page_url': request.build_absolute_uri(),
                'page_title': title,
                'referrer': request.META.get('HTTP_REFERER', ''),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': request.META.get('REMOTE_ADDR', ''),
                'is_mobile': 'Mobile' in request.META.get('HTTP_USER_AGENT', ''),
                'browser': 'Unknown' # Simplified
            }
            # DashboardAnalyticsService.record_page_view(data, request_meta=request.META)
            # Since DashboardAnalyticsService.record_page_view expects request_meta for some fields, we pass it.
            # But wait, DashboardAnalyticsService signature is record_page_view(data, request_meta).
            DashboardAnalyticsService.record_page_view(data, request.META)
        except Exception as e:
            logger.warning(f"Failed to track view in HomeService: {e}")

    @staticmethod
    def handle_contact_submission(data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Process contact form submission.
        Returns (success, message).
        """
        try:
            inquiry = ContactInquiry.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data.get('phone', ''),
                subject=data['subject'],
                message=data['message'],
                inquiry_type=data.get('inquiry_type', 'general')
            )

            # Send Notification Email
            if getattr(settings, 'SEND_REAL_EMAILS', False):
                try:
                    send_mail(
                        f"New Contact Inquiry: {inquiry.subject}",
                        f"From: {inquiry.name} <{inquiry.email}>\n\n{inquiry.message}",
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.DEFAULT_FROM_EMAIL],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"Email sending failed: {e}")

            return True, "Thank you for your inquiry. We will get back to you soon!"

        except Exception as e:
            logger.error(f"Contact submission failed: {e}", exc_info=True)
            return False, "Sorry, there was an error processing your request."

    @staticmethod
    def handle_newsletter_signup(email: str, name: str = '') -> tuple[bool, str]:
        """
        Process newsletter signup.
        Returns (success, message).
        """
        try:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'name': name, 'is_active': True}
            )

            if created:
                # Send Welcome Email
                if getattr(settings, 'SEND_REAL_EMAILS', False):
                    try:
                        send_mail(
                            "Welcome to Bhanjyang Cooperative Newsletter",
                            f"Dear {name or 'Subscriber'},\n\nThank you for subscribing!",
                            settings.DEFAULT_FROM_EMAIL,
                            [email],
                            fail_silently=False
                        )
                    except Exception as e:
                         logger.error(f"Newsletter welcome email failed: {e}")
                
                return True, "Thank you for subscribing to our newsletter!"
            else:
                if not subscriber.is_active:
                    subscriber.is_active = True
                    subscriber.unsubscribed_at = None
                    subscriber.save()
                    return True, "Welcome back! Your subscription has been reactivated."
                
                return False, "You are already subscribed to our newsletter."

        except Exception as e:
            logger.error(f"Newsletter signup failed: {e}", exc_info=True)
            return False, "An error occurred. Please try again."
