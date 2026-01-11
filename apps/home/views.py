from django.views.generic import TemplateView, View
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import StatisticSerializer, TestimonialSerializer

from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.vary import vary_on_headers
from django.utils.translation import activate

from apps.core.view_mixins import NepaliLanguageMixin
from .services import HomeService
from .forms import ContactForm, NewsletterSignupForm
from .models import Statistic, Testimonial

@method_decorator(cache_page(300), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class IndexView(NepaliLanguageMixin, TemplateView):
    """
    Main Homepage View.
    Uses HomeService for data fetching and caching strategy.
    """
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Track Page View
        HomeService.track_view(self.request, "Bhanjyang Cooperative - Home")
        
        # Service Data
        service_data = HomeService.get_home_context(is_staff=self.request.user.is_staff)
        context.update(service_data)
        
        # Forms (Always fresh instances)
        context['contact_form'] = ContactForm()
        context['newsletter_form'] = NewsletterSignupForm()
        
        return context


@method_decorator(never_cache, name='dispatch')
class OfflineView(TemplateView):
    """
    Offline page view - shown when user is offline.
    This page is cached by service worker for offline access.
    """
    template_name = 'offline.html'


@method_decorator(cache_page(1800), name='dispatch')
class RemittanceView(NepaliLanguageMixin, TemplateView):
    """
    Remittance Services Page.
    """
    template_name = 'home/remittance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        HomeService.track_view(self.request, "Remittance Services - Bhanjyang Cooperative")
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Remittance Services', 'url': '/remittance/'} # Corrected URL assuming root
        ]
        return context


class ContactSubmissionView(View):
    """
    Handle Contact Form POST requests.
    
    DEPRECATED: This view is kept for backward compatibility.
    New submissions should use the contact app endpoint directly.
    This view forwards requests to the contact app.
    """
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        # Forward to contact app endpoint for consolidation
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        
        # Import contact app view to reuse its logic
        from apps.contact.views import contact_view
        
        # Call contact app view directly
        return contact_view(request)


class NewsletterSignupView(View):
    """
    Handle Newsletter Signup POST requests (AJAX).
    """
    def dispatch(self, request, *args, **kwargs):
        """Force Nepali language for this view"""
        activate('ne')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            success, message = HomeService.handle_newsletter_signup(
                form.cleaned_data['email'], 
                form.cleaned_data.get('name', '')
            )
            return JsonResponse({'success': success, 'message': message})
        
        return JsonResponse({'success': False, 'message': 'Invalid email address', 'errors': form.errors}, status=400)


@method_decorator(cache_page(180), name='dispatch')
class StatisticsAPI(NepaliLanguageMixin, generics.ListAPIView):
    """
    API endpoint that allows statistics to be viewed.
    """
    queryset = Statistic.objects.filter(is_active=True).order_by('order')
    serializer_class = StatisticSerializer
    permission_classes = [AllowAny]


@method_decorator(cache_page(180), name='dispatch')
class TestimonialsAPI(NepaliLanguageMixin, generics.ListAPIView):
    """
    API endpoint that allows testimonials to be viewed.
    """
    queryset = Testimonial.objects.filter(is_active=True).order_by('order')
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]