import logging
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.core.view_mixins import NepaliLanguageMixin
from apps.core.error_handling import ErrorResponse

from .forms import ContactForm, KYMForm
from .models import ContactSubmission, KYMSubmission
from .services import ContactService, KYMService
from .utils.rate_limiting import rate_limit_by_ip

logger = logging.getLogger(__name__)


@method_decorator(rate_limit_by_ip('5/m'), name='dispatch')
class ContactView(NepaliLanguageMixin, View):
    """Main contact form view"""
    template_name = 'contact/contact.html'
    
    def get(self, request, *args, **kwargs):
        """Render contact form page"""
        context = {
            'form': ContactForm(),
            'breadcrumbs': [
                {'name': _('Home'), 'url': '/'},
                {'name': _('Contact Us'), 'url': '/contact/'}
            ]
        }
        
        # Add office locations if available
        try:
            from .models import OfficeLocation
            context['office_locations'] = OfficeLocation.objects.filter(is_active=True).order_by('order')
        except Exception as e:
            logger.warning(f"Could not fetch office locations: {e}")
            context['office_locations'] = []
            
        # Add FAQs
        try:
            from .models import FAQ
            context['faqs'] = FAQ.objects.filter(is_active=True).order_by('order', 'created_at')
        except Exception as e:
            logger.warning(f"Could not fetch FAQs: {e}")
            context['faqs'] = []
        
        return render(request, self.template_name, context)
    
    def _is_ajax_request(self, request):
        """Check if request is AJAX"""
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    def post(self, request, *args, **kwargs):
        """Handle contact form submission"""
        if not self._is_ajax_request(request):
            logger.warning("Non-AJAX POST request rejected")
            return JsonResponse({
                'success': False,
                'message': _('This endpoint only accepts AJAX requests.')
            }, status=400)
        
        form = ContactForm(request.POST, request.FILES)
        
        if not form.is_valid():
            return JsonResponse({
                'success': False,
                'message': _('Please correct the errors in the form.'),
                'errors': form.errors
            }, status=400)
        
        try:
            # Use service to handle submission
            submission = ContactService.create_contact_submission(form.cleaned_data, request.FILES, request.META)
            
            # Send notification emails
            ContactService.send_contact_notification_emails(submission)
            
            return JsonResponse({
                'success': True,
                'message': _('Thank you! Your message has been sent successfully.'),
                'submission_id': submission.id
            })
            
        except Exception as e:
            logger.error(f"Error processing contact submission: {e}", exc_info=True)
            
            return ErrorResponse.json_error(
                message=_('An error occurred while processing your request. Please try again later.'),
                status_code=500,
                error_code='SUBMISSION_ERROR',
                details={'exception': str(e)} if settings.DEBUG else None
            )


@method_decorator(rate_limit_by_ip('3/m'), name='dispatch')
class KYMFormView(NepaliLanguageMixin, View):
    """Know Your Member (KYM) form view"""
    template_name = 'contact/kym_form.html'
    
    def get(self, request, *args, **kwargs):
        """Render KYM form page"""
        context = {
            'form': KYMForm(),
            'breadcrumbs': [
                {'name': _('Home'), 'url': '/'},
                {'name': _('Contact'), 'url': '/contact/'},
                {'name': _('KYM Form'), 'url': '/contact/kym/'}
            ]
        }
        return render(request, self.template_name, context)
    
    def _is_ajax_request(self, request):
        """Check if request is AJAX"""
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    def post(self, request, *args, **kwargs):
        """Handle KYM form submission"""
        if not self._is_ajax_request(request):
            logger.warning("Non-AJAX KYM POST request rejected")
            return JsonResponse({
                'success': False,
                'message': _('This endpoint only accepts AJAX requests.')
            }, status=400)
        
        form = KYMForm(request.POST, request.FILES)
        
        if not form.is_valid():
            return JsonResponse({
                'success': False,
                'message': _('Please correct the errors in the form.'),
                'errors': form.errors
            }, status=400)
        
        try:
            # Use service to handle submission
            submission = KYMService.create_kym_submission(form.cleaned_data, request.FILES, request.META)
            
            return JsonResponse({
                'success': True,
                'message': _('KYM form submitted successfully! We will review your submission and contact you soon.'),
                'submission_id': submission.id
            })
            
        except Exception as e:
            logger.error(f"Error processing KYM submission: {e}", exc_info=True)
            
            return JsonResponse({
                'success': False,
                'message': _('An error occurred while processing your submission. Please try again later.')
            }, status=500)


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse

class KYMDownloadPDFView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View to download KYM submission as PDF (Admin/Staff only)"""
    
    def test_func(self):
        return self.request.user.is_staff
        
    def get(self, request, pk, *args, **kwargs):
        pdf_buffer = KYMService.generate_kym_pdf(pk)
        if not pdf_buffer:
            from django.contrib import messages
            messages.error(request, _("Failed to generate PDF for this submission."))
            from django.shortcuts import redirect
            return redirect('admin:contact_kymsubmission_changelist')
            
        submission = KYMSubmission.objects.get(id=pk)
        filename = f"KYM_{submission.full_name.replace(' ', '_')}_{submission.id}.pdf"
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class PrivacyPolicyView(NepaliLanguageMixin, TemplateView):
    """Render the privacy policy page."""
    template_name = 'contact/privacy_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from apps.about.models import CooperativeInfo
        
        # Fetch cooperative info for dynamic contact details
        cooperative_info = None
        try:
            cooperative_info = CooperativeInfo.objects.active().first()
        except Exception as e:
            logger.warning(f"Could not fetch cooperative info for privacy policy: {e}")
            
        context['cooperative_info'] = cooperative_info
        context['breadcrumbs'] = [
            {'name': _('Home'), 'url': '/'},
            {'name': _('Contact'), 'url': '/contact/'},
            {'name': _('Privacy Policy'), 'url': '/contact/privacy-policy/'}
        ]
        return context
