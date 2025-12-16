from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ContactSubmission, KYMSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    """Admin interface for managing contact form submissions."""
    
    list_display = [
        'name', 'email', 'subject', 'status_badge', 'attachment_info', 'created_at', 'is_recent_badge'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = [
        'created_at', 'updated_at', 'ip_address', 'user_agent', 
        'is_recent_badge', 'message_preview'
    ]
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone'),
            'classes': ('wide',)
        }),
        ('Message Details', {
            'fields': ('subject', 'message', 'message_preview', 'attachment'),
            'classes': ('wide',)
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at', 'is_recent_badge'),
            'classes': ('collapse',)
        }),
        ('Admin Management', {
            'fields': ('status', 'admin_notes', 'resolved_at'),
            'classes': ('wide',)
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_spam', 'mark_as_in_progress']
    
    def status_badge(self, obj):
        """Display status as a colored badge"""
        colors = {
            'new': '#3b82f6',      # blue
            'in_progress': '#f59e0b',  # yellow
            'resolved': '#10b981',     # green
            'spam': '#ef4444',         # red
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def is_recent_badge(self, obj):
        """Display recent submissions with a badge"""
        if obj.is_recent():
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px;">NEW</span>'
            )
        return ''
    is_recent_badge.short_description = 'Recent'
    is_recent_badge.admin_order_field = 'created_at'
    
    def message_preview(self, obj):
        """Show a preview of the message"""
        if len(obj.message) > 200:
            return f"{obj.message[:200]}..."
        return obj.message
    message_preview.short_description = 'Message Preview'
    
    def attachment_info(self, obj):
        """Display attachment information"""
        if obj.has_attachment():
            filename = obj.get_attachment_filename()
            size = obj.get_attachment_size_display()
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">📎 {}</span><br>'
                '<span style="font-size: 11px; color: #6b7280;">{}</span>',
                filename, size
            )
        return format_html('<span style="color: #6b7280;">No attachment</span>')
    attachment_info.short_description = 'Attachment'
    attachment_info.admin_order_field = 'attachment'
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected submissions as resolved"""
        updated = queryset.update(
            status='resolved', 
            resolved_at=timezone.now()
        )
        self.message_user(
            request, 
            f'Successfully marked {updated} submission(s) as resolved.'
        )
    mark_as_resolved.short_description = "Mark selected submissions as resolved"
    
    def mark_as_spam(self, request, queryset):
        """Mark selected submissions as spam"""
        updated = queryset.update(status='spam')
        self.message_user(
            request, 
            f'Successfully marked {updated} submission(s) as spam.'
        )
    mark_as_spam.short_description = "Mark selected submissions as spam"
    
    def mark_as_in_progress(self, request, queryset):
        """Mark selected submissions as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(
            request, 
            f'Successfully marked {updated} submission(s) as in progress.'
        )
    mark_as_in_progress.short_description = "Mark selected submissions as in progress"
    
    def get_queryset(self, request):
        """Optimize queryset for admin list view"""
        return super().get_queryset(request).select_related()
    
    def has_add_permission(self, request):
        """Disable adding new submissions through admin"""
        return False
    
@admin.register(KYMSubmission)
class KYMSubmissionAdmin(admin.ModelAdmin):
    """Admin interface for managing KYM form submissions."""
    
    list_display = [
        'full_name', 'email', 'phone', 'status_badge', 'occupation', 
        'created_at', 'is_recent_badge'
    ]
    list_filter = ['status', 'created_at', 'district', 'gender']
    search_fields = ['full_name', 'email', 'phone', 'permanent_address', 'occupation']
    readonly_fields = [
        'created_at', 'updated_at', 'ip_address', 'user_agent', 
        'is_recent_badge', 'document_preview'
    ]
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'dob', 'gender', 'marital_status', 'nationality'),
            'classes': ('wide',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'permanent_address', 'district', 'province'),
            'classes': ('wide',)
        }),
        ('Family Details', {
            'fields': ('father_name', 'mother_name', 'spouse_name', 'grand_father_name', 'nominee_name'),
            'classes': ('wide',)
        }),
        ('Occupation & Income', {
            'fields': ('occupation', 'income_source', 'estimated_income'),
            'classes': ('wide',)
        }),
        ('Documents', {
            'fields': ('citizenship_front', 'citizenship_back', 'passport_photo', 
                      'address_proof', 'income_proof', 'document_preview'),
            'classes': ('wide',)
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at', 'is_recent_badge'),
            'classes': ('collapse',)
        }),
        ('Admin Management', {
            'fields': ('status', 'admin_notes', 'reviewed_at', 'reviewed_by'),
            'classes': ('wide',)
        }),
    )
    
    actions = ['mark_as_approved', 'mark_as_rejected', 'mark_as_under_review']
    
    def status_badge(self, obj):
        """Display status as a colored badge"""
        colors = {
            'pending': '#3b82f6',      # blue
            'under_review': '#f59e0b',  # yellow
            'approved': '#10b981',     # green
            'rejected': '#ef4444',     # red
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def is_recent_badge(self, obj):
        """Display recent submissions with a badge"""
        if obj.is_recent():
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px;">NEW</span>'
            )
        return ''
    is_recent_badge.short_description = 'Recent'
    is_recent_badge.admin_order_field = 'created_at'
    
    def document_preview(self, obj):
        """Show document links"""
        docs = []
        if obj.citizenship_front:
            docs.append(f'<a href="{obj.citizenship_front.url}" target="_blank">Citizenship Front</a>')
        if obj.citizenship_back:
            docs.append(f'<a href="{obj.citizenship_back.url}" target="_blank">Citizenship Back</a>')
        if obj.passport_photo:
            docs.append(f'<a href="{obj.passport_photo.url}" target="_blank">Passport Photo</a>')
        if obj.address_proof:
            docs.append(f'<a href="{obj.address_proof.url}" target="_blank">Address Proof</a>')
        if obj.income_proof:
            docs.append(f'<a href="{obj.income_proof.url}" target="_blank">Income Proof</a>')
        
        if docs:
            return format_html('<br>'.join(docs))
        return 'No documents'
    document_preview.short_description = 'Documents'
    
    def mark_as_approved(self, request, queryset):
        """Mark selected submissions as approved"""
        updated = queryset.update(
            status='approved',
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(
            request,
            f'Successfully marked {updated} submission(s) as approved.'
        )
    mark_as_approved.short_description = "Mark selected submissions as approved"
    
    def mark_as_rejected(self, request, queryset):
        """Mark selected submissions as rejected"""
        updated = queryset.update(
            status='rejected',
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(
            request,
            f'Successfully marked {updated} submission(s) as rejected.'
        )
    mark_as_rejected.short_description = "Mark selected submissions as rejected"
    
    def mark_as_under_review(self, request, queryset):
        """Mark selected submissions as under review"""
        updated = queryset.update(status='under_review')
        self.message_user(
            request,
            f'Successfully marked {updated} submission(s) as under review.'
        )
    mark_as_under_review.short_description = "Mark selected submissions as under review"
    
    def has_add_permission(self, request):
        """Disable adding new submissions through admin"""
        return False

# Register with custom admin site
from apps.admin.admin_site import admin_site

admin_site.register(ContactSubmission, ContactSubmissionAdmin)
admin_site.register(KYMSubmission, KYMSubmissionAdmin)
