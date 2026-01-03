from django.utils import timezone
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
import logging
from typing import Dict, Any, List, Optional, Tuple

from .models import (
    Subscriber, NewsArticle, Event, Category, Comment, 
    Newsletter, ContentAnalytics
)
from .security import (
    EmailSecurityManager, SpamProtectionManager, SecurityAuditLogger
)
from .performance import (
    NewsEventsCache, NewsEventsPerformanceMonitor, NewsEventsQueryOptimizer,
    NewsEventsCDNManager
)

logger = logging.getLogger(__name__)

class NewsService:
    """Service for handling News Article logic"""

    @staticmethod
    def get_home_page_data() -> Dict[str, Any]:
        """
        Get data for the news and events home page.
        Uses caching and query optimization.
        """
        # Get cache key
        cache_key = NewsEventsCache.get_article_list_cache_key(limit=6)
        
        # Try to get cached data
        cached_data = NewsEventsCache.get_cached_article_list(cache_key)
        if cached_data:
            logger.debug("Using cached news data")
            return cached_data
        
        # Get raw data with optimization
        recent_articles = NewsEventsQueryOptimizer.get_recent_articles(limit=6)
        upcoming_events = NewsEventsQueryOptimizer.get_upcoming_events(limit=3)
        featured_content = NewsEventsQueryOptimizer.get_featured_content(limit=3)
        categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
        
        # Get statistics with default values
        article_stats = NewsEventsQueryOptimizer.get_article_statistics() or {}
        event_stats = NewsEventsQueryOptimizer.get_event_statistics() or {}
        
        # Ensure all required keys exist with default 0
        article_stats.setdefault('published_articles', 0)
        article_stats.setdefault('total_views', 0)
        event_stats.setdefault('upcoming_events', 0)
        
        # Optimize image URLs
        recent_articles = NewsEventsCDNManager.get_optimized_image_urls(recent_articles)
        # Note: upcoming_events and featured_content logic for images might be needed too if not handled inside optimizer
        
        # Create cacheable context
        context = {
            'recent_articles': recent_articles,
            'upcoming_events': upcoming_events,
            'featured_content': featured_content,
            'categories': categories,
            'article_stats': article_stats,
            'event_stats': event_stats,
        }
        
        # Cache the data
        NewsEventsCache.cache_article_list(context, cache_key)
        
        return context

    @staticmethod
    def get_article_detail(slug: str, user=None, request=None) -> Dict[str, Any]:
        """
        Get article detail with view counting and security checks.
        Returns a dict with article and context, or raises Http404.
        
        Security: Checks cache for invalid slugs to prevent DoS attacks
        and reduce database load from repeated 404 requests.
        """
        from .performance import NewsEventsCache
        from django.http import Http404
        
        # Check if this slug is cached as invalid (404)
        if NewsEventsCache.is_invalid_slug_cached('article', slug):
            logger.debug(f"Invalid slug cached, raising 404: {slug}")
            raise Http404("Article not found")
        
        try:
            article = get_object_or_404(
                NewsEventsQueryOptimizer.get_optimized_article_queryset(),
                slug=slug,
                status=NewsArticle.Status.PUBLISHED
            )
        except Http404:
            # Cache the invalid slug to prevent future database queries
            NewsEventsCache.cache_invalid_slug('article', slug)
            raise
        
        # Check login requirement
        if article.require_login and (not user or not user.is_authenticated):
            if request:
                SecurityAuditLogger.log_content_action(request, 'article', article.pk, 'view', False, "Login required")
            return {'login_required': True}
        
        # Increment view count
        article.increment_view_count()
        
        if request:
            SecurityAuditLogger.log_content_action(request, 'article', article.pk, 'view', True)
        
        # Get related content
        related_articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
            category=article.category,
            status=NewsArticle.Status.PUBLISHED
        ).exclude(pk=article.pk)[:3]
        
        # Get comments
        comments = Comment.objects.filter(
            article=article,
            status=Comment.Status.APPROVED
        ).order_by('-created_at')
        
        # Note: optimized_image_url is now a property that automatically
        # returns the optimized WebP image URL, no need to set it manually
        
        return {
            'article': article,
            'related_articles': related_articles,
            'comments': comments,
            'login_required': False
        }

    @staticmethod
    def get_article_list(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get filtered and paginated article list.
        """
        category_slug = params.get('category')
        search_query = params.get('q', '').strip()
        featured_only = params.get('featured') == 'true'
        author_id = params.get('author')
        status_filter = params.get('status')
        has_image = params.get('has_image') == 'true'
        min_read_time = params.get('min_read_time')
        max_read_time = params.get('max_read_time')
        sort_by = params.get('sort_by', 'date')
        order = params.get('order', 'desc')
        page = params.get('page', 1)
        page_size = int(params.get('page_size', 12))

        # Base queryset
        articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
            status=NewsArticle.Status.PUBLISHED
        )

        # Filters
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            articles = articles.filter(category=category)
        
        if search_query:
            articles = articles.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        if featured_only:
            articles = articles.filter(is_featured=True)
            
        if author_id:
            articles = articles.filter(author_id=author_id)
            
        if has_image:
            articles = articles.exclude(image='').exclude(image__isnull=True)
            
        if min_read_time:
            try:
                articles = articles.filter(read_time__gte=int(min_read_time))
            except ValueError:
                pass
                
        if max_read_time:
            try:
                articles = articles.filter(read_time__lte=int(max_read_time))
            except ValueError:
                pass

        # Sorting
        sort_map = {
            'relevance': '-view_count',
            'date': 'published_date',
            'views': 'view_count',
            'title': 'title',
        }
        sort_field = sort_map.get(sort_by, 'published_date')
        if order == 'desc' and not sort_field.startswith('-'):
            sort_field = f'-{sort_field}'
        elif order == 'asc' and sort_field.startswith('-'):
            sort_field = sort_field[1:]
        
        articles = articles.order_by(sort_field)

        # Pagination
        page_size = min(max(1, page_size), 100)
        paginator = Paginator(articles, page_size)
        page_obj = paginator.get_page(page)

        # Optimize images
        page_obj.object_list = NewsEventsCDNManager.get_optimized_image_urls(page_obj.object_list)
        
        # Get categories for sidebar/filter
        categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')

        return {
            'page_obj': page_obj,
            'articles': page_obj,
            'categories': categories,
            'selected_category': category_slug,
            'search_query': search_query,
            'featured_only': featured_only
        }

class EventService:
    """Service for handling Event logic"""

    @staticmethod
    def get_event_detail(slug: str, request=None) -> Dict[str, Any]:
        """
        Get event detail details.
        
        Security: Checks cache for invalid slugs to prevent DoS attacks
        and reduce database load from repeated 404 requests.
        """
        from .performance import NewsEventsCache
        from django.http import Http404
        
        # Check if this slug is cached as invalid (404)
        if NewsEventsCache.is_invalid_slug_cached('event', slug):
            logger.debug(f"Invalid slug cached, raising 404: {slug}")
            raise Http404("Event not found")
        
        try:
            event = get_object_or_404(
                NewsEventsQueryOptimizer.get_optimized_event_queryset(),
                slug=slug,
                status=Event.Status.PUBLISHED
            )
        except Http404:
            # Cache the invalid slug to prevent future database queries
            NewsEventsCache.cache_invalid_slug('event', slug)
            raise
        
        event.increment_view_count()
        if request:
            SecurityAuditLogger.log_content_action(request, 'event', event.pk, 'view', True)
        
        related_events = NewsEventsQueryOptimizer.get_optimized_event_queryset().filter(
            event_type=event.event_type,
            status=Event.Status.PUBLISHED
        ).exclude(pk=event.pk)[:3]
        
        # Note: optimized_image_url is now a property that automatically
        # returns the optimized WebP image URL, no need to set it manually
        
        return {
            'event': event,
            'related_events': related_events
        }

    @staticmethod
    def get_event_list(params: Dict[str, Any]) -> Dict[str, Any]:
        """Get filtered event list"""
        event_type = params.get('type')
        upcoming_only = params.get('upcoming', 'true') == 'true'
        page = params.get('page', 1)

        events = NewsEventsQueryOptimizer.get_optimized_event_queryset().filter(
            status=Event.Status.PUBLISHED
        )

        if event_type:
            events = events.filter(event_type=event_type)
        
        if upcoming_only:
            events = events.filter(event_date__gt=timezone.now()).order_by('event_date')
        else:
            events = events.filter(event_date__lt=timezone.now()).order_by('-event_date')
            
        paginator = Paginator(events, 10)
        page_obj = paginator.get_page(page)
        
        page_obj.object_list = NewsEventsCDNManager.get_optimized_image_urls(page_obj.object_list)
        
        return {
            'page_obj': page_obj,
            'events': page_obj,
            'event_types': Event.EventType.choices,
            'selected_type': event_type,
            'upcoming_only': upcoming_only
        }

class InteractionService:
    """Service for handling user interactions like subscriptions and comments"""

    @staticmethod
    def handle_subscription(data: Dict[str, Any], request=None) -> Tuple[bool, str]:
        """Handle newsletter subscription"""
        email = data.get('email')
        try:
            with transaction.atomic():
                existing_subscriber = Subscriber.objects.filter(email=email).first()
                if existing_subscriber:
                    if existing_subscriber.status == Subscriber.Status.UNSUBSCRIBED:
                        existing_subscriber.status = Subscriber.Status.ACTIVE
                        existing_subscriber.subscribed_at = timezone.now()
                        if 'first_name' in data: existing_subscriber.first_name = data['first_name']
                        if 'last_name' in data: existing_subscriber.last_name = data['last_name']
                        existing_subscriber.save()
                        
                        if 'categories' in data:
                            existing_subscriber.categories.set(data['categories'])
                            
                        if request:
                            SecurityAuditLogger.log_subscription_attempt(request, email, True, "Reactivated")
                        return True, 'Your subscription has been reactivated!'
                    else:
                        if request:
                            SecurityAuditLogger.log_subscription_attempt(request, email, False, "Already subscribed")
                        return False, 'This email is already subscribed to our newsletter.'
                
                subscriber = Subscriber(
                    email=email,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    frequency=data.get('frequency', 'weekly')
                )
                if request:
                    subscriber.ip_address = request.META.get('REMOTE_ADDR', 'unknown')
                    subscriber.user_agent = request.META.get('HTTP_USER_AGENT', '')
                subscriber.save()
                
                if 'categories' in data:
                    subscriber.categories.set(data['categories'])
                
                if EmailSecurityManager.send_confirmation_email(subscriber):
                    if request:
                        SecurityAuditLogger.log_subscription_attempt(request, email, True, "Confirmation sent")
                    return True, 'Thank you for subscribing! Please check your email to confirm your subscription.'
                else:
                    if request:
                        SecurityAuditLogger.log_subscription_attempt(request, email, True, "Subscription saved, confirmation failed")
                    return True, 'Thank you for subscribing!'
                    
        except Exception as e:
            logger.error(f"Subscription failed: {e}")
            if request:
                SecurityAuditLogger.log_subscription_attempt(request, email, False, f"Error: {str(e)}")
            return False, 'Subscription failed. Please try again later.'

    @staticmethod
    def handle_comment_submission(data: Dict[str, Any], article_slug: str, request=None) -> Tuple[bool, str]:
        """Handle comment submission"""
        try:
            article = NewsArticle.objects.get(slug=article_slug, status=NewsArticle.Status.PUBLISHED)
            if not article.allow_comments:
                return False, 'Comments are disabled for this article.'
            
            with transaction.atomic():
                comment = Comment(
                    article=article,
                    author_name=data.get('author_name'),
                    author_email=data.get('author_email'),
                    content=data.get('content')
                )
                if request:
                    comment.ip_address = request.META.get('REMOTE_ADDR', 'unknown')
                    comment.user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                spam_check = SpamProtectionManager.check_spam_indicators(comment.content, comment.author_email, comment.ip_address)
                if spam_check['is_spam']:
                    comment.status = Comment.Status.SPAM
                    if request:
                        SecurityAuditLogger.log_content_action(request, 'comment', article.pk, 'submit', False, f"Spam detected: {', '.join(spam_check['reasons'])}")
                else:
                    comment.status = Comment.Status.PENDING
                    if request:
                        SecurityAuditLogger.log_content_action(request, 'comment', article.pk, 'submit', True)
                
                comment.save()
                article.comment_count = F('comment_count') + 1
                article.save(update_fields=['comment_count'])
                
                return True, 'Your comment has been submitted and is awaiting moderation.'
        except NewsArticle.DoesNotExist:
            return False, 'Article not found.'
        except Exception as e:
            logger.error(f"Comment submission failed: {e}")
            if request:
                pass # logging handled by caller or fallback
            return False, 'Comment submission failed. Please try again later.'
    
    @staticmethod
    def handle_share(article_slug: str, request=None) -> Tuple[bool, str]:
        """Handle article share"""
        article = get_object_or_404(NewsArticle, slug=article_slug, status=NewsArticle.Status.PUBLISHED)
        article.increment_share_count()
        if request:
            SecurityAuditLogger.log_content_action(request, 'article', article.pk, 'share', True)
        return True, 'Article shared successfully!'

class SearchService:
    """Service for handling complex searches"""

    @staticmethod
    def perform_search(params: Dict[str, Any], request=None) -> Dict[str, Any]:
        """Perform search across Articles and Events with full filtering and pagination"""
        query = params.get('query', '')
        content_type = params.get('content_type', 'all')
        category_id = params.get('category')
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        featured_only = params.get('featured_only', False)
        sort_by = params.get('sort_by', 'relevance')
        
        # Advanced filters
        author = params.get('author')
        status_filter = params.get('status')
        has_image = params.get('has_image', False)
        min_read_time = params.get('min_read_time')
        max_read_time = params.get('max_read_time')
        
        results = []
        
        # Search articles
        if content_type in ['all', 'articles']:
            articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
                status=NewsArticle.Status.PUBLISHED
            )
            
            if query:
                articles = articles.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(excerpt__icontains=query)
                )
            
            if category_id:
                articles = articles.filter(category_id=category_id)
            
            if date_from:
                articles = articles.filter(published_date__gte=date_from)
            
            if date_to:
                articles = articles.filter(published_date__lte=date_to)
            
            if featured_only:
                articles = articles.filter(is_featured=True)
            
            if author:
                articles = articles.filter(author=author)
            
            if status_filter == 'published':
                articles = articles.filter(status=NewsArticle.Status.PUBLISHED)
            elif status_filter == 'draft':
                articles = articles.filter(status=NewsArticle.Status.DRAFT)
            
            if has_image:
                articles = articles.exclude(image='').exclude(image__isnull=True)
            
            if min_read_time:
                articles = articles.filter(read_time__gte=min_read_time)
            
            if max_read_time:
                articles = articles.filter(read_time__lte=max_read_time)
            
            # Apply sorting for articles
            if sort_by == 'date':
                articles = articles.order_by('-published_date')
            elif sort_by == 'views':
                articles = articles.order_by('-view_count')
            elif sort_by == 'title':
                articles = articles.order_by('title')
            else:  # relevance
                articles = articles.order_by('-published_date')
            
            results.extend(list(articles))
        
        # Search events
        if content_type in ['all', 'events']:
            events = NewsEventsQueryOptimizer.get_optimized_event_queryset().filter(
                status=Event.Status.PUBLISHED
            )
            
            if query:
                events = events.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(short_description__icontains=query)
                )
            
            if date_from:
                events = events.filter(event_date__gte=date_from)
            
            if date_to:
                events = events.filter(event_date__lte=date_to)
            
            if featured_only:
                events = events.filter(is_featured=True)
            
            # Apply sorting for events
            if sort_by == 'date':
                events = events.order_by('-event_date')
            elif sort_by == 'views':
                events = events.order_by('-view_count')
            elif sort_by == 'title':
                events = events.order_by('title')
            else:  # relevance
                events = events.order_by('-event_date')
            
            results.extend(list(events))
            
        # Global sorting (if mixed content)
        # If 'relevance' or 'date', we might want to sort the combined list
        if len(results) > 0:
            if sort_by in ['date', 'relevance']:
                # Sort by date descending (assuming both have some date field or we rely on insertion order if we did queries right?)
                # Articles have published_date, Events have event_date.
                # Let's try to normalize for sorting
                def get_date(obj):
                    if hasattr(obj, 'published_date'): return obj.published_date
                    if hasattr(obj, 'event_date'): return obj.event_date
                    return timezone.now()
                results.sort(key=get_date, reverse=True)
            elif sort_by == 'views':
                results.sort(key=lambda x: x.view_count, reverse=True)
            elif sort_by == 'title':
                results.sort(key=lambda x: x.title)

        # Pagination
        paginator = Paginator(results, 20)
        page_num = params.get('page', 1)
        if request:
            page_num = request.GET.get('page', 1) # Prefer request param if available and params is dict from form cleaned_data
        
        page_obj = paginator.get_page(page_num)
        
        return {
            'page_obj': page_obj,
            'results': page_obj, # Alias for template compatibility if needed
            'query': query,
            'results_count': len(results)
        }


class NewsletterService:
    """Service for handling newsletter operations"""
    
    @staticmethod
    def dispatch_newsletter(newsletter_id: int) -> Dict[str, Any]:
        """
        Dispatch newsletter to all subscribers asynchronously.
        
        Args:
            newsletter_id: ID of the Newsletter object
        
        Returns:
            Dict with task information or error message
        """
        try:
            # Check if Celery is available
            try:
                from .tasks import send_newsletter_to_all, CELERY_AVAILABLE
                
                if CELERY_AVAILABLE:
                    # Dispatch asynchronously using Celery
                    result = send_newsletter_to_all.delay(newsletter_id)
                    return {
                        'success': True,
                        'task_id': result.id,
                        'message': 'Newsletter dispatch started in background',
                        'async': True
                    }
                else:
                    # Fallback to synchronous sending (not recommended for large lists)
                    logger.warning("Celery not available, sending synchronously")
                    from .tasks import send_newsletter_to_all
                    result = send_newsletter_to_all(newsletter_id)
                    return {
                        'success': True,
                        'message': result.get('message', 'Newsletter sent'),
                        'async': False
                    }
            except ImportError:
                logger.error("Newsletter tasks not available")
                return {
                    'success': False,
                    'message': 'Newsletter dispatch not configured',
                    'async': False
                }
                
        except Exception as e:
            logger.error(f"Error dispatching newsletter: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'async': False
            }
    
    @staticmethod
    def get_newsletter_status(newsletter_id: int) -> Dict[str, Any]:
        """
        Get the current status of a newsletter dispatch.
        
        Args:
            newsletter_id: ID of the Newsletter object
        
        Returns:
            Dict with newsletter status information
        """
        try:
            from .models import Newsletter
            newsletter = Newsletter.objects.get(pk=newsletter_id)
            
            return {
                'id': newsletter.id,
                'title': newsletter.title,
                'status': newsletter.status,
                'status_display': newsletter.get_status_display(),
                'total_sent': newsletter.total_sent,
                'total_opened': newsletter.total_opened,
                'total_clicked': newsletter.total_clicked,
                'sent_date': newsletter.sent_date.isoformat() if newsletter.sent_date else None,
                'scheduled_date': newsletter.scheduled_date.isoformat() if newsletter.scheduled_date else None,
            }
        except Newsletter.DoesNotExist:
            return {'error': 'Newsletter not found'}
        except Exception as e:
            logger.error(f"Error getting newsletter status: {e}", exc_info=True)
            return {'error': str(e)}
