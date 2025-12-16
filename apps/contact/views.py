from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
# from django_ratelimit.decorators import ratelimit  # Commented out until installed
# from django_ratelimit.exceptions import Ratelimited  # Commented out until installed
from .forms import ContactForm, KYMForm
from .models import ContactSubmission, KYMSubmission
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

from asgiref.sync import sync_to_async

# @ratelimit(key='ip', rate='5/m', method='POST', block=True)  # Commented out until installed
# @ratelimit(key=get_email_from_request, rate='3/h', method='POST', block=True)  # Commented out until installed
async def contact_view(request):
    """
    Handles displaying the contact form and processing submitted data via Fetch API.
    Returns a JSON response.
    """
    # Performance monitoring
    start_time = time.time()
    # db_queries_start = len(connection.queries) # connection.queries is not thread-safe in async
    
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
        logger.info(f"Contact form GET request processed in {processing_time:.3f}s")
        
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
                    # Handle file upload - Async file handling needs care, usually synchronous for now or via wrapper
                    # For simplicity in this step, we'll keep file handling part of the sync_to_async wrapped block or simplify
                    attachment = None
                    if 'attachment' in request.FILES:
                        attachment = request.FILES['attachment']
                    
                    # Wrap DB operations
                    @sync_to_async
                    def save_submission():
                        return ContactSubmission.objects.create(
                            name=name,
                            email=from_email,
                            phone=phone,
                            subject=subject,
                            message=message_body,
                            attachment=attachment,
                            ip_address=ip_address,
                            user_agent=user_agent
                        )
                    
                    submission = await save_submission()
                    logger.info(f"Contact submission saved with ID: {submission.id}")
                    
                    # Prepare email content
                    full_subject = f"Website Contact: {subject}"
                    # submission methods need sync access if they touch DB, but here simple properties are likely fine 
                    # OR we access them inside the sync block. 
                    # Let's simplify and build string here.
                    
                    full_message = f"""
New message from Bhanjyang Cooperative website:

Name: {name}
Email: {from_email}
Phone: {phone if phone else 'Not provided'}
Submission ID: {submission.id}
IP Address: {ip_address}
Date: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
--------------------------------------------------

Message:
{message_body}

---
This submission has been automatically saved to the database.
You can manage it through the admin interface.
                    """
                    
                    email_data = {
                        'subject': full_subject,
                        'message': full_message,
                        'submission_id': submission.id
                    }
                    
                    # Async Email Sending
                    @sync_to_async
                    def send_emails_sync():
                        try:
                             # Try to use celery if available
                            send_contact_email.delay(email_data)
                            send_auto_response_email.delay(from_email, name, subject, submission.id)
                        except AttributeError:
                            # Celery not installed, send synchronously
                            send_contact_email(email_data)
                            send_auto_response_email(from_email, name, subject, submission.id)

                    await send_emails_sync()
                    
                    logger.info(f"Email tasks queued for submission {submission.id}")
                    
                    processing_time = time.time() - start_time
                    logger.info(f"Contact form POST request processed successfully in {processing_time:.3f}s for submission {submission.id}")
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Thank you! Your message has been sent successfully.',
                        'submission_id': submission.id
                    })
                    
                except Exception as e:
                    logger.exception(f"Error saving submission or sending email: {e}")
                    
                    return JsonResponse({
                        'success': False,
                        'message': f'An error occurred while processing your request: {str(e)}'
                    }, status=500)
            else:
                logger.warning(f"Form is invalid: {form.errors}")
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
        else:
            logger.warning("Not an AJAX request")
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
            try:
                # Get form data
                cleaned_data = form.cleaned_data
                
                # Get client information
                ip_address = request.META.get('REMOTE_ADDR', '')
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                # Save to database
                kym_submission = KYMSubmission.objects.create(
                    full_name=cleaned_data['full_name'],
                    dob=cleaned_data['dob'],
                    gender=cleaned_data['gender'],
                    marital_status=cleaned_data['marital_status'],
                    nationality=cleaned_data.get('nationality', 'Nepali'),
                    phone=cleaned_data['phone'],
                    email=cleaned_data['email'],
                    permanent_address=cleaned_data['permanent_address'],
                    district=cleaned_data.get('district', 'Kaski'),
                    province=cleaned_data.get('province', 'Gandaki Province'),
                    father_name=cleaned_data['father_name'],
                    mother_name=cleaned_data['mother_name'],
                    spouse_name=cleaned_data.get('spouse_name', ''),
                    grand_father_name=cleaned_data['grand_father_name'],
                    nominee_name=cleaned_data.get('nominee_name', ''),
                    occupation=cleaned_data['occupation'],
                    income_source=cleaned_data['income_source'],
                    estimated_income=cleaned_data.get('estimated_income'),
                    citizenship_front=cleaned_data['citizenship_front'],
                    citizenship_back=cleaned_data['citizenship_back'],
                    passport_photo=cleaned_data['passport_photo_upload'],
                    address_proof=cleaned_data['address_proof_upload'],
                    income_proof=cleaned_data.get('income_proof_upload'),
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                logger.info(f"KYM submission saved with ID: {kym_submission.id}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'KYM form submitted successfully! We will review your submission and contact you soon.',
                    'submission_id': kym_submission.id
                })
                
            except Exception as e:
                logger.exception(f"Error saving KYM submission: {e}")
                return JsonResponse({
                    'success': False,
                    'message': f'An error occurred while processing your submission: {str(e)}'
                }, status=500)
        else:
            logger.warning(f"KYM form is invalid: {form.errors}")
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


def privacy_policy_view(request):
    """Render the privacy policy page."""
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Contact', 'url': '/contact/'},
        {'name': 'Privacy Policy', 'url': '/contact/privacy-policy/'}
    ]
    return render(request, 'contact/privacy_policy.html', {'breadcrumbs': breadcrumbs})
