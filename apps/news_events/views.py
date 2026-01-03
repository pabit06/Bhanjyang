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
from django.utils.translation import activate, gettext_lazy as _
from django.http import Http404

from apps.core.view_mixins import NepaliLanguageMixin

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

class NewsHomeView(NepaliLanguageMixin, View):
    """Main news and events page"""
    
    @method_decorator(performance_monitor)
    def get(self, request):
        try:
            context = NewsService.get_home_page_data()
            context['subscription_form'] = SubscriptionForm()
            context['breadcrumbs'] = [
                {'name': 'Home', 'url': '/'},
                {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'}
            ]
            return render(request, 'news_events/home.html', context)
        except Exception as e:
            logger.error(f"Error loading news home page: {e}", exc_info=True)
            messages.error(request, _("समाचार पृष्ठ लोड गर्न असफल भयो। कृपया पछि फेरि प्रयास गर्नुहोस्।"))
            # Try to get basic data even on error
            try:
                from .models import NewsArticle, Event, Category
                recent_articles = NewsArticle.objects.filter(
                    status=NewsArticle.Status.PUBLISHED
                ).order_by('-published_date')[:6]
                upcoming_events = Event.objects.filter(
                    status=Event.Status.PUBLISHED,
                    event_date__gte=timezone.now()
                ).order_by('event_date')[:3]
                categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
            except:
                recent_articles = []
                upcoming_events = []
                categories = []
            
            return render(request, 'news_events/home.html', {
                'recent_articles': recent_articles,
                'upcoming_events': upcoming_events,
                'featured_content': {'articles': [], 'events': []},
                'categories': categories,
                'article_stats': {},
                'event_stats': {},
                'subscription_form': SubscriptionForm(),
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'}
                ]
            })

class ArticleDetailView(NepaliLanguageMixin, View):
    """Article detail page"""
    
    @method_decorator(performance_monitor)
    def get(self, request, slug):
        try:
            data = NewsService.get_article_detail(slug, request.user, request)
            
            if data.get('login_required'):
                messages.warning(request, _("यो लेख हेर्नको लागि कृपया लगइन गर्नुहोस्।"))
                return redirect('auth:login')
                
            context = {
                'article': data['article'],
                'related_articles': data['related_articles'],
                'comments': data['comments'],
                'comment_form': CommentForm(),
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                    {'name': data['article'].title, 'url': data['article'].get_absolute_url()}
                ]
            }
            return render(request, 'news_events/article_detail.html', context)
        except Http404:
            # Show custom 404 page with recent articles
            try:
                from .models import NewsArticle
                recent_articles = NewsEventsQueryOptimizer.get_optimized_article_queryset().filter(
                    status=NewsArticle.Status.PUBLISHED
                ).order_by('-published_date')[:6]
            except:
                recent_articles = []
            
            context = {
                'recent_articles': recent_articles,
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                    {'name': 'लेख फेला परेन', 'url': '#'}
                ]
            }
            return render(request, 'news_events/article_not_found.html', context, status=404)
        except Exception as e:
            logger.error(f"Error loading article detail for slug '{slug}': {e}", exc_info=True)
            messages.error(request, _("लेख लोड गर्न असफल भयो। कृपया पछि फेरि प्रयास गर्नुहोस्।"))
            return redirect('news_events:article-list')

class EventDetailView(NepaliLanguageMixin, View):
    """Event detail page"""
    
    @method_decorator(performance_monitor)
    def get(self, request, slug):
        try:
            data = EventService.get_event_detail(slug, request)
            context = {
                'event': data['event'],
                'related_events': data['related_events'],
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                    {'name': 'कार्यक्रमहरू', 'url': '/news-events/events/'},
                    {'name': data['event'].title, 'url': data['event'].get_absolute_url()}
                ]
            }
            return render(request, 'news_events/event_detail.html', context)
        except Http404:
            # Show custom 404 page with recent events
            try:
                from .models import Event
                recent_events = NewsEventsQueryOptimizer.get_optimized_event_queryset().filter(
                    status=Event.Status.PUBLISHED
                ).order_by('-event_date')[:6]
            except:
                recent_events = []
            
            context = {
                'recent_events': recent_events,
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                    {'name': 'कार्यक्रम फेला परेन', 'url': '#'}
                ]
            }
            return render(request, 'news_events/event_not_found.html', context, status=404)
        except Exception as e:
            logger.error(f"Error loading event detail for slug '{slug}': {e}", exc_info=True)
            messages.error(request, _("कार्यक्रम लोड गर्न असफल भयो। कृपया पछि फेरि प्रयास गर्नुहोस्।"))
            return redirect('news_events:event-list')

