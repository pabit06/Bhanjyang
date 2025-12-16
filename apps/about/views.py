from django.views.generic import TemplateView, ListView, DetailView, View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from .services import AboutService
from .forms import ContactForm, NewsletterSignupForm, FeedbackForm
from .models import CooperativeInfo

@method_decorator(cache_page(600), name='dispatch')
@method_decorator(vary_on_headers('User-Agent'), name='dispatch')
class AboutHomeView(TemplateView):
    template_name = 'about/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(AboutService.get_about_home_data(
            is_staff=self.request.user.is_staff
        ))
        return context


class TimelineView(ListView):
    template_name = 'about/timeline.html'
    paginate_by = 12
    context_object_name = 'page_obj' # Standard behavior for Paginator in CBV actually passes 'page_obj', but 'timeline_events' is object_list
    
    def get_queryset(self):
        return AboutService.get_timeline_events()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Timeline', 'url': '/about/timeline/'}
        ]
        return context


class AchievementsView(ListView):
    template_name = 'about/achievements.html'
    paginate_by = 12
    
    def get_queryset(self):
        return AboutService.get_achievements()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Achievements', 'url': '/about/achievements/'}
        ]
        return context


class AffiliationsView(TemplateView):
    template_name = 'about/affiliations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['affiliations'] = AboutService.get_affiliations()
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Affiliations', 'url': '/about/affiliations/'}
        ]
        return context


class LeadershipView(TemplateView):
    template_name = 'about/leadership.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leadership_messages'] = AboutService.get_leadership_messages()
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Leadership', 'url': '/about/leadership/'}
        ]
        return context


class TeamView(TemplateView):
    template_name = 'about/team.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comm, management = AboutService.get_active_team()
        context['committees'] = comm
        context['management_team'] = management
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Our Team', 'url': '/about/team/'}
        ]
        return context


class PastTeamView(TemplateView):
    template_name = 'about/past_team.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['committees'] = AboutService.get_past_committees()
        context['breadcrumbs'] = [
             {'name': 'Home', 'url': '/'},
             {'name': 'About Us', 'url': '/about/'},
             {'name': 'Our Team', 'url': '/about/team/'},
             {'name': 'Past Committees', 'url': '/about/team/past/'}
        ]
        return context


class CooperativeDetailView(DetailView):
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

# Forms and APIs

class ContactView(View):
    def get(self, request):
        return render(request, 'about/contact.html', {'form': ContactForm()})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            if AboutService.send_contact_emails(form.cleaned_data):
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect('about:contact_success')
            else:
                messages.error(request, 'Sorry, there was an error sending your message.')
        return render(request, 'about/contact.html', {'form': form})


class ContactSuccessView(TemplateView):
    template_name = 'about/contact_success.html'


class NewsletterSignupView(View):
    def post(self, request):
        # Implementation similar to home app
        # Since logic is in AboutService, use it.
        # This handles AJAX/JSON
        import json
        try:
             data = json.loads(request.body)
             form = NewsletterSignupForm(data)
             if form.is_valid():
                 AboutService.send_newsletter_welcome_email(form.cleaned_data)
                 return JsonResponse({'success': True, 'message': 'Subscribed!'})
             return JsonResponse({'success': False, 'errors': form.errors})
        except:
             return JsonResponse({'success': False, 'message': 'Invalid data'}, status=400)


class FeedbackView(View):
    def post(self, request):
        import json
        try:
             data = json.loads(request.body)
             form = FeedbackForm(data)
             if form.is_valid():
                 AboutService.send_feedback_email(form.cleaned_data)
                 return JsonResponse({'success': True, 'message': 'Feedback sent!'})
             return JsonResponse({'success': False, 'errors': form.errors})
        except:
             return JsonResponse({'success': False, 'message': 'Invalid data'}, status=400)

class GalleryView(TemplateView):
    template_name = 'about/gallery.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': 'About Us', 'url': '/about/'},
            {'name': 'Gallery', 'url': '/gallery/'}
        ]
        return context
