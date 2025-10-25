from django import forms
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.utils.safestring import mark_safe
from .models import ContactInquiry, NewsletterSubscriber
import re


class ContactForm(forms.Form):
    """Contact form for homepage with enhanced security"""
    name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s\u0900-\u097F]+$',
                message='Name can only contain letters and spaces.',
                code='invalid_name'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
            'placeholder': 'Your Full Name',
            'required': True,
            'autocomplete': 'name'
        })
    )
    
    email = forms.EmailField(
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
            'placeholder': 'your.email@example.com',
            'required': True,
            'autocomplete': 'email'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[\+]?[0-9\s\-\(\)]{7,15}$',
                message='Please enter a valid phone number.',
                code='invalid_phone'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
            'placeholder': 'Your Phone Number (Optional)',
            'autocomplete': 'tel'
        })
    )
    
    inquiry_type = forms.ChoiceField(
        choices=[
            ('general', 'General Inquiry'),
            ('service', 'Service Information'),
            ('complaint', 'Complaint'),
            ('suggestion', 'Suggestion'),
            ('support', 'Technical Support'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
            'placeholder': 'Subject of your inquiry',
            'required': True,
            'autocomplete': 'off'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
            'placeholder': 'Please describe your inquiry in detail...',
            'rows': 5,
            'required': True
        })
    )
    
    def clean_name(self):
        """Clean and validate name field"""
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        return escape(name)
    
    def clean_subject(self):
        """Clean and validate subject field"""
        subject = self.cleaned_data.get('subject', '').strip()
        if len(subject) < 5:
            raise ValidationError('Subject must be at least 5 characters long.')
        return escape(subject)
    
    def clean_message(self):
        """Clean and validate message field"""
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise ValidationError('Message must be at least 10 characters long.')
        
        # Check for potential spam patterns
        spam_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                # Allow some URLs/emails but flag suspicious patterns
                if len(re.findall(pattern, message, re.IGNORECASE)) > 2:
                    raise ValidationError('Message contains too many links or email addresses.')
        
        return escape(message)
    
    def clean_phone(self):
        """Clean and validate phone field"""
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            # Remove all non-digit characters except + at the beginning
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            if not cleaned_phone.startswith('+'):
                cleaned_phone = '+' + cleaned_phone
            return cleaned_phone
        return phone


class NewsletterSignupForm(forms.Form):
    """Newsletter signup form with enhanced security"""
    name = forms.CharField(
        max_length=100,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s\u0900-\u097F]*$',
                message='Name can only contain letters and spaces.',
                code='invalid_name'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
            'placeholder': 'Your Name (Optional)',
            'autocomplete': 'name'
        })
    )
    
    email = forms.EmailField(
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
            'placeholder': 'your.email@example.com',
            'required': True,
            'autocomplete': 'email'
        })
    )
    
    def clean_name(self):
        """Clean and validate name field"""
        name = self.cleaned_data.get('name', '').strip()
        if name and len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        return escape(name) if name else ''
    
    def clean_email(self):
        """Clean and validate email field"""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        # Check if email is already subscribed
        if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
            raise ValidationError('This email is already subscribed to our newsletter.')
        
        # Additional email validation
        if len(email) > 254:  # RFC 5321 limit
            raise ValidationError('Email address is too long.')
        
        return email


class TestimonialForm(forms.ModelForm):
    """Form for submitting testimonials"""
    class Meta:
        model = ContactInquiry  # Using ContactInquiry as base for testimonial submissions
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
                'placeholder': 'your.email@example.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
                'placeholder': 'Testimonial Title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent',
                'placeholder': 'Share your experience with Bhanjyang Cooperative...',
                'rows': 5
            }),
        }


class QuickContactForm(forms.Form):
    """Quick contact form for homepage"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent text-sm',
            'placeholder': 'Your Name',
            'required': True
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent text-sm',
            'placeholder': 'Email',
            'required': True
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-deuraligreen focus:border-transparent text-sm',
            'placeholder': 'Quick message...',
            'rows': 3,
            'required': True
        })
    )
