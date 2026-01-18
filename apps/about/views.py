from typing import Dict, Any
from django.db.models import QuerySet
from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from .services import AboutService
from .models import (
    CooperativeInfo, LeadershipMessage, Committee, Staff, 
    CooperativeTimeline, CooperativeStatistic, CooperativeAffiliation
)
from .view_mixins import SafeContextDataMixin, BaseAboutView
from apps.core.view_mixins import create_breadcrumbs, NepaliLanguageMixin
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
        
        # Safely get cooperative info (published only, unless staff)
        if self.request.user.is_staff:
            context.update(self.safe_get_data(
                'cooperative_info',
                lambda: CooperativeInfo.objects.first(),
                default=None
            ))
        else:
            context.update(self.safe_get_data(
                'cooperative_info',
                lambda: CooperativeInfo.objects.filter(status=CooperativeInfo.Status.PUBLISHED).first(),
                default=None
            ))
        
        # Safely get timeline events (limited to 6 for introduction page)
        if self.request.user.is_staff:
            context.update(self.safe_get_data(
                'timeline_events',
                lambda: list(CooperativeTimeline.objects.all()[:6]),
                default=[]
            ))
        else:
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
        
        # Safely get the most recent published chairman message
        if self.request.user.is_staff:
            context.update(self.safe_get_data(
                'message',
                lambda: LeadershipMessage.objects.filter(
                    message_type='chairman'
                ).order_by('-order', '-created_at').first(),
                default=None
            ))
        else:
            context.update(self.safe_get_data(
                'message',
                lambda: LeadershipMessage.objects.filter(
                    message_type='chairman',
                    status=LeadershipMessage.Status.PUBLISHED
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
        
        # Safely get the most recent published manager message
        if self.request.user.is_staff:
            context.update(self.safe_get_data(
                'message',
                lambda: LeadershipMessage.objects.filter(
                    message_type='manager'
                ).order_by('-order', '-created_at').first(),
                default=None
            ))
        else:
            context.update(self.safe_get_data(
                'message',
                lambda: LeadershipMessage.objects.filter(
                    message_type='manager',
                    status=LeadershipMessage.Status.PUBLISHED
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
            ).prefetch_related('memberships__person', 'memberships').order_by('order')),
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
        
        # Safely get all published testimonials, ordered by featured first, then order
        if self.request.user.is_staff:
            context.update(self.safe_get_data(
                'testimonials',
                lambda: list(Testimonial.objects.all().order_by('-is_featured', 'order', '-created_at')),
                default=[]
            ))
        else:
            context.update(self.safe_get_data(
                'testimonials',
                lambda: list(Testimonial.objects.filter(
                    status=Testimonial.Status.PUBLISHED
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
        """Optimize queryset with status filtering"""
        if self.request.user.is_staff:
            return CooperativeInfo.objects.all()
        return CooperativeInfo.objects.filter(status=CooperativeInfo.Status.PUBLISHED)
    
    def dispatch(self, request, *args, **kwargs):
        """Handle redirect if only one cooperative exists and matches the slug"""
        # If there's only one published cooperative, redirect to introduction page
        # ONLY if the requested slug matches that cooperative.
        # Otherwise, let it 404 (handled by super().dispatch causing get_object to fail).
        published_coops = CooperativeInfo.objects.filter(status=CooperativeInfo.Status.PUBLISHED)
        if published_coops.count() == 1:
            coop = published_coops.first()
            if kwargs.get('slug') == coop.slug:
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

class PreviewContentView(NepaliLanguageMixin, TemplateView):
    """
    Preview view for draft/scheduled content.
    
    Allows staff users to preview content before publishing using token-based URLs.
    """
    template_name = 'about/preview.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Only allow staff users to preview with valid token"""
        if not request.user.is_staff:
            raise Http404("Preview not available")
        
        token = kwargs.get('token')
        pk = kwargs.get('pk')
        if token:
            from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
            signer = TimestampSigner()
            try:
                verified_pk = signer.unsign(token, max_age=3600)  # Token valid for 1 hour
                if str(verified_pk) != str(pk):
                    raise Http404("Invalid preview token")
            except (BadSignature, SignatureExpired):
                raise Http404("Preview link expired or invalid")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        model_name = kwargs.get('model_name')
        pk = kwargs.get('pk')
        
        # Map model names to model classes
        model_map = {
            'cooperativeinfo': CooperativeInfo,
            'cooperativetimeline': CooperativeTimeline,
            'cooperativestatistic': CooperativeStatistic,
            'cooperativeaffiliation': CooperativeAffiliation,
            'leadershipmessage': LeadershipMessage,
        }
        
        model_class = model_map.get(model_name.lower())
        if not model_class:
            raise Http404("Invalid model")
        
        # Get the content object (can be draft or scheduled)
        content = get_object_or_404(model_class, pk=pk)
        
        context['content'] = content
        context['model_name'] = model_name
        context['is_preview'] = True
        
        return context


class ContactView(RedirectView):
    """
    DEPRECATED: Redirects to main contact app.
    This view is kept for backward compatibility with any existing links.
    """
    permanent = False
    pattern_name = 'contact:contact_view'
