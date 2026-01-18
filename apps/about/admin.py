"""
Admin interface for the About app.

Provides enhanced admin interfaces for all About app models with:
- Custom filters (ActiveFilter, FeaturedFilter)
- Bulk actions (activate, deactivate, feature, unfeature, publish, draft, schedule, archive)
- Optimized querysets
- Inline editing for related models
- Content versioning with django-reversion-compare
- Preview functionality for draft/scheduled content
- Audit logging for content changes
"""
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib import messages
from reversion_compare.admin import CompareVersionAdmin
import logging
from .models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)

logger = logging.getLogger(__name__)


class ActiveFilter(SimpleListFilter):
    """Filter for active/inactive items"""
    title = _('Status')
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('active', _('Active')),
            ('inactive', _('Inactive')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)


class FeaturedFilter(SimpleListFilter):
    """Filter for featured items"""
    title = _('Featured')
    parameter_name = 'is_featured'
    
    def lookups(self, request, model_admin):
        return (
            ('featured', _('Featured')),
            ('not_featured', _('Not Featured')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'featured':
            return queryset.filter(is_featured=True)
        if self.value() == 'not_featured':
            return queryset.filter(is_featured=False)


# =============================================================================
# Base Admin Classes
# =============================================================================

class BaseContentAdmin(admin.ModelAdmin):
    """
    Base admin class for content models with common functionality.
    
    Provides:
    - Active/Inactive status filtering
    - Bulk activate/deactivate actions
    - Timestamp fields (readonly)
    """
    readonly_fields = ('created_at', 'updated_at')
    list_filter = (ActiveFilter,)
    actions = ['activate_selected', 'deactivate_selected']
    
    def activate_selected(self, request, queryset):
        """Bulk activate selected items"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} item(s) were successfully activated.', messages.SUCCESS)
    activate_selected.short_description = "Activate selected items"
    
    def deactivate_selected(self, request, queryset):
        """Bulk deactivate selected items"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} item(s) were successfully deactivated.', messages.SUCCESS)
    deactivate_selected.short_description = "Deactivate selected items"


class BaseFeaturedAdmin(BaseContentAdmin):
    """
    Base admin class for models with featured functionality.
    
    Extends BaseContentAdmin with:
    - Featured filtering
    - Bulk feature/unfeature actions
    """
    list_filter = (ActiveFilter, FeaturedFilter)
    actions = BaseContentAdmin.actions + ['feature_selected', 'unfeature_selected']
    
    def feature_selected(self, request, queryset):
        """Bulk feature selected items"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} item(s) were successfully featured.', messages.SUCCESS)
    feature_selected.short_description = "Feature selected items"
    
    def unfeature_selected(self, request, queryset):
        """Bulk unfeature selected items"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} item(s) were successfully unfeatured.', messages.SUCCESS)
    unfeature_selected.short_description = "Unfeature selected items"


class CooperativeInfoAdmin(CompareVersionAdmin):
    """Enhanced admin interface for cooperative information"""
    list_display = ('cooperative_name', 'status', 'scheduled_date', 'published_date', 'established_date', 'preview_link', 'actions_column', 'created_at')
    list_filter = ('status', 'scheduled_date', 'established_date', 'created_at')
    search_fields = ('cooperative_name', 'cooperative_name_nepali', 'description', 'our_story', 'registration_number')
    prepopulated_fields = {'slug': ('cooperative_name',)}
    ordering = ('-created_at',)
    list_per_page = 25
    readonly_fields = ('published_date', 'published_by', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('cooperative_name', 'cooperative_name_nepali', 'slug')
        }),
        ('Cooperative Details', {
            'fields': ('established_date', 'registration_number', 'license_number')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        ('Mission & Vision', {
            'fields': ('mission', 'vision', 'values')
        }),
        ('Description', {
            'fields': ('description', 'description_nepali')
        }),
        ('Our Story', {
            'fields': ('our_story', 'our_story_nepali', 'our_story_image'),
            'description': _('Content displayed in the "Our Story" section on the About Us page')
        }),
        ('Home Page Content', {
            'fields': ('introduction_text', 'introduction_text_nepali', 'why_choose_us_text', 'why_choose_us_text_nepali'),
            'description': _('Content for home page sections. Years of service is automatically calculated from established date.')
        }),
        ('Publication Status', {
            'fields': ('status', 'scheduled_date', 'published_date', 'published_by'),
            'description': _('Set status to Published to make this content visible on the site. Use Scheduled to auto-publish at a specific time.')
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'og_image'),
            'classes': ('collapse',),
            'description': _('SEO meta tags for home page. If left blank, defaults will be used.')
        }),
        ('Media', {
            'fields': ('logo', 'featured_image'),
            'classes': ('collapse',)
        }),
        ('Legacy', {
            'fields': ('is_active',),
            'classes': ('collapse',),
            'description': _('Legacy field - automatically synced with status. Use status field instead.')
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
    
    def actions_column(self, obj):
        """Custom actions column"""
        if obj.slug:
            view_url = reverse('about:cooperative_detail', kwargs={'slug': obj.slug})
        else:
            view_url = reverse('about:introduction')
        return format_html(
            '<a href="{}" class="button" target="_blank">View on Site</a>',
            view_url
        )
    actions_column.short_description = 'Actions'
    
    def has_add_permission(self, request):
        """Restrict creation to a single instance"""
        # If an instance already exists, deny adding another
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def publish_selected(self, request, queryset):
        """Bulk publish selected content"""
        count = queryset.update(
            status=CooperativeInfo.Status.PUBLISHED,
            published_date=timezone.now(),
            published_by=request.user,
            is_active=True
        )
        self.message_user(request, f'{count} item(s) published successfully.', messages.SUCCESS)
    publish_selected.short_description = "Publish selected items"
    
    def draft_selected(self, request, queryset):
        """Bulk move selected content to draft"""
        count = queryset.update(status=CooperativeInfo.Status.DRAFT, is_active=False)
        self.message_user(request, f'{count} item(s) moved to draft.', messages.SUCCESS)
    draft_selected.short_description = "Move selected to draft"
    
    def schedule_selected(self, request, queryset):
        """Bulk schedule selected content"""
        count = queryset.update(status=CooperativeInfo.Status.SCHEDULED, is_active=False)
        self.message_user(request, f'{count} item(s) scheduled. Set scheduled_date to auto-publish.', messages.SUCCESS)
    schedule_selected.short_description = "Schedule selected items"
    
    def archive_selected(self, request, queryset):
        """Bulk archive selected content"""
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No items selected.', messages.WARNING)
            return
        logger.info(f"User {request.user.username} archived {count} CooperativeInfo items")
        queryset.update(status=CooperativeInfo.Status.ARCHIVED, is_active=False)
        self.message_user(
            request,
            f'{count} item(s) archived successfully. Associated media files are preserved.',
            messages.SUCCESS
        )
    archive_selected.short_description = "Archive selected items"
    
    def save_model(self, request, obj, form, change):
        """Auto-set published_by and published_date when publishing"""
        was_published = obj.status == CooperativeInfo.Status.PUBLISHED
        is_publishing = obj.status == CooperativeInfo.Status.PUBLISHED and not obj.published_date
        
        if is_publishing:
            obj.published_date = timezone.now()
            obj.published_by = request.user
            logger.info(f"User {request.user.username} published CooperativeInfo '{obj.cooperative_name}' (ID: {obj.pk})")
        elif change and was_published:
            logger.info(f"User {request.user.username} updated published CooperativeInfo '{obj.cooperative_name}' (ID: {obj.pk})")
        
        # Sync is_active with status for backward compatibility
        obj.is_active = (obj.status == CooperativeInfo.Status.PUBLISHED)
        super().save_model(request, obj, form, change)


class CooperativeTimelineAdmin(CompareVersionAdmin):
    """Enhanced admin interface for timeline events"""
    list_display = ('title', 'event_date', 'event_type', 'status', 'is_featured', 'scheduled_date', 'published_date', 'preview_link', 'order')
    list_filter = ('status', 'is_featured', 'event_type', 'event_date', 'scheduled_date')
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_featured')
    ordering = ('-event_date', 'order')
    date_hierarchy = 'event_date'
    list_per_page = 25
    readonly_fields = ('published_date', 'published_by', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'event_date', 'event_type')
        }),
        ('Publication Status', {
            'fields': ('status', 'scheduled_date', 'published_date', 'published_by'),
            'description': _('Set status to Published to make this event visible on the site.')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured')
        }),
        ('Legacy', {
            'fields': ('is_active',),
            'classes': ('collapse',),
            'description': _('Legacy field - automatically synced with status.')
        }),
    )
    
    actions = ['publish_selected', 'draft_selected', 'schedule_selected', 'archive_selected', 'feature_selected', 'unfeature_selected']
    
    def preview_link(self, obj):
        """Preview link for content"""
        if obj.pk:
            url = obj.get_preview_url()
            return format_html('<a href="{}" target="_blank" class="button">Preview</a>', url)
        return '-'
    preview_link.short_description = 'Preview'
    
    def publish_selected(self, request, queryset):
        count = queryset.update(status=CooperativeTimeline.Status.PUBLISHED, published_date=timezone.now(), published_by=request.user)
        self.message_user(request, f'{count} item(s) published successfully.', messages.SUCCESS)
    publish_selected.short_description = "Publish selected items"
    
    def draft_selected(self, request, queryset):
        count = queryset.update(status=CooperativeTimeline.Status.DRAFT)
        self.message_user(request, f'{count} item(s) moved to draft.', messages.SUCCESS)
    draft_selected.short_description = "Move selected to draft"
    
    def schedule_selected(self, request, queryset):
        count = queryset.update(status=CooperativeTimeline.Status.SCHEDULED)
        self.message_user(request, f'{count} item(s) scheduled.', messages.SUCCESS)
    schedule_selected.short_description = "Schedule selected items"
    
    def archive_selected(self, request, queryset):
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No items selected.', messages.WARNING)
            return
        logger.info(f"User {request.user.username} archived {count} CooperativeTimeline items")
        queryset.update(status=CooperativeTimeline.Status.ARCHIVED)
        self.message_user(request, f'{count} item(s) archived successfully.', messages.SUCCESS)
    archive_selected.short_description = "Archive selected items"
    
    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} item(s) were successfully featured.', messages.SUCCESS)
    feature_selected.short_description = "Feature selected items"
    
    def unfeature_selected(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} item(s) were successfully unfeatured.', messages.SUCCESS)
    unfeature_selected.short_description = "Unfeature selected items"
    
    def save_model(self, request, obj, form, change):
        was_published = obj.status == CooperativeTimeline.Status.PUBLISHED
        is_publishing = obj.status == CooperativeTimeline.Status.PUBLISHED and not obj.published_date
        if is_publishing:
            obj.published_date = timezone.now()
            obj.published_by = request.user
            logger.info(f"User {request.user.username} published CooperativeTimeline '{obj.title}' (ID: {obj.pk})")
        elif change and was_published:
            logger.info(f"User {request.user.username} updated published CooperativeTimeline '{obj.title}' (ID: {obj.pk})")
        obj.is_active = (obj.status == CooperativeTimeline.Status.PUBLISHED)
        super().save_model(request, obj, form, change)


