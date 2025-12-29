from typing import Dict, Any
from django.db.models import QuerySet
from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _, activate
from .services import AboutService
from .models import CooperativeInfo, LeadershipMessage, Committee, Staff
from .view_mixins import SafeContextDataMixin
from apps.core.view_mixins import create_breadcrumbs
from apps.home.models import Testimonial

@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class AboutHomeView(RedirectView):
    """Redirect /about/ to introduction page"""
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs) -> str:
        return reverse('about:introduction')


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class IntroductionView(SafeContextDataMixin, TemplateView):
    """Introduction page with Our Story, Vision & Mission, and Timeline"""
    template_name = 'about/introduction.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Safely get cooperative info
        context.update(self.safe_get_data(
            'cooperative_info',
            lambda: CooperativeInfo.objects.active().first(),
            default=None
        ))
        
        # Safely get timeline events (limited to 6 for introduction page)
        context.update(self.safe_get_data(
            'timeline_events',
            lambda: list(AboutService.get_timeline_events()[:6]),
            default=[]
        ))
        
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('About Us'), None),
            (_('Introduction'), 'about:introduction')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class TimelineView(ListView):
    template_name = 'about/timeline.html'
    paginate_by = 12
    context_object_name = 'page_obj'
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self) -> QuerySet:
        return AboutService.get_timeline_events()
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('About Us'), None),
            (_('Timeline'), 'about:timeline')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class AffiliationsView(SafeContextDataMixin, TemplateView):
    template_name = 'about/affiliations.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Safely get affiliations
        context.update(self.safe_get_data(
            'affiliations',
            lambda: list(AboutService.get_affiliations()),
            default=[]
        ))
        
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('About Us'), None),
            (_('Affiliations'), 'about:affiliations')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class ChairpersonMessageView(SafeContextDataMixin, TemplateView):
    """Dedicated page for Chairperson Message"""
    template_name = 'about/chairperson_message.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Safely get the most recent active chairman message
        context.update(self.safe_get_data(
            'message',
            lambda: LeadershipMessage.objects.filter(
                message_type='chairman',
                is_active=True
            ).order_by('-order', '-created_at').first(),
            default=None
        ))
        
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('About Us'), None),
            (_('Chairperson Message'), 'about:chairperson_message')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class ManagerCommitmentView(SafeContextDataMixin, TemplateView):
    """Dedicated page for Manager Commitment"""
    template_name = 'about/manager_commitment.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Safely get the most recent active manager message
        context.update(self.safe_get_data(
            'message',
            lambda: LeadershipMessage.objects.filter(
                message_type='manager',
                is_active=True
            ).order_by('-order', '-created_at').first(),
            default=None
        ))
        
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('About Us'), None),
            (_('Manager Commitment'), 'about:manager_commitment')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class BoardOfDirectorsView(SafeContextDataMixin, TemplateView):
    """Dedicated page for Board of Directors (Committees)"""
    template_name = 'about/board_of_directors.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Safely get all active committees with optimized query
        context.update(self.safe_get_data(
            'committees',
            lambda: list(Committee.objects.filter(
                is_active=True
            ).prefetch_related('memberships__person').order_by('order')),
            default=[]
        ))
        
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('About Us'), None),
            (_('Board of Directors'), 'about:board_of_directors')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class ManagementView(SafeContextDataMixin, TemplateView):
    """Dedicated page for Management Team (Staff)"""
    template_name = 'about/management.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Safely get all active staff members with optimized query
        context.update(self.safe_get_data(
            'management_team',
            lambda: list(Staff.objects.filter(
                is_active=True
            ).select_related('person').order_by('order')),
            default=[]
        ))
        
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('About Us'), None),
            (_('Management'), 'about:management')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class MemberTestimonialsView(SafeContextDataMixin, TemplateView):
    """Dedicated page for Member Testimonials"""
    template_name = 'about/member_testimonials.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Safely get all active testimonials, ordered by featured first, then order
        context.update(self.safe_get_data(
            'testimonials',
            lambda: list(Testimonial.objects.filter(
                is_active=True
            ).order_by('-is_featured', 'order', '-created_at')),
            default=[]
        ))
        
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('About Us'), None),
            (_('Member Testimonials'), 'about:member_testimonials')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class CooperativeDetailView(DetailView):
    model = CooperativeInfo
    template_name = 'about/cooperative_detail.html'
    context_object_name = 'cooperative'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self) -> QuerySet:
        """Optimize queryset with select_related if needed"""
        return CooperativeInfo.objects.active()
    
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language and handle redirect if needed"""
        activate('ne')
        # If there's only one active cooperative, redirect to introduction page
        # since introduction already shows the cooperative info.
        active_count = CooperativeInfo.objects.active().count()
        if active_count == 1:
            # Only one cooperative exists, redirect to introduction
            return redirect('about:introduction')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('About Us'), None),
            (self.object.cooperative_name_nepali or self.object.cooperative_name, 'about:cooperative_detail', {'slug': self.object.slug})
        )
        return context

# Forms and APIs

class ContactView(RedirectView):
    """
    DEPRECATED: Redirects to main contact app.
    This view is kept for backward compatibility with any existing links.
    """
    permanent = False
    pattern_name = 'contact:contact_view'


# NewsletterSignupView and FeedbackView removed - no longer needed

# GalleryView removed - use main gallery app at /gallery/ instead
