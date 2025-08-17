from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

def contact_view(request):
    """
    Handles displaying the contact form and processing submitted data via Fetch API.
    Returns a JSON response.
    """
    # Handle GET request to just display the page
    if request.method == 'GET':
        form = ContactForm()
        return render(request, 'contact/contact.html', {'form': form})

    # Handle POST request from the form submission
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            # Form is valid, proceed to send email
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone', 'N/A') # Safely get optional phone
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']

            full_subject = f"Website Contact: {subject}"
            full_message = f"""
            New message from Bhanjyang Cooperative website:
            
            Name: {name}
            Email: {from_email}
            Phone: {phone}
            --------------------------------------------------
            
            Message:
            {message_body}
            """
            
            try:
                # Send the email using settings from settings.py
                send_mail(
                    subject=full_subject,
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['admin@bhanjyang.coop.np'],
                    fail_silently=False,
                )
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you! Your message has been sent successfully.'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'An error occurred: {e}'
                }, status=500)
        else:
            # Form is invalid, return errors
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
            
    # If not GET or POST, it's a bad request
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
