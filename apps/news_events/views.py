# news_events/views.py

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from .models import NewsArticle, Event, Category, Subscriber, Comment, Newsletter, ContentAnalytics
from .forms import (
    NewsArticleForm, EventForm, CategoryForm, SubscriptionForm, 
    CommentForm, NewsletterForm, ContentSearchForm, BulkActionForm
)
from .security import (
    ContentSecurityValidator, SpamProtectionManager, RateLimitManager,
    SecurityAuditLogger, EmailSecurityManager, rate_limit_subscriptions,
    rate_limit_comments, require_content_permission
)
from .performance import (
    NewsEventsCache, NewsEventsPerformanceMonitor, NewsEventsQueryOptimizer,
    NewsEventsCDNManager, performance_monitor
)

logger = logging.getLogger(__name__)

@performance_monitor
def news_events_home_view(request):
    """
    Main news and events page with enhanced features
    """
    # Get cache key
    cache_key = NewsEventsCache.get_article_list_cache_key(limit=6)
    
    # Try to get cached data
    cached_data = NewsEventsCache.get_cached_article_list(cache_key)
    if cached_data:
        logger.debug("Using cached news data")
        # Add non-picklable objects to cached context
        context = cached_data.copy()
        context.update({
            'subscription_form': SubscriptionForm(),
        })
        return render(request, 'news_events/home.html', context)
    
    # Get recent articles with optimization
    recent_articles = NewsEventsQueryOptimizer.get_recent_articles(limit=6)
    upcoming_events = NewsEventsQueryOptimizer.get_upcoming_events(limit=3)
    featured_content = NewsEventsQueryOptimizer.get_featured_content(limit=3)
    categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
    
    # Get statistics
    article_stats = NewsEventsQueryOptimizer.get_article_statistics()
    event_stats = NewsEventsQueryOptimizer.get_event_statistics()
    
    # Optimize image URLs
    recent_articles = NewsEventsCDNManager.get_optimized_image_urls(recent_articles)
    
    # Create context with picklable data only
    cacheable_context = {
        'recent_articles': recent_articles,
        'upcoming_events': upcoming_events,
        'featured_content': featured_content,
        'categories': categories,
        'article_stats': article_stats,
        'event_stats': event_stats,
    }
    
    # Cache the picklable data
    NewsEventsCache.cache_article_list(cacheable_context, cache_key)
    
    # Add non-picklable objects to context after caching
    context = cacheable_context.copy()
    context.update({
        'subscription_form': SubscriptionForm(),
    })
    
    return render(request, 'news_events/home.html', context)

@staff_member_required
def analytics_dashboard_view(request):
    """Simple analytics dashboard page view - staff only"""
    context = {
        'GA_TRACKING_ID': getattr(settings, 'GA_TRACKING_ID', ''),
    }
    return render(request, 'news_events/analytics_dashboard.html', context)

@performance_monitor
def article_detail_view(request, slug):
    """
    Article detail view with analytics and security
    """
    article = get_object_or_404(
        NewsEventsQueryOptimizer.get_optimized_article_queryset(),
        slug=slug,
        status=NewsArticle.Status.PUBLISHED
    )
    
    # Check if login is required
    if article.require_login and not request.user.is_authenticated:
        SecurityAuditLogger.log_content_action(request, 'article', article.pk, 'view', False, "Login required")
        messages.warning(request, "Please log in to view this article.")
        return redirect('auth:login')
    
    # Increment view count
    article.increment_view_count()
    
    # Log successful view
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
    
    # Optimize image URL
    article.optimized_image_url = NewsEventsCDNManager.optimize_image_url(article.image)
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
        'comment_form': CommentForm(),
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'News & Events', 'url': '/news-events/'},
            {'name': article.title, 'url': article.get_absolute_url()}
        ],
    }
    
    return render(request, 'news_events/article_detail.html', context)

