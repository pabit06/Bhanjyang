from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.contrib import messages
from reversion_compare.admin import CompareVersionAdmin
import logging
from .models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    NewsletterSubscriber, ContactInquiry, PageView, ContentVariant
)

logger = logging.getLogger(__name__)


@admin.register(HomePageContent)
class HomePageContentAdmin(CompareVersionAdmin):
    list_display = ['title', 'status', 'scheduled_date', 'published_date', 'order', 'preview_link', 'created_at']
    list_filter = ['status', 'scheduled_date', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['order']
    ordering = ['order', '-created_at']
    readonly_fields = ['published_date', 'published_by', 'created_at', 'updated_at']
    
    class Media:
        js = ('home/js/admin_bulk_actions.js',)
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description', 'order')
        }),
        ('Publication Status', {
            'fields': ('status', 'scheduled_date', 'published_date', 'published_by'),
            'description': 'Set status to Published to make this content visible on the site. Use Scheduled to auto-publish at a specific time.'
        }),
        ('Legacy', {
            'fields': ('is_active',),
            'classes': ('collapse',),
            'description': 'Legacy field - automatically synced with status. Use status field instead.'
        }),
        ('Images', {
            'fields': ('hero_image', 'background_image'),
            'classes': ('collapse',)
        }),
        ('Call to Action Buttons', {
            'fields': ('primary_button_text', 'primary_button_url', 'secondary_button_text', 'secondary_button_url'),
            'classes': ('collapse',),
            'description': 'Configure buttons for hero slides. Leave empty to use default buttons.'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_selected', 'draft_selected', 'schedule_selected', 'archive_selected']
    
    def preview_link(self, obj):
        """Preview link for content"""
        if obj.pk:
            url = obj.get_preview_url()
            return format_html('<a href="{}" target="_blank" class="button">Preview</a>', url)
        return '-'
    preview_link.short_description = 'Preview'
    
    def publish_selected(self, request, queryset):
        """Bulk publish selected content"""
        count = queryset.update(
            status=HomePageContent.Status.PUBLISHED,
            published_date=timezone.now(),
            published_by=request.user
        )
        self.message_user(request, f'{count} item(s) published successfully.', messages.SUCCESS)
    publish_selected.short_description = "Publish selected items"
    
    def draft_selected(self, request, queryset):
        """Bulk move selected content to draft"""
        count = queryset.update(status=HomePageContent.Status.DRAFT)
        self.message_user(request, f'{count} item(s) moved to draft.', messages.SUCCESS)
    draft_selected.short_description = "Move selected to draft"
    
    def schedule_selected(self, request, queryset):
        """Bulk schedule selected content"""
        count = queryset.update(status=HomePageContent.Status.SCHEDULED)
        self.message_user(request, f'{count} item(s) scheduled. Set scheduled_date to auto-publish.', messages.SUCCESS)
    schedule_selected.short_description = "Schedule selected items"
    
    def archive_selected(self, request, queryset):
        """Bulk archive selected content"""
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No items selected.', messages.WARNING)
            return
        
        # Log the action
        logger.info(f"User {request.user.username} archived {count} HomePageContent items")
        
        queryset.update(status=HomePageContent.Status.ARCHIVED)
        self.message_user(
            request, 
            f'{count} item(s) archived successfully. Associated media files are preserved.',
            messages.SUCCESS
        )
    archive_selected.short_description = "Archive selected items"
    
    def save_model(self, request, obj, form, change):
        """Auto-set published_by and published_date when publishing"""
        was_published = obj.status == HomePageContent.Status.PUBLISHED
        is_publishing = obj.status == HomePageContent.Status.PUBLISHED and not obj.published_date
        
        if is_publishing:
            obj.published_date = timezone.now()
            obj.published_by = request.user
            logger.info(
                f"User {request.user.username} published HomePageContent '{obj.title}' (ID: {obj.pk})"
            )
        elif change and was_published:
            # Log updates to published content
            logger.info(
                f"User {request.user.username} updated published HomePageContent '{obj.title}' (ID: {obj.pk})"
            )
        
        # Sync is_active with status for backward compatibility
        obj.is_active = (obj.status == HomePageContent.Status.PUBLISHED)
        super().save_model(request, obj, form, change)


@admin.register(Testimonial)
class TestimonialAdmin(CompareVersionAdmin):
    list_display = ['name', 'status', 'rating', 'is_featured', 'scheduled_date', 'published_date', 'preview_link', 'language']
    list_filter = ['status', 'is_featured', 'language', 'rating', 'scheduled_date', 'created_at']
    search_fields = ['name', 'position', 'company', 'content']
    list_editable = ['is_featured', 'rating']
    ordering = ['order', '-created_at']
    readonly_fields = ['published_date', 'published_by', 'created_at', 'updated_at']
    
    class Media:
        js = ('home/js/admin_bulk_actions.js',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'position', 'company', 'photo')
        }),
        ('Testimonial Content', {
            'fields': ('content', 'rating', 'language')
        }),
        ('Publication Status', {
            'fields': ('status', 'scheduled_date', 'published_date', 'published_by'),
            'description': 'Set status to Published to make this testimonial visible on the site.'
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'order')
        }),
        ('Legacy', {
            'fields': ('is_active',),
            'classes': ('collapse',),
            'description': 'Legacy field - automatically synced with status.'
        }),
    )
    
    actions = ['publish_selected', 'draft_selected', 'schedule_selected', 'archive_selected']
    
    def preview_link(self, obj):
        """Preview link for testimonial"""
        if obj.pk:
            url = obj.get_preview_url()
            return format_html('<a href="{}" target="_blank" class="button">Preview</a>', url)
        return '-'
    preview_link.short_description = 'Preview'
    
    def publish_selected(self, request, queryset):
        count = queryset.update(
            status=Testimonial.Status.PUBLISHED,
            published_date=timezone.now(),
            published_by=request.user
        )
        self.message_user(request, f'{count} testimonial(s) published successfully.', messages.SUCCESS)
    publish_selected.short_description = "Publish selected testimonials"
    
    def draft_selected(self, request, queryset):
        count = queryset.update(status=Testimonial.Status.DRAFT)
        self.message_user(request, f'{count} testimonial(s) moved to draft.', messages.SUCCESS)
    draft_selected.short_description = "Move selected to draft"
    
    def schedule_selected(self, request, queryset):
        count = queryset.update(status=Testimonial.Status.SCHEDULED)
        self.message_user(request, f'{count} testimonial(s) scheduled.', messages.SUCCESS)
    schedule_selected.short_description = "Schedule selected testimonials"
    
    def archive_selected(self, request, queryset):
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No items selected.', messages.WARNING)
            return
        logger.info(f"User {request.user.username} archived {count} Testimonial items")
        queryset.update(status=Testimonial.Status.ARCHIVED)
        self.message_user(
            request, 
            f'{count} testimonial(s) archived successfully. Associated media files are preserved.',
            messages.SUCCESS
        )
    archive_selected.short_description = "Archive selected testimonials"
    
    def save_model(self, request, obj, form, change):
        was_published = obj.status == Testimonial.Status.PUBLISHED
        is_publishing = obj.status == Testimonial.Status.PUBLISHED and not obj.published_date
        
        if is_publishing:
            obj.published_date = timezone.now()
            obj.published_by = request.user
            logger.info(f"User {request.user.username} published Testimonial '{obj.name}' (ID: {obj.pk})")
        elif change and was_published:
            logger.info(f"User {request.user.username} updated published Testimonial '{obj.name}' (ID: {obj.pk})")
        
        obj.is_active = (obj.status == Testimonial.Status.PUBLISHED)
        super().save_model(request, obj, form, change)


