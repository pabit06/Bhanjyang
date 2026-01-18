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
            Dictionary containing content for the homepage sections.
        """
        from .constants import CACHE_TIMEOUT_HOMEPAGE
        
        cache_key = f'homepage_data_{is_staff}'
        cached_data = cache.get(cache_key)

        if cached_data and not is_staff:
            # Always fetch popup notice fresh (not from cache)
            cached_data['popup_notice'] = HomeService._get_popup_notice()
            return cached_data

        try:
            # Fetch all data components
            context = {
                'homepage_content': HomeService._get_homepage_content(),
                'homepage_contents': HomeService._get_all_homepage_contents(),
                'featured_testimonials': HomeService._get_featured_testimonials(),
                'featured_statistics': HomeService._get_featured_statistics(),
                'featured_announcements': HomeService._get_featured_announcements(),
                'popup_notice': HomeService._get_popup_notice(),
                'featured_services': HomeService._get_featured_services(),
                'featured_gallery': HomeService._get_featured_gallery(),
                'breadcrumbs': [{'name': 'Home', 'url': '/'}]
            }

            # Cache for 5 minutes if not staff
            if not is_staff:
                try:
                    cache.set(cache_key, context, CACHE_TIMEOUT_HOMEPAGE)
                except Exception as e:
                    logger.warning(f"Failed to cache homepage data: {e}")
            
            return context

        except Exception as e:
            logger.error(f"Error fetching homepage data: {e}", exc_info=True)
            return HomeService._get_error_context(str(e))

    # =========================================================================
    # Helper Methods for Data Fetching
    # =========================================================================

    @staticmethod
    def _get_homepage_content():
        """Get the main homepage content block"""
        try:
            homepage_contents = HomeService._get_all_homepage_contents()
            return homepage_contents[0] if homepage_contents else None
        except Exception as e:
            logger.warning(f"Error fetching homepage content: {e}")
            return None

    @staticmethod
    def _get_all_homepage_contents():
        """Get all published homepage content blocks"""
        try:
            return list(HomePageContent.objects.filter(
                status=HomePageContent.Status.PUBLISHED
            ).select_related('published_by').order_by('order'))
        except Exception as e:
            logger.warning(f"Error fetching all homepage contents: {e}")
            return []

    @staticmethod
    def _get_featured_testimonials():
        """Get featured testimonials"""
        from .constants import LIMIT_TESTIMONIALS
        
        try:
            return list(Testimonial.objects.filter(
                is_featured=True, status=Testimonial.Status.PUBLISHED
            ).select_related('published_by').order_by('order')[:LIMIT_TESTIMONIALS])
        except Exception as e:
            logger.warning(f"Error fetching testimonials: {e}")
            return []

    @staticmethod
    def _get_featured_statistics():
        """Get featured statistics (preferring About app)"""
        from .constants import LIMIT_STATISTICS
        
        # Try About app first
        try:
            from apps.about.models import CooperativeStatistic
            return list(CooperativeStatistic.objects.filter(
                is_featured=True, is_active=True
            ).order_by('order')[:LIMIT_STATISTICS])
        except (ImportError, Exception):
            # Fallback to Home app
            try:
                logger.warning("Using fallback statistics from home app")
                return list(Statistic.objects.filter(
                    is_featured=True, status=Statistic.Status.PUBLISHED
                ).select_related('published_by').order_by('order')[:LIMIT_STATISTICS])
            except Exception as e:
                logger.error(f"Error fetching statistics: {e}")
                return []

    @staticmethod
    def _get_featured_announcements():
        """Get featured announcements and notices"""
        from .constants import LIMIT_ANNOUNCEMENTS, LIMIT_NOTICES, LIMIT_ANNOUNCEMENTS_TOTAL
        
        try:
            # 1. Get Announcements
            announcements = list(Announcement.objects.filter(
                is_featured=True, status=Announcement.Status.PUBLISHED
            ).select_related('published_by').exclude(
                Q(expiry_date__isnull=False) & Q(expiry_date__lt=timezone.now())
            ).order_by('-priority', '-publish_date')[:LIMIT_ANNOUNCEMENTS])
            
            # 2. Get Notices (if available)
            try:
                from apps.news_events.models import Notice
                notices = list(Notice.objects.filter(
                    is_active=True,
                    is_pinned=True
                ).order_by('-published_date')[:LIMIT_NOTICES])
                
                # Combine
                all_items = announcements + notices
                # Sort by date
                all_items.sort(key=lambda x: getattr(x, 'published_date', getattr(x, 'publish_date', None)), reverse=True)
                return all_items[:LIMIT_ANNOUNCEMENTS_TOTAL]
                
            except ImportError:
                return announcements[:LIMIT_ANNOUNCEMENTS_TOTAL]
                
        except Exception as e:
            logger.error(f"Error fetching announcements: {e}")
            return []

    @staticmethod
    def _get_popup_notice():
        """Get the most relevant active popup notice"""
        try:
            from apps.news_events.models import PopupNotice, Notice
            now = timezone.now()
            
            # 1. Check dedicated PopupNotice (Highest Priority)
            popup = PopupNotice.objects.filter(
                is_active=True,
                start_date__lte=now
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=now)
            ).order_by('-priority', '-start_date').first()
            
            if popup:
                return popup
                
            # 2. Check regular Notice with show_as_popup=True
            regular_notice = Notice.objects.filter(
                is_active=True,
                show_as_popup=True
            ).order_by('-is_pinned', '-published_date').first()
            
            if regular_notice:
                return HomeService._wrap_notice_as_popup(regular_notice)
                
            return None
            
        except (ImportError, Exception) as e:
            if isinstance(e, ImportError):
                logger.debug("News app not available for popup notices")
            else:
                logger.warning(f"Error fetching popup notice: {e}")
            return None

    @staticmethod
    def _wrap_notice_as_popup(notice):
        """Wrap a regular Notice to look like a PopupNotice"""
        from django.utils.translation import gettext_lazy as _
        
        class NoticeAsPopup:
            def __init__(self, n):
                self.title = n.title
                self.description = n.content
                self.image = None
                self.image_alt = ""
                self.link_url = f"/news-events/notices/{n.slug}/"
                self.link_text = str(_("पूरै सूचना हेर्नुहोस्"))
                self.open_in_new_tab = False
                self.is_active = n.is_active
                self.auto_close_duration = None
                
        return NoticeAsPopup(notice)

    @staticmethod
    def _get_featured_services():
        """Get featured services from Services app"""
        from .constants import LIMIT_SERVICES, DEFAULT_SERVICE_COLOR, DEFAULT_LOAN_COLOR, DEFAULT_FD_COLOR
        services_list = []
        
        try:
            from apps.services.models import SavingsAccount, LoanType, FixedDeposit
            
            # 1. Savings
            savings = SavingsAccount.objects.filter(
                is_featured=True, is_active=True
            ).order_by('-interest_rate').first()
            
            if savings:
                services_list.append({
                    'title': savings.english_name,
                    'description': savings.description or f"Interest rate: {savings.interest_rate}%",
                    'icon': savings.icon or 'fas fa-piggy-bank',
                    'interest_rate': f"Up to {savings.interest_rate}%",
                    'link_url': savings.get_absolute_url(),
                    'link_text': 'View Details',
                    'color': savings.color or DEFAULT_SERVICE_COLOR
                })
                
            # 2. Loans
            loan = LoanType.objects.filter(
                is_featured=True, is_active=True
            ).order_by('english_name').first()
            
            if loan:
                rate_text = f"{loan.annual_interest_rate}%" if loan.annual_interest_rate else "Contact us"
                services_list.append({
                    'title': loan.english_name,
                    'description': loan.description or "Flexible loan options",
                    'icon': loan.icon or 'fas fa-hand-holding-usd',
                    'interest_rate': f"From {rate_text}",
                    'link_url': loan.get_absolute_url(),
                    'link_text': 'Explore Options',
                    'color': loan.color or DEFAULT_LOAN_COLOR
                })
                
            # 3. Fixed Deposit
            fd = FixedDeposit.objects.filter(
                is_active=True
            ).order_by('-interest_rate').first()
            
            if fd:
                services_list.append({
                    'title': f"Fixed Deposit ({fd.get_duration_months_display()})",
                    'description': "Secure your future with fixed deposits",
                    'icon': 'fas fa-comments-dollar',
                    'interest_rate': f"Up to {fd.interest_rate}%",
                    'link_url': reverse('services:fixed_deposit_list'),
                    'link_text': 'View Rates',
                    'color': DEFAULT_FD_COLOR
                })
                
            return services_list[:LIMIT_SERVICES]
            
        except (ImportError, Exception):
            logger.warning("Services app not available or error fetching services")
            return []

    @staticmethod
    def _get_featured_gallery():
        """Get featured gallery images"""
        from .constants import LIMIT_GALLERY
        try:
            return list(GalleryImage.objects.filter(
                is_featured=True, is_active=True
            ).order_by('order')[:LIMIT_GALLERY])
        except Exception:
            return []

    @staticmethod
    def _get_error_context(error_msg):
        """Return safe error context"""
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
