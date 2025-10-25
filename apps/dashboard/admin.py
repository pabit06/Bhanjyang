from django.contrib import admin
from .models import (
    PerformanceMetric, PageView, ErrorLog, UserSession, PerformanceReport,
    PerformanceAlert, AlertLog, DashboardWidget, UserDashboardPreference, AuditLog
)
from apps.core.admin_site import admin_site

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'value', 'unit', 'page_url', 'timestamp', 'user']
    list_filter = ['metric_type', 'timestamp', 'user']
    search_fields = ['page_url', 'user_agent']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['page_title', 'page_url', 'load_time', 'is_mobile', 'timestamp', 'user']
    list_filter = ['is_mobile', 'browser', 'timestamp', 'user']
    search_fields = ['page_url', 'page_title', 'user_agent']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['error_type', 'error_message', 'page_url', 'resolved', 'timestamp', 'user']
    list_filter = ['error_type', 'resolved', 'timestamp', 'user']
    search_fields = ['error_message', 'page_url']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(resolved=True)
        self.message_user(request, f"{queryset.count()} errors marked as resolved.")
    mark_as_resolved.short_description = "Mark selected errors as resolved"

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'ip_address', 'start_time', 'end_time', 'page_views', 'is_mobile']
    list_filter = ['is_mobile', 'browser', 'start_time', 'user']
    search_fields = ['session_id', 'ip_address', 'user__username']
    readonly_fields = ['start_time']
    date_hierarchy = 'start_time'

@admin.register(PerformanceReport)
class PerformanceReportAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'start_date', 'end_date', 'generated_at', 'generated_by']
    list_filter = ['report_type', 'generated_at', 'generated_by']
    search_fields = ['summary']
    readonly_fields = ['generated_at', 'report_data']
    date_hierarchy = 'generated_at'

@admin.register(PerformanceAlert)
class PerformanceAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'threshold_value', 'severity', 'is_active', 'created_at', 'created_by']
    list_filter = ['alert_type', 'severity', 'is_active', 'created_at']
    search_fields = ['description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ['alert', 'triggered_at', 'current_value', 'is_resolved', 'resolved_by']
    list_filter = ['is_resolved', 'triggered_at', 'alert__alert_type']
    search_fields = ['message']
    readonly_fields = ['triggered_at']
    date_hierarchy = 'triggered_at'
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user)
        self.message_user(request, f"{queryset.count()} alerts marked as resolved.")
    mark_as_resolved.short_description = "Mark selected alerts as resolved"

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'widget_type', 'position_x', 'position_y', 'width', 'height', 'is_active', 'created_by']
    list_filter = ['widget_type', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'user', 'ip_address', 'timestamp', 'description']
    list_filter = ['action_type', 'timestamp', 'user']
    search_fields = ['description', 'ip_address', 'user__username']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Register all models with custom admin site
admin_site.register(PerformanceMetric, PerformanceMetricAdmin)
admin_site.register(PageView, PageViewAdmin)
admin_site.register(ErrorLog, ErrorLogAdmin)
admin_site.register(UserSession, UserSessionAdmin)
admin_site.register(PerformanceReport, PerformanceReportAdmin)
admin_site.register(PerformanceAlert, PerformanceAlertAdmin)
admin_site.register(AlertLog, AlertLogAdmin)
admin_site.register(DashboardWidget, DashboardWidgetAdmin)
admin_site.register(AuditLog, AuditLogAdmin)