class CooperativeStatisticAdmin(CompareVersionAdmin):
    """Admin interface for statistics - Home Page Impact Section
    
    These statistics appear in the "Our Impact" section on the home page.
    Only statistics with is_featured=True and status=Published will be displayed.
    Maximum 4 statistics are shown on the home page, ordered by 'order' field.
    """
    list_display = ('title', 'value', 'unit', 'statistic_type', 'status', 'is_featured', 'scheduled_date', 'published_date', 'preview_link', 'order', 'preview_display')
    list_filter = ('statistic_type', 'status', 'is_featured', 'scheduled_date')
    search_fields = ('title', 'description', 'value')
    list_editable = ('order', 'is_featured')  # Allow quick editing
    ordering = ('order', 'title')
    list_per_page = 25
    readonly_fields = ('published_date', 'published_by', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'value', 'unit', 'description', 'statistic_type'),
            'description': _(
                '<strong>Home Page Impact Section Statistics</strong><br>'
                'These statistics are displayed in the "Our Impact" section on the home page.<br>'
                'Only statistics with <strong>Featured</strong> and <strong>Status=Published</strong> will be shown.<br>'
                'Maximum 4 statistics are displayed, ordered by the "Display Order" field.<br><br>'
                '<strong>Examples:</strong><br>'
                '• Title: "Active Members", Value: "10K+", Unit: "members"<br>'
                '• Title: "Years of Service", Value: "25+", Unit: "years"<br>'
                '• Title: "Total Savings", Value: "500", Unit: "Million NPR"'
            )
        }),
        ('Publication Status', {
            'fields': ('status', 'scheduled_date', 'published_date', 'published_by'),
            'description': _('Set status to Published to make this statistic visible on the site.')
        }),
        ('Visual Settings', {
            'fields': ('icon', 'color'),
            'classes': ('collapse',),
            'description': _(
                '<strong>Icon:</strong> Use FontAwesome icon classes. Examples:<br>'
                '• fas fa-users (for members)<br>'
                '• fas fa-chart-line (for growth)<br>'
                '• fas fa-hand-holding-usd (for loans)<br>'
                '• fas fa-piggy-bank (for savings)<br>'
                '• fas fa-calendar-check (for years)<br><br>'
                '<strong>Color:</strong> Choose "deuraligreen" (green) or "bhanjyangred" (red) for border and icon colors.'
            )
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured'),
            'description': _(
                '<strong>Display Order:</strong> Lower numbers appear first (0, 1, 2, 3...).<br>'
                '<strong>Featured:</strong> Only featured statistics appear on home page. Check this to display.'
            )
        }),
        ('Legacy', {
            'fields': ('is_active',),
            'classes': ('collapse',),
            'description': _('Legacy field - automatically synced with status.')
        }),
    )
    
    actions = ['publish_selected', 'draft_selected', 'schedule_selected', 'archive_selected', 'feature_selected', 'unfeature_selected']
    
    def preview_link(self, obj):
        """Preview link for content"""
        if obj.pk:
            url = obj.get_preview_url()
            return format_html('<a href="{}" target="_blank" class="button">Preview</a>', url)
        return '-'
    preview_link.short_description = 'Preview'
    
    def publish_selected(self, request, queryset):
        count = queryset.update(status=CooperativeStatistic.Status.PUBLISHED, published_date=timezone.now(), published_by=request.user)
        self.message_user(request, f'{count} item(s) published successfully.', messages.SUCCESS)
    publish_selected.short_description = "Publish selected items"
    
    def draft_selected(self, request, queryset):
        count = queryset.update(status=CooperativeStatistic.Status.DRAFT)
        self.message_user(request, f'{count} item(s) moved to draft.', messages.SUCCESS)
    draft_selected.short_description = "Move selected to draft"
    
    def schedule_selected(self, request, queryset):
        count = queryset.update(status=CooperativeStatistic.Status.SCHEDULED)
        self.message_user(request, f'{count} item(s) scheduled.', messages.SUCCESS)
    schedule_selected.short_description = "Schedule selected items"
    
    def archive_selected(self, request, queryset):
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No items selected.', messages.WARNING)
            return
        logger.info(f"User {request.user.username} archived {count} CooperativeStatistic items")
        queryset.update(status=CooperativeStatistic.Status.ARCHIVED)
        self.message_user(request, f'{count} item(s) archived successfully.', messages.SUCCESS)
    archive_selected.short_description = "Archive selected items"
    
    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} item(s) were successfully featured.', messages.SUCCESS)
    feature_selected.short_description = "Feature selected items"
    
    def unfeature_selected(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} item(s) were successfully unfeatured.', messages.SUCCESS)
    unfeature_selected.short_description = "Unfeature selected items"
    
    def save_model(self, request, obj, form, change):
        was_published = obj.status == CooperativeStatistic.Status.PUBLISHED
        is_publishing = obj.status == CooperativeStatistic.Status.PUBLISHED and not obj.published_date
        if is_publishing:
            obj.published_date = timezone.now()
            obj.published_by = request.user
            logger.info(f"User {request.user.username} published CooperativeStatistic '{obj.title}' (ID: {obj.pk})")
        elif change and was_published:
            logger.info(f"User {request.user.username} updated published CooperativeStatistic '{obj.title}' (ID: {obj.pk})")
        obj.is_active = (obj.status == CooperativeStatistic.Status.PUBLISHED)
        super().save_model(request, obj, form, change)
    
    def preview_display(self, obj):
        """Show a preview of how the statistic will look"""
        if obj.is_featured and obj.is_active:
            status = format_html('<span style="color: green; font-weight: bold;">✓ Featured & Active</span>')
        elif obj.is_active:
            status = format_html('<span style="color: orange;">Active (not featured)</span>')
        else:
            status = format_html('<span style="color: red;">Inactive</span>')
        
        icon_preview = ''
        if obj.icon:
            icon_color = '#dc2626' if obj.color == 'bhanjyangred' else '#059669'
            icon_preview = format_html(
                '<i class="{}" style="color: {}; margin-right: 5px; font-size: 16px;"></i>',
                obj.icon,
                icon_color
            )
        else:
            icon_preview = '<span style="color: #999;">No icon</span>'
        
        return format_html(
            '{} {} | Order: {}',
            icon_preview,
            status,
            obj.order
        )
    preview_display.short_description = 'Status Preview'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related()


