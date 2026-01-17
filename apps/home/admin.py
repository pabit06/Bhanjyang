from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    NewsletterSubscriber, ContactInquiry, PageView
)


@admin.register(HomePageContent)
class HomePageContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description', 'order', 'is_active')
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


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'rating', 'is_featured', 'is_active', 'language']
    list_filter = ['is_featured', 'is_active', 'language', 'rating', 'created_at']
    search_fields = ['name', 'position', 'company', 'content']
    list_editable = ['is_featured', 'is_active', 'rating']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'position', 'company', 'photo')
        }),
        ('Testimonial Content', {
            'fields': ('content', 'rating', 'language')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ['title', 'value', 'icon', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active', 'color']
    search_fields = ['title', 'value', 'description']
    list_editable = ['is_featured', 'is_active']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Statistic Information', {
            'fields': ('title', 'value', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'is_featured', 'is_active', 'order')
        }),
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'announcement_type', 'priority', 'is_featured', 'is_active', 'publish_date']
    list_filter = ['announcement_type', 'priority', 'is_featured', 'is_active', 'publish_date']
    search_fields = ['title', 'content', 'summary']
    list_editable = ['is_featured', 'is_active', 'priority']
    ordering = ['-priority', '-publish_date']
    date_hierarchy = 'publish_date'
    
    fieldsets = (
        ('Announcement Content', {
            'fields': ('title', 'summary', 'content', 'image')
        }),
        ('Settings', {
            'fields': ('announcement_type', 'priority', 'is_featured', 'is_active')
        }),
        ('Publishing', {
            'fields': ('publish_date', 'expiry_date')
        }),
    )
    
    actions = ['mark_as_featured', 'mark_as_unfeatured', 'mark_as_active', 'mark_as_inactive']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} announcements marked as featured.")
    mark_as_featured.short_description = "Mark selected announcements as featured"
    
    def mark_as_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} announcements marked as unfeatured.")
    mark_as_unfeatured.short_description = "Mark selected announcements as unfeatured"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} announcements marked as active.")
    mark_as_active.short_description = "Mark selected announcements as active"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} announcements marked as inactive.")
    mark_as_inactive.short_description = "Mark selected announcements as inactive"





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


# Register with custom admin site
from apps.admin.admin_site import admin_site

# Unregister from default admin site if already registered
from django.contrib import admin
for model in [HomePageContent, Testimonial, Statistic, Announcement, NewsletterSubscriber, ContactInquiry, PageView]:
    if model in admin.site._registry:
        admin.site.unregister(model)

# Register with custom admin site
admin_site.register(HomePageContent, HomePageContentAdmin)
admin_site.register(Testimonial, TestimonialAdmin)
admin_site.register(Statistic, StatisticAdmin)
admin_site.register(Announcement, AnnouncementAdmin)
admin_site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
admin_site.register(ContactInquiry, ContactInquiryAdmin)
admin_site.register(PageView, PageViewAdmin)