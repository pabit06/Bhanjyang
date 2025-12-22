"""
Base mixins and utilities for views to reduce code duplication.
"""
from typing import Dict, List, Any, Optional
from django.http import HttpRequest, JsonResponse
from django.views.generic import DetailView
from apps.services.services import ServiceAnalyticsService


class BreadcrumbMixin:
    """Mixin to add breadcrumb functionality to views."""
    
    breadcrumbs: List[Dict[str, str]] = []
    
    def get_breadcrumbs(self) -> List[Dict[str, str]]:
        """Get breadcrumbs for the current view."""
        return self.breadcrumbs
    
    def get_context_data(self, **kwargs):
        """Add breadcrumbs to context."""
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class ServiceTrackingMixin:
    """Mixin to track service usage analytics."""
    
    service_type: str = ''
    tracking_event: str = 'page_views'
    
    def get_object(self):
        """Track service usage when object is retrieved."""
        obj = super().get_object()
        if self.service_type and hasattr(obj, 'id'):
            ServiceAnalyticsService.track_usage(
                self.service_type, 
                obj.id, 
                self.tracking_event
            )
        return obj


class ServiceDetailViewMixin(BreadcrumbMixin, ServiceTrackingMixin):
    """Combined mixin for service detail views with breadcrumbs and tracking."""
    pass


def create_breadcrumbs(*items: tuple) -> List[Dict[str, str]]:
    """
    Helper function to create breadcrumb lists.
    
    Args:
        *items: Tuples of (name, url) pairs
        
    Returns:
        List of breadcrumb dictionaries
        
    Example:
        breadcrumbs = create_breadcrumbs(
            ('Home', '/'),
            ('Services', '/services/'),
            ('Loan Details', None)  # Current page
        )
    """
    breadcrumbs = []
    for name, url in items:
        breadcrumbs.append({'name': name, 'url': url or '#'})
    return breadcrumbs

