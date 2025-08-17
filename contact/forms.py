from django import forms

class ContactForm(forms.Form):
    """
    Form for users to send a message, now including an optional phone number.
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition',
            'placeholder': 'Your Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition',
            'placeholder': 'Your Email Address'
        })
    )
    # Add the new optional phone field
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition',
            'placeholder': 'Your Phone Number (Optional)'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deuraligreen focus:border-transparent transition',
            'rows': 6,
            'placeholder': 'Your Message'
        })
    )
