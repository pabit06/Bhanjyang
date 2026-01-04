from typing import Dict, Any
from django.db.models import QuerySet
from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from .services import AboutService
from .models import CooperativeInfo, LeadershipMessage, Committee, Staff
from .view_mixins import SafeContextDataMixin, BaseAboutView
from apps.core.view_mixins import create_breadcrumbs
from apps.home.models import Testimonial


class AboutHomeView(BaseAboutView, RedirectView):
    """Redirect /about/ to introduction page"""
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs) -> str:
        return reverse('about:introduction')


class IntroductionView(BaseAboutView, SafeContextDataMixin, TemplateView):
    """Introduction page with Our Story, Vision & Mission, and Timeline"""
    template_name = 'about/introduction.html'
    
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


class TimelineView(BaseAboutView, ListView):
    """Timeline events list view with pagination"""
    template_name = 'about/timeline.html'
    paginate_by = 12
    context_object_name = 'page_obj'
    
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


class AffiliationsView(BaseAboutView, SafeContextDataMixin, TemplateView):
    """Affiliations page displaying cooperative affiliations"""
    template_name = 'about/affiliations.html'
    
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


class ChairpersonMessageView(BaseAboutView, SafeContextDataMixin, TemplateView):
    """Dedicated page for Chairperson Message"""
    template_name = 'about/chairperson_message.html'
    
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


class ManagerCommitmentView(BaseAboutView, SafeContextDataMixin, TemplateView):
    """Dedicated page for Manager Commitment"""
    template_name = 'about/manager_commitment.html'
    
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


class BoardOfDirectorsView(BaseAboutView, SafeContextDataMixin, TemplateView):
    """Dedicated page for Board of Directors (Committees)"""
    template_name = 'about/board_of_directors.html'
    
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


class ManagementView(BaseAboutView, SafeContextDataMixin, TemplateView):
    """Dedicated page for Management Team (Staff)"""
    template_name = 'about/management.html'
    
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


class MemberTestimonialsView(BaseAboutView, SafeContextDataMixin, TemplateView):
    """Dedicated page for Member Testimonials"""
    template_name = 'about/member_testimonials.html'
    
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


class CooperativeDetailView(BaseAboutView, DetailView):
    """Detail view for cooperative information"""
    model = CooperativeInfo
    template_name = 'about/cooperative_detail.html'
    context_object_name = 'cooperative'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self) -> QuerySet:
        """Optimize queryset with select_related if needed"""
        return CooperativeInfo.objects.active()
    
    def dispatch(self, request, *args, **kwargs):
        """Handle redirect if only one cooperative exists"""
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
