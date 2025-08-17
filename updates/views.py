from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import NewsArticle, Event, Category, Subscriber
from .forms import SubscriptionForm

def calculate_read_time(content):
    if not content: return 0
    word_count = len(content.split())
    read_time = (word_count + 199) // 200
    return max(1, read_time)

def news_list_view(request):
    news_articles = NewsArticle.objects.filter(status=NewsArticle.Status.PUBLISHED).select_related('author', 'category')[:3]
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')[:3]
    subscription_form = SubscriptionForm()
    categories = Category.objects.all()

    for article in news_articles:
        article.read_time_minutes = calculate_read_time(article.content)

    context = {
        'news_articles': news_articles,
        'upcoming_events': upcoming_events,
        'subscription_form': subscription_form,
        'categories': categories,
    }
    return render(request, 'updates/news_events.html', context)

def news_detail_view(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, status=NewsArticle.Status.PUBLISHED)
    article.read_time_minutes = calculate_read_time(article.content)
    related_articles = NewsArticle.objects.filter(category=article.category, status=NewsArticle.Status.PUBLISHED).exclude(pk=article.pk)[:2]
    
    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'updates/news_detail.html', context)

def all_news_list_view(request):
    all_articles = NewsArticle.objects.filter(status=NewsArticle.Status.PUBLISHED).select_related('author', 'category')
    paginator = Paginator(all_articles, 6) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj, 
        'page_title': 'All News Articles'
    }
    return render(request, 'updates/all_news_list.html', context)

def article_by_category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    articles = NewsArticle.objects.filter(category=category, status=NewsArticle.Status.PUBLISHED).select_related('author', 'category')
    paginator = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'page_title': f'News in "{category.name}"',
        'category': category,
    }
    return render(request, 'updates/all_news_list.html', context)

def event_list_view(request):
    event_list = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')
    paginator = Paginator(event_list, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'page_title': 'All Upcoming Events'}
    return render(request, 'updates/event_list.html', context)

def past_event_list_view(request):
    past_events = Event.objects.filter(event_date__lt=timezone.now()).order_by('-event_date')
    paginator = Paginator(past_events, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'page_title': 'Past Events Archive'}
    return render(request, 'updates/past_event_list.html', context)

def subscribe_view(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Thank you for subscribing!'})
        else:
            error_message = form.errors.get('email', ['Invalid request.'])[0]
            return JsonResponse({'success': False, 'message': error_message})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
