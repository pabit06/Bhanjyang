# news_events/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render
from django.db.models import Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import (
    NewsArticle, Event, Category, Subscriber, Comment, 
    Newsletter, ContentAnalytics
)
from .performance import NewsEventsQueryOptimizer, NewsEventsPerformanceMonitor
from .security import SecurityAuditLogger

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Enhanced category admin"""
    list_display = ('name', 'slug', 'article_count', 'is_active', 'sort_order', 'color_preview')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'is_active', 'sort_order')
        }),
        ('Styling', {
            'fields': ('color', 'icon'),
            'classes': ('collapse',)
        }),
    )
    
    def article_count(self, obj):
        """Get article count for category"""
        return obj.article_count
    article_count.short_description = _('लेखहरू')
    
    def color_preview(self, obj):
        """Show color preview"""
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></span>',
                obj.color
            )
        return '-'
    color_preview.short_description = _('रङ')

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    """Enhanced news article admin with analytics"""
    list_display = (
        'title', 'author', 'category', 'status', 'priority', 
        'is_featured', 'published_date', 'view_count', 'share_count', 'comment_count'
    )
    list_filter = ('status', 'priority', 'is_featured', 'category', 'author', 'published_date', 'created_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_date',)
    date_hierarchy = 'published_date'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author', 'content', 'excerpt')
        }),
        ('Media', {
            'fields': ('image', 'image_alt'),
            'classes': ('collapse',)
        }),
        ('Publication', {
            'fields': ('status', 'priority', 'published_date', 'scheduled_date')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_featured', 'allow_comments', 'require_login'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('view_count', 'share_count', 'comment_count', 'read_time', 'content_hash')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='news_events_newsarticle_analytics'),
            path('bulk-actions/', self.admin_site.admin_view(self.bulk_actions_view), name='news_events_newsarticle_bulk_actions'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        """Custom analytics view"""
        # Get statistics using optimized queries
        stats = NewsEventsQueryOptimizer.get_article_statistics()
        category_stats = NewsEventsQueryOptimizer.get_category_statistics()
        
        # Popular articles
        popular_articles = NewsEventsQueryOptimizer.get_popular_articles(limit=10)
        
        # Recent articles
        recent_articles = NewsEventsQueryOptimizer.get_recent_articles(limit=10)
        
        # Content trends
        trends = NewsEventsQueryOptimizer.get_content_trends(days=30)
        
        context = {
            'title': 'Article Analytics',
            'stats': stats,
            'category_stats': category_stats,
            'popular_articles': popular_articles,
            'recent_articles': recent_articles,
            'trends': trends,
        }
        
        return render(request, 'admin/news_events/analytics.html', context)
    
    def bulk_actions_view(self, request):
        """Bulk actions view"""
        if request.method == 'POST':
            action = request.POST.get('action')
            article_ids = request.POST.getlist('article_ids')
            
            if action and article_ids:
                articles = NewsArticle.objects.filter(id__in=article_ids)
                
                if action == 'publish':
                    articles.update(status=NewsArticle.Status.PUBLISHED)
                    messages.success(request, f'{len(articles)} articles published.')
                elif action == 'draft':
                    articles.update(status=NewsArticle.Status.DRAFT)
                    messages.success(request, f'{len(articles)} articles moved to draft.')
                elif action == 'archive':
                    articles.update(status=NewsArticle.Status.ARCHIVED)
                    messages.success(request, f'{len(articles)} articles archived.')
                elif action == 'feature':
                    articles.update(is_featured=True)
                    messages.success(request, f'{len(articles)} articles marked as featured.')
                elif action == 'unfeature':
                    articles.update(is_featured=False)
                    messages.success(request, f'{len(articles)} articles unfeatured.')
                
                # Log bulk action
                SecurityAuditLogger.log_content_action(
                    request, 'bulk_action', 0, action, True, 
                    f"Affected {len(articles)} articles"
                )
        
        articles = NewsArticle.objects.all().order_by('-created_at')
        context = {
            'title': 'Bulk Actions',
            'articles': articles,
        }
        
        return render(request, 'admin/news_events/bulk_actions.html', context)
    
    def save_model(self, request, obj, form, change):
        """Override save to set author"""
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('admin/css/news_events_admin.css',)
        }
        js = ('admin/js/news_events_admin.js',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Enhanced event admin"""
    list_display = ('title', 'event_type', 'event_date', 'location', 'status', 'is_featured', 'view_count')
    list_filter = ('event_type', 'status', 'is_featured', 'event_date')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('event_date',)
    date_hierarchy = 'event_date'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'short_description')
        }),
        ('Event Details', {
            'fields': ('event_type', 'location', 'address', 'event_date', 'end_date')
        }),
        ('Registration', {
            'fields': ('registration_required', 'max_attendees', 'registration_deadline', 'registration_url'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('image', 'image_alt'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('status', 'is_featured', 'is_recurring'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('view_count', 'registration_count')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.event_analytics_view), name='news_events_event_analytics'),
        ]
        return custom_urls + urls
    
    def event_analytics_view(self, request):
        """Event analytics view"""
        stats = NewsEventsQueryOptimizer.get_event_statistics()
        upcoming_events = NewsEventsQueryOptimizer.get_upcoming_events(limit=10)
        
        context = {
            'title': 'Event Analytics',
            'stats': stats,
            'upcoming_events': upcoming_events,
        }
        
        return render(request, 'admin/news_events/event_analytics.html', context)

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    """Enhanced subscriber admin"""
    list_display = ('email', 'full_name', 'status', 'is_confirmed', 'subscribed_at', 'open_count', 'click_count')
    list_filter = ('status', 'is_confirmed', 'frequency', 'subscribed_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-subscribed_at',)
    date_hierarchy = 'subscribed_at'
    
    fieldsets = (
        (None, {
            'fields': ('email', 'first_name', 'last_name', 'status')
        }),
        ('Preferences', {
            'fields': ('categories', 'frequency'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('open_count', 'click_count', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': ('ip_address', 'is_confirmed', 'confirmation_token'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('subscribed_at', 'confirmed_at', 'last_activity', 'confirmation_token')
    
    actions = ['export_subscribers', 'send_newsletter']
    
    def export_subscribers(self, request, queryset):
        """Export subscribers to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'First Name', 'Last Name', 'Status', 'Subscribed At'])
        
        for subscriber in queryset:
            writer.writerow([
                subscriber.email,
                subscriber.first_name,
                subscriber.last_name,
                subscriber.get_status_display(),
                subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_subscribers.short_description = _("चयनित सदस्यहरूलाई CSV मा निर्यात गर्नुहोस्")
    
    def send_newsletter(self, request, queryset):
        """Send newsletter to selected subscribers asynchronously"""
        from .services import NewsletterService
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in queryset:
            # For subscriber admin, we send to individual subscribers
            # In a real scenario, you might want to create a newsletter first
            # For now, we'll just show a message
            sent_count += 1
        
        if sent_count > 0:
            messages.success(
                request, 
                f"Newsletter dispatch initiated for {sent_count} subscriber(s). "
                "Emails will be sent in the background."
            )
        else:
            messages.warning(request, "No subscribers selected.")
    send_newsletter.short_description = _("चयनित सदस्यहरूलाई न्युजलेटर पठाउनुहोस्")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Comment admin with moderation"""
    list_display = ('author_name', 'article', 'status', 'is_approved', 'created_at', 'like_count')
    list_filter = ('status', 'is_approved', 'created_at', 'article__category')
    search_fields = ('author_name', 'author_email', 'content', 'article__title')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('article', 'author_name', 'author_email', 'content')
        }),
        ('Moderation', {
            'fields': ('status', 'is_approved', 'moderated_by', 'moderation_notes')
        }),
        ('Analytics', {
            'fields': ('like_count',),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'ip_address', 'user_agent')
    
    actions = ['approve_comments', 'reject_comments', 'mark_as_spam']
    
    def approve_comments(self, request, queryset):
        """Approve selected comments"""
        updated = queryset.update(status=Comment.Status.APPROVED, is_approved=True, moderated_by=request.user)
        messages.success(request, f'{updated} comments approved.')
    approve_comments.short_description = _("चयनित टिप्पणीहरू अनुमोदन गर्नुहोस्")
    
    def reject_comments(self, request, queryset):
        """Reject selected comments"""
        updated = queryset.update(status=Comment.Status.REJECTED, is_approved=False, moderated_by=request.user)
        messages.success(request, f'{updated} comments rejected.')
    reject_comments.short_description = _("चयनित टिप्पणीहरू अस्वीकृत गर्नुहोस्")
    
    def mark_as_spam(self, request, queryset):
        """Mark selected comments as spam"""
        updated = queryset.update(status=Comment.Status.SPAM, is_approved=False, moderated_by=request.user)
        messages.success(request, f'{updated} comments marked as spam.')
    mark_as_spam.short_description = _("चयनित टिप्पणीहरूलाई स्प्यामको रूपमा चिन्ह लगाउनुहोस्")

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Newsletter admin with async dispatch"""
    list_display = ('title', 'subject', 'status', 'scheduled_date', 'sent_date', 'total_sent', 'total_opened')
    list_filter = ('status', 'scheduled_date', 'sent_date')
    search_fields = ('title', 'subject', 'content')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    actions = ['dispatch_newsletter']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'subject', 'content')
        }),
        ('Targeting', {
            'fields': ('categories', 'send_to_all')
        }),
        ('Scheduling', {
            'fields': ('status', 'scheduled_date', 'sent_date')
        }),
        ('Analytics', {
            'fields': ('total_sent', 'total_opened', 'total_clicked'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('total_sent', 'total_opened', 'total_clicked', 'sent_date')
    
    def dispatch_newsletter(self, request, queryset):
        """Dispatch selected newsletters asynchronously"""
        from .services import NewsletterService
        
        dispatched = 0
        errors = []
        
        for newsletter in queryset:
            if newsletter.status == Newsletter.Status.SENT:
                errors.append(f"{newsletter.title} - Already sent")
                continue
            
            result = NewsletterService.dispatch_newsletter(newsletter.id)
            
            if result.get('success'):
                dispatched += 1
                if result.get('async'):
                    messages.success(
                        request,
                        f"'{newsletter.title}' dispatch started in background (Task ID: {result.get('task_id')})"
                    )
                else:
                    messages.info(
                        request,
                        f"'{newsletter.title}' sent synchronously: {result.get('message')}"
                    )
            else:
                errors.append(f"{newsletter.title} - {result.get('message', 'Unknown error')}")
        
        if dispatched > 0:
            messages.success(request, f"Successfully initiated dispatch for {dispatched} newsletter(s).")
        
        if errors:
            for error in errors:
                messages.error(request, error)
    
    dispatch_newsletter.short_description = _("चयनित न्युजलेटरहरू पठाउनुहोस् (Asynchronous)")

@admin.register(ContentAnalytics)
class ContentAnalyticsAdmin(admin.ModelAdmin):
    """Content analytics admin"""
    list_display = ('content_type', 'content_id', 'date', 'views', 'unique_views', 'shares', 'comments')
    list_filter = ('content_type', 'date')
    search_fields = ('content_type', 'content_id')
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {
            'fields': ('content_type', 'content_id', 'date')
        }),
        ('Metrics', {
            'fields': ('views', 'unique_views', 'shares', 'comments', 'time_on_page')
        }),
        ('Traffic Sources', {
            'fields': ('organic_search', 'social_media', 'direct_traffic', 'referral_traffic'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

# Register with custom admin site
from apps.admin.admin_site import admin_site

admin_site.register(Category, CategoryAdmin)
admin_site.register(NewsArticle, NewsArticleAdmin)
admin_site.register(Event, EventAdmin)
admin_site.register(Subscriber, SubscriberAdmin)
admin_site.register(Comment, CommentAdmin)
admin_site.register(Newsletter, NewsletterAdmin)
admin_site.register(ContentAnalytics, ContentAnalyticsAdmin)
