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
            # Always fetch popup notice fresh (not from cache) to ensure active status is current
            try:
                from apps.news_events.models import PopupNotice, Notice
                now = timezone.now()
                
                # First check PopupNotice
                active_popup_notices = PopupNotice.objects.filter(
                    is_active=True,
                    start_date__lte=now
                ).filter(
                    Q(end_date__isnull=True) | Q(end_date__gte=now)
                ).order_by('-priority', '-start_date')
                
                popup_notice = active_popup_notices.first() if active_popup_notices.exists() else None
                
                # If no PopupNotice, check regular Notice
                if not popup_notice:
                    active_regular_notices = Notice.objects.filter(
                        is_active=True,
                        show_as_popup=True
                    ).order_by('-is_pinned', '-published_date')
                    
                    if active_regular_notices.exists():
                        regular_notice = active_regular_notices.first()
                        class NoticeAsPopup:
                            def __init__(self, notice):
                                self.title = notice.title
                                self.description = notice.content
                                self.image = None
                                self.image_alt = ""
                                self.link_url = f"/news-events/notices/{notice.slug}/"
                                # Use translatable text instead of hardcoded
                                from django.utils.translation import gettext_lazy as _
                                self.link_text = str(_("पूरै सूचना हेर्नुहोस्"))
                                self.open_in_new_tab = False
                                self.is_active = notice.is_active
                                self.auto_close_duration = None  # Regular notices don't have auto-close by default
                        
                        popup_notice = NoticeAsPopup(regular_notice)
                
                cached_data['popup_notice'] = popup_notice
            except Exception as e:
                logger.warning(f"Error fetching fresh popup notice: {e}")
                cached_data['popup_notice'] = None
            
            return cached_data

        try:
            # 1. Page Content - Get all published content blocks for hero slider
            homepage_contents = list(HomePageContent.objects.filter(
                status=HomePageContent.Status.PUBLISHED
            ).order_by('order'))
            # Keep first one as main content for backward compatibility
            content = homepage_contents[0] if homepage_contents else None

            # 2. Featured Testimonials
            testimonials = list(Testimonial.objects.filter(
                is_featured=True, status=Testimonial.Status.PUBLISHED
            ).order_by('order')[:3])

            # 3. Statistics - Use CooperativeStatistic from about app
            stats = []
            try:
                from apps.about.models import CooperativeStatistic
                stats = list(CooperativeStatistic.objects.filter(
                    is_featured=True, is_active=True
                ).order_by('order')[:4])
            except ImportError:
                logger.warning("About app not available, using home app statistics")
                # Fallback to home app statistics
                stats = list(Statistic.objects.filter(
                    is_featured=True, status=Statistic.Status.PUBLISHED
                ).order_by('order')[:4])

            # 4. Announcements (Published & Not Expired)
            announcements = list(Announcement.objects.filter(
                is_featured=True, status=Announcement.Status.PUBLISHED
            ).exclude(
                Q(expiry_date__isnull=False) & Q(expiry_date__lt=timezone.now())
            ).order_by('-priority', '-publish_date')[:3])
            
            # 4b. Add Notices to announcements section
            try:
                from apps.news_events.models import Notice
                # Get pinned and active notices (limit to 3 more to fill up to 6 total)
                notices = list(Notice.objects.filter(
                    is_active=True,
                    is_pinned=True  # Only show pinned notices in announcements
                ).order_by('-published_date')[:3])
                
                # Combine announcements and notices, sorted by date
                all_announcements = announcements + notices
                # Sort by date (most recent first)
                all_announcements.sort(key=lambda x: x.published_date if hasattr(x, 'published_date') else x.publish_date, reverse=True)
                # Limit to 6 total items
                announcements = all_announcements[:6]
            except ImportError:
                logger.warning("News Events app not available, notices not added to announcements")
            except Exception as e:
                logger.error(f"Error fetching notices for announcements: {e}")

            # 5. Popup Notice - Get highest priority active notice
            # Check both PopupNotice and regular Notice models
            popup_notice = None
            try:
                from apps.news_events.models import PopupNotice, Notice
                now = timezone.now()
                
                # First, check PopupNotice (higher priority)
                active_popup_notices = PopupNotice.objects.filter(
                    is_active=True,  # Must be active
                    start_date__lte=now  # Must have started
                ).filter(
                    Q(end_date__isnull=True) | Q(end_date__gte=now)  # Either no end date OR not expired
                ).order_by('-priority', '-start_date')
                
                popup_notice = active_popup_notices.first() if active_popup_notices.exists() else None
                
                # If no PopupNotice, check regular Notice with show_as_popup=True
                if not popup_notice:
                    active_regular_notices = Notice.objects.filter(
                        is_active=True,
                        show_as_popup=True
                    ).order_by('-is_pinned', '-published_date')
                    
                    if active_regular_notices.exists():
                        # Convert regular Notice to popup-compatible format
                        regular_notice = active_regular_notices.first()
                        # Create a simple object that mimics PopupNotice structure
                        class NoticeAsPopup:
                            def __init__(self, notice):
                                self.title = notice.title
                                self.description = notice.content
                                self.image = None  # Regular notices don't have image field
                                self.image_alt = ""
                                self.link_url = f"/news-events/notices/{notice.slug}/"
                                # Use translatable text
                                from django.utils.translation import gettext_lazy as _
                                self.link_text = str(_("पूरै सूचना हेर्नुहोस्"))
                                self.open_in_new_tab = False
                                self.notice_type = notice.get_notice_type_display()
                                self.is_active = notice.is_active
                                self.auto_close_duration = None  # Regular notices don't have auto-close by default
                        
                        popup_notice = NoticeAsPopup(regular_notice)
                
                # Debug logging (only in debug mode)
                if settings.DEBUG and popup_notice:
                    logger.debug(f"Popup notice found: {popup_notice.title} (Active: {popup_notice.is_active})")
            except ImportError:
                logger.warning("News Events app not available, popup notice not loaded")
            except Exception as e:
                logger.error(f"Error fetching popup notice: {e}")
                popup_notice = None

            # 6. Services - Get from services app
            featured_services_list = []
            try:
                from apps.services.models import SavingsAccount, LoanType, FixedDeposit
            except ImportError:
                logger.warning("Services app not available, skipping featured services")
                SavingsAccount = LoanType = FixedDeposit = None
            
            if SavingsAccount and LoanType and FixedDeposit:
                # Get featured services from different service types
                
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
            gallery_images = []
            try:
                gallery_images = list(GalleryImage.objects.filter(
                    is_featured=True, is_active=True
                ).order_by('order')[:6])
            except Exception as e:
                logger.warning(f"Error fetching gallery images: {e}")

            context = {
                'homepage_content': content,
                'homepage_contents': homepage_contents,  # All content blocks for hero slider
                'featured_testimonials': testimonials,
                'featured_statistics': stats,
                'featured_announcements': announcements,
                'popup_notice': popup_notice,  # Popup notice for home page modal
                'featured_services': services,
                'featured_gallery': gallery_images,
                'breadcrumbs': [{'name': 'Home', 'url': '/'}]
            }

            # Cache for 5 minutes if not staff
            # Note: popup_notice is always fetched fresh, not from cache
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
                'notices': [],
                'featured_services': [],
                'featured_gallery': [],
                'error': "Unable to load content."
            }
    
    @staticmethod
    def get_content_stats():
        """Get statistics about content status"""
        from .models import HomePageContent, Testimonial, Statistic, Announcement
        
        stats = {
            'homepage_content': {
                'published': HomePageContent.objects.filter(status=HomePageContent.Status.PUBLISHED).count(),
                'draft': HomePageContent.objects.filter(status=HomePageContent.Status.DRAFT).count(),
                'scheduled': HomePageContent.objects.filter(status=HomePageContent.Status.SCHEDULED).count(),
                'archived': HomePageContent.objects.filter(status=HomePageContent.Status.ARCHIVED).count(),
            },
            'testimonials': {
                'published': Testimonial.objects.filter(status=Testimonial.Status.PUBLISHED).count(),
                'draft': Testimonial.objects.filter(status=Testimonial.Status.DRAFT).count(),
                'scheduled': Testimonial.objects.filter(status=Testimonial.Status.SCHEDULED).count(),
                'archived': Testimonial.objects.filter(status=Testimonial.Status.ARCHIVED).count(),
            },
            'statistics': {
                'published': Statistic.objects.filter(status=Statistic.Status.PUBLISHED).count(),
                'draft': Statistic.objects.filter(status=Statistic.Status.DRAFT).count(),
                'scheduled': Statistic.objects.filter(status=Statistic.Status.SCHEDULED).count(),
                'archived': Statistic.objects.filter(status=Statistic.Status.ARCHIVED).count(),
            },
            'announcements': {
                'published': Announcement.objects.filter(status=Announcement.Status.PUBLISHED).count(),
                'draft': Announcement.objects.filter(status=Announcement.Status.DRAFT).count(),
                'scheduled': Announcement.objects.filter(status=Announcement.Status.SCHEDULED).count(),
                'archived': Announcement.objects.filter(status=Announcement.Status.ARCHIVED).count(),
            },
        }
        return stats
    
    @staticmethod
    def track_variant_view(variant_id):
        """Track a view for an A/B test variant"""
        from .models import ContentVariant
        try:
            variant = ContentVariant.objects.get(pk=variant_id, is_active=True)
            variant.views += 1
            variant.save(update_fields=['views'])
            return True
        except ContentVariant.DoesNotExist:
            logger.warning(f"Variant {variant_id} not found")
            return False
    
    @staticmethod
    def track_variant_conversion(variant_id):
        """Track a conversion for an A/B test variant"""
        from .models import ContentVariant
        try:
            variant = ContentVariant.objects.get(pk=variant_id, is_active=True)
            variant.conversions += 1
            variant.save(update_fields=['conversions'])
            return True
        except ContentVariant.DoesNotExist:
            logger.warning(f"Variant {variant_id} not found")
            return False
    
    @staticmethod
    def get_winning_variant(content_type_id, object_id):
        """Get the winning variant for a content object based on conversion rate"""
        from .models import ContentVariant
        from django.contrib.contenttypes.models import ContentType
        
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
            variants = ContentVariant.objects.filter(
                content_type=content_type,
                object_id=object_id,
                is_active=True
            )
            
            if not variants.exists():
                return None
            
            # Find variant with highest conversion rate
            winning_variant = max(variants, key=lambda v: v.conversion_rate)
            return winning_variant
        except Exception as e:
            logger.error(f"Error getting winning variant: {e}")
            return None

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
            # Check if DashboardAnalyticsService is available
            from apps.dashboard.services import DashboardAnalyticsService
            
            # Prepare data compatible with record_page_view
            data = {
                'page_url': request.build_absolute_uri(),
                'page_title': title,
                'referrer': request.META.get('HTTP_REFERER', ''),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': request.META.get('REMOTE_ADDR', ''),
                'is_mobile': 'Mobile' in request.META.get('HTTP_USER_AGENT', ''),
                'browser': 'Unknown'  # Simplified
            }
            DashboardAnalyticsService.record_page_view(data, request.META)
        except ImportError:
            logger.debug("DashboardAnalyticsService not available, skipping page view tracking")
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
            # Try to use contact app's service for consolidation
            try:
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
            except ImportError:
                logger.info("Contact app service not available, using local ContactInquiry model")
            except Exception as e:
                logger.warning(f"Contact app service failed, falling back to local model: {e}")
            
            # Also create ContactInquiry for backward compatibility with admin/tests
            # This ensures the inquiry is always saved even if contact app fails
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