@admin.register(Statistic)
class StatisticAdmin(CompareVersionAdmin):
    list_display = ['title', 'value', 'status', 'is_featured', 'scheduled_date', 'published_date', 'preview_link', 'icon']
    list_filter = ['status', 'is_featured', 'color', 'scheduled_date', 'created_at']
    search_fields = ['title', 'value', 'description']
    list_editable = ['is_featured']
    ordering = ['order', '-created_at']
    readonly_fields = ['published_date', 'published_by', 'created_at', 'updated_at']
    
    class Media:
        js = ('home/js/admin_bulk_actions.js',)
    
    fieldsets = (
        ('Statistic Information', {
            'fields': ('title', 'value', 'description')
        }),
        ('Publication Status', {
            'fields': ('status', 'scheduled_date', 'published_date', 'published_by'),
            'description': 'Set status to Published to make this statistic visible on the site.'
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'is_featured', 'order')
        }),
        ('Legacy', {
            'fields': ('is_active',),
            'classes': ('collapse',),
            'description': 'Legacy field - automatically synced with status.'
        }),
    )
    
    actions = ['publish_selected', 'draft_selected', 'schedule_selected', 'archive_selected']
    
    def preview_link(self, obj):
        """Preview link for statistic"""
        if obj.pk:
            url = obj.get_preview_url()
            return format_html('<a href="{}" target="_blank" class="button">Preview</a>', url)
        return '-'
    preview_link.short_description = 'Preview'
    
    def publish_selected(self, request, queryset):
        count = queryset.update(
            status=Statistic.Status.PUBLISHED,
            published_date=timezone.now(),
            published_by=request.user
        )
        self.message_user(request, f'{count} statistic(s) published successfully.', messages.SUCCESS)
    publish_selected.short_description = "Publish selected statistics"
    
    def draft_selected(self, request, queryset):
        count = queryset.update(status=Statistic.Status.DRAFT)
        self.message_user(request, f'{count} statistic(s) moved to draft.', messages.SUCCESS)
    draft_selected.short_description = "Move selected to draft"
    
    def schedule_selected(self, request, queryset):
        count = queryset.update(status=Statistic.Status.SCHEDULED)
        self.message_user(request, f'{count} statistic(s) scheduled.', messages.SUCCESS)
    schedule_selected.short_description = "Schedule selected statistics"
    
    def archive_selected(self, request, queryset):
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No items selected.', messages.WARNING)
            return
        logger.info(f"User {request.user.username} archived {count} Statistic items")
        queryset.update(status=Statistic.Status.ARCHIVED)
        self.message_user(
            request, 
            f'{count} statistic(s) archived successfully.',
            messages.SUCCESS
        )
    archive_selected.short_description = "Archive selected statistics"
    
    def save_model(self, request, obj, form, change):
        was_published = obj.status == Statistic.Status.PUBLISHED
        is_publishing = obj.status == Statistic.Status.PUBLISHED and not obj.published_date
        
        if is_publishing:
            obj.published_date = timezone.now()
            obj.published_by = request.user
            logger.info(f"User {request.user.username} published Statistic '{obj.title}' (ID: {obj.pk})")
        elif change and was_published:
            logger.info(f"User {request.user.username} updated published Statistic '{obj.title}' (ID: {obj.pk})")
        
        obj.is_active = (obj.status == Statistic.Status.PUBLISHED)
        super().save_model(request, obj, form, change)


