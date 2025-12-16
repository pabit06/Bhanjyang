import logging
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

# Direct imports from model for specific non-service needs (like RSS)
from .models import NewsArticle, Event, Category, Subscriber

from .forms import (
    SubscriptionForm, CommentForm, ContentSearchForm
)
from .services import (
    NewsService, EventService, InteractionService, SearchService
)
from .security import (
    rate_limit_subscriptions, rate_limit_comments
)
from .performance import (
    performance_monitor, NewsEventsQueryOptimizer
)

logger = logging.getLogger(__name__)

class NewsHomeView(View):
    """Main news and events page"""
    
    @method_decorator(performance_monitor)
    def get(self, request):
        context = NewsService.get_home_page_data()
        context['subscription_form'] = SubscriptionForm()
        return render(request, 'news_events/home.html', context)

class ArticleDetailView(View):
    """Article detail page"""
    
    @method_decorator(performance_monitor)
    def get(self, request, slug):
        data = NewsService.get_article_detail(slug, request.user, request)
        
        if data.get('login_required'):
            messages.warning(request, "Please log in to view this article.")
            return redirect('auth:login')
            
        context = {
            'article': data['article'],
            'related_articles': data['related_articles'],
            'comments': data['comments'],
            'comment_form': CommentForm(),
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'News & Events', 'url': '/news-events/'},
                {'name': data['article'].title, 'url': data['article'].get_absolute_url()}
            ]
        }
        return render(request, 'news_events/article_detail.html', context)

class EventDetailView(View):
    """Event detail page"""
    
    @method_decorator(performance_monitor)
    def get(self, request, slug):
        data = EventService.get_event_detail(slug, request)
        context = {
            'event': data['event'],
            'related_events': data['related_events'],
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'News & Events', 'url': '/news-events/'},
                {'name': 'Events', 'url': '/news-events/events/'},
                {'name': data['event'].title, 'url': data['event'].get_absolute_url()}
            ]
        }
        return render(request, 'news_events/event_detail.html', context)

class ArticleListView(View):
    """Article listing with filters"""
    
    @method_decorator(performance_monitor)
    def get(self, request):
        data = NewsService.get_article_list(request.GET)
        context = data
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'News & Events', 'url': '/news-events/'},
            {'name': 'All Articles', 'url': '/news-events/articles/'}
        ]
        return render(request, 'news_events/article_list.html', context)

class EventListView(View):
    """Event listing with filters"""
    
    @method_decorator(performance_monitor)
    def get(self, request):
        data = EventService.get_event_list(request.GET)
        context = data
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'News & Events', 'url': '/news-events/'},
            {'name': 'Events', 'url': '/news-events/events/'}
        ]
        return render(request, 'news_events/event_list.html', context)

class SubscriptionView(View):
    """Handle newsletter subscriptions"""
    
    @method_decorator(rate_limit_subscriptions)
    def post(self, request):
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            success, message = InteractionService.handle_subscription(form.cleaned_data, request)
            return JsonResponse({'success': success, 'message': message})
        else:
            error = form.errors.get('email', ['Invalid email.'])[0]
            # Log failure via specialized service if strict logging is needed,
            # but InteractionService logs inside handle_subscription only.
            # Here we might want to log invalid form attempts too.
            # Simplified for brevity as service layer handles logic.
            return JsonResponse({'success': False, 'message': error})

class CommentSubmissionView(View):
    """Handle comment submissions"""
    
    @method_decorator(rate_limit_comments)
    def post(self, request, article_slug):
        form = CommentForm(request.POST)
        if form.is_valid():
            success, message = InteractionService.handle_comment_submission(
                form.cleaned_data, article_slug, request
            )
            return JsonResponse({'success': success, 'message': message})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid comment data.'})

class ArticleShareView(View):
    """Handle article sharing analytics"""
    
    def post(self, request, article_slug):
        success, message = InteractionService.handle_share(article_slug, request)
        return JsonResponse({'success': success, 'message': message})

class SearchView(View):
    """Global search view"""
    
    @method_decorator(performance_monitor)
    def get(self, request):
        form = ContentSearchForm(request.GET)
        context = {
            'form': form,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'News & Events', 'url': '/news-events/'},
                {'name': 'Search', 'url': '/news-events/search/'}
            ]
        }
        
        if form.is_valid():
            results_data = SearchService.perform_search(form.cleaned_data, request)
            context.update(results_data)
            return render(request, 'news_events/search_results.html', context)
        
        return render(request, 'news_events/search.html', context)

# ... (Previous imports and standard views)

@staff_member_required
def analytics_dashboard_view(request):
    """Staff analytics dashboard"""
    context = {'GA_TRACKING_ID': getattr(settings, 'GA_TRACKING_ID', '')}
    return render(request, 'news_events/analytics_dashboard.html', context)

@login_required
def confirm_subscription_view(request, token):
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token)
        if not subscriber.is_confirmed:
            subscriber.is_confirmed = True
            subscriber.confirmed_at = timezone.now()
            subscriber.save()
            messages.success(request, "Your subscription has been confirmed! Thank you.")
        else:
            messages.info(request, "Your subscription is already confirmed.")
    except Subscriber.DoesNotExist:
        messages.error(request, "Invalid confirmation token.")
    return redirect('news_events:home')

@login_required
def unsubscribe_view(request, token):
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token)
        subscriber.status = Subscriber.Status.UNSUBSCRIBED
        subscriber.save()
        messages.success(request, "You have been unsubscribed.")
    except Subscriber.DoesNotExist:
        messages.error(request, "Invalid token.")
    return redirect('news_events:home')

def rss_feed_view(request):
    """RSS Feed"""
    articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
        status=NewsArticle.Status.PUBLISHED
    ).order_by('-published_date')[:15]
    
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

# Initializing Legacy Function Names for URL Compatibility if needed,
# or better yet, I should update urls.py to use the new classes.
news_events_home_view = NewsHomeView.as_view()
article_detail_view = ArticleDetailView.as_view()
event_detail_view = EventDetailView.as_view()
article_list_view = ArticleListView.as_view()
event_list_view = EventListView.as_view()
subscribe_view = SubscriptionView.as_view()
comment_submit_view = CommentSubmissionView.as_view()
share_article_view = ArticleShareView.as_view()
search_view = SearchView.as_view()
