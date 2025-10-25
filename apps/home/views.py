from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.core.paginator import Paginator
from django.db import transaction
import json
import uuid
import logging

# Set up logging
logger = logging.getLogger(__name__)

from apps.about.models import Committee, Membership, Person
from .models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    ServiceHighlight, NewsletterSubscriber,
    ContactInquiry, PageView
)
from .forms import ContactForm, NewsletterSignupForm
from gallery.models import GalleryImage


def track_page_view(request, page_url, page_title=""):
    """Track page views for analytics with error handling"""
    try:
        # Sanitize inputs
        page_url = page_url[:500] if page_url else ""
        page_title = page_title[:200] if page_title else ""
        user_ip = request.META.get('REMOTE_ADDR', '')[:45]  # IPv6 max length
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        referrer = request.META.get('HTTP_REFERER', '')[:500]
        session_id = request.session.session_key or str(uuid.uuid4())
        
        PageView.objects.create(
            page_url=page_url,
            page_title=page_title,
            user_ip=user_ip,
            user_agent=user_agent,
            referrer=referrer,
            session_id=session_id[:100]
        )
    except Exception as e:
        # Log error instead of printing
        logger.error(f"Analytics error: {e}", exc_info=True)


@cache_page(300)  # Cache for 5 minutes
@vary_on_headers('User-Agent')
def index(request):
    """
    Enhanced homepage view with dynamic content and caching
    """
    # Track page view
    track_page_view(request, request.build_absolute_uri(), "Bhanjyang Cooperative - Home")
    
    cache_key = f'homepage_data_{request.user.is_staff}'
    cached_data = cache.get(cache_key)
    
    if cached_data and not request.user.is_staff:
        # Attach non-cacheable objects (like forms) at render-time to avoid pickling issues
        cached_render_context = {
            **cached_data,
            'contact_form': ContactForm(),
            'newsletter_form': NewsletterSignupForm(),
        }
        return render(request, 'home/index.html', cached_render_context)
    
    # Fetch dynamic content with error handling
    try:
        # Get featured content with select_related for performance
        featured_testimonials = Testimonial.objects.filter(
            is_featured=True, is_active=True
        ).order_by('order')[:3]
        
        featured_statistics = Statistic.objects.filter(
            is_featured=True, is_active=True
        ).order_by('order')[:4]
        
        featured_announcements = Announcement.objects.filter(
            is_featured=True, is_active=True
        ).exclude(
            Q(expiry_date__isnull=False) & Q(expiry_date__lt=timezone.now())
        ).order_by('-priority', '-publish_date')[:3]
        
        featured_services = list(ServiceHighlight.objects.filter(
            is_featured=True, is_active=True
        ).order_by('order')[:3])
        
        featured_gallery = GalleryImage.objects.filter(
            is_featured=True, is_active=True
        ).order_by('order')[:6]
        
        # Get main homepage content
        homepage_content = HomePageContent.objects.filter(
            is_active=True
        ).order_by('order').first()
        
    except Exception as e:
        # Log error and provide fallback data
        logger.error(f"Error fetching homepage data: {e}", exc_info=True)
        featured_testimonials = []
        featured_statistics = []
        featured_announcements = []
        featured_services = []
        featured_gallery = []
        homepage_content = None
    
    # Cache only serializable parts to avoid PicklingError
    cached_context = {
        'breadcrumbs': [{'name': 'Home', 'url': '/'}],
        'featured_testimonials': list(featured_testimonials),
        'featured_statistics': list(featured_statistics),
        'featured_announcements': list(featured_announcements),
        'featured_services': featured_services,  # already a list above
        'featured_gallery': list(featured_gallery),
        'homepage_content': homepage_content,
    }

    # Attach forms only at render time
    context = {
        **cached_context,
        'contact_form': ContactForm(),
        'newsletter_form': NewsletterSignupForm(),
    }
    
    # Cache for 5 minutes (best-effort; skip if non-picklable)
    try:
        cache.set(cache_key, cached_context, 300)
    except Exception as e:
        logger.warning(f"Skipping homepage context cache due to serialization error: {e}")
    
    return render(request, 'home/index.html', context)


