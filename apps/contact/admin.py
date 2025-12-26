import csv
import json
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from datetime import timedelta
from .models import ContactSubmission, KYMSubmission, OfficeLocation


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
    
    actions = [
        'mark_as_resolved', 'mark_as_spam', 'mark_as_in_progress', 
        'mark_as_new', 'export_to_csv', 'delete_selected'
    ]
    
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
    
    def mark_as_new(self, request, queryset):
        """Mark selected submissions as new"""
        updated = queryset.update(status='new')
        self.message_user(
            request,
            f'Successfully marked {updated} submission(s) as new.'
        )
    mark_as_new.short_description = "Mark selected submissions as new"
    
    def delete_selected(self, request, queryset):
        """Delete selected submissions"""
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f'Successfully deleted {count} submission(s).'
        )
    delete_selected.short_description = "🗑️ Delete selected submissions"
    
    def export_to_csv(self, request, queryset):
        """Export selected contact submissions to CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="contact_submissions_{}.csv"'.format(
            timezone.now().strftime('%Y%m%d_%H%M%S')
        )
        
        # Write BOM for Excel UTF-8 support
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Email', 'Phone', 'Subject', 'Message', 
            'Status', 'Has Attachment', 'IP Address', 'Created At', 
            'Updated At', 'Resolved At', 'Admin Notes'
        ])
        
        for submission in queryset:
            writer.writerow([
                submission.id,
                submission.name,
                submission.email,
                submission.phone or '',
                submission.subject,
                submission.message[:500] + '...' if len(submission.message) > 500 else submission.message,
                submission.get_status_display(),
                'Yes' if submission.has_attachment() else 'No',
                str(submission.ip_address),
                submission.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                submission.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                submission.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if submission.resolved_at else '',
                submission.admin_notes or ''
            ])
        
        return response
    export_to_csv.short_description = "📊 Export selected submissions to CSV"
    
    def get_urls(self):
        """Add custom analytics URL"""
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='contact_contactsubmission_analytics'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        """Contact submissions analytics dashboard"""
        from django.db.models.functions import TruncDate
        
        # Date range (last 30 days by default)
        days = int(request.GET.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get submissions in date range
        submissions = ContactSubmission.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Daily submissions trend
        daily_trends = submissions.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        trends_data = {
            'labels': [item['day'].strftime('%Y-%m-%d') for item in daily_trends],
            'data': [item['count'] for item in daily_trends]
        }
        
        # Status breakdown
        status_breakdown = submissions.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        status_data = {
            'labels': [item['status'] for item in status_breakdown],
            'data': [item['count'] for item in status_breakdown],
            'colors': ['#3b82f6', '#f59e0b', '#10b981', '#ef4444']  # blue, yellow, green, red
        }
        
        # Top subjects
        top_subjects = submissions.values('subject').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Statistics
        stats = {
            'total': submissions.count(),
            'new': submissions.filter(status='new').count(),
            'in_progress': submissions.filter(status='in_progress').count(),
            'resolved': submissions.filter(status='resolved').count(),
            'spam': submissions.filter(status='spam').count(),
            'with_attachments': submissions.exclude(attachment__isnull=True).exclude(attachment='').count(),
            'avg_per_day': round(submissions.count() / days, 2) if days > 0 else 0
        }
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Contact Submissions Analytics',
            'stats': stats,
            'trends_data': json.dumps(trends_data),
            'status_data': json.dumps(status_data),
            'top_subjects': top_subjects,
            'days': days,
            'start_date': start_date,
            'end_date': end_date,
        }
        
        return render(request, 'admin/contact/analytics.html', context)
    
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
    
    actions = [
        'mark_as_approved', 'mark_as_rejected', 'mark_as_under_review',
        'mark_as_pending', 'export_to_csv', 'delete_selected'
    ]
    
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
    
    def mark_as_pending(self, request, queryset):
        """Mark selected submissions as pending"""
        updated = queryset.update(status='pending')
        self.message_user(
            request,
            f'Successfully marked {updated} submission(s) as pending.'
        )
    mark_as_pending.short_description = "Mark selected submissions as pending"
    
    def delete_selected(self, request, queryset):
        """Delete selected submissions"""
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f'Successfully deleted {count} submission(s).'
        )
    delete_selected.short_description = "🗑️ Delete selected submissions"
    
    def export_to_csv(self, request, queryset):
        """Export selected KYM submissions to CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="kym_submissions_{}.csv"'.format(
            timezone.now().strftime('%Y%m%d_%H%M%S')
        )
        
        # Write BOM for Excel UTF-8 support
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Full Name', 'Email', 'Phone', 'Date of Birth', 'Gender', 
            'Marital Status', 'Nationality', 'Permanent Address', 'District', 
            'Province', 'Occupation', 'Income Source', 'Estimated Income',
            'Father Name', 'Mother Name', 'Spouse Name', 'Grand Father Name',
            'Nominee Name', 'Status', 'IP Address', 'Created At', 'Updated At',
            'Reviewed At', 'Reviewed By'
        ])
        
        for submission in queryset:
            writer.writerow([
                submission.id,
                submission.full_name,
                submission.email,
                submission.phone or '',
                submission.dob.strftime('%Y-%m-%d') if submission.dob else '',
                submission.get_gender_display() if submission.gender else '',
                submission.get_marital_status_display() if submission.marital_status else '',
                submission.nationality or '',
                submission.permanent_address or '',
                submission.district or '',
                submission.province or '',
                submission.occupation or '',
                submission.income_source or '',
                submission.estimated_income or '',
                submission.father_name or '',
                submission.mother_name or '',
                submission.spouse_name or '',
                submission.grand_father_name or '',
                submission.nominee_name or '',
                submission.get_status_display(),
                str(submission.ip_address),
                submission.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                submission.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                submission.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if submission.reviewed_at else '',
                submission.reviewed_by.username if submission.reviewed_by else ''
            ])
        
        return response
    export_to_csv.short_description = "📊 Export selected submissions to CSV"
    
    def has_add_permission(self, request):
        """Disable adding new submissions through admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting submissions through admin"""
        return False
    
    def get_urls(self):
        """Add custom analytics URL"""
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='contact_kymsubmission_analytics'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        """KYM submissions analytics dashboard"""
        from django.db.models.functions import TruncDate
        
        # Date range (last 30 days by default)
        days = int(request.GET.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get submissions in date range
        submissions = KYMSubmission.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Daily submissions trend
        daily_trends = submissions.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        trends_data = {
            'labels': [item['day'].strftime('%Y-%m-%d') for item in daily_trends],
            'data': [item['count'] for item in daily_trends]
        }
        
        # Status breakdown
        status_breakdown = submissions.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        status_data = {
            'labels': [item['status'] for item in status_breakdown],
            'data': [item['count'] for item in status_breakdown],
            'colors': ['#3b82f6', '#f59e0b', '#10b981', '#ef4444']  # blue, yellow, green, red
        }
        
        # District breakdown
        district_breakdown = submissions.values('district').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Statistics
        stats = {
            'total': submissions.count(),
            'pending': submissions.filter(status='pending').count(),
            'under_review': submissions.filter(status='under_review').count(),
            'approved': submissions.filter(status='approved').count(),
            'rejected': submissions.filter(status='rejected').count(),
            'avg_per_day': round(submissions.count() / days, 2) if days > 0 else 0
        }
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'KYM Submissions Analytics',
            'stats': stats,
            'trends_data': json.dumps(trends_data),
            'status_data': json.dumps(status_data),
            'district_breakdown': district_breakdown,
            'days': days,
            'start_date': start_date,
            'end_date': end_date,
        }
        
        return render(request, 'admin/contact/kym_analytics.html', context)


