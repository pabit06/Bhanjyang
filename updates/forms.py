from django import forms
from .models import Subscriber

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 text-gray-800 rounded-l-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors',
                'placeholder': 'Enter your email address...',
                'aria-label': 'Email Address',
                'required': True
            })
        }