@admin.register(Announcement)
class AnnouncementAdmin(CompareVersionAdmin):
    list_display = ['title', 'announcement_type', 'status', 'priority', 'is_featured', 'scheduled_date', 'published_date', 'preview_link', 'publish_date']
    list_filter = ['status', 'announcement_type', 'priority', 'is_featured', 'scheduled_date', 'publish_date']
    search_fields = ['title', 'content', 'summary']
    list_editable = ['is_featured', 'priority']
    ordering = ['-priority', '-publish_date']
    date_hierarchy = 'publish_date'
    readonly_fields = ['published_date', 'published_by', 'created_at', 'updated_at']
    
    class Media:
        js = ('home/js/admin_bulk_actions.js',)
    
    fieldsets = (
        ('Announcement Content', {
            'fields': ('title', 'summary', 'content', 'image')
        }),
        ('Publication Status', {
            'fields': ('status', 'scheduled_date', 'published_date', 'published_by'),
            'description': 'Set status to Published to make this announcement visible on the site.'
        }),
        ('Settings', {
            'fields': ('announcement_type', 'priority', 'is_featured')
        }),
        ('Publishing', {
            'fields': ('publish_date', 'expiry_date', 'auto_expire'),
            'description': 'Set expiry_date and enable auto_expire to automatically archive this announcement when it expires.'
        }),
        ('Legacy', {
            'fields': ('is_active',),
            'classes': ('collapse',),
            'description': 'Legacy field - automatically synced with status.'
        }),
    )
    
    actions = ['publish_selected', 'draft_selected', 'schedule_selected', 'archive_selected', 'mark_as_featured', 'mark_as_unfeatured']
    
    def preview_link(self, obj):
        """Preview link for announcement"""
        if obj.pk:
            url = obj.get_preview_url()
            return format_html('<a href="{}" target="_blank" class="button">Preview</a>', url)
        return '-'
    preview_link.short_description = 'Preview'
    
    def publish_selected(self, request, queryset):
        count = queryset.update(
            status=Announcement.Status.PUBLISHED,
            published_date=timezone.now(),
            published_by=request.user
        )
        self.message_user(request, f'{count} announcement(s) published successfully.', messages.SUCCESS)
    publish_selected.short_description = "Publish selected announcements"
    
    def draft_selected(self, request, queryset):
        count = queryset.update(status=Announcement.Status.DRAFT)
        self.message_user(request, f'{count} announcement(s) moved to draft.', messages.SUCCESS)
    draft_selected.short_description = "Move selected to draft"
    
    def schedule_selected(self, request, queryset):
        count = queryset.update(status=Announcement.Status.SCHEDULED)
        self.message_user(request, f'{count} announcement(s) scheduled.', messages.SUCCESS)
    schedule_selected.short_description = "Schedule selected announcements"
    
    def archive_selected(self, request, queryset):
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No items selected.', messages.WARNING)
            return
        logger.info(f"User {request.user.username} archived {count} Announcement items")
        queryset.update(status=Announcement.Status.ARCHIVED)
        self.message_user(
            request, 
            f'{count} announcement(s) archived successfully. Associated media files are preserved.',
            messages.SUCCESS
        )
    archive_selected.short_description = "Archive selected announcements"
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} announcements marked as featured.", messages.SUCCESS)
    mark_as_featured.short_description = "Mark selected announcements as featured"
    
    def mark_as_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} announcements marked as unfeatured.", messages.SUCCESS)
    mark_as_unfeatured.short_description = "Mark selected announcements as unfeatured"
    
    def save_model(self, request, obj, form, change):
        was_published = obj.status == Announcement.Status.PUBLISHED
        is_publishing = obj.status == Announcement.Status.PUBLISHED and not obj.published_date
        
        if is_publishing:
            obj.published_date = timezone.now()
            obj.published_by = request.user
            logger.info(f"User {request.user.username} published Announcement '{obj.title}' (ID: {obj.pk})")
        elif change and was_published:
            logger.info(f"User {request.user.username} updated published Announcement '{obj.title}' (ID: {obj.pk})")
        
        obj.is_active = (obj.status == Announcement.Status.PUBLISHED)
        super().save_model(request, obj, form, change)