class CooperativeAffiliationAdmin(CompareVersionAdmin):
    """Admin interface for affiliations"""
    list_display = ('name', 'affiliation_type', 'status', 'is_featured', 'scheduled_date', 'published_date', 'preview_link', 'order')
    list_filter = ('affiliation_type', 'status', 'is_featured', 'scheduled_date')
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_featured')
    ordering = ('order', 'name')
    readonly_fields = ('published_date', 'published_by', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'affiliation_type', 'website', 'logo')
        }),
        ('Publication Status', {
            'fields': ('status', 'scheduled_date', 'published_date', 'published_by'),
            'description': _('Set status to Published to make this affiliation visible on the site.')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured')
        }),
        ('Legacy', {
            'fields': ('is_active',),
            'classes': ('collapse',),
            'description': _('Legacy field - automatically synced with status.')
        }),
    )
    
    actions = ['publish_selected', 'draft_selected', 'schedule_selected', 'archive_selected', 'feature_selected', 'unfeature_selected']
    
    def preview_link(self, obj):
        """Preview link for content"""
        if obj.pk:
            url = obj.get_preview_url()
            return format_html('<a href="{}" target="_blank" class="button">Preview</a>', url)
        return '-'
    preview_link.short_description = 'Preview'
    
    def publish_selected(self, request, queryset):
        count = queryset.update(status=CooperativeAffiliation.Status.PUBLISHED, published_date=timezone.now(), published_by=request.user)
        self.message_user(request, f'{count} item(s) published successfully.', messages.SUCCESS)
    publish_selected.short_description = "Publish selected items"
    
    def draft_selected(self, request, queryset):
        count = queryset.update(status=CooperativeAffiliation.Status.DRAFT)
        self.message_user(request, f'{count} item(s) moved to draft.', messages.SUCCESS)
    draft_selected.short_description = "Move selected to draft"
    
    def schedule_selected(self, request, queryset):
        count = queryset.update(status=CooperativeAffiliation.Status.SCHEDULED)
        self.message_user(request, f'{count} item(s) scheduled.', messages.SUCCESS)
    schedule_selected.short_description = "Schedule selected items"
    
    def archive_selected(self, request, queryset):
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No items selected.', messages.WARNING)
            return
        logger.info(f"User {request.user.username} archived {count} CooperativeAffiliation items")
        queryset.update(status=CooperativeAffiliation.Status.ARCHIVED)
        self.message_user(request, f'{count} item(s) archived successfully.', messages.SUCCESS)
    archive_selected.short_description = "Archive selected items"
    
    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} item(s) were successfully featured.', messages.SUCCESS)
    feature_selected.short_description = "Feature selected items"
    
    def unfeature_selected(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} item(s) were successfully unfeatured.', messages.SUCCESS)
    unfeature_selected.short_description = "Unfeature selected items"
    
    def save_model(self, request, obj, form, change):
        was_published = obj.status == CooperativeAffiliation.Status.PUBLISHED
        is_publishing = obj.status == CooperativeAffiliation.Status.PUBLISHED and not obj.published_date
        if is_publishing:
            obj.published_date = timezone.now()
            obj.published_by = request.user
            logger.info(f"User {request.user.username} published CooperativeAffiliation '{obj.name}' (ID: {obj.pk})")
        elif change and was_published:
            logger.info(f"User {request.user.username} updated published CooperativeAffiliation '{obj.name}' (ID: {obj.pk})")
        obj.is_active = (obj.status == CooperativeAffiliation.Status.PUBLISHED)
        super().save_model(request, obj, form, change)


