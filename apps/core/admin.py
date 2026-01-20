from .security_admin import APIKeyAdmin, SecurityLogAdmin
from apps.admin.admin_site import admin_site
from .models import APIKey, SecurityLog, PageSEO
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


@admin.register(PageSEO, site=admin_site)
class PageSEOAdmin(admin.ModelAdmin):
    """Admin for PageSEO model"""
    list_display = ('page', 'meta_title', 'is_active', 'updated_at')
    list_filter = ('is_active', 'page')
    search_fields = ('meta_title', 'meta_description', 'meta_keywords')
    fieldsets = (
        (_('Page Information'), {
            'fields': ('page', 'is_active')
        }),
        (_('SEO Meta Tags'), {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'description': _('These fields override the global site_info SEO settings for this specific page.')
        }),
        (_('Open Graph (Social Media)'), {
            'fields': ('og_title', 'og_description', 'og_image'),
            'description': _('Settings for social media sharing. If empty, will use meta fields or site_info defaults.')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('page',)
        return self.readonly_fields


# Register auth models
admin_site.register(User)
admin_site.register(Group)

# Register core models
admin_site.register(APIKey, APIKeyAdmin)
admin_site.register(SecurityLog, SecurityLogAdmin)
