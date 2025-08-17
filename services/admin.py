from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SavingsAccount, FixedDeposit, LoanType, 
    RemittanceService, ServiceCategory, MemberRelief
)


@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    list_display = [
        'account_type', 'nepali_name', 'english_name', 
        'interest_rate', 'minimum_balance', 'is_featured', 'is_active'
    ]
    list_filter = ['is_active', 'is_featured', 'account_type']
    search_fields = ['nepali_name', 'english_name', 'description']
    list_editable = ['interest_rate', 'minimum_balance', 'is_featured', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('account_type', 'nepali_name', 'english_name')
        }),
        ('Financial Details', {
            'fields': ('interest_rate', 'minimum_balance')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'is_featured')
        }),
        ('Additional Information', {
            'fields': ('description', 'features')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FixedDeposit)
class FixedDepositAdmin(admin.ModelAdmin):
    list_display = [
        'duration_months', 'payment_frequency', 'interest_rate', 
        'minimum_amount', 'maximum_amount', 'is_active'
    ]
    list_filter = ['is_active', 'duration_months', 'payment_frequency']
    search_fields = ['duration_months', 'payment_frequency']
    list_editable = ['interest_rate', 'minimum_amount', 'maximum_amount', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Deposit Details', {
            'fields': ('duration_months', 'payment_frequency')
        }),
        ('Financial Details', {
            'fields': ('interest_rate', 'minimum_amount', 'maximum_amount')
        }),
        ('Display Settings', {
            'fields': ('icon',)
        }),
        ('Additional Information', {
            'fields': ('description', 'benefits')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = [
        'loan_category', 'nepali_name', 'english_name',
        'monthly_installment_rate', 'quarterly_installment_rate', 
        'monthly_interest_rate', 'is_featured', 'is_active'
    ]
    list_filter = ['is_active', 'is_featured', 'loan_category']
    search_fields = ['nepali_name', 'english_name', 'description']
    list_editable = [
        'monthly_installment_rate', 'quarterly_installment_rate', 
        'monthly_interest_rate', 'is_featured', 'is_active'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('loan_category', 'nepali_name', 'english_name')
        }),
        ('Interest Rates', {
            'fields': (
                'monthly_installment_rate', 'quarterly_installment_rate', 
                'monthly_interest_rate'
            )
        }),
        ('Loan Limits', {
            'fields': ('minimum_amount', 'maximum_amount', 'max_tenure_years')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'is_featured')
        }),
        ('Additional Information', {
            'fields': ('description', 'requirements', 'benefits')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RemittanceService)
class RemittanceServiceAdmin(admin.ModelAdmin):
    list_display = [
        'service_type', 'name', 'processing_time', 
        'transfer_limit_min', 'transfer_limit_max', 'is_active'
    ]
    list_filter = ['is_active', 'service_type']
    search_fields = ['name', 'description', 'features']
    list_editable = ['processing_time', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service_type', 'name', 'description')
        }),
        ('Features & Limits', {
            'fields': ('features', 'transfer_limit_min', 'transfer_limit_max')
        }),
        ('Processing & Fees', {
            'fields': ('processing_time', 'fees')
        }),
        ('Display Settings', {
            'fields': ('icon',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MemberRelief)
class MemberReliefAdmin(admin.ModelAdmin):
    list_display = [
        'relief_type', 'title', 'nepali_title', 'is_active'
    ]
    list_filter = ['is_active', 'relief_type']
    search_fields = ['title', 'nepali_title', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('relief_type', 'title', 'nepali_title')
        }),
        ('Content', {
            'fields': ('description', 'eligibility', 'benefits')
        }),
        ('Process & Documents', {
            'fields': ('application_process', 'required_documents')
        }),
        ('Contact & Media', {
            'fields': ('contact_info', 'image')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'nepali_name', 'order', 'color', 'is_active'
    ]
    list_filter = ['is_active', 'color']
    search_fields = ['name', 'nepali_name', 'description']
    list_editable = ['order', 'color', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'nepali_name', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Customize admin site
admin.site.site_header = "Bhanjyang Cooperative Services Admin"
admin.site.site_title = "Services Admin"
admin.site.index_title = "Financial Services Management"