class LeadershipMessageAdmin(CompareVersionAdmin):
    """Admin interface for leadership messages"""
    list_display = ('title', 'author_name', 'author_position', 'message_type', 'status', 'is_featured', 'scheduled_date', 'published_date', 'preview_link', 'order')
    list_filter = ('message_type', 'status', 'is_featured', 'scheduled_date')
    search_fields = ('title', 'author_name', 'content')
    list_editable = ('order', 'is_featured')
    ordering = ('order', 'message_type')
    readonly_fields = ('published_date', 'published_by', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'message_type', 'content')
        }),
        ('Author Information', {
            'fields': ('author_name', 'author_position', 'author_photo')
        }),
        ('Publication Status', {
            'fields': ('status', 'scheduled_date', 'published_date', 'published_by'),
            'description': _('Set status to Published to make this message visible on the site.')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured')
        }),
        ('Legacy', {
            'fields': ('is_active',),
            'classes': ('collapse',),
            'description': _('Legacy field - automatically synced with status.')
        }),
    )
    
    actions = ['publish_selected', 'draft_selected', 'schedule_selected', 'archive_selected', 'feature_selected', 'unfeature_selected']
    
    def preview_link(self, obj):
        """Preview link for content"""
        if obj.pk:
            url = obj.get_preview_url()
            return format_html('<a href="{}" target="_blank" class="button">Preview</a>', url)
        return '-'
    preview_link.short_description = 'Preview'
    
    def publish_selected(self, request, queryset):
        count = queryset.update(status=LeadershipMessage.Status.PUBLISHED, published_date=timezone.now(), published_by=request.user)
        self.message_user(request, f'{count} item(s) published successfully.', messages.SUCCESS)
    publish_selected.short_description = "Publish selected items"
    
    def draft_selected(self, request, queryset):
        count = queryset.update(status=LeadershipMessage.Status.DRAFT)
        self.message_user(request, f'{count} item(s) moved to draft.', messages.SUCCESS)
    draft_selected.short_description = "Move selected to draft"
    
    def schedule_selected(self, request, queryset):
        count = queryset.update(status=LeadershipMessage.Status.SCHEDULED)
        self.message_user(request, f'{count} item(s) scheduled.', messages.SUCCESS)
    schedule_selected.short_description = "Schedule selected items"
    
    def archive_selected(self, request, queryset):
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No items selected.', messages.WARNING)
            return
        logger.info(f"User {request.user.username} archived {count} LeadershipMessage items")
        queryset.update(status=LeadershipMessage.Status.ARCHIVED)
        self.message_user(request, f'{count} item(s) archived successfully.', messages.SUCCESS)
    archive_selected.short_description = "Archive selected items"
    
    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} item(s) were successfully featured.', messages.SUCCESS)
    feature_selected.short_description = "Feature selected items"
    
    def unfeature_selected(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} item(s) were successfully unfeatured.', messages.SUCCESS)
    unfeature_selected.short_description = "Unfeature selected items"
    
    def save_model(self, request, obj, form, change):
        was_published = obj.status == LeadershipMessage.Status.PUBLISHED
        is_publishing = obj.status == LeadershipMessage.Status.PUBLISHED and not obj.published_date
        if is_publishing:
            obj.published_date = timezone.now()
            obj.published_by = request.user
            logger.info(f"User {request.user.username} published LeadershipMessage '{obj.title}' (ID: {obj.pk})")
        elif change and was_published:
            logger.info(f"User {request.user.username} updated published LeadershipMessage '{obj.title}' (ID: {obj.pk})")
        obj.is_active = (obj.status == LeadershipMessage.Status.PUBLISHED)
        super().save_model(request, obj, form, change)


