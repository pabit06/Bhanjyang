"""
Social Media Integration for News Events App.

Provides social media sharing functionality for articles and events.
"""
from typing import Dict, Any, Optional
from django.urls import reverse
from django.conf import settings
from django.utils.html import escape
import logging
import urllib.parse

from .models import NewsArticle, Event

logger = logging.getLogger(__name__)


class SocialMediaService:
    """Service for social media integration and sharing."""
    
    @staticmethod
    def get_share_urls(
        content_type: str,
        content_id: int,
        title: str,
        description: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate social media sharing URLs.
        
        Args:
            content_type: 'article' or 'event'
            content_id: Content ID
            title: Content title
            description: Content description/excerpt
            image_url: Optional image URL
            
        Returns:
            Dictionary with social media platform URLs
        """
        # Build absolute URL
        if content_type == 'article':
            path = reverse('news_events:article-detail', kwargs={'slug': ''})
            # We'll need the actual slug, so this is a template
            # In practice, you'd pass the full URL
            base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://example.com'
        else:
            path = reverse('news_events:event-detail', kwargs={'slug': ''})
            base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://example.com'
        
        # For now, return template URLs - in practice, you'd build the full URL
        # This is a helper that would be called with the actual content object
        return SocialMediaService._build_share_urls(base_url, title, description, image_url)
    
    @staticmethod
    def _build_share_urls(
        url: str,
        title: str,
        description: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, str]:
        """Build share URLs for different platforms."""
        encoded_url = urllib.parse.quote(url)
        encoded_title = urllib.parse.quote(title)
        encoded_description = urllib.parse.quote(description or '')
        
        return {
            'facebook': f'https://www.facebook.com/sharer/sharer.php?u={encoded_url}',
            'twitter': f'https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}',
            'linkedin': f'https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}',
            'whatsapp': f'https://wa.me/?text={encoded_title}%20{encoded_url}',
            'telegram': f'https://t.me/share/url?url={encoded_url}&text={encoded_title}',
            'email': f'mailto:?subject={encoded_title}&body={encoded_description}%20{encoded_url}',
        }
    
    @staticmethod
    def get_article_share_urls(article: NewsArticle) -> Dict[str, str]:
        """
        Get social media share URLs for an article.
        
        Args:
            article: NewsArticle instance
            
        Returns:
            Dictionary with social media platform URLs
        """
        base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://example.com'
        article_url = f"{base_url}{article.get_absolute_url()}"
        
        description = article.excerpt or article.title
        image_url = article.optimized_image_url or ''
        if image_url and not image_url.startswith('http'):
            image_url = f"{base_url}{image_url}"
        
        return SocialMediaService._build_share_urls(
            url=article_url,
            title=article.title,
            description=description,
            image_url=image_url
        )
    
    @staticmethod
    def get_event_share_urls(event: Event) -> Dict[str, str]:
        """
        Get social media share URLs for an event.
        
        Args:
            event: Event instance
            
        Returns:
            Dictionary with social media platform URLs
        """
        base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://example.com'
        event_url = f"{base_url}{event.get_absolute_url()}"
        
        description = event.short_description or event.title
        image_url = ''
        if hasattr(event, 'image') and event.image:
            try:
                image_url = event.image.url
                if not image_url.startswith('http'):
                    image_url = f"{base_url}{image_url}"
            except:
                pass
        
        return SocialMediaService._build_share_urls(
            url=event_url,
            title=event.title,
            description=description,
            image_url=image_url
        )
    
    @staticmethod
    def track_social_share(
        content_type: str,
        content_id: int,
        platform: str,
        request=None
    ) -> bool:
        """
        Track social media share.
        
        Args:
            content_type: 'article' or 'event'
            content_id: Content ID
            platform: Social media platform name
            request: HTTP request object
            
        Returns:
            True if tracked successfully
        """
        try:
            if content_type == 'article':
                article = NewsArticle.objects.get(pk=content_id)
                article.increment_share_count()
                
                # Track in analytics if available
                from .models import ContentAnalytics
                from django.utils import timezone
                analytics, _ = ContentAnalytics.objects.get_or_create(
                    content_type='article',
                    content_id=content_id,
                    date=timezone.now().date(),
                    defaults={'shares': 0}
                )
                analytics.shares = (analytics.shares or 0) + 1
                analytics.save()
                
            elif content_type == 'event':
                event = Event.objects.get(pk=content_id)
                # Events might not have share_count, so we'll track in analytics
                from .models import ContentAnalytics
                from django.utils import timezone
                analytics, _ = ContentAnalytics.objects.get_or_create(
                    content_type='event',
                    content_id=content_id,
                    date=timezone.now().date(),
                    defaults={'shares': 0}
                )
                analytics.shares = (analytics.shares or 0) + 1
                analytics.save()
            
            # Log the share
            if request:
                from .security import SecurityAuditLogger
                SecurityAuditLogger.log_content_action(
                    request, content_type, content_id, 'share', True, f"Shared on {platform}"
                )
            
            logger.info(f"Social share tracked: {content_type} {content_id} on {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking social share: {e}")
            return False
    
    @staticmethod
    def get_open_graph_meta(article: Optional[NewsArticle] = None, event: Optional[Event] = None) -> Dict[str, str]:
        """
        Generate Open Graph meta tags for social media sharing.
        
        Args:
            article: Optional NewsArticle instance
            event: Optional Event instance
            
        Returns:
            Dictionary with Open Graph meta tags
        """
        base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://example.com'
        
        if article:
            url = f"{base_url}{article.get_absolute_url()}"
            title = article.title
            description = article.excerpt or article.title
            image = article.optimized_image_url or ''
            if image and not image.startswith('http'):
                image = f"{base_url}{image}"
            og_type = 'article'
        elif event:
            url = f"{base_url}{event.get_absolute_url()}"
            title = event.title
            description = event.short_description or event.title
            image = ''
            if hasattr(event, 'image') and event.image:
                try:
                    image = event.image.url
                    if not image.startswith('http'):
                        image = f"{base_url}{image}"
                except:
                    pass
            og_type = 'event'
        else:
            return {}
        
        site_name = getattr(settings, 'SITE_NAME', 'Bhanjyang Cooperative')
        
        return {
            'og:title': escape(title),
            'og:description': escape(description),
            'og:url': url,
            'og:type': og_type,
            'og:image': image,
            'og:site_name': site_name,
            'twitter:card': 'summary_large_image',
            'twitter:title': escape(title),
            'twitter:description': escape(description),
            'twitter:image': image,
        }

