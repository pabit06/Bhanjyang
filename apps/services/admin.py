from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
import json

from .models import (
    SavingsAccount, FixedDeposit, LoanType, 
    RemittanceService, MemberRelief, DigitalService,
    ServiceApplication, ServiceAnalytics, ServiceRecommendation,
    ExchangeRate
)

# HELPER FUNCTIONS for common admin enhancements
def create_boolean_icon(field_name, description):
    """Creates a method that returns a check or cross icon for a boolean field."""
    def boolean_icon(self, obj):
        is_true = getattr(obj, field_name)
        icon = '✅' if is_true else '❌'
        return icon
    boolean_icon.short_description = description
    return boolean_icon

def create_color_preview(field_name):
    """Creates a method that displays a color swatch."""
    def color_preview(self, obj):
        color = getattr(obj, field_name)
        if not color:
            return "N/A"
        # Use Tailwind CSS class names if they match, otherwise use style
        # Note: This requires your admin CSS to include Tailwind or custom styles
        return format_html(
            '<span style="background-color: var(--color-{0}, {0}); width: 20px; height: 20px; display: inline-block; border-radius: 50%; border: 1px solid #ccc;"></span> {0}',
            color
        )
    color_preview.short_description = "Color Preview"
    return color_preview

@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    """Admin interface for Savings Accounts with visual enhancements."""
    list_display = [
        'english_name', 'nepali_name', 'category', 'interest_rate', 'minimum_balance', 
        'is_featured_icon', 'is_active_icon', 'display_color'
    ]
    list_filter = ['category', 'is_active', 'is_featured', 'account_type']
    search_fields = ['nepali_name', 'english_name', 'description']
    list_editable = ['interest_rate', 'minimum_balance']
    readonly_fields = ['created_at', 'updated_at', 'slug']
    
    fieldsets = (
        ('Basic Information', {'fields': ('account_type', 'english_name', 'nepali_name', 'slug')}),
        ('Financial Details', {'fields': ('interest_rate', 'minimum_balance')}),
        ('Display Settings', {'fields': ('icon', 'color', 'is_featured', 'is_active')}),
        ('Additional Information', {'fields': ('description', 'features')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    is_featured_icon = create_boolean_icon('is_featured', 'Featured')
    is_active_icon = create_boolean_icon('is_active', 'Active')
    display_color = create_color_preview('color')
    display_color.short_description = "Color"


@admin.register(FixedDeposit)
class FixedDepositAdmin(admin.ModelAdmin):
    """Admin interface for Fixed Deposits with added actions."""
    list_display = [
        '__str__', 'interest_rate', 'minimum_amount', 'maximum_amount', 'is_active_icon'
    ]
    list_filter = ['is_active', 'duration_months', 'payment_frequency']
    search_fields = ['description', 'benefits']
    list_editable = ['interest_rate', 'minimum_amount', 'maximum_amount']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['activate_deposits', 'deactivate_deposits']
    
    fieldsets = (
        ('Deposit Details', {'fields': ('duration_months', 'payment_frequency')}),
        ('Financial Details', {'fields': ('interest_rate', 'minimum_amount', 'maximum_amount')}),
        ('Display & Info', {'fields': ('benefits',)}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    is_active_icon = create_boolean_icon('is_active', 'Active')

    @admin.action(description='Activate selected fixed deposits')
    def activate_deposits(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Successfully activated {updated} fixed deposit(s).', 'success')

    @admin.action(description='Deactivate selected fixed deposits')
    def deactivate_deposits(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Successfully deactivated {updated} fixed deposit(s).', 'success')

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    """Admin interface for Loan Types with calculated fields."""
    list_display = [
        'english_name', 'monthly_interest_rate', 'annual_interest_display',
        'is_featured_icon', 'is_active_icon', 'image_preview'
    ]
    list_filter = ['is_active', 'is_featured', 'loan_category']
    search_fields = ['nepali_name', 'english_name']
    list_editable = ['monthly_interest_rate']
    readonly_fields = ['created_at', 'updated_at', 'slug', 'image_preview']
    
    fieldsets = (
        ('Basic Information', {'fields': ('loan_category', 'english_name', 'nepali_name', 'slug')}),
        ('Interest Rates', {'fields': ('monthly_interest_rate',)}),
        ('Loan Limits', {'fields': ('minimum_amount', 'maximum_amount', 'max_tenure_years')}),
        ('Display Settings', {'fields': ('icon', 'color', 'is_featured', 'is_active')}),
        ('Media', {'fields': ('image', 'image_preview')}),
        ('Additional Information', {'fields': ('description', 'requirements', 'benefits')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    is_featured_icon = create_boolean_icon('is_featured', 'Featured')
    is_active_icon = create_boolean_icon('is_active', 'Active')

    @admin.display(description='Annual Interest Rate (%)')
    def annual_interest_display(self, obj):
        return obj.annual_interest_rate

    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "No Image"

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    """Admin interface for Exchange Rates with NRB integration."""
    list_display = [
        'currency_code', 'buy_rate', 'sell_rate', 'mid_rate', 
        'rate_date', 'source', 'is_active'
    ]
    list_filter = ['currency_code', 'rate_date', 'source', 'is_active']
    search_fields = ['currency_code', 'notes']
    list_editable = ['buy_rate', 'sell_rate', 'is_active']
    readonly_fields = ['mid_rate', 'created_at', 'updated_at']
    date_hierarchy = 'rate_date'
    ordering = ['-rate_date', 'currency_code']
    
    fieldsets = (
        ('Rate Information', {
            'fields': ('currency_code', 'rate_date', 'buy_rate', 'sell_rate', 'mid_rate')
        }),
        ('Metadata', {
            'fields': ('source', 'is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    is_active_icon = create_boolean_icon('is_active', 'Active')
    
    actions = ['fetch_nrb_rates', 'deactivate_old_rates']
    
    @admin.action(description='Fetch latest rates from NRB')
    def fetch_nrb_rates(self, request, queryset):
        """Action to fetch rates from NRB API."""
        from .services import ExchangeRateService
        try:
            count = ExchangeRateService.fetch_nrb_rates()
            self.message_user(
                request, 
                f'Successfully fetched {count} exchange rate(s) from NRB.', 
                'success'
            )
        except Exception as e:
            self.message_user(
                request, 
                f'Error fetching rates: {str(e)}', 
                'error'
            )
    
    @admin.action(description='Deactivate rates older than today')
    def deactivate_old_rates(self, request, queryset):
        """Deactivate rates that are not current."""
        from django.utils import timezone
        today = timezone.now().date()
        updated = queryset.filter(rate_date__lt=today).update(is_active=False)
        self.message_user(
            request, 
            f'Deactivated {updated} old rate(s).', 
            'success'
        )

@admin.register(RemittanceService)
class RemittanceServiceAdmin(admin.ModelAdmin):
    """Admin interface for Remittance Services."""
    list_display = ['english_name', 'service_type', 'processing_time', 'is_active_icon']
    list_filter = ['is_active', 'service_type']
    search_fields = ['english_name', 'description']
    list_editable = ['processing_time']
    readonly_fields = ['created_at', 'updated_at', 'slug']
    is_active_icon = create_boolean_icon('is_active', 'Active')

@admin.register(MemberRelief)
class MemberReliefAdmin(admin.ModelAdmin):
    """Admin interface for Member Relief programs with image previews."""
    list_display = ['english_name', 'relief_type', 'is_active_icon', 'image_preview']
    list_filter = ['is_active', 'relief_type']
    search_fields = ['english_name', 'nepali_name']
    readonly_fields = ['created_at', 'updated_at', 'slug', 'image_preview']
    fieldsets = (
        ('Basic Information', {'fields': ('relief_type', 'english_name', 'nepali_name', 'slug')}),
        ('Content', {'fields': ('description', 'eligibility', 'benefits')}),
        ('Process & Media', {'fields': ('application_process', 'image', 'image_preview')}),
        ('Display Settings', {'fields': ('icon', 'color', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    is_active_icon = create_boolean_icon('is_active', 'Active')

    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image.url
            )
        return "No Image"

@admin.register(DigitalService)
class DigitalServiceAdmin(admin.ModelAdmin):
    """Admin interface for Digital Services."""
    list_display = ['english_name', 'service_type', 'is_featured_icon', 'is_active_icon', 'image_preview']
    list_filter = ['is_active', 'is_featured', 'service_type']
    search_fields = ['english_name', 'nepali_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'slug', 'image_preview']
    fieldsets = (
        ('Basic Information', {'fields': ('service_type', 'english_name', 'nepali_name', 'slug')}),
        ('Content', {'fields': ('description', 'features', 'requirements', 'fees')}),
        ('Media', {'fields': ('image', 'image_preview')}),
        ('Display Settings', {'fields': ('icon', 'color', 'is_featured', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    is_featured_icon = create_boolean_icon('is_featured', 'Featured')
    is_active_icon = create_boolean_icon('is_active', 'Active')
    
    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image.url
            )
        return "No Image"

    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "No Image"

@admin.register(ServiceApplication)
class ServiceApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Service Applications with custom actions and linking."""
    list_display = [
        'applicant_name', 'link_to_service', 'status', 'status_badge', 'applied_date'
    ]
    list_filter = ['status', 'content_type', 'applied_date']
    search_fields = ['applicant_name', 'applicant_email', 'applicant_phone']
    list_editable = ['status']
    readonly_fields = [
        'applied_date', 'reviewed_date', 'applicant_name', 
        'applicant_email', 'applicant_phone', 'applicant_address', 'additional_info',
        'link_to_service'
    ]
    actions = ['mark_as_approved', 'mark_as_rejected', 'mark_as_under_review']
    
    fieldsets = (
        ('Application Summary', {'fields': ('status', 'link_to_service')}),
        ('Applicant Details', {'fields': ('applicant_name', 'applicant_email', 'applicant_phone', 'applicant_address')}),
        ('Application Data', {'fields': ('additional_info',), 'classes': ('collapse',)}),
        ('Review Information', {'fields': ('reviewed_date', 'reviewed_by', 'notes')}),
        ('Timestamps', {'fields': ('applied_date',)}),
    )

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending': 'blue', 'approved': 'green', 'rejected': 'red',
            'under_review': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {0}; color: white; padding: 3px 8px; border-radius: 12px;">{1}</span>',
            color, obj.get_status_display()
        )

    @admin.display(description='Service')
    def link_to_service(self, obj):
        if obj.service_object:
            app_label = obj.content_type.app_label
            model_name = obj.content_type.model
            link = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.object_id])
            return mark_safe(f'<a href="{link}">View {obj.service_name}</a>')
        return "N/A"

    @admin.action(description='Mark selected applications as Approved')
    def mark_as_approved(self, request, queryset):
        queryset.update(status='approved', reviewed_date=timezone.now(), reviewed_by=request.user.username)
        self.message_user(request, f'Marked {queryset.count()} application(s) as Approved.', 'success')

    @admin.action(description='Mark selected as Rejected')
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected', reviewed_date=timezone.now(), reviewed_by=request.user.username)
        self.message_user(request, f'Marked {queryset.count()} application(s) as Rejected.', 'warning')

    @admin.action(description='Mark selected as Under Review')
    def mark_as_under_review(self, request, queryset):
        queryset.update(status='under_review', reviewed_by=request.user.username)
        self.message_user(request, f'Marked {queryset.count()} application(s) as Under Review.', 'info')

@admin.register(ServiceAnalytics)
class ServiceAnalyticsAdmin(admin.ModelAdmin):
    """Read-only admin for service analytics."""
    list_display = ['date', 'link_to_service', 'page_views', 'applications_received', 'calculator_usage']
    list_filter = ['date']
    readonly_fields = [f.name for f in ServiceAnalytics._meta.fields]

    # Re-using the link_to_service method from ServiceApplicationAdmin
    link_to_service = ServiceApplicationAdmin.link_to_service

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ServiceRecommendation)
class ServiceRecommendationAdmin(admin.ModelAdmin):
    """Read-only admin for service recommendations with pretty-printed JSON."""
    list_display = ['created_at', 'user_profile_summary', 'confidence_score']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'pretty_user_profile', 'pretty_recommended_services', 'recommendation_reason', 'confidence_score']

    @admin.display(description='User Profile')
    def user_profile_summary(self, obj):
        profile = obj.user_profile
        age = profile.get('age', 'N/A')
        income = profile.get('monthly_income', 'N/A')
        return f"Age: {age}, Income: NPR {income:,}"

    @admin.display(description='User Profile Data')
    def pretty_user_profile(self, obj):
        return mark_safe(f"<pre>{json.dumps(obj.user_profile, indent=2)}</pre>")

    @admin.display(description='Recommended Services')
    def pretty_recommended_services(self, obj):
        return mark_safe(f"<pre>{json.dumps(obj.recommended_services, indent=2)}</pre>")

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

# Register with custom admin site
from apps.admin.admin_site import admin_site

admin_site.register(SavingsAccount, SavingsAccountAdmin)
admin_site.register(FixedDeposit, FixedDepositAdmin)
admin_site.register(LoanType, LoanTypeAdmin)
admin_site.register(ExchangeRate, ExchangeRateAdmin)
admin_site.register(RemittanceService, RemittanceServiceAdmin)
admin_site.register(DigitalService, DigitalServiceAdmin)
admin_site.register(MemberRelief, MemberReliefAdmin)
admin_site.register(ServiceApplication, ServiceApplicationAdmin)
admin_site.register(ServiceAnalytics, ServiceAnalyticsAdmin)
admin_site.register(ServiceRecommendation, ServiceRecommendationAdmin)
