import logging
import time
from typing import Dict, Any
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Try to import Sentry SDK for error tracking
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None

from apps.core.view_mixins import NepaliLanguageMixin
from apps.core.error_handling import ErrorResponse

from .forms import ContactForm
from .models import ContactSubmission
from .services import ContactService
from .utils.error_codes import (
    ContactErrorCodes,
    get_status_code_for_error,
    get_user_friendly_message
)

logger = logging.getLogger(__name__)


class ContactView(NepaliLanguageMixin, View):
    """Main contact form view"""
    template_name = 'contact/contact.html'
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Render contact form page"""
        # Get context from service (includes form, FAQs, office_locations, information_officer, etc.)
        # Note: Form is instantiated in service layer where __init__ sets recaptcha_enabled and
        # recaptcha_site_key attributes and modifies fields dictionary accordingly.
        # Do not reassign these attributes here to avoid inconsistent state between attributes and fields.
        is_staff = request.user.is_staff if hasattr(request, 'user') and request.user.is_authenticated else False
        context = ContactService.get_contact_page_context(is_staff=is_staff)
        
        # Update breadcrumbs with translated strings
        context['breadcrumbs'] = [
            {'name': _('Home'), 'url': '/'},
            {'name': _('Contact Us'), 'url': '/contact/'}
        ]
        
        return render(request, self.template_name, context)
    
    def _is_ajax_request(self, request: HttpRequest) -> bool:
        """Check if request is AJAX"""
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        """Handle contact form submission"""
        submission_start_time = time.time()
        
        if not self._is_ajax_request(request):
            logger.warning("Non-AJAX POST request rejected")
            return ErrorResponse.json_error(
                message=_('This endpoint only accepts AJAX requests.'),
                status_code=400,
                error_code=ContactErrorCodes.AJAX_REQUIRED
            )
        
        # Track form validation time
        validation_start = time.time()
        form = ContactForm(request.POST, request.FILES)
        is_valid = form.is_valid()
        validation_time = (time.time() - validation_start) * 1000
        
        if not is_valid:
            return ErrorResponse.json_error(
                message=get_user_friendly_message(ContactErrorCodes.FORM_VALIDATION_ERROR),
                status_code=400,
                error_code=ContactErrorCodes.FORM_VALIDATION_ERROR,
                errors=form.errors
            )
        
        try:
            # Track file upload processing (happens in create_contact_submission)
            file_upload_start = time.time()
            
            # Use service to handle submission
            submission = ContactService.create_contact_submission(form.cleaned_data, request.FILES, request.META)
            
            file_upload_time = (time.time() - file_upload_start) * 1000
            
            # Track email queue time
            email_queue_start = time.time()
            ContactService.send_contact_notification_emails(submission)
            email_queue_time = (time.time() - email_queue_start) * 1000
            
            total_time = (time.time() - submission_start_time) * 1000
            
            # Track form submission performance
            from .utils.performance import track_form_submission_performance
            track_form_submission_performance(
                form_validation_time=validation_time,
                file_upload_time=file_upload_time,
                email_queue_time=email_queue_time,
                total_time=total_time,
                request_meta=request.META,
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                session_id=request.session.session_key if hasattr(request, 'session') else None,
                submission_id=submission.id
            )
            
            return JsonResponse({
                'success': True,
                'message': _('Thank you! Your message has been sent successfully.'),
                'submission_id': submission.id
            })
            
        except Exception as e:
            logger.error(f"Error processing contact submission: {e}", exc_info=True)
            
            # Capture exception in Sentry if available
            if SENTRY_AVAILABLE:
                try:
                    with sentry_sdk.push_scope() as scope:
                        scope.set_tag("error_type", "contact_submission")
                        scope.set_tag("submission_path", request.path)
                        scope.set_context("request", {
                            "method": request.method,
                            "path": request.path,
                            "user_agent": request.META.get('HTTP_USER_AGENT', ''),
                            "ip": request.META.get('REMOTE_ADDR', ''),
                        })
                        if hasattr(request, 'user') and request.user.is_authenticated:
                            scope.set_user({"id": request.user.id, "email": request.user.email})
                        sentry_sdk.capture_exception(e)
                except Exception as sentry_error:
                    logger.warning(f"Failed to capture exception in Sentry: {sentry_error}")
            
            # Determine error code based on exception type
            error_code = ContactErrorCodes.SUBMISSION_ERROR
            if isinstance(e, ValueError):
                error_code = ContactErrorCodes.VALIDATION_ERROR
            elif 'file' in str(e).lower() or 'upload' in str(e).lower():
                error_code = ContactErrorCodes.FILE_UPLOAD_ERROR
            elif 'database' in str(e).lower() or 'db' in str(e).lower():
                error_code = ContactErrorCodes.DATABASE_ERROR
            
            return ErrorResponse.json_error(
                message=get_user_friendly_message(error_code),
                status_code=get_status_code_for_error(error_code),
                error_code=error_code,
                details={'exception': str(e)} if settings.DEBUG else None
            )


class PrivacyPolicyView(NepaliLanguageMixin, TemplateView):
    """Render the privacy policy page."""
    template_name = 'contact/privacy_policy.html'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
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
