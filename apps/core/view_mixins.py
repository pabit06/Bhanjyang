"""
Base mixins and utilities for views to reduce code duplication.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
from django.http import HttpRequest, JsonResponse
from django.views.generic import DetailView
from django.urls import reverse, NoReverseMatch
from django.utils.translation import activate
from apps.services.services import ServiceAnalyticsService


class NepaliLanguageMixin:
    """Mixin to force Nepali language for views."""
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view."""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)


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


def create_breadcrumbs(*items: Union[Tuple[str, str], Tuple[str, str, Dict]]) -> List[Dict[str, str]]:
    """
    Helper function to create breadcrumb lists.
    
    Supports both hardcoded URLs and URL names (using Django's reverse).
    
    Args:
        *items: Tuples of (name, url_or_url_name) or (name, url_name, kwargs)
               - If url_or_url_name starts with '/', it's treated as a hardcoded URL
               - If url_or_url_name contains ':', it's treated as a URL name (e.g., 'about:home')
               - If url_or_url_name is None or '#', it's treated as current page (no link)
               - Optional third element can be a dict of kwargs for reverse()
        
    Returns:
        List of breadcrumb dictionaries
        
    Example:
        # Using URL names (recommended - will auto-update if URLs change)
        breadcrumbs = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', 'about:home'),
            ('Timeline', 'about:timeline')
        )
        
        # Using hardcoded URLs (not recommended)
        breadcrumbs = create_breadcrumbs(
            ('Home', '/'),
            ('Services', '/services/'),
            ('Loan Details', None)  # Current page
        )
        
        # Using URL names with kwargs
        breadcrumbs = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', 'about:home'),
            ('Cooperative', 'about:cooperative_detail', {'slug': 'my-coop'})
        )
    """
    breadcrumbs = []
    for item in items:
        if len(item) == 2:
            name, url_or_name = item
            kwargs = {}
        elif len(item) == 3:
            name, url_or_name, kwargs = item
        else:
            raise ValueError(f"Invalid breadcrumb item: {item}. Expected (name, url) or (name, url_name, kwargs)")
        
        # Determine if it's a URL name or hardcoded URL
        if url_or_name is None or url_or_name == '#':
            # Current page - no link
            url = '#'
        elif url_or_name.startswith('/') or url_or_name.startswith('http'):
            # Hardcoded URL
            url = url_or_name
        elif ':' in url_or_name:
            # URL name (e.g., 'about:home')
            try:
                url = reverse(url_or_name, kwargs=kwargs)
            except NoReverseMatch:
                # Fallback to '#' if URL name doesn't exist
                url = '#'
        else:
            # Treat as hardcoded URL if no ':' found
            url = url_or_name
        
        breadcrumbs.append({'name': name, 'url': url})
    return breadcrumbs