@performance_monitor
def event_detail_view(request, slug):
    """
    Event detail view with analytics
    """
    event = get_object_or_404(
        NewsEventsQueryOptimizer.get_optimized_event_queryset(),
        slug=slug,
        status=Event.Status.PUBLISHED
    )
    
    # Increment view count
    event.increment_view_count()
    
    # Log successful view
    SecurityAuditLogger.log_content_action(request, 'event', event.pk, 'view', True)
    
    # Get related events
    related_events = NewsEventsQueryOptimizer.get_optimized_event_queryset().filter(
        event_type=event.event_type,
        status=Event.Status.PUBLISHED
    ).exclude(pk=event.pk)[:3]
    
    # Optimize image URL
    event.optimized_image_url = NewsEventsCDNManager.optimize_image_url(event.image)
    
    context = {
        'event': event,
        'related_events': related_events,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'News & Events', 'url': '/news-events/'},
            {'name': 'Events', 'url': '/news-events/events/'},
            {'name': event.title, 'url': event.get_absolute_url()}
        ],
    }
    
    return render(request, 'news_events/event_detail.html', context)

@performance_monitor
def article_list_view(request):
    """
    Article list view with advanced filtering and pagination
    """
    # Get filter parameters
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()
    featured_only = request.GET.get('featured') == 'true'
    page = request.GET.get('page', 1)
    
    # Advanced filters from ContentSearchForm
    author_id = request.GET.get('author')
    status_filter = request.GET.get('status')
    has_image = request.GET.get('has_image') == 'true'
    min_read_time = request.GET.get('min_read_time')
    max_read_time = request.GET.get('max_read_time')
    sort_by = request.GET.get('sort_by', 'date')
    order = request.GET.get('order', 'desc')
    page_size = int(request.GET.get('page_size', 12))
    
    # Build queryset
    articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
        status=NewsArticle.Status.PUBLISHED
    )
    
    # Apply filters
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
    
    # Advanced filters
    if author_id:
        articles = articles.filter(author_id=author_id)
    
    if status_filter == 'published':
        articles = articles.filter(status=NewsArticle.Status.PUBLISHED)
    elif status_filter == 'draft':
        articles = articles.filter(status=NewsArticle.Status.DRAFT)
    
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
    
    # Apply sorting
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
    
    # Paginate with custom page size
    page_size = min(max(1, page_size), 100)  # Limit between 1-100
    paginator = Paginator(articles, page_size)
    page_obj = paginator.get_page(page)
    
    # Optimize image URLs
    page_obj.object_list = NewsEventsCDNManager.get_optimized_image_urls(page_obj.object_list)
    
    # Get categories for filter
    categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
        'featured_only': featured_only,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'News & Events', 'url': '/news-events/'},
            {'name': 'All Articles', 'url': '/news-events/articles/'}
        ],
    }
    
    return render(request, 'news_events/article_list.html', context)

@performance_monitor
def event_list_view(request):
    """
    Event list view with filtering
    """
    event_type = request.GET.get('type')
    upcoming_only = request.GET.get('upcoming', 'true') == 'true'
    page = request.GET.get('page', 1)
    
    # Build queryset
    events = NewsEventsQueryOptimizer.get_optimized_event_queryset().filter(
        status=Event.Status.PUBLISHED
    )
    
    # Apply filters
    if event_type:
        events = events.filter(event_type=event_type)
    
    if upcoming_only:
        events = events.filter(event_date__gt=timezone.now())
        events = events.order_by('event_date')
    else:
        events = events.filter(event_date__lt=timezone.now())
        events = events.order_by('-event_date')
    
    # Paginate
    paginator = Paginator(events, 10)
    page_obj = paginator.get_page(page)
    
    # Optimize image URLs
    page_obj.object_list = NewsEventsCDNManager.get_optimized_image_urls(page_obj.object_list)
    
    context = {
        'page_obj': page_obj,
        'event_types': Event.EventType.choices,
        'selected_type': event_type,
        'upcoming_only': upcoming_only,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'News & Events', 'url': '/news-events/'},
            {'name': 'Events', 'url': '/news-events/events/'}
        ],
    }
    
    return render(request, 'news_events/event_list.html', context)