# Team Models Admin
class PersonAdmin(BaseContentAdmin):
    """Admin interface for Person model"""
    list_display = ('full_name', 'email', 'phone', 'position_general', 'is_active', 'created_at')
    list_filter = (ActiveFilter, 'created_at')
    search_fields = ('full_name', 'email', 'bio')
    list_editable = ('is_active',)  # Allow quick editing of active status
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('full_name', 'photo', 'bio')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'position_general')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class MembershipInlineForm(forms.ModelForm):
    """Custom form for MembershipInline that allows creating Person on the fly"""
    person_name = forms.CharField(
        max_length=100,
        required=False,
        help_text="Enter name directly (Person will be created automatically if not exists)"
    )
    
    class Meta:
        model = Membership
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If membership exists and has person, pre-fill the name
        if self.instance and self.instance.pk and self.instance.person:
            self.fields['person_name'].initial = self.instance.person.full_name
            self.fields['person_name'].widget.attrs['placeholder'] = self.instance.person.full_name
        else:
            self.fields['person_name'].widget.attrs['placeholder'] = 'Enter full name'
        
        # Make person field optional in the form
        self.fields['person'].required = False
        self.fields['person'].help_text = "Or select existing person (leave blank if entering name above)"
        
        # Make start_date optional
        self.fields['start_date'].required = False
        # Get committee from instance or parent (safely)
        committee = None
        try:
            if self.instance and self.instance.pk and hasattr(self.instance, 'committee'):
                committee = getattr(self.instance, 'committee', None)
        except Exception:
            pass
        
        if hasattr(self, 'committee'):
            committee = self.committee
        
        if committee and hasattr(committee, 'start_date') and committee.start_date:
            self.fields['start_date'].help_text = f"Optional - will use committee start date ({committee.start_date}) if not provided"
        else:
            self.fields['start_date'].help_text = "Optional - will use committee start date if not provided"
    
    def clean(self):
        cleaned_data = super().clean()
        person = cleaned_data.get('person')
        person_name = cleaned_data.get('person_name', '').strip()
        
        # Either person or person_name must be provided
        if not person and not person_name:
            # Check if instance already has a person (for existing memberships)
            if self.instance and self.instance.pk and self.instance.person_id:
                # Keep existing person
                cleaned_data['person'] = self.instance.person
            else:
                raise forms.ValidationError("Either select a person or enter a name.")
        
        # If both are provided, prioritize the explicit selection (person)
        if person and person_name:
            # Clear person_name so save() uses the selected person
            cleaned_data['person_name'] = ''
        
        # Validate position
        position = cleaned_data.get('position')
        position_custom = cleaned_data.get('position_custom')
        
        if not position:
            self.add_error('position', "Please select a position.")
        
        if position == 'other' and not position_custom:
            self.add_error('position_custom', "Custom position must be provided when 'Other' is selected.")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        person_name = self.cleaned_data.get('person_name', '').strip()
        person = self.cleaned_data.get('person')
        
        # Priority: Use selected person if provided, otherwise use person_name
        if person:
            # Use selected person
            instance.person = person
        elif person_name:
            # Create or get Person from name
            person_obj, created = Person.objects.get_or_create(
                full_name=person_name,
                defaults={'is_active': True}
            )
            instance.person = person_obj
        else:
            # If neither is provided, this should have been caught in clean()
            # But handle it gracefully
            if not instance.person_id:
                raise ValueError("Person must be provided either by name or selection")
        
        # Get committee from instance or from form attribute (safely)
        committee = None
        try:
            if instance.committee_id:  # Check if committee FK is set
                committee = instance.committee
        except Exception:
            pass
        
        if not committee and hasattr(self, 'committee') and self.committee:
            committee = self.committee
        
        # If start_date is not provided but committee has start_date, use it
        if not instance.start_date and committee and hasattr(committee, 'start_date') and committee.start_date:
            instance.start_date = committee.start_date
        
        if commit:
            instance.save()
        return instance


