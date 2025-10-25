from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
import json
from .models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)
from .forms import ContactForm, NewsletterSignupForm, FeedbackForm


def about_home_view(request):
    """
    Main about page view with comprehensive cooperative information
    """
    # Get cooperative information
    cooperative_info = CooperativeInfo.objects.filter(is_active=True).first()
    
    # Get featured timeline events
    timeline_events = CooperativeTimeline.objects.filter(
        is_active=True, 
        is_featured=True
    ).order_by('-event_date')[:6]
    
    # Get featured achievements
    achievements = CooperativeAchievement.objects.filter(
        is_active=True, 
        is_featured=True
    ).order_by('-received_date')[:6]
    
    # Get all statistics
    statistics = CooperativeStatistic.objects.filter(
        is_active=True
    ).order_by('order')
    
    # Get featured affiliations
    affiliations = CooperativeAffiliation.objects.filter(
        is_active=True, 
        is_featured=True
    ).order_by('order')
    
    # Get leadership messages
    leadership_messages = LeadershipMessage.objects.filter(
        is_active=True
    ).order_by('order')
    
    # Get team statistics for the team section
    total_committees = Committee.objects.filter(is_active=True).count()
    total_staff = Staff.objects.filter(is_active=True).count()
    
    context = {
        'cooperative_info': cooperative_info,
        'timeline_events': timeline_events,
        'achievements': achievements,
        'statistics': statistics,
        'affiliations': affiliations,
        'leadership_messages': leadership_messages,
        'total_committees': total_committees,
        'total_staff': total_staff,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'}
        ],
    }
    
    return render(request, 'about/about.html', context)


def timeline_view(request):
    """
    Timeline page view with all cooperative events
    """
    timeline_events = CooperativeTimeline.objects.filter(
        is_active=True
    ).order_by('-event_date')
    
    # Pagination
    paginator = Paginator(timeline_events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': 'Timeline', 'url': '/about/timeline/'}
        ],
    }
    
    return render(request, 'about/timeline.html', context)


def achievements_view(request):
    """
    Achievements page view with all cooperative achievements
    """
    achievements = CooperativeAchievement.objects.filter(
        is_active=True
    ).order_by('-received_date')
    
    # Pagination
    paginator = Paginator(achievements, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': 'Achievements', 'url': '/about/achievements/'}
        ],
    }
    
    return render(request, 'about/achievements.html', context)


def affiliations_view(request):
    """
    Affiliations page view with all cooperative affiliations
    """
    affiliations = CooperativeAffiliation.objects.filter(
        is_active=True
    ).order_by('order')
    
    context = {
        'affiliations': affiliations,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': 'Affiliations', 'url': '/about/affiliations/'}
        ],
    }
    
    return render(request, 'about/affiliations.html', context)


def leadership_view(request):
    """
    Leadership page view with all leadership messages
    """
    leadership_messages = LeadershipMessage.objects.filter(
        is_active=True
    ).order_by('order')
    
    context = {
        'leadership_messages': leadership_messages,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': 'Leadership', 'url': '/about/leadership/'}
        ],
    }
    
    return render(request, 'about/leadership.html', context)


def team_view(request):
    """
    Team page view with active committees and management team
    """
    active_committees = Committee.objects.filter(is_active=True).prefetch_related('memberships__person')
    management_team = Staff.objects.filter(is_active=True).select_related('person')
    
    context = {
        'committees': active_committees,
        'management_team': management_team,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': 'Our Team', 'url': '/about/team/'}
        ],
    }
    return render(request, 'about/team.html', context)


def past_team_view(request):
    """
    Past team page view with inactive committees
    """
    past_committees = Committee.objects.filter(is_active=False).order_by('-tenure_bs').prefetch_related('memberships__person')
    
    context = {
        'committees': past_committees,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': 'Our Team', 'url': '/about/team/'},
            {'name': 'Past Committees', 'url': '/about/team/past/'}
        ],
    }
    return render(request, 'about/past_team.html', context)


class CooperativeDetailView(DetailView):
    """Detail view for cooperative information"""
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


# Form handling views
@never_cache
def contact_view(request):
    """Handle contact form submissions"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Send email notification
            try:
                send_mail(
                    subject=f"New Contact Form Submission: {form.cleaned_data['subject']}",
                    message=f"""
Name: {form.cleaned_data['name']}
Email: {form.cleaned_data['email']}
Phone: {form.cleaned_data.get('phone', 'Not provided')}
Inquiry Type: {form.cleaned_data['inquiry_type']}
Subject: {form.cleaned_data['subject']}

Message:
{form.cleaned_data['message']}
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL] if hasattr(settings, 'CONTACT_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                
                # Send confirmation email to user
                send_mail(
                    subject="Thank you for contacting Bhanjyang Cooperative",
                    message=f"""
Dear {form.cleaned_data['name']},

Thank you for contacting Bhanjyang Multipurpose Cooperative Ltd. We have received your inquiry and will respond to you within 24 hours.

Your inquiry details:
Subject: {form.cleaned_data['subject']}
Type: {form.cleaned_data['inquiry_type']}

We appreciate your interest in our services.

Best regards,
Bhanjyang Cooperative Team
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[form.cleaned_data['email']],
                    fail_silently=False,
                )
                
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect('about:contact_success')
                
            except Exception as e:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')
    else:
        form = ContactForm()
    
    return render(request, 'about/contact.html', {'form': form})


@csrf_exempt
@require_POST
def newsletter_signup_view(request):
    """Handle newsletter signup via AJAX"""
    try:
        data = json.loads(request.body)
        form = NewsletterSignupForm(data)
        
        if form.is_valid():
            # Here you would typically save to database
            # For now, we'll just send a confirmation email
            
            send_mail(
                subject="Welcome to Bhanjyang Cooperative Newsletter",
                message=f"""
Dear {form.cleaned_data.get('name', 'Subscriber')},

Thank you for subscribing to our newsletter! You will now receive updates about:

{', '.join(form.cleaned_data.get('interests', []))}

We look forward to keeping you informed about our latest news, services, and community initiatives.

Best regards,
Bhanjyang Cooperative Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[form.cleaned_data['email']],
                fail_silently=False,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Successfully subscribed to newsletter!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })


@csrf_exempt
@require_POST
def feedback_view(request):
    """Handle feedback form submissions"""
    try:
        data = json.loads(request.body)
        form = FeedbackForm(data)
        
        if form.is_valid():
            # Send feedback email
            send_mail(
                subject=f"Website Feedback - Rating: {form.cleaned_data['rating']}/5",
                message=f"""
Feedback Category: {form.cleaned_data['feedback_type']}
Rating: {form.cleaned_data['rating']}/5
Email: {form.cleaned_data.get('email', 'Not provided')}

Comments:
{form.cleaned_data.get('comments', 'No additional comments')}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.FEEDBACK_EMAIL] if hasattr(settings, 'FEEDBACK_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your feedback!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })


def gallery_view(request):
    """Gallery page view"""
    context = {
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': 'Gallery', 'url': '/about/gallery/'}
        ],
    }
    return render(request, 'about/gallery.html', context)


def contact_success_view(request):
    """Contact form success page"""
    return render(request, 'about/contact_success.html')