@rate_limit_subscriptions
@require_http_methods(["POST"])
def subscribe_view(request):
    """
    Newsletter subscription with enhanced security
    """
    form = SubscriptionForm(request.POST)
    
    if form.is_valid():
        try:
            with transaction.atomic():
                subscriber = form.save(commit=False)
                
                # Add security information
                subscriber.ip_address = request.META.get('REMOTE_ADDR', 'unknown')
                subscriber.user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                # Check if email already exists
                existing_subscriber = Subscriber.objects.filter(email=subscriber.email).first()
                if existing_subscriber:
                    if existing_subscriber.status == Subscriber.Status.UNSUBSCRIBED:
                        # Reactivate subscription
                        existing_subscriber.status = Subscriber.Status.ACTIVE
                        existing_subscriber.subscribed_at = timezone.now()
                        existing_subscriber.save()
                        SecurityAuditLogger.log_subscription_attempt(request, subscriber.email, True, "Reactivated")
                        return JsonResponse({
                            'success': True, 
                            'message': 'Your subscription has been reactivated!'
                        })
                    else:
                        SecurityAuditLogger.log_subscription_attempt(request, subscriber.email, False, "Already subscribed")
                        return JsonResponse({
                            'success': False, 
                            'message': 'This email is already subscribed to our newsletter.'
                        })
                
                # Save new subscriber
                subscriber.save()
                form.save_m2m()  # Save categories
                
                # Send confirmation email
                if EmailSecurityManager.send_confirmation_email(subscriber):
                    SecurityAuditLogger.log_subscription_attempt(request, subscriber.email, True, "Confirmation sent")
                    return JsonResponse({
                        'success': True, 
                        'message': 'Thank you for subscribing! Please check your email to confirm your subscription.'
                    })
                else:
                    SecurityAuditLogger.log_subscription_attempt(request, subscriber.email, True, "Subscription saved, confirmation failed")
                    return JsonResponse({
                        'success': True, 
                        'message': 'Thank you for subscribing!'
                    })
                
        except Exception as e:
            logger.error(f"Subscription failed: {e}")
            SecurityAuditLogger.log_subscription_attempt(request, request.POST.get('email', ''), False, f"Error: {str(e)}")
            return JsonResponse({
                'success': False, 
                'message': 'Subscription failed. Please try again later.'
            })
    else:
        error_message = form.errors.get('email', ['Invalid email address.'])[0]
        SecurityAuditLogger.log_subscription_attempt(request, request.POST.get('email', ''), False, error_message)
        return JsonResponse({
            'success': False, 
            'message': error_message
        })

@rate_limit_comments
@require_http_methods(["POST"])
def comment_submit_view(request, article_slug):
    """
    Comment submission with spam protection
    """
    article = get_object_or_404(NewsArticle, slug=article_slug, status=NewsArticle.Status.PUBLISHED)
    
    if not article.allow_comments:
        return JsonResponse({
            'success': False, 
            'message': 'Comments are disabled for this article.'
        })
    
    form = CommentForm(request.POST)
    
    if form.is_valid():
        try:
            with transaction.atomic():
                comment = form.save(commit=False)
                comment.article = article
                
                # Add security information
                comment.ip_address = request.META.get('REMOTE_ADDR', 'unknown')
                comment.user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                # Check for spam
                spam_check = SpamProtectionManager.check_spam_indicators(
                    comment.content, 
                    comment.author_email, 
                    comment.ip_address
                )
                
                if spam_check['is_spam']:
                    comment.status = Comment.Status.SPAM
                    SecurityAuditLogger.log_content_action(
                        request, 'comment', article.pk, 'submit', False, 
                        f"Spam detected: {', '.join(spam_check['reasons'])}"
                    )
                else:
                    comment.status = Comment.Status.PENDING
                    SecurityAuditLogger.log_content_action(request, 'comment', article.pk, 'submit', True)
                
                comment.save()
                
                # Update article comment count
                article.comment_count = F('comment_count') + 1
                article.save(update_fields=['comment_count'])
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Your comment has been submitted and is awaiting moderation.'
                })
                
        except Exception as e:
            logger.error(f"Comment submission failed: {e}")
            SecurityAuditLogger.log_content_action(request, 'comment', article.pk, 'submit', False, f"Error: {str(e)}")
            return JsonResponse({
                'success': False, 
                'message': 'Comment submission failed. Please try again later.'
            })
    else:
        error_message = form.errors.get('content', ['Invalid comment.'])[0]
        SecurityAuditLogger.log_content_action(request, 'comment', article.pk, 'submit', False, error_message)
        return JsonResponse({
            'success': False, 
            'message': error_message
        })

