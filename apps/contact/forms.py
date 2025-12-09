from django import forms
from django.core.validators import FileExtensionValidator
import os

class ContactForm(forms.Form):
    """Contact form for general inquiries."""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'Your full name',
            'autocomplete': 'name'
        }),
        label='Name'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'your.email@example.com',
            'autocomplete': 'email'
        }),
        label='Email'
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': '+977-XXXXXXXXXX',
            'autocomplete': 'tel'
        }),
        label='Phone (Optional)'
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'Subject of your inquiry',
            'autocomplete': 'off'
        }),
        label='Subject'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200 resize-none',
            'rows': 5,
            'placeholder': 'Your message here...',
            'autocomplete': 'off'
        }),
        label='Message',
        min_length=10
    )
    
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
        }),
        label='Attachment (Optional)',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )

class KYMForm(forms.Form):
    """Know Your Member (KYM) form for member registration and verification."""
    
    # Personal Details
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'As per your ID'
        }),
        label='Full Name',
        help_text='Enter your full name as it appears on your citizenship/ID card'
    )
    
    dob = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'type': 'date'
        }),
        label='Date of Birth'
    )
    
    gender = forms.ChoiceField(
        choices=[
            ('', 'Select Gender'),
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ],
        widget=forms.Select(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200'
        }),
        label='Gender'
    )
    
    marital_status = forms.ChoiceField(
        choices=[
            ('', 'Select Status'),
            ('single', 'Single'),
            ('married', 'Married'),
            ('divorced', 'Divorced'),
            ('widowed', 'Widowed')
        ],
        widget=forms.Select(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200'
        }),
        label='Marital Status'
    )
    
    nationality = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'e.g., Nepali'
        }),
        label='Nationality',
        initial='Nepali'
    )
    
    # Contact Information
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': '+977-XXXXXXXXXX'
        }),
        label='Phone Number'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'your.email@example.com'
        }),
        label='Email Address'
    )
    
    permanent_address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'Street, Village, Ward No.'
        }),
        label='Permanent Address'
    )
    
    district = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'e.g., Kaski'
        }),
        label='District',
        initial='Kaski'
    )
    
    province = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'e.g., Gandaki Province'
        }),
        label='Province',
        initial='Gandaki Province'
    )
    
    # Family Details
    father_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': "Father's Full Name"
        }),
        label="Father's Name"
    )
    
    mother_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': "Mother's Full Name"
        }),
        label="Mother's Name"
    )
    
    spouse_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': "Spouse's Full Name"
        }),
        label="Spouse's Name (if married)"
    )
    
    grand_father_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': "Grand Father's Full Name"
        }),
        label="Grand Father's Name"
    )
    
    nominee_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'Full name of your nominee'
        }),
        label='Nominee Name (Optional)'
    )
    
    # Occupation & Income Details
    occupation = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'Your profession/business'
        }),
        label='Occupation'
    )
    
    income_source = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'e.g., Salary, Business, Agriculture'
        }),
        label='Source of Income'
    )
    
    estimated_income = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'placeholder': 'e.g., 500000'
        }),
        label='Estimated Annual Income (NPR)'
    )
    
    # Document Uploads
    citizenship_front = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label='Citizenship/ID Card (Front)',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    citizenship_back = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label='Citizenship/ID Card (Back)',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    passport_photo_upload = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'accept': '.jpg,.jpeg,.png'
        }),
        label='Passport-sized Photo',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    
    address_proof_upload = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label='Address Proof (e.g., Utility Bill)',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    income_proof_upload = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors duration-200',
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label='Occupation/Income Proof (Optional)',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # File size validation (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        
        file_fields = [
            'citizenship_front', 'citizenship_back', 'passport_photo_upload',
            'address_proof_upload', 'income_proof_upload'
        ]
        
        for field in file_fields:
            if field in cleaned_data and cleaned_data[field]:
                file = cleaned_data[field]
                if file.size > max_size:
                    raise forms.ValidationError(f'{field.replace("_", " ").title()} file size must be less than 5MB.')
        
        return cleaned_data