@admin.register(OfficeLocation)
class OfficeLocationAdmin(admin.ModelAdmin):
    """Admin interface for managing office locations."""
    
    list_display = [
        'name', 'location_type_badge', 'address', 'phone', 'is_active', 'order'
    ]
    list_filter = ['location_type', 'is_active']
    search_fields = ['name', 'address', 'phone', 'email']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'location_type', 'address', 'description'),
            'classes': ('wide',)
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude'),
            'description': 'Latitude and longitude for map display'
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'hours'),
            'classes': ('wide',)
        }),
        ('Additional Information', {
            'fields': ('image', 'services'),
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def location_type_badge(self, obj):
        """Display location type as a colored badge"""
        colors = {
            'main_office': '#3b82f6',      # blue
            'branch_office': '#10b981',     # green
            'service_center': '#f59e0b',   # yellow
            'atm_center': '#8b5cf6',       # purple
        }
        color = colors.get(obj.location_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_location_type_display()
        )
    location_type_badge.short_description = 'Type'
    location_type_badge.admin_order_field = 'location_type'


# Register with custom admin site
from apps.admin.admin_site import admin_site

admin_site.register(ContactSubmission, ContactSubmissionAdmin)
admin_site.register(KYMSubmission, KYMSubmissionAdmin)
admin_site.register(OfficeLocation, OfficeLocationAdmin)
