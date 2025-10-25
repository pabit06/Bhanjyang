from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
    """Contact form for inquiries"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300',
            'placeholder': 'Your Full Name',
            'required': True
        }),
        label=_('Full Name')
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300',
            'placeholder': 'your.email@example.com',
            'required': True
        }),
        label=_('Email Address')
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300',
            'placeholder': '+977-XX-XXXXXXX'
        }),
        label=_('Phone Number')
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300',
            'placeholder': 'Subject of your inquiry',
            'required': True
        }),
        label=_('Subject')
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300 resize-none',
            'placeholder': 'Please describe your inquiry in detail...',
            'rows': 5,
            'required': True
        }),
        label=_('Message')
    )
    
    inquiry_type = forms.ChoiceField(
        choices=[
            ('general', _('General Inquiry')),
            ('membership', _('Membership Information')),
            ('loan', _('Loan Services')),
            ('savings', _('Savings Products')),
            ('complaint', _('Complaint/Suggestion')),
            ('other', _('Other')),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition-all duration-300',
            'required': True
        }),
        label=_('Inquiry Type')
    )
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError(_('Please enter a valid phone number.'))
        return phone

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