@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    list_editable = ['is_active']
    ordering = ['-subscribed_at']
    readonly_fields = ['subscribed_at', 'unsubscribed_at']
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'name', 'is_active')
        }),
        ('Subscription Details', {
            'fields': ('subscribed_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['unsubscribe_selected']
    
    def unsubscribe_selected(self, request, queryset):
        queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} subscribers unsubscribed.")
    unsubscribe_selected.short_description = "Unsubscribe selected subscribers"


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'inquiry_type', 'is_resolved', 'created_at']
    list_filter = ['inquiry_type', 'is_resolved', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_resolved']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Inquiry Information', {
            'fields': ('name', 'email', 'phone', 'subject', 'message', 'inquiry_type')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_by', 'response')
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_unresolved']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user)
        self.message_user(request, f"{queryset.count()} inquiries marked as resolved.")
    mark_as_resolved.short_description = "Mark selected inquiries as resolved"
    
    def mark_as_unresolved(self, request, queryset):
        queryset.update(is_resolved=False, resolved_at=None, resolved_by=None)
        self.message_user(request, f"{queryset.count()} inquiries marked as unresolved.")
    mark_as_unresolved.short_description = "Mark selected inquiries as unresolved"


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['page_title', 'page_url', 'user_ip', 'created_at']
    list_filter = ['created_at']
    search_fields = ['page_url', 'page_title', 'user_ip']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Page Information', {
            'fields': ('page_url', 'page_title')
        }),
        ('User Information', {
            'fields': ('user_ip', 'user_agent', 'referrer', 'session_id')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Page views are created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Page views should not be edited


# Register ContentVariant admin
@admin.register(ContentVariant)
class ContentVariantAdmin(admin.ModelAdmin):
    list_display = ['variant_name', 'content_object', 'is_active', 'views', 'conversions', 'conversion_rate_display', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['variant_name', 'variant_data']
    readonly_fields = ['views', 'conversions', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Variant Information', {
            'fields': ('content_type', 'object_id', 'variant_name', 'variant_data')
        }),
        ('A/B Testing', {
            'fields': ('is_active', 'views', 'conversions'),
            'description': 'Views and conversions are tracked automatically. Activate variants to start A/B testing.'
        }),
    )
    
    def conversion_rate_display(self, obj):
        """Display conversion rate as percentage"""
        return f"{obj.conversion_rate:.2f}%"
    conversion_rate_display.short_description = 'Conversion Rate'


# Register with custom admin site
from apps.admin.admin_site import admin_site

# Unregister from default admin site if already registered
from django.contrib import admin
for model in [HomePageContent, Testimonial, Statistic, Announcement, NewsletterSubscriber, ContactInquiry, PageView, ContentVariant]:
    if model in admin.site._registry:
        admin.site.unregister(model)

# Register with custom admin site
admin_site.register(HomePageContent, HomePageContentAdmin)
admin_site.register(Testimonial, TestimonialAdmin)
admin_site.register(Statistic, StatisticAdmin)
admin_site.register(Announcement, AnnouncementAdmin)
admin_site.register(ContentVariant, ContentVariantAdmin)
admin_site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
admin_site.register(ContactInquiry, ContactInquiryAdmin)
admin_site.register(PageView, PageViewAdmin)