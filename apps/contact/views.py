"""
Views for the Contact app.

This module contains view functions for contact form, KYM form, and privacy policy pages.
"""
import logging
import time

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.utils.translation import activate

from apps.core.error_handling import ErrorLogger, ErrorResponse

from .forms import ContactForm, KYMForm
from .services import ContactService, KYMService
from .utils.rate_limiting import rate_limit_by_ip, rate_limit_by_email

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
@rate_limit_by_ip('5/m')  # 5 requests per minute per IP
def contact_view(request):
    """
    Handle contact form display and submission.
    
    GET: Display the contact form page
    POST: Process contact form submission via AJAX
    
    Returns JSON response for POST requests, rendered template for GET.
    """
    activate('ne')
    start_time = time.time()
    
    if request.method == 'GET':
        context = ContactService.get_contact_page_context()
        processing_time = time.time() - start_time
        logger.info(f"Contact form GET request processed in {processing_time:.3f}s")
        return render(request, 'contact/contact.html', context)
    
    # POST request handling
    if not _is_ajax_request(request):
        logger.warning("Non-AJAX POST request rejected")
        return JsonResponse({
            'success': False,
            'message': 'This endpoint only accepts AJAX requests.'
        }, status=400)
    
    logger.info("Processing AJAX contact form submission")
    form = ContactForm(request.POST, request.FILES)
    
    if not form.is_valid():
        logger.warning(f"Form validation failed: {form.errors}")
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    
    # Check email-based rate limiting (3 per hour)
    email_rate_limit = rate_limit_by_email('3/h')
    is_limited, limit_message = email_rate_limit(form.cleaned_data.get('email', ''))
    if is_limited:
        logger.warning(f"Email rate limit exceeded for: {form.cleaned_data.get('email', 'unknown')}")
        return JsonResponse({
            'success': False,
            'message': limit_message,
            'error_code': 'EMAIL_RATE_LIMIT_EXCEEDED'
        }, status=429)
    
    try:
        # Create submission using service
        submission = ContactService.create_contact_submission(
            form_data=form.cleaned_data,
            files=request.FILES,
            request_meta=request.META
        )
        
        # Send notification emails
        ContactService.send_contact_notification_emails(submission)
        
        processing_time = time.time() - start_time
        logger.info(
            f"Contact form processed successfully in {processing_time:.3f}s "
            f"for submission {submission.id}"
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you! Your message has been sent successfully.',
            'submission_id': submission.id
        })
        
    except Exception as e:
        ErrorLogger.log_error(e, request, context={'form': 'contact'})
        
        return ErrorResponse.json_error(
            message='An error occurred while processing your request. Please try again later.',
            status_code=500,
            error_code='SUBMISSION_ERROR',
            details={'exception': str(e)} if settings.DEBUG else None
        )


@require_http_methods(["GET", "POST"])
@rate_limit_by_ip('3/m')  # 3 requests per minute per IP (KYM form is more sensitive)
def kym_form_view(request):
    """
    Handle KYM form display and submission.
    
    GET: Display the KYM form page
    POST: Process KYM form submission via AJAX
    
    Returns JSON response for POST requests, rendered template for GET.
    """
    activate('ne')
    if request.method == 'GET':
        context = KYMService.get_kym_page_context()
        return render(request, 'contact/kym_form.html', context)
    
    # POST request handling - require AJAX for consistency with contact_view
    if not _is_ajax_request(request):
        logger.warning("Non-AJAX KYM POST request rejected")
        return JsonResponse({
            'success': False,
            'message': 'This endpoint only accepts AJAX requests.'
        }, status=400)
    
    logger.info("Processing AJAX KYM form submission")
    form = KYMForm(request.POST, request.FILES)
    
    if not form.is_valid():
        logger.warning(f"KYM form validation failed: {form.errors}")
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    
    # Check email-based rate limiting (2 per hour for KYM - more restrictive)
    email_rate_limit = rate_limit_by_email('2/h')
    is_limited, limit_message = email_rate_limit(form.cleaned_data.get('email', ''))
    if is_limited:
        logger.warning(f"Email rate limit exceeded for KYM: {form.cleaned_data.get('email', 'unknown')}")
        return JsonResponse({
            'success': False,
            'message': limit_message,
            'error_code': 'EMAIL_RATE_LIMIT_EXCEEDED'
        }, status=429)
    
    try:
        submission = KYMService.create_kym_submission(
            form_data=form.cleaned_data,
            files=request.FILES,
            request_meta=request.META
        )
        
        logger.info(f"KYM submission saved with ID: {submission.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'KYM form submitted successfully! We will review your submission and contact you soon.',
            'submission_id': submission.id
        })
        
    except Exception as e:
        ErrorLogger.log_error(e, request, context={'form': 'kym'})
        logger.exception(f"Error saving KYM submission: {e}")
        
        # Security fix: Don't expose exception details to users
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while processing your submission. Please try again later.'
        }, status=500)


def privacy_policy_view(request):
    """Render the privacy policy page."""
    activate('ne')
    from apps.about.models import CooperativeInfo
    
    # Fetch cooperative info for dynamic contact details
    cooperative_info = None
    try:
        cooperative_info = CooperativeInfo.objects.active().first()
    except Exception as e:
        logger.warning(f"Could not fetch cooperative info for privacy policy: {e}")
    
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Contact', 'url': '/contact/'},
        {'name': 'Privacy Policy', 'url': '/contact/privacy-policy/'}
    ]
    
    context = {
        'breadcrumbs': breadcrumbs,
        'cooperative_info': cooperative_info
    }
    
    return render(request, 'contact/privacy_policy.html', context)


def _is_ajax_request(request):
    """
    Check if request is an AJAX request.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        bool: True if request is AJAX, False otherwise
    """
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
