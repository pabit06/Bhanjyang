from django.views.generic import TemplateView, ListView, DetailView, View, RedirectView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.urls import reverse_lazy, reverse

from .services import AboutService
from .forms import NewsletterSignupForm, FeedbackForm
from .models import CooperativeInfo
from apps.core.error_handling import (
    ErrorResponse, ErrorLogger, handle_view_errors, safe_json_parse
)
from apps.core.view_mixins import create_breadcrumbs

@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class AboutHomeView(RedirectView):
    """Redirect /about/ to introduction page"""
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        return reverse('about:introduction')


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class IntroductionView(TemplateView):
    """Introduction page with Our Story, Vision & Mission, and Timeline"""
    template_name = 'about/introduction.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Get cooperative info
            from .models import CooperativeInfo
            context['cooperative_info'] = CooperativeInfo.objects.active().first()
            # Get timeline events (limited to 6 for introduction page)
            context['timeline_events'] = AboutService.get_timeline_events()[:6]
        except Exception as e:
            from apps.core.error_handling import ErrorLogger
            ErrorLogger.log_error(e, self.request if hasattr(self, 'request') else None)
            context['cooperative_info'] = None
            context['timeline_events'] = []
        
        context['breadcrumbs'] = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', None),
            ('Introduction', 'about:introduction')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class TimelineView(ListView):
    template_name = 'about/timeline.html'
    paginate_by = 12
    context_object_name = 'page_obj'
    
    def get_queryset(self):
        return AboutService.get_timeline_events()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', None),
            ('Timeline', 'about:timeline')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class AffiliationsView(TemplateView):
    template_name = 'about/affiliations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['affiliations'] = AboutService.get_affiliations()
        except Exception as e:
            from apps.core.error_handling import ErrorLogger
            ErrorLogger.log_error(e, self.request if hasattr(self, 'request') else None)
            context['affiliations'] = []
        
        context['breadcrumbs'] = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', None),
            ('Affiliations', 'about:affiliations')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class ChairpersonMessageView(TemplateView):
    """Dedicated page for Chairperson Message"""
    template_name = 'about/chairperson_message.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import LeadershipMessage
        try:
            # Get the most recent active chairman message
            context['message'] = LeadershipMessage.objects.filter(
                message_type='chairman',
                is_active=True
            ).order_by('-order', '-created_at').first()
        except Exception as e:
            from apps.core.error_handling import ErrorLogger
            ErrorLogger.log_error(e, self.request if hasattr(self, 'request') else None)
            context['message'] = None
        
        context['breadcrumbs'] = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', None),
            ('Chairperson Message', 'about:chairperson_message')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class ManagerCommitmentView(TemplateView):
    """Dedicated page for Manager Commitment"""
    template_name = 'about/manager_commitment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import LeadershipMessage
        try:
            # Get the most recent active manager message
            context['message'] = LeadershipMessage.objects.filter(
                message_type='manager',
                is_active=True
            ).order_by('-order', '-created_at').first()
        except Exception as e:
            from apps.core.error_handling import ErrorLogger
            ErrorLogger.log_error(e, self.request if hasattr(self, 'request') else None)
            context['message'] = None
        
        context['breadcrumbs'] = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', None),
            ('Manager Commitment', 'about:manager_commitment')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class BoardOfDirectorsView(TemplateView):
    """Dedicated page for Board of Directors (Committees)"""
    template_name = 'about/board_of_directors.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Committee
        try:
            # Get all active committees (board, audit, etc.) with optimized query
            context['committees'] = Committee.objects.filter(
                is_active=True
            ).prefetch_related('memberships__person').order_by('order')
        except Exception as e:
            from apps.core.error_handling import ErrorLogger
            ErrorLogger.log_error(e, self.request if hasattr(self, 'request') else None)
            context['committees'] = []
        
        context['breadcrumbs'] = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', None),
            ('Board of Directors', 'about:board_of_directors')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class ManagementView(TemplateView):
    """Dedicated page for Management Team (Staff)"""
    template_name = 'about/management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Staff
        try:
            # Get all active staff members with optimized query
            context['management_team'] = Staff.objects.filter(
                is_active=True
            ).select_related('person').order_by('order')
        except Exception as e:
            from apps.core.error_handling import ErrorLogger
            ErrorLogger.log_error(e, self.request if hasattr(self, 'request') else None)
            context['management_team'] = []
        
        context['breadcrumbs'] = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', None),
            ('Management', 'about:management')
        )
        return context


