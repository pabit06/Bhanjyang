"""
Production-ready settings for the home app
"""
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class HomeAppConfig:
    """Configuration class for home app production settings"""
    
    # Cache settings
    CACHE_TIMEOUTS = {
        'homepage': 300,  # 5 minutes
        'about_page': 600,  # 10 minutes
        'gallery': 900,  # 15 minutes
        'api_data': 180,  # 3 minutes
    }
    
    # Pagination settings
    PAGINATION_SIZE = 12
    
    # Security settings
    MAX_FORM_SUBMISSIONS_PER_HOUR = 10
    MAX_EMAIL_LENGTH = 254
    MAX_NAME_LENGTH = 100
    MAX_MESSAGE_LENGTH = 2000
    
    # Content limits
    MAX_FEATURED_ITEMS = {
        'testimonials': 3,
        'statistics': 4,
        'announcements': 3,
        'services': 3,
        'gallery': 6,
    }
    
    @classmethod
    def get_cache_key(cls, key_type, user_is_staff=False):
        """Generate cache key with user context"""
        staff_suffix = '_staff' if user_is_staff else ''
        return f'home_{key_type}{staff_suffix}'
    
    @classmethod
    def get_cache_timeout(cls, key_type):
        """Get cache timeout for specific content type"""
        return cls.CACHE_TIMEOUTS.get(key_type, 300)
    
    @classmethod
    def is_production(cls):
        """Check if running in production mode"""
        return getattr(settings, 'DEBUG', False) is False
    
    @classmethod
    def should_send_emails(cls):
        """Check if emails should be sent"""
        return getattr(settings, 'SEND_REAL_EMAILS', False) and cls.is_production()


class SecurityUtils:
    """Security utilities for the home app"""
    
    @staticmethod
    def sanitize_input(text, max_length=None):
        """Sanitize user input"""
        if not text:
            return ''
        
        # Strip whitespace
        text = text.strip()
        
        # Limit length
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        # Escape HTML
        from django.utils.html import escape
        return escape(text)
    
    @staticmethod
    def validate_file_upload(file, allowed_types=None, max_size=None):
        """Validate file uploads"""
        if not file:
            return True, None
        
        # Check file size
        if max_size and file.size > max_size:
            return False, f"File size exceeds {max_size} bytes"
        
        # Check file type
        if allowed_types:
            content_type = getattr(file, 'content_type', '')
            if content_type not in allowed_types:
                return False, f"File type {content_type} not allowed"
        
        return True, None
    
    @staticmethod
    def check_rate_limit(request, action, limit=None):
        """Check rate limiting for actions"""
        if not limit:
            limit = HomeAppConfig.MAX_FORM_SUBMISSIONS_PER_HOUR
        
        # Get user identifier
        user_id = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR', '')
        
        # Check cache for recent submissions
        cache_key = f'rate_limit_{action}_{user_id}'
        recent_submissions = cache.get(cache_key, 0)
        
        if recent_submissions >= limit:
            return False, "Rate limit exceeded. Please try again later."
        
        # Increment counter
        cache.set(cache_key, recent_submissions + 1, 3600)  # 1 hour
        return True, None


class PerformanceUtils:
    """Performance utilities for the home app"""
    
    @staticmethod
    def optimize_queryset(queryset, select_related=None, prefetch_related=None):
        """Optimize queryset with select_related and prefetch_related"""
        if select_related:
            queryset = queryset.select_related(*select_related)
        
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        
        return queryset
    
    @staticmethod
    def paginate_queryset(queryset, page_number, per_page=None):
        """Paginate queryset efficiently"""
        if not per_page:
            per_page = HomeAppConfig.PAGINATION_SIZE
        
        paginator = Paginator(queryset, per_page)
        
        try:
            page = paginator.page(page_number)
        except:
            page = paginator.page(1)
        
        return page, paginator
    
    @staticmethod
    def get_featured_content(model_class, limit=None, **filters):
        """Get featured content efficiently"""
        if not limit:
            limit = HomeAppConfig.MAX_FEATURED_ITEMS.get(model_class.__name__.lower(), 3)
        
        return model_class.objects.filter(
            is_featured=True,
            is_active=True,
            **filters
        ).order_by('order')[:limit]


class ContentUtils:
    """Content management utilities"""
    
    @staticmethod
    def get_active_announcements():
        """Get active announcements excluding expired ones"""
        return Announcement.objects.filter(
            is_featured=True,
            is_active=True
        ).exclude(
            Q(expiry_date__isnull=False) & Q(expiry_date__lt=timezone.now())
        ).order_by('-priority', '-publish_date')
    
    @staticmethod
    def get_homepage_content():
        """Get main homepage content"""
        return HomePageContent.objects.filter(
            is_active=True
        ).order_by('order').first()
    
    @staticmethod
    def get_gallery_categories():
        """Get gallery images grouped by category"""
        gallery_images = GalleryImage.objects.filter(
            is_active=True
        ).order_by('order', '-created_at')
        
        categories = {}
        for image in gallery_images:
            if image.category not in categories:
                categories[image.category] = []
            categories[image.category].append(image)
        
        return categories


class EmailUtils:
    """Email utilities for the home app"""
    
    @staticmethod
    def send_contact_notification(inquiry):
        """Send contact form notification email"""
        if not HomeAppConfig.should_send_emails():
            return False
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"New Contact Inquiry: {inquiry.subject}"
            message = f"""
            Name: {inquiry.name}
            Email: {inquiry.email}
            Phone: {inquiry.phone}
            Subject: {inquiry.subject}
            Message: {inquiry.message}
            Inquiry Type: {inquiry.inquiry_type}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send contact notification: {e}", exc_info=True)
            return False
    
    @staticmethod
    def send_newsletter_confirmation(subscriber):
        """Send newsletter confirmation email"""
        if not HomeAppConfig.should_send_emails():
            return False
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = "Welcome to Bhanjyang Cooperative Newsletter"
            message = f"""
            Dear {subscriber.name or 'Subscriber'},
            
            Thank you for subscribing to our newsletter! You will now receive updates about our services, events, and important announcements.
            
            Best regards,
            Bhanjyang Cooperative Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=False,
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send newsletter confirmation: {e}", exc_info=True)
            return False


# Import models for ContentUtils
try:
    from .models import Announcement, HomePageContent, GalleryImage
except ImportError:
    # Handle import errors gracefully
    pass
