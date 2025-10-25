from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from .forms import ContactForm, KYMForm
from .models import ContactSubmission
from .tasks import send_contact_email, send_auto_response_email
import logging
import time
from django.db import connection

logger = logging.getLogger(__name__)

def get_email_from_request(request):
    """Extract email from POST data for rate limiting"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email', '').strip().lower()
            return email if email else None
        except:
            return None
    return None

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key=get_email_from_request, rate='3/h', method='POST', block=True)
def contact_view(request):
    """
    Handles displaying the contact form and processing submitted data via Fetch API.
    Returns a JSON response.
    """
    # Performance monitoring
    start_time = time.time()
    db_queries_start = len(connection.queries)
    # Handle GET request to just display the page
    if request.method == 'GET':
        form = ContactForm()
        breadcrumbs = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Contact', 'url': '/contact/'}
        ]
        context = {
            'form': form,
            'breadcrumbs': breadcrumbs
        }
        
        # Log performance metrics for GET requests
        processing_time = time.time() - start_time
        db_queries_count = len(connection.queries) - db_queries_start
        logger.info(f"Contact form GET request processed in {processing_time:.3f}s with {db_queries_count} DB queries")
        
        return render(request, 'contact/contact.html', context)

    # Handle POST request from the form submission
    if request.method == 'POST':
        logger.info(f"POST request received. X-Requested-With: {request.headers.get('X-Requested-With')}")
        
        # Check if rate limited
        if getattr(request, 'limited', False):
            logger.warning(f"Rate limit exceeded for IP: {request.META.get('REMOTE_ADDR')}")
            # Check which rate limit was exceeded
            if hasattr(request, 'limited') and 'email' in str(request.limited):
                return JsonResponse({
                    'success': False,
                    'message': 'Too many submissions from this email address. Please wait before submitting again.'
                }, status=429)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Too many requests from this IP address. Please wait a moment before submitting again.'
                }, status=429)
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            logger.info("AJAX request detected, processing...")
            form = ContactForm(request.POST)

            if form.is_valid():
                logger.info("Form is valid, saving to database and sending email...")
                
                # Get form data
                name = form.cleaned_data['name']
                from_email = form.cleaned_data['email']
                phone = form.cleaned_data.get('phone', '') # Safely get optional phone
                subject = form.cleaned_data['subject']
                message_body = form.cleaned_data['message']
                
                # Get client information
                ip_address = request.META.get('REMOTE_ADDR', '')
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                try:
                    # Handle file upload
                    attachment = None
                    if 'attachment' in request.FILES:
                        attachment = request.FILES['attachment']
                    
                    # Save to database first
                    submission = ContactSubmission.objects.create(
                        name=name,
                        email=from_email,
                        phone=phone,
                        subject=subject,
                        message=message_body,
                        attachment=attachment,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    logger.info(f"Contact submission saved with ID: {submission.id}")
                    
                    # Prepare email content
                    full_subject = f"Website Contact: {subject}"
                    attachment_info = ""
                    if submission.has_attachment():
                        attachment_info = f"Attachment: {submission.get_attachment_filename()} ({submission.get_attachment_size_display()})"
                    
                    full_message = f"""
New message from Bhanjyang Cooperative website:

Name: {name}
Email: {from_email}
Phone: {phone if phone else 'Not provided'}
Submission ID: {submission.id}
IP Address: {ip_address}
Date: {submission.created_at.strftime('%Y-%m-%d %H:%M:%S')}
{attachment_info}
--------------------------------------------------

Message:
{message_body}

---
This submission has been automatically saved to the database.
You can manage it through the admin interface.
                    """
                    
                    # Send emails asynchronously using Celery
                    email_data = {
                        'subject': full_subject,
                        'message': full_message,
                        'submission_id': submission.id
                    }
                    
                    # Queue the email tasks
                    send_contact_email.delay(email_data)
                    send_auto_response_email.delay(from_email, name, subject, submission.id)
                    
                    logger.info(f"Email tasks queued for submission {submission.id}")
                    
                    # Log performance metrics for successful POST requests
                    processing_time = time.time() - start_time
                    db_queries_count = len(connection.queries) - db_queries_start
                    logger.info(f"Contact form POST request processed successfully in {processing_time:.3f}s with {db_queries_count} DB queries for submission {submission.id}")
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Thank you! Your message has been sent successfully.',
                        'submission_id': submission.id
                    })
                    
                except Exception as e:
                    logger.exception(f"Error saving submission or sending email: {e}")
                    
                    # Log performance metrics for error cases
                    processing_time = time.time() - start_time
                    db_queries_count = len(connection.queries) - db_queries_start
                    logger.error(f"Contact form POST request failed in {processing_time:.3f}s with {db_queries_count} DB queries. Error: {str(e)}")
                    
                    return JsonResponse({
                        'success': False,
                        'message': f'An error occurred while processing your request: {str(e)}'
                    }, status=500)
            else:
                logger.warning(f"Form is invalid: {form.errors}")
                # Form is invalid, return errors
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
        else:
            logger.warning("Not an AJAX request")
            # Not an AJAX request, return error
            return JsonResponse({
                'success': False,
                'message': 'This endpoint only accepts AJAX requests.'
            }, status=400)
            
    # If not GET or POST, it's a bad request
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


def kym_form_view(request):
    """Render the KYM form page."""
    if request.method == 'GET':
        form = KYMForm()
        breadcrumbs = [
            {'name': 'Home', 'url': '/'},
            {'name': 'KYM Form', 'url': '/contact/kym-form/'}
        ]
        context = {
            'form': form,
            'breadcrumbs': breadcrumbs
        }
        return render(request, 'contact/kym_form.html', context)
    
    # Handle POST request for form submission
    if request.method == 'POST':
        form = KYMForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the form data
            # In a real application, you would save this to a database
            # For now, we'll just return a success response
            return JsonResponse({
                'success': True,
                'message': 'KYM form submitted successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


def privacy_policy_view(request):
    """Render the privacy policy page."""
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Contact', 'url': '/contact/'},
        {'name': 'Privacy Policy', 'url': '/contact/privacy-policy/'}
    ]
    return render(request, 'contact/privacy_policy.html', {'breadcrumbs': breadcrumbs})
