from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)


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


@admin.register(CooperativeInfo)
class CooperativeInfoAdmin(admin.ModelAdmin):
    """Enhanced admin interface for cooperative information"""
    list_display = ('cooperative_name', 'established_date', 'registration_number', 'is_active', 'created_at', 'actions_column')
    list_filter = (ActiveFilter, 'established_date', 'created_at')
    search_fields = ('cooperative_name', 'cooperative_name_nepali', 'description', 'registration_number')
    prepopulated_fields = {'slug': ('cooperative_name',)}
    ordering = ('-created_at',)
    list_per_page = 25
    
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
        ('Media', {
            'fields': ('logo', 'featured_image'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def actions_column(self, obj):
        """Custom actions column"""
        return format_html(
            '<a href="{}" class="button">View on Site</a>',
            reverse('about:home')
        )
    actions_column.short_description = 'Actions'
    
    actions = ['activate_selected', 'deactivate_selected']
    
    def activate_selected(self, request, queryset):
        """Bulk activate selected items"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} items were successfully activated.')
    activate_selected.short_description = "Activate selected items"
    
    def deactivate_selected(self, request, queryset):
        """Bulk deactivate selected items"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} items were successfully deactivated.')
    deactivate_selected.short_description = "Deactivate selected items"


@admin.register(CooperativeTimeline)
class CooperativeTimelineAdmin(admin.ModelAdmin):
    """Enhanced admin interface for timeline events"""
    list_display = ('title', 'event_date', 'event_type', 'is_featured', 'is_active', 'order')
    list_filter = (ActiveFilter, FeaturedFilter, 'event_type', 'event_date')
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_featured', 'is_active')
    ordering = ('-event_date', 'order')
    date_hierarchy = 'event_date'
    list_per_page = 25
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'event_date', 'event_type')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['activate_selected', 'deactivate_selected', 'feature_selected', 'unfeature_selected']
    
    def feature_selected(self, request, queryset):
        """Bulk feature selected items"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} items were successfully featured.')
    feature_selected.short_description = "Feature selected items"
    
    def unfeature_selected(self, request, queryset):
        """Bulk unfeature selected items"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} items were successfully unfeatured.')
    unfeature_selected.short_description = "Unfeature selected items"


@admin.register(CooperativeAchievement)
class CooperativeAchievementAdmin(admin.ModelAdmin):
    """Admin interface for achievements"""
    list_display = ('title', 'achievement_type', 'awarding_organization', 'received_date', 'is_featured')
    list_filter = ('achievement_type', 'is_featured', 'is_active', 'received_date')
    search_fields = ('title', 'description', 'awarding_organization')
    ordering = ('-received_date', 'order')
    date_hierarchy = 'received_date'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'achievement_type', 'received_date', 'awarding_organization')
        }),
        ('Media', {
            'fields': ('certificate_image', 'logo'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CooperativeStatistic)
class CooperativeStatisticAdmin(admin.ModelAdmin):
    """Admin interface for statistics"""
    list_display = ('title', 'value', 'unit', 'statistic_type', 'is_featured')
    list_filter = ('statistic_type', 'is_featured', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('order', 'title')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'value', 'unit', 'description', 'statistic_type')
        }),
        ('Visual Settings', {
            'fields': ('icon', 'color'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CooperativeAffiliation)
class CooperativeAffiliationAdmin(admin.ModelAdmin):
    """Admin interface for affiliations"""
    list_display = ('name', 'affiliation_type', 'is_featured', 'is_active')
    list_filter = ('affiliation_type', 'is_featured', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'affiliation_type', 'website')
        }),
        ('Media', {
            'fields': ('logo',),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LeadershipMessage)
class LeadershipMessageAdmin(admin.ModelAdmin):
    """Admin interface for leadership messages"""
    list_display = ('title', 'author_name', 'author_position', 'message_type', 'is_featured')
    list_filter = ('message_type', 'is_featured', 'is_active')
    search_fields = ('title', 'author_name', 'content')
    ordering = ('order', 'message_type')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'message_type', 'content')
        }),
        ('Author Information', {
            'fields': ('author_name', 'author_position', 'author_photo')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


# Register with custom admin site
from apps.core.admin_site import admin_site

admin_site.register(CooperativeInfo, CooperativeInfoAdmin)
admin_site.register(CooperativeTimeline, CooperativeTimelineAdmin)
admin_site.register(CooperativeAchievement, CooperativeAchievementAdmin)
admin_site.register(CooperativeStatistic, CooperativeStatisticAdmin)
admin_site.register(CooperativeAffiliation, CooperativeAffiliationAdmin)
admin_site.register(LeadershipMessage, LeadershipMessageAdmin)

# Team Models Admin
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Admin interface for Person model"""
    list_display = ('full_name', 'email', 'phone', 'position_general', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('full_name', 'email', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    
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


class MembershipInline(admin.TabularInline):
    """Inline admin for Committee memberships"""
    model = Membership
    extra = 1
    autocomplete_fields = ['person']
    fields = ('person', 'position', 'order', 'is_active')


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    """Admin interface for Committee model"""
    list_display = ('name', 'tenure_bs', 'is_active', 'order', 'member_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'tenure_bs', 'description')
    prepopulated_fields = {'slug': ('name', 'tenure_bs')}
    inlines = [MembershipInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'tenure_bs', 'slug', 'description')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def member_count(self, obj):
        return obj.memberships.count()
    member_count.short_description = 'Members'


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Admin interface for Membership model"""
    list_display = ('person', 'committee', 'position', 'order', 'is_active')
    list_filter = ('is_active', 'committee')
    search_fields = ('person__full_name', 'position', 'committee__name')
    autocomplete_fields = ['person', 'committee']
    
    fieldsets = (
        ('Membership Information', {
            'fields': ('person', 'committee', 'position')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """Admin interface for Staff model"""
    list_display = ('person', 'position', 'department', 'is_active', 'order')
    list_filter = ('is_active', 'department')
    search_fields = ('person__full_name', 'position', 'department')
    autocomplete_fields = ['person']
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('person', 'position', 'department')
        }),
        ('Employment Details', {
            'fields': ('start_date', 'salary_range', 'qualifications')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )

# Register team models with custom admin site
admin_site.register(Person, PersonAdmin)
admin_site.register(Committee, CommitteeAdmin)
admin_site.register(Membership, MembershipAdmin)
admin_site.register(Staff, StaffAdmin)
