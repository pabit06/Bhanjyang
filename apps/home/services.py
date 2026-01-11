from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.urls import reverse
from typing import Dict, Any, List

from .models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    NewsletterSubscriber, ContactInquiry
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
        Retrieve all data required for the homepage with caching strategy.
        
        Fetches homepage content, featured testimonials, statistics, announcements,
        service highlights, and gallery images. Results are cached for 5 minutes
        for non-staff users to improve performance.
        
        Args:
            is_staff: If True, bypasses cache to show real-time data
            
        Returns:
            Dictionary containing:
                - homepage_content: HomePageContent instance
                - featured_testimonials: List of featured testimonials (max 3)
                - featured_statistics: List of featured statistics (max 4)
                - featured_announcements: List of active announcements (max 3)
                - featured_services: List of featured service highlights (max 3)
                - featured_gallery: List of featured gallery images (max 6)
                - breadcrumbs: Navigation breadcrumbs
                - error: Error message if data fetching fails
                
        Example:
            >>> context = HomeService.get_home_context()
            >>> len(context['featured_testimonials'])
            3
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

            # 5. Services - Get from services app
            from apps.services.models import SavingsAccount, LoanType, FixedDeposit
            
            # Get featured services from different service types
            featured_services_list = []
            
            # Get featured savings accounts (max 1)
            featured_savings = SavingsAccount.objects.filter(
                is_featured=True, is_active=True
            ).order_by('-interest_rate')[:1]
            for savings in featured_savings:
                featured_services_list.append({
                    'title': savings.english_name,
                    'description': savings.description or f"Interest rate: {savings.interest_rate}%",
                    'icon': savings.icon or 'fas fa-piggy-bank',
                    'interest_rate': f"Up to {savings.interest_rate}%",
                    'link_url': savings.get_absolute_url(),
                    'link_text': 'View Details',
                    'color': savings.color or 'deuraligreen'
                })
            
            # Get featured loan types (max 1)
            featured_loans = LoanType.objects.filter(
                is_featured=True, is_active=True
            ).order_by('english_name')[:1]
            for loan in featured_loans:
                interest_display = f"{loan.annual_interest_rate}%" if loan.annual_interest_rate else "Contact us"
                featured_services_list.append({
                    'title': loan.english_name,
                    'description': loan.description or "Flexible loan options for your needs",
                    'icon': loan.icon or 'fas fa-hand-holding-usd',
                    'interest_rate': f"From {interest_display}",
                    'link_url': loan.get_absolute_url(),
                    'link_text': 'Explore Options',
                    'color': loan.color or 'bhanjyangred'
                })
            
            # Get featured fixed deposits (max 1) - get the highest rate
            featured_fd = FixedDeposit.objects.filter(
                is_active=True
            ).order_by('-interest_rate')[:1]
            for fd in featured_fd:
                featured_services_list.append({
                    'title': f"Fixed Deposit ({fd.get_duration_months_display()})",
                    'description': f"Secure your future with fixed deposits",
                    'icon': 'fas fa-comments-dollar',
                    'interest_rate': f"Up to {fd.interest_rate}%",
                    'link_url': reverse('services:fixed_deposit_list'),
                    'link_text': 'View Deposit Rates',
                    'color': 'purple'
                })
            
            # Limit to 3 services total
            services = featured_services_list[:3]

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
    def track_view(request, title: str = "Home") -> None:
        """
        Track page view for analytics purposes.
        
        Delegates to DashboardAnalyticsService to record page views with
        user agent, IP address, and other metadata for analytics.
        
        Args:
            request: Django HttpRequest object
            title: Page title for tracking (default: "Home")
            
        Returns:
            None
            
        Note:
            If tracking fails, the error is logged but doesn't interrupt
            the main application flow.
        """
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
        Process contact form submission from homepage.
        
        DEPRECATED: This method is kept for backward compatibility.
        New submissions should use ContactService.create_contact_submission() from contact app.
        This method now forwards to the contact app's service.
        
        Args:
            data: Dictionary containing contact form data:
                - name: Submitter's name
                - email: Submitter's email
                - phone: Submitter's phone (optional)
                - subject: Inquiry subject
                - message: Inquiry message
                - inquiry_type: Type of inquiry (default: 'general')
                
        Returns:
            Tuple of (success: bool, message: str):
                - success: True if submission processed successfully
                - message: Success or error message for user display
        """
        try:
            # Use contact app's service for consolidation
            from apps.contact.services import ContactService
            
            # Create a mock request meta for IP and user agent tracking
            request_meta = {
                'REMOTE_ADDR': '127.0.0.1',
                'HTTP_USER_AGENT': 'HomePage-ContactForm/1.0'
            }
            
            # Create submission using contact app's service
            submission = ContactService.create_contact_submission(
                form_data=data,
                files={},  # No file attachments from home page form
                request_meta=request_meta
            )
            
            # Send notification emails
            ContactService.send_contact_notification_emails(submission)
            
            # Also create ContactInquiry for backward compatibility with admin/tests
            inquiry = ContactInquiry.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data.get('phone', ''),
                subject=data['subject'],
                message=data['message'],
                inquiry_type=data.get('inquiry_type', 'general')
            )
            
            return True, "Thank you for your inquiry. We will get back to you soon!"

        except Exception as e:
            logger.error(f"Contact submission failed: {e}", exc_info=True)
            return False, "Sorry, there was an error processing your request."

    @staticmethod
    def handle_newsletter_signup(email: str, name: str = '') -> tuple[bool, str]:
        """
        Process newsletter subscription signup.
        
        Creates or reactivates a newsletter subscription and sends welcome email.
        Prevents duplicate subscriptions and handles reactivation of previously
        unsubscribed users.
        
        Args:
            email: Subscriber's email address (required)
            name: Subscriber's name (optional, defaults to empty string)
            
        Returns:
            Tuple of (success: bool, message: str):
                - success: True if signup processed successfully
                - message: Success or error message for user display
                
        Example:
            >>> success, msg = HomeService.handle_newsletter_signup(
            ...     'user@example.com', 'John Doe'
            ... )
            >>> success
            True
            >>> 'subscribed' in msg.lower()
            True
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
