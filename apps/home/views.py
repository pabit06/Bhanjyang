from django.views.generic import TemplateView, View
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import StatisticSerializer, TestimonialSerializer

from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from .services import HomeService
from .forms import ContactForm, NewsletterSignupForm
from .models import Statistic, Testimonial

@method_decorator(cache_page(300), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class IndexView(TemplateView):
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


@method_decorator(cache_page(1800), name='dispatch')
class RemittanceView(TemplateView):
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
    """
    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            success, message = HomeService.handle_contact_submission(form.cleaned_data)
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': success, 'message': message})
            
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('home:index')
        
        # Invalid Form
        if request.headers.get('Content-Type') == 'application/json':
             return JsonResponse({'success': False, 'message': 'Invalid form data', 'errors': form.errors}, status=400)
        
        messages.error(request, "Please correct the errors in the form.")
        return redirect('home:index')


class NewsletterSignupView(View):
    """
    Handle Newsletter Signup POST requests (AJAX).
    """
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
class StatisticsAPI(generics.ListAPIView):
    """
    API endpoint that allows statistics to be viewed.
    """
    queryset = Statistic.objects.filter(is_active=True).order_by('order')
    serializer_class = StatisticSerializer
    permission_classes = [AllowAny]


@method_decorator(cache_page(180), name='dispatch')
class TestimonialsAPI(generics.ListAPIView):
    """
    API endpoint that allows testimonials to be viewed.
    """
    queryset = Testimonial.objects.filter(is_active=True).order_by('order')
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]