@cache_page(600)  # Cache for 10 minutes
def about_view(request):
    """
    Enhanced about page view with dynamic content
    """
    track_page_view(request, request.build_absolute_uri(), "About Us - Bhanjyang Cooperative")
    
    cache_key = f'about_page_data_{request.user.is_staff}'
    cached_data = cache.get(cache_key)
    
    if cached_data and not request.user.is_staff:
        return render(request, 'home/about.html', cached_data)
    
    context = {
        'board_members': [],
        'account_supervisor_committee': [],
        'branch_management_sub_committee': [],
        'loan_subcommittee': [],
        'advisory_committee': [],
        'management_team': [],
        'chairman': None,
        'manager': None,
        'former_committees_names': [],
    }

    try:
        # Fetch all active committees and their members efficiently
        active_committees = Committee.objects.filter(is_active=True).prefetch_related('memberships__person').order_by('order')
        
        # A dictionary to map committee names (keywords) to context keys
        committee_map = {
            'Board of Directors': 'board_members',
            'सञ्चालक समिति': 'board_members',
            'Account Supervisor': 'account_supervisor_committee',
            'लेखा समिति': 'account_supervisor_committee',
            'Branch Management': 'branch_management_sub_committee',
            'सेवा केन्द्र': 'branch_management_sub_committee',
            'Loan Subcommittee': 'loan_subcommittee',
            'ऋण उपसमिति': 'loan_subcommittee',
            'Advisory': 'advisory_committee',
            'सल्लाहकार': 'advisory_committee',
            'Management Team': 'management_team',
            'कर्मचारी': 'management_team',
        }

        # Populate the context dictionary based on committee names
        for committee in active_committees:
            for keyword, key in committee_map.items():
                if keyword in committee.name:
                    context[key] = committee.memberships.order_by('order')
                    break
        
        # Specifically find the Chairman and Manager for the message section
        if context['board_members']:
            chairman_membership = context['board_members'].filter(position__icontains='Chairman').first()
            if not chairman_membership:
                chairman_membership = context['board_members'].filter(position__icontains='अध्यक्ष').first()
            if chairman_membership:
                context['chairman'] = chairman_membership.person

        if context['management_team']:
            manager_membership = context['management_team'].filter(position__icontains='Manager').first()
            if not manager_membership:
                manager_membership = context['management_team'].filter(position__icontains='व्यवस्थापक').first()
            if manager_membership:
                context['manager'] = manager_membership.person
                
        # Fetch names of former committees
        context['former_committees_names'] = Committee.objects.filter(is_active=False).values_list('name', flat=True).order_by('-tenure_bs')

    except Exception as e:
        logger.error(f"Error fetching data for about page: {e}", exc_info=True)
    
    # Cache for 10 minutes
    cache.set(cache_key, context, 600)
    
    return render(request, 'home/about.html', context)




def remittance_view(request):
    """
    Enhanced remittance services page
    """
    track_page_view(request, request.build_absolute_uri(), "Remittance Services - Bhanjyang Cooperative")
    
    context = {
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Remittance Services', 'url': '/remittance/'}
        ],
    }
    return render(request, 'home/remittance.html', context)


