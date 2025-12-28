from django import forms
from django.utils.translation import gettext_lazy as _

# Note: ContactForm has been removed - use contact app's ContactForm instead
# This consolidation ensures all contact submissions are saved to the database

class NewsletterSignupForm(forms.Form):
    """Newsletter signup form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300',
            'placeholder': 'Enter your email address',
            'required': True
        }),
        label=_('Email Address')
    )
    
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300',
            'placeholder': 'Your Name (Optional)'
        }),
        label=_('Name')
    )
    
    interests = forms.MultipleChoiceField(
        choices=[
            ('news', _('Latest News & Updates')),
            ('services', _('New Services & Products')),
            ('events', _('Events & Programs')),
            ('financial_tips', _('Financial Tips & Advice')),
            ('community', _('Community Initiatives')),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        }),
        label=_('Areas of Interest')
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Here you could add logic to check if email already exists in newsletter
        return email

class FeedbackForm(forms.Form):
    """Feedback form for website improvements"""
    
    RATING_CHOICES = [
        (5, _('Excellent')),
        (4, _('Very Good')),
        (3, _('Good')),
        (2, _('Fair')),
        (1, _('Poor')),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'space-y-2'
        }),
        label=_('Overall Rating')
    )
    
    feedback_type = forms.ChoiceField(
        choices=[
            ('website', _('Website Design & Navigation')),
            ('content', _('Content Quality')),
            ('services', _('Services Information')),
            ('performance', _('Website Performance')),
            ('mobile', _('Mobile Experience')),
            ('other', _('Other')),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300',
            'required': True
        }),
        label=_('Feedback Category')
    )
    
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300 resize-none',
            'placeholder': 'Please share your detailed feedback...',
            'rows': 4
        }),
        label=_('Additional Comments')
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300',
            'placeholder': 'your.email@example.com (Optional)'
        }),
        label=_('Email (Optional)')
    )