@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class MemberTestimonialsView(TemplateView):
    """Dedicated page for Member Testimonials"""
    template_name = 'about/member_testimonials.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.home.models import Testimonial
        try:
            # Get all active testimonials, ordered by featured first, then order
            context['testimonials'] = list(Testimonial.objects.filter(
                is_active=True
            ).order_by('-is_featured', 'order', '-created_at'))
        except Exception as e:
            from apps.core.error_handling import ErrorLogger
            ErrorLogger.log_error(e, self.request if hasattr(self, 'request') else None)
            context['testimonials'] = []
        
        context['breadcrumbs'] = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', None),
            ('Member Testimonials', 'about:member_testimonials')
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
    
    def get_queryset(self):
        """Optimize queryset with select_related if needed"""
        return CooperativeInfo.objects.active()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = create_breadcrumbs(
            ('Home', 'home:index'),
            ('About Us', None),
            (self.object.cooperative_name, 'about:cooperative_detail', {'slug': self.object.slug})
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


class NewsletterSignupView(View):
    @handle_view_errors
    def post(self, request):
        """Handle newsletter signup form submission"""
        # Parse JSON safely
        data, error_response = safe_json_parse(request)
        if error_response:
            return error_response
        
        form = NewsletterSignupForm(data)
        if form.is_valid():
            try:
                AboutService.send_newsletter_welcome_email(form.cleaned_data)
                return ErrorResponse.json_success(message='Subscribed successfully!')
            except Exception as e:
                ErrorLogger.log_error(e, request)
                return ErrorResponse.json_error(
                    message='Failed to process subscription. Please try again later.',
                    status_code=500,
                    error_code='SUBSCRIPTION_ERROR'
                )
        else:
            # Convert form.errors to dict for proper JSON serialization
            errors_dict = {
                field: errors if isinstance(errors, list) else [str(errors)]
                for field, errors in form.errors.items()
            }
            ErrorLogger.log_validation_error(errors_dict, request, form_name='NewsletterSignupForm')
            return ErrorResponse.json_error(
                message='Please correct the errors below.',
                status_code=400,
                errors=errors_dict,
                error_code='VALIDATION_ERROR'
            )


class FeedbackView(View):
    @handle_view_errors
    def post(self, request):
        """Handle feedback form submission"""
        # Parse JSON safely
        data, error_response = safe_json_parse(request)
        if error_response:
            return error_response
        
        form = FeedbackForm(data)
        if form.is_valid():
            try:
                AboutService.send_feedback_email(form.cleaned_data)
                return ErrorResponse.json_success(message='Feedback sent successfully!')
            except Exception as e:
                ErrorLogger.log_error(e, request)
                return ErrorResponse.json_error(
                    message='Failed to send feedback. Please try again later.',
                    status_code=500,
                    error_code='FEEDBACK_ERROR'
                )
        else:
            # Convert form.errors to dict for proper JSON serialization
            errors_dict = {
                field: errors if isinstance(errors, list) else [str(errors)]
                for field, errors in form.errors.items()
            }
            ErrorLogger.log_validation_error(errors_dict, request, form_name='FeedbackForm')
            return ErrorResponse.json_error(
                message='Please correct the errors below.',
                status_code=400,
                errors=errors_dict,
                error_code='VALIDATION_ERROR'
            )

# GalleryView removed - use main gallery app at /gallery/ instead
