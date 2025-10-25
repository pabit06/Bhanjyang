from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import APIKey, SecurityLog

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'key_display', 'is_active', 'requests_per_hour', 'requests_per_day', 'last_used', 'created_at']
    list_filter = ['is_active', 'created_at', 'user']
    search_fields = ['name', 'user__username', 'key']
    readonly_fields = ['key', 'created_at', 'last_used']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'user', 'key', 'is_active')
        }),
        ('Expiration', {
            'fields': ('expires_at',),
            'description': 'Leave empty for no expiration'
        }),
        ('Rate Limiting', {
            'fields': ('requests_per_hour', 'requests_per_day')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_used'),
            'classes': ('collapse',)
        })
    )
    
    def key_display(self, obj):
        """Display masked API key"""
        if obj.key:
            return f"{obj.key[:8]}...{obj.key[-4:]}"
        return "Not generated"
    key_display.short_description = "API Key"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['activate_keys', 'deactivate_keys', 'regenerate_keys']
    
    def activate_keys(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} API keys activated.")
    activate_keys.short_description = "Activate selected API keys"
    
    def deactivate_keys(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} API keys deactivated.")
    deactivate_keys.short_description = "Deactivate selected API keys"
    
    def regenerate_keys(self, request, queryset):
        for api_key in queryset:
            api_key.key = api_key.generate_key()
            api_key.save()
        self.message_user(request, f"{queryset.count()} API keys regenerated.")
    regenerate_keys.short_description = "Regenerate selected API keys"

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'ip_address', 'user', 'timestamp', 'details_display']
    list_filter = ['event_type', 'timestamp', 'user']
    search_fields = ['ip_address', 'user__username', 'details']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def details_display(self, obj):
        """Display details in a readable format"""
        if obj.details:
            details_str = str(obj.details)[:100]
            if len(str(obj.details)) > 100:
                details_str += "..."
            return details_str
        return "-"
    details_display.short_description = "Details"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['export_security_logs']
    
    def export_security_logs(self, request, queryset):
        """Export security logs to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="security_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Event Type', 'IP Address', 'User', 'Timestamp', 'Details', 'User Agent'])
        
        for log in queryset:
            writer.writerow([
                log.get_event_type_display(),
                log.ip_address,
                log.user.username if log.user else 'Anonymous',
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                str(log.details),
                log.user_agent[:100] if log.user_agent else ''
            ])
        
        return response
    export_security_logs.short_description = "Export selected logs to CSV"
    
    def has_add_permission(self, request):
        return False  # Security logs should only be created programmatically