@require_POST
@transaction.atomic
def contact_submit(request):
    """
    Handle contact form submissions with improved security and error handling
    """
    form = ContactForm(request.POST)
    
    if form.is_valid():
        try:
            # Save inquiry to database
            inquiry = ContactInquiry.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                inquiry_type=form.cleaned_data.get('inquiry_type', 'general')
            )
            
            # Send email notification
            if getattr(settings, 'SEND_REAL_EMAILS', False):
                try:
                    send_mail(
                        f"New Contact Inquiry: {inquiry.subject}",
                        f"""
                        Name: {inquiry.name}
                        Email: {inquiry.email}
                        Phone: {inquiry.phone}
                        Subject: {inquiry.subject}
                        Message: {inquiry.message}
                        Inquiry Type: {inquiry.inquiry_type}
                        """,
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.DEFAULT_FROM_EMAIL],
                        fail_silently=False,
                    )
                except Exception as email_error:
                    logger.error(f"Email sending failed: {email_error}", exc_info=True)
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for your inquiry. We will get back to you soon!'
                })
            else:
                messages.success(request, 'Thank you for your inquiry. We will get back to you soon!')
                return redirect('home:index')
                
        except Exception as e:
            logger.error(f"Error processing contact form: {e}", exc_info=True)
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'Sorry, there was an error processing your request. Please try again.'
                })
            else:
                messages.error(request, 'Sorry, there was an error processing your request. Please try again.')
                return redirect('home:index')
    else:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors in the form.',
                'errors': form.errors
            })
        else:
            messages.error(request, 'Please correct the errors in the form.')
            return redirect('home:index')


@require_POST
@csrf_exempt
@transaction.atomic
def newsletter_signup(request):
    """
    Handle newsletter signup (AJAX endpoint) with improved security
    """
    form = NewsletterSignupForm(request.POST)
    
    if form.is_valid():
        try:
            email = form.cleaned_data['email']
            name = form.cleaned_data.get('name', '')
            
            # Check if already subscribed
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'name': name, 'is_active': True}
            )
            
            if created:
                # Send confirmation email
                if getattr(settings, 'SEND_REAL_EMAILS', False):
                    try:
                        send_mail(
                            "Welcome to Bhanjyang Cooperative Newsletter",
                            f"""
                            Dear {name or 'Subscriber'},
                            
                            Thank you for subscribing to our newsletter! You will now receive updates about our services, events, and important announcements.
                            
                            Best regards,
                            Bhanjyang Cooperative Team
                            """,
                            settings.DEFAULT_FROM_EMAIL,
                            [email],
                            fail_silently=False,
                        )
                    except Exception as email_error:
                        logger.error(f"Newsletter confirmation email failed: {email_error}", exc_info=True)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for subscribing to our newsletter!'
                })
            else:
                if subscriber.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'You are already subscribed to our newsletter.'
                    })
                else:
                    # Reactivate subscription
                    subscriber.is_active = True
                    subscriber.unsubscribed_at = None
                    subscriber.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Welcome back! Your subscription has been reactivated.'
                    })
                    
        except Exception as e:
            logger.error(f"Error processing newsletter signup: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': 'Sorry, there was an error processing your subscription. Please try again.'
            })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Please enter a valid email address.',
            'errors': form.errors
        })


def api_statistics(request):
    """
    API endpoint for statistics (for dynamic updates) with error handling
    """
    try:
        statistics = Statistic.objects.filter(
            is_active=True
        ).order_by('order')
        
        data = []
        for stat in statistics:
            data.append({
                'title': stat.title,
                'value': stat.value,
                'description': stat.description,
                'icon': stat.icon,
                'color': stat.color,
            })
        
        return JsonResponse({'statistics': data})
        
    except Exception as e:
        logger.error(f"Error in api_statistics: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


def api_testimonials(request):
    """
    API endpoint for testimonials with error handling
    """
    try:
        testimonials = Testimonial.objects.filter(
            is_active=True
        ).order_by('order')
        
        data = []
        for testimonial in testimonials:
            data.append({
                'name': testimonial.name,
                'position': testimonial.position,
                'company': testimonial.company,
                'content': testimonial.content,
                'rating': testimonial.rating,
                'photo': testimonial.photo.url if testimonial.photo else None,
                'language': testimonial.language,
            })
        
        return JsonResponse({'testimonials': data})
        
    except Exception as e:
        logger.error(f"Error in api_testimonials: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)