class ArticleListView(NepaliLanguageMixin, View):
    """Article listing with filters"""
    
    @method_decorator(performance_monitor)
    def get(self, request, category_slug=None):
        try:
            # Prepare params dict with category_slug if provided
            # Convert QueryDict to regular dict
            params = dict(request.GET)
            if category_slug:
                params['category'] = category_slug
            
            data = NewsService.get_article_list(params)
            context = data
            
            # Set breadcrumbs based on whether it's a category view or all articles
            if category_slug:
                try:
                    from .models import Category
                    category = Category.objects.get(slug=category_slug, is_active=True)
                    context['breadcrumbs'] = [
                        {'name': 'Home', 'url': '/'},
                        {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                        {'name': 'सबै समाचार', 'url': '/news-events/articles/'},
                        {'name': category.name, 'url': category.get_absolute_url()}
                    ]
                except Category.DoesNotExist:
                    # Invalid category, use default breadcrumbs
                    context['breadcrumbs'] = [
                        {'name': 'Home', 'url': '/'},
                        {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                        {'name': 'सबै समाचार', 'url': '/news-events/articles/'}
                    ]
            else:
                context['breadcrumbs'] = [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                    {'name': 'सबै समाचार', 'url': '/news-events/articles/'}
                ]
            
            return render(request, 'news_events/article_list.html', context)
        except Exception as e:
            logger.error(f"Error loading article list: {e}", exc_info=True)
            messages.error(request, _("लेखहरू लोड गर्न असफल भयो। कृपया पछि फेरि प्रयास गर्नुहोस्।"))
            return render(request, 'news_events/article_list.html', {
                'page_obj': None,
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                    {'name': 'सबै समाचार', 'url': '/news-events/articles/'}
                ]
            })

class EventListView(NepaliLanguageMixin, View):
    """Event listing with filters"""
    
    @method_decorator(performance_monitor)
    def get(self, request):
        try:
            data = EventService.get_event_list(request.GET)
            context = data
            context['breadcrumbs'] = [
                {'name': 'Home', 'url': '/'},
                {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                {'name': 'कार्यक्रमहरू', 'url': '/news-events/events/'}
            ]
            return render(request, 'news_events/event_list.html', context)
        except Exception as e:
            logger.error(f"Error loading event list: {e}", exc_info=True)
            messages.error(request, _("कार्यक्रमहरू लोड गर्न असफल भयो। कृपया पछि फेरि प्रयास गर्नुहोस्।"))
            return render(request, 'news_events/event_list.html', {
                'page_obj': None,
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                    {'name': 'कार्यक्रमहरू', 'url': '/news-events/events/'}
                ]
            })

class SubscriptionView(NepaliLanguageMixin, View):
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

class CommentSubmissionView(NepaliLanguageMixin, View):
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

class ArticleShareView(NepaliLanguageMixin, View):
    """Handle article sharing analytics"""
    
    def post(self, request, article_slug):
        success, message = InteractionService.handle_share(article_slug, request)
        return JsonResponse({'success': success, 'message': message})

class SearchView(NepaliLanguageMixin, View):
    """Global search view"""
    
    @method_decorator(performance_monitor)
    def get(self, request):
        try:
            form = ContentSearchForm(request.GET)
            context = {
                'form': form,
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                    {'name': 'खोज', 'url': '/news-events/search/'}
                ]
            }
            
            if form.is_valid():
                results_data = SearchService.perform_search(form.cleaned_data, request)
                context.update(results_data)
                return render(request, 'news_events/search_results.html', context)
            
            return render(request, 'news_events/search.html', context)
        except Exception as e:
            logger.error(f"Error performing search: {e}", exc_info=True)
            messages.error(request, _("खोज गर्न असफल भयो। कृपया पछि फेरि प्रयास गर्नुहोस्।"))
            return render(request, 'news_events/search.html', {
                'form': ContentSearchForm(),
                'breadcrumbs': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'समाचार र कार्यक्रमहरू', 'url': '/news-events/'},
                    {'name': 'खोज', 'url': '/news-events/search/'}
                ]
            })

# ... (Previous imports and standard views)

@staff_member_required
def analytics_dashboard_view(request):
    """Staff analytics dashboard"""
    activate('ne')
    context = {'GA_TRACKING_ID': getattr(settings, 'GA_TRACKING_ID', '')}
    return render(request, 'news_events/analytics_dashboard.html', context)

@login_required
def confirm_subscription_view(request, token):
    activate('ne')
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token)
        if not subscriber.is_confirmed:
            subscriber.is_confirmed = True
            subscriber.confirmed_at = timezone.now()
            subscriber.save()
            messages.success(request, _("तपाईंको सदस्यता पुष्टि भयो! धन्यवाद।"))
        else:
            messages.info(request, _("तपाईंको सदस्यता पहिले नै पुष्टि भइसकेको छ।"))
    except Subscriber.DoesNotExist:
        messages.error(request, _("अवैध पुष्टिकरण टोकन।"))
    except Exception as e:
        logger.error(f"Error confirming subscription: {e}", exc_info=True)
        messages.error(request, _("सदस्यता पुष्टि गर्न असफल भयो। कृपया पछि फेरि प्रयास गर्नुहोस्।"))
    return redirect('news_events:home')

@login_required
def unsubscribe_view(request, token):
    activate('ne')
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token)
        subscriber.status = Subscriber.Status.UNSUBSCRIBED
        subscriber.save()
        messages.success(request, _("तपाईंको सदस्यता रद्द भयो।"))
    except Subscriber.DoesNotExist:
        messages.error(request, _("अवैध टोकन।"))
    except Exception as e:
        logger.error(f"Error unsubscribing: {e}", exc_info=True)
        messages.error(request, _("सदस्यता रद्द गर्न असफल भयो। कृपया पछि फेरि प्रयास गर्नुहोस्।"))
    return redirect('news_events:home')

def rss_feed_view(request):
    """RSS Feed"""
    activate('ne')
    try:
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
    except Exception as e:
        logger.error(f"Error generating RSS feed: {e}", exc_info=True)
        # Return empty RSS feed on error
        context = {
            'articles': [],
            'events': [],
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