@require_http_methods(["POST"])
def share_article_view(request, article_slug):
    """
    Article sharing with analytics
    """
    article = get_object_or_404(NewsArticle, slug=article_slug, status=NewsArticle.Status.PUBLISHED)
    
    # Increment share count
    article.increment_share_count()
    
    # Log sharing
    SecurityAuditLogger.log_content_action(request, 'article', article.pk, 'share', True)
    
    return JsonResponse({
        'success': True, 
        'message': 'Article shared successfully!'
    })

@performance_monitor
def search_view(request):
    """
    Advanced content search with comprehensive filters
    """
    form = ContentSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get('query', '')
        content_type = form.cleaned_data.get('content_type', 'all')
        category = form.cleaned_data.get('category')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        featured_only = form.cleaned_data.get('featured_only', False)
        sort_by = form.cleaned_data.get('sort_by', 'relevance')
        
        # New advanced filters
        author = form.cleaned_data.get('author')
        status_filter = form.cleaned_data.get('status')
        has_image = form.cleaned_data.get('has_image', False)
        min_read_time = form.cleaned_data.get('min_read_time')
        max_read_time = form.cleaned_data.get('max_read_time')
        
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
            
            if category:
                articles = articles.filter(category=category)
            
            if date_from:
                articles = articles.filter(published_date__gte=date_from)
            
            if date_to:
                articles = articles.filter(published_date__lte=date_to)
            
            if featured_only:
                articles = articles.filter(is_featured=True)
            
            # Apply new advanced filters
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
            
            # Apply sorting
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
            
            # Apply sorting
            if sort_by == 'date':
                events = events.order_by('-event_date')
            elif sort_by == 'views':
                events = events.order_by('-view_count')
            elif sort_by == 'title':
                events = events.order_by('title')
            else:  # relevance
                events = events.order_by('-event_date')
            
            results.extend(list(events))
        
        # Paginate results
        paginator = Paginator(results, 20)
        page_obj = paginator.get_page(request.GET.get('page', 1))
        
        context = {
            'form': form,
            'page_obj': page_obj,
            'query': query,
            'results_count': len(results),
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'News & Events', 'url': '/news-events/'},
                {'name': 'Search', 'url': '/news-events/search/'}
            ],
        }
        
        return render(request, 'news_events/search_results.html', context)
    
    else:
        context = {
            'form': form,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'News & Events', 'url': '/news-events/'},
                {'name': 'Search', 'url': '/news-events/search/'}
            ],
        }
        return render(request, 'news_events/search.html', context)

@login_required
def confirm_subscription_view(request, token):
    """
    Confirm newsletter subscription
    """
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token)
        
        if subscriber.is_confirmed:
            messages.info(request, "Your subscription is already confirmed.")
        else:
            subscriber.is_confirmed = True
            subscriber.confirmed_at = timezone.now()
            subscriber.save()
            messages.success(request, "Your subscription has been confirmed! Thank you.")
        
        return redirect('news_events:home')
        
    except Subscriber.DoesNotExist:
        messages.error(request, "Invalid confirmation token.")
        return redirect('news_events:home')

@login_required
def unsubscribe_view(request, token):
    """
    Unsubscribe from newsletter
    """
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token)
        subscriber.status = Subscriber.Status.UNSUBSCRIBED
        subscriber.save()
        messages.success(request, "You have been unsubscribed from our newsletter.")
        
    except Subscriber.DoesNotExist:
        messages.error(request, "Invalid unsubscribe token.")
    
    return redirect('news_events:home')

# RSS Feed views
def rss_feed_view(request):
    """
    RSS feed for articles and upcoming events
    """
    articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
        status=NewsArticle.Status.PUBLISHED
    ).order_by('-published_date')[:15]
    
    # Include upcoming events
    events = NewsEventsQueryOptimizer.get_optimized_event_queryset().filter(
        status=Event.Status.PUBLISHED,
        event_date__gte=timezone.now()
    ).order_by('event_date')[:10]
    
    context = {
        'articles': articles,
        'events': events,
        'site_url': getattr(settings, 'SITE_URL', request.build_absolute_uri('/')),
        'site_name': getattr(settings, 'SITE_NAME', 'Bhanjyang Cooperative'),
    }
    
    response = render(request, 'news_events/rss.xml', context)
    response['Content-Type'] = 'application/rss+xml; charset=utf-8'
    return response