class MembershipInline(admin.TabularInline):
    """Inline admin for Committee memberships - Tabular format for easy editing"""
    model = Membership
    form = MembershipInlineForm
    extra = 1  # Show one empty row for adding new members
    autocomplete_fields = ['person']
    fields = ('person_name', 'person', 'position', 'position_custom', 'order', 'start_date', 'end_date', 'is_active')
    verbose_name = "Committee Member"
    verbose_name_plural = "Committee Members"
    ordering = ('order', 'person__full_name')
    can_delete = True
    show_change_link = True
    
    # Make fields more compact and user-friendly
    # Removed 'collapse' class so table is always visible for easy editing
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('person', 'committee').order_by('order', 'person__full_name')
    
    def get_formset(self, request, obj=None, **kwargs):
        """Override to pass committee object to forms"""
        formset_class = super().get_formset(request, obj, **kwargs)
        
        # Store committee for closure
        committee_obj = obj
        
        # Create custom formset that passes committee to forms
        class MembershipFormSet(formset_class):
            def _construct_form(self, i, **kwargs):
                form = super()._construct_form(i, **kwargs)
                # Set committee on form for use in save method
                if committee_obj:
                    form.committee = committee_obj
                return form
        
        return MembershipFormSet


class CommitteeAdmin(admin.ModelAdmin):
    """Admin interface for Committee model"""
    list_display = ('name', 'tenure_bs', 'is_active', 'order', 'member_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'tenure_bs', 'description')
    prepopulated_fields = {'slug': ('name', 'tenure_bs')}
    inlines = [MembershipInline]
    list_editable = ('order', 'is_active')  # Quick edit from list view
    save_on_top = True  # Save buttons at top and bottom
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'tenure_bs', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('photo',)
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def member_count(self, obj):
        """Display count of active committee members"""
        count = obj.memberships.filter(is_active=True).count()
        return count
    member_count.short_description = 'Active Members'


class MembershipAdmin(admin.ModelAdmin):
    """Admin interface for Membership model"""
    list_display = ('person', 'committee', 'position', 'order', 'is_active')
    list_filter = ('is_active', 'committee')
    search_fields = ('person__full_name', 'position', 'committee__name')
    autocomplete_fields = ['person', 'committee']
    list_editable = ('order', 'is_active')  # Allow quick editing
    list_select_related = ('person', 'committee')
    
    fieldsets = (
        ('Membership Information', {
            'fields': ('person', 'committee', 'position', 'position_custom')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


class StaffAdmin(admin.ModelAdmin):
    """Admin interface for Staff model"""
    list_display = ('person', 'position', 'department', 'is_information_officer_badge', 'is_active', 'order')
    list_filter = ('is_active', 'department', 'is_information_officer')
    search_fields = ('person__full_name', 'position', 'department')
    autocomplete_fields = ['person']
    list_editable = ('order', 'is_active')  # Allow quick editing
    list_select_related = ('person',)
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('person', 'position', 'department')
        }),
        ('Employment Details', {
            'fields': ('start_date', 'salary_range', 'qualifications')
        }),
        (_('RTI Act 2064 - Information Officer (सूचना अधिकारी)'), {
            'fields': ('is_information_officer', 'information_officer_email'),
            'classes': ('collapse',),
            'description': _('Designate this staff member as the Information Officer. Only one staff can be the active Information Officer at a time.')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    @admin.display(boolean=True, description=_('Information Officer'))
    def is_information_officer_badge(self, obj):
        """Display badge for Information Officer"""
        return obj.is_information_officer


# Register with custom admin site
from apps.admin.admin_site import admin_site

# Register all models with custom admin site
admin_site.register(CooperativeInfo, CooperativeInfoAdmin)
admin_site.register(CooperativeTimeline, CooperativeTimelineAdmin)
admin_site.register(CooperativeStatistic, CooperativeStatisticAdmin)
admin_site.register(CooperativeAffiliation, CooperativeAffiliationAdmin)
admin_site.register(LeadershipMessage, LeadershipMessageAdmin)
admin_site.register(Person, PersonAdmin)
admin_site.register(Committee, CommitteeAdmin)
admin_site.register(Membership, MembershipAdmin)
admin_site.register(Staff, StaffAdmin)
