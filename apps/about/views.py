from django.views.generic import TemplateView, ListView, DetailView, View, FormView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.urls import reverse_lazy

from .services import AboutService
from .forms import ContactForm, NewsletterSignupForm, FeedbackForm
from .models import CooperativeInfo
from apps.core.error_handling import (
    ErrorResponse, ErrorLogger, handle_view_errors, safe_json_parse
)

@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class AboutHomeView(TemplateView):
    template_name = 'about/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(AboutService.get_about_home_data(
            is_staff=self.request.user.is_staff
        ))
        return context


class TimelineView(ListView):
    template_name = 'about/timeline.html'
    paginate_by = 12
    context_object_name = 'page_obj'
    
    def get_queryset(self):
        return AboutService.get_timeline_events()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Timeline', 'url': '/about/timeline/'}
        ]
        return context


class AffiliationsView(TemplateView):
    template_name = 'about/affiliations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['affiliations'] = AboutService.get_affiliations()
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Affiliations', 'url': '/about/affiliations/'}
        ]
        return context


class LeadershipView(TemplateView):
    template_name = 'about/leadership.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leadership_messages'] = AboutService.get_leadership_messages()
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Leadership', 'url': '/about/leadership/'}
        ]
        return context


class TeamView(TemplateView):
    template_name = 'about/team.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comm, management = AboutService.get_active_team()
        context['committees'] = comm
        context['management_team'] = management
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Our Team', 'url': '/about/team/'}
        ]
        return context


class PastTeamView(TemplateView):
    template_name = 'about/past_team.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['committees'] = AboutService.get_past_committees()
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Our Team', 'url': '/about/team/'},
             {'name': 'Past Committees', 'url': '/about/team/past/'}
        ]
        return context


class CooperativeDetailView(DetailView):
    model = CooperativeInfo
    template_name = 'about/cooperative_detail.html'
    context_object_name = 'cooperative'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': self.object.cooperative_name, 'url': self.object.get_absolute_url()}
        ]
        return context

# Forms and APIs

class ContactView(FormView):
    template_name = 'about/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('about:contact_success')

    def form_valid(self, form):
        if AboutService.send_contact_emails(form.cleaned_data):
            messages.success(self.request, 'Thank you for your message! We will get back to you soon.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Sorry, there was an error sending your message.')
            return self.form_invalid(form)


class ContactSuccessView(TemplateView):
    template_name = 'about/contact_success.html'


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

class GalleryView(TemplateView):
    template_name = 'about/gallery.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': 'Gallery', 'url': '/gallery/'}
        ]
        return context
