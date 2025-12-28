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
from .models import (
    CooperativeInfo, CooperativeTimeline,
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


class CooperativeInfoAdmin(admin.ModelAdmin):
    """Enhanced admin interface for cooperative information"""
    list_display = ('cooperative_name', 'established_date', 'registration_number', 'is_active', 'created_at', 'actions_column')
    list_filter = (ActiveFilter, 'established_date', 'created_at')
    search_fields = ('cooperative_name', 'cooperative_name_nepali', 'description', 'our_story', 'registration_number')
    prepopulated_fields = {'slug': ('cooperative_name',)}
    list_editable = ('is_active',)  # Allow quick editing of active status
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
        ('Our Story', {
            'fields': ('our_story', 'our_story_nepali', 'our_story_image'),
            'description': _('Content displayed in the "Our Story" section on the About Us page')
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
        if obj.slug:
            view_url = reverse('about:cooperative_detail', kwargs={'slug': obj.slug})
        else:
            view_url = reverse('about:introduction')
        return format_html(
            '<a href="{}" class="button" target="_blank">View on Site</a>',
            view_url
        )
    actions_column.short_description = 'Actions'
    
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
        self.message_user(request, f'{updated} item(s) were successfully featured.', messages.SUCCESS)
    feature_selected.short_description = "Feature selected items"
    
    def unfeature_selected(self, request, queryset):
        """Bulk unfeature selected items"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} item(s) were successfully unfeatured.', messages.SUCCESS)
    unfeature_selected.short_description = "Unfeature selected items"


class CooperativeStatisticAdmin(admin.ModelAdmin):
    """Admin interface for statistics"""
    list_display = ('title', 'value', 'unit', 'statistic_type', 'is_featured', 'is_active', 'order')
    list_filter = ('statistic_type', 'is_featured', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_featured', 'is_active')  # Allow quick editing
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


class CooperativeAffiliationAdmin(admin.ModelAdmin):
    """Admin interface for affiliations"""
    list_display = ('name', 'affiliation_type', 'is_featured', 'is_active', 'order')
    list_filter = ('affiliation_type', 'is_featured', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_featured', 'is_active')  # Allow quick editing
    ordering = ('order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'affiliation_type', 'website', 'logo')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


class LeadershipMessageAdmin(admin.ModelAdmin):
    """Admin interface for leadership messages"""
    list_display = ('title', 'author_name', 'author_position', 'message_type', 'is_featured', 'is_active', 'order')
    list_filter = ('message_type', 'is_featured', 'is_active')
    search_fields = ('title', 'author_name', 'content')
    list_editable = ('order', 'is_featured', 'is_active')  # Allow quick editing
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


# Team Models Admin
class PersonAdmin(admin.ModelAdmin):
    """Admin interface for Person model"""
    list_display = ('full_name', 'email', 'phone', 'position_general', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('full_name', 'email', 'bio')
    list_editable = ('is_active',)  # Allow quick editing of active status
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
