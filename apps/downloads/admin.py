# downloads/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import DownloadableFile, FileCategory, PriorityLevel
from .performance import DownloadsQueryOptimizer, DownloadsPerformanceMonitor


class DownloadableFileAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for the DownloadableFile model with better styling and functionality.
    """
    # Fields to display in the main list view
    list_display = (
        'get_thumbnail',
        'title',
        'get_category_badge',
        'get_priority_badge',
        'get_status_badges',
        'get_file_info',
        'get_statistics',
        'uploaded_at',
    )

    # Fields to allow filtering by in the sidebar
    list_filter = (
        'category', 
        'priority', 
        'is_active', 
        'is_featured', 
        'requires_login',
        'file_type',
        'uploaded_at',
        ('expires_at', admin.EmptyFieldListFilter),
    )

    # Fields to enable searching on
    search_fields = ('title', 'description', 'tags')

    # Set how many items show per page
    list_per_page = 25

    # Enable date hierarchy
    date_hierarchy = 'uploaded_at'

    # Organize fields in the detail view
    fieldsets = (
        ('📄 Basic Information', {
            'fields': ('title', 'description', 'category', 'tags'),
            'classes': ('wide',)
        }),
        ('📁 File Details', {
            'fields': ('file', 'thumbnail', 'file_type'),
            'classes': ('wide',)
        }),
        ('⚙️ Settings & Access', {
            'fields': ('is_active', 'is_featured', 'priority', 'requires_login', 'expires_at'),
            'classes': ('wide',)
        }),
        ('📊 Statistics', {
            'fields': ('download_count', 'view_count', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Make automatically managed fields read-only in the detail view
    readonly_fields = ('uploaded_at', 'updated_at', 'download_count', 'view_count', 'file_type')

    # Add actions
    actions = [
        'mark_as_featured', 
        'mark_as_not_featured', 
        'activate_files', 
        'deactivate_files',
        'set_high_priority',
        'set_urgent_priority',
        'export_file_list'
    ]

    # Custom methods for better display
    def get_thumbnail(self, obj):
        """Display thumbnail or file type icon."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail.url
            )
        else:
            # Return file type icon
            icon_map = {
                'pdf': '📄',
                'doc': '📝', 'docx': '📝',
                'xls': '📊', 'xlsx': '📊',
                'ppt': '📽️', 'pptx': '📽️',
                'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️',
                'txt': '📄'
            }
            icon = icon_map.get(obj.file_type, '📄')
            return format_html('<span style="font-size: 24px;">{}</span>', icon)
    get_thumbnail.short_description = '📁'

    def get_category_badge(self, obj):
        """Display category as a colored badge."""
        colors = {
            'FRM': '#3B82F6',  # Blue
            'RPT': '#10B981',   # Green
            'PCY': '#F59E0B',   # Yellow
            'PUB': '#8B5CF6',   # Purple
            'MAN': '#EF4444',   # Red
            'CERT': '#06B6D4',  # Cyan
            'BRO': '#F97316',   # Orange
            'OTH': '#6B7280',   # Gray
        }
        color = colors.get(obj.category, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_category_display()
        )
    get_category_badge.short_description = 'Category'

    def get_priority_badge(self, obj):
        """Display priority as a colored badge."""
        colors = {
            'LOW': '#6B7280',   # Gray
            'MED': '#3B82F6',    # Blue
            'HIGH': '#F59E0B',   # Yellow
            'URG': '#EF4444',    # Red
        }
        icons = {
            'LOW': '⬇️',
            'MED': '➡️',
            'HIGH': '⬆️',
            'URG': '🚨',
        }
        color = colors.get(obj.priority, '#6B7280')
        icon = icons.get(obj.priority, '')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_priority_display()
        )
    get_priority_badge.short_description = 'Priority'

    def get_status_badges(self, obj):
        """Display status badges."""
        badges = []
        if obj.is_featured:
            badges.append('<span style="background-color: #FBBF24; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: bold;">⭐ Featured</span>')
        if obj.requires_login:
            badges.append('<span style="background-color: #3B82F6; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: bold;">🔒 Login</span>')
        if obj.is_expired:
            badges.append('<span style="background-color: #EF4444; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: bold;">⏰ Expired</span>')
        if not obj.is_active:
            badges.append('<span style="background-color: #6B7280; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: bold;">❌ Inactive</span>')
        
        return format_html(' '.join(badges)) if badges else format_html('<span style="color: #10B981; font-weight: bold;">✅ Active</span>')
    get_status_badges.short_description = 'Status'

    def get_file_info(self, obj):
        """Display file information."""
        return format_html(
            '<div style="font-size: 12px;">'
            '<div><strong>Type:</strong> {}</div>'
            '<div><strong>Size:</strong> {}</div>'
            '</div>',
            obj.file_type.upper() if obj.file_type else 'Unknown',
            obj.file_size
        )
    get_file_info.short_description = 'File Info'

    def get_statistics(self, obj):
        """Display download and view statistics."""
        return format_html(
            '<div style="font-size: 12px;">'
            '<div>📥 <strong>{}</strong> downloads</div>'
            '<div>👁️ <strong>{}</strong> views</div>'
            '</div>',
            obj.download_count,
            obj.view_count
        )
    get_statistics.short_description = 'Statistics'

    # Action methods
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"✅ {queryset.count()} files marked as featured.")
    mark_as_featured.short_description = "⭐ Mark as Featured"

    def mark_as_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"❌ {queryset.count()} files unmarked as featured.")
    mark_as_not_featured.short_description = "⭐ Remove Featured Status"

    def activate_files(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"✅ {queryset.count()} files activated.")
    activate_files.short_description = "✅ Activate Files"

    def deactivate_files(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"❌ {queryset.count()} files deactivated.")
    deactivate_files.short_description = "❌ Deactivate Files"

    def set_high_priority(self, request, queryset):
        queryset.update(priority=PriorityLevel.HIGH)
        self.message_user(request, f"⬆️ {queryset.count()} files set to High Priority.")
    set_high_priority.short_description = "⬆️ Set High Priority"

    def set_urgent_priority(self, request, queryset):
        queryset.update(priority=PriorityLevel.URGENT)
        self.message_user(request, f"🚨 {queryset.count()} files set to Urgent Priority.")
    set_urgent_priority.short_description = "🚨 Set Urgent Priority"

    def export_file_list(self, request, queryset):
        """Export selected files to CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="downloadable_files.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Title', 'Category', 'Priority', 'File Type', 'Size', 'Downloads', 'Views', 'Featured', 'Active', 'Upload Date'])
        
        for file_obj in queryset:
            writer.writerow([
                file_obj.title,
                file_obj.get_category_display(),
                file_obj.get_priority_display(),
                file_obj.file_type,
                file_obj.file_size,
                file_obj.download_count,
                file_obj.view_count,
                'Yes' if file_obj.is_featured else 'No',
                'Yes' if file_obj.is_active else 'No',
                file_obj.uploaded_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_file_list.short_description = "📊 Export to CSV"

    # Custom admin views
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='downloads_downloadablefile_analytics'),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        """Custom analytics view with performance optimizations."""
        # Get statistics using optimized queries
        stats = DownloadsQueryOptimizer.get_file_statistics()
        category_stats = DownloadsQueryOptimizer.get_category_statistics()
        
        # Priority breakdown
        priority_stats = DownloadableFile.objects.values('priority').annotate(count=Count('id')).order_by('-count')
        
        # Recent uploads (last 30 days)
        recent_uploads = DownloadableFile.objects.filter(
            uploaded_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        context = {
            'title': 'Download Analytics',
            'total_files': stats.get('total_files', 0),
            'active_files': stats.get('active_files', 0),
            'featured_files': stats.get('featured_files', 0),
            'expired_files': stats.get('expired_files', 0),
            'recent_uploads': recent_uploads,
            'category_stats': category_stats,
            'priority_stats': priority_stats,
        }
        
        return render(request, 'admin/downloads/analytics.html', context)

    class Media:
        css = {
            'all': ('admin/css/downloads_admin.css',)
        }
        js = ('admin/js/downloads_admin.js',)


# Register with custom admin site
from apps.admin.admin_site import admin_site

admin_site.register(DownloadableFile, DownloadableFileAdmin)