"""
Member Forms for Registration, KYC, and Profile Management
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from .models import (
    MemberRegistration, Member, KYCDocument, 
    Ward, MemberAccount, MemberLoan
)


class MemberRegistrationForm(forms.ModelForm):
    """
    Form for member registration (Step 1: Location Verification)
    """
    
    terms_agreement = forms.BooleanField(
        required=True,
        label=_('I agree to the Terms and Conditions'),
        error_messages={
            'required': _('You must agree to the Terms and Conditions to continue.')
        }
    )
    
    class Meta:
        model = MemberRegistration
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'permanent_address', 'ward', 'tole_name'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'नाम प्रविष्ट गर्नुहोस्'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'थर प्रविष्ट गर्नुहोस्'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'इमेल ठेगाना प्रविष्ट गर्नुहोस्'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'फोन नम्बर प्रविष्ट गर्नुहोस्'
            }),
            'permanent_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'स्थायी ठेगाना प्रविष्ट गर्नुहोस्'
            }),
            'ward': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tole_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'टोल/गाउँको नाम प्रविष्ट गर्नुहोस्'
            }),
        }
        labels = {
            'first_name': _('नाम'),
            'last_name': _('थर'),
            'email': _('इमेल ठेगाना'),
            'phone': _('फोन नम्बर'),
            'permanent_address': _('स्थायी ठेगाना'),
            'ward': _('वडा नम्बर'),
            'tole_name': _('टोल/गाउँको नाम'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active wards
        self.fields['ward'].queryset = Ward.objects.filter(is_active=True)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('यो इमेल ठेगाना पहिले नै प्रयोग भएको छ।'))
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if MemberRegistration.objects.filter(phone=phone).exists():
            raise ValidationError(_('यो फोन नम्बर पहिले नै प्रयोग भएको छ।'))
        return phone
    
    def save(self, commit=True):
        registration = super().save(commit=False)
        registration.status = 'pending_location'
        
        if commit:
            registration.save()
            
        return registration


class KYCDocumentForm(forms.ModelForm):
    """
    Form for KYC document upload (Step 2: After Location Approval)
    """
    
    citizenship_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'नागरिकता नम्बर प्रविष्ट गर्नुहोस्'
        }),
        label=_('नागरिकता नम्बर')
    )
    citizenship_issue_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label=_('नागरिकता जारी मिति')
    )
    citizenship_issue_district = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'नागरिकता जारी जिल्ला प्रविष्ट गर्नुहोस्'
        }),
        label=_('नागरिकता जारी जिल्ला')
    )
    father_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'बुबाको नाम प्रविष्ट गर्नुहोस्'
        }),
        label=_('बुबाको नाम')
    )
    mother_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'आमाको नाम प्रविष्ट गर्नुहोस्'
        }),
        label=_('आमाको नाम')
    )
    spouse_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'पत्नी/पतिको नाम (वैकल्पिक)'
        }),
        label=_('पत्नी/पतिको नाम')
    )
    occupation = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'पेशा प्रविष्ट गर्नुहोस्'
        }),
        label=_('पेशा')
    )
    workplace = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'कार्यस्थल (वैकल्पिक)'
        }),
        label=_('कार्यस्थल')
    )
    monthly_income = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'मासिक आम्दानी (रुपैयाँमा)'
        }),
        label=_('मासिक आम्दानी')
    )
    
    class Meta:
        model = MemberRegistration
        fields = [
            'citizenship_document', 'address_proof'
        ]
        widgets = {
            'citizenship_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'address_proof': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }
        labels = {
            'citizenship_document': _('नागरिकता प्रमाणपत्र'),
            'address_proof': _('ठेगाना प्रमाणपत्र'),
        }
    
    def clean_citizenship_document(self):
        document = self.cleaned_data.get('citizenship_document')
        if document:
            # Check file size (max 5MB)
            if document.size > 5 * 1024 * 1024:
                raise ValidationError(_('फाइलको आकार ५ MB भन्दा कम हुनुपर्छ।'))
            
            # Check file type
            allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
            if document.content_type not in allowed_types:
                raise ValidationError(_('केवल PDF, JPG, JPEG, र PNG फाइलहरू मात्र स्वीकार्य छन्।'))
        
        return document
    
    def clean_address_proof(self):
        document = self.cleaned_data.get('address_proof')
        if document:
            # Check file size (max 5MB)
            if document.size > 5 * 1024 * 1024:
                raise ValidationError(_('फाइलको आकार ५ MB भन्दा कम हुनुपर्छ।'))
            
            # Check file type
            allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
            if document.content_type not in allowed_types:
                raise ValidationError(_('केवल PDF, JPG, JPEG, र PNG फाइलहरू मात्र स्वीकार्य छन्।'))
        
        return document


class MemberLoginForm(AuthenticationForm):
    """
    Custom login form for members
    """
    
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'इमेल ठेगाना प्रविष्ट गर्नुहोस्'
        }),
        label=_('इमेल ठेगाना')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'पासवर्ड प्रविष्ट गर्नुहोस्'
        }),
        label=_('पासवर्ड')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('इमेल ठेगाना')
        self.fields['password'].label = _('पासवर्ड')


class MemberProfileForm(forms.ModelForm):
    """
    Form for member profile updates
    """
    
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'middle_name', 'phone', 'alternate_phone',
            'permanent_address', 'tole_name', 'father_name', 'mother_name',
            'spouse_name', 'occupation', 'workplace', 'monthly_income',
            'profile_photo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'permanent_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'tole_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_name': forms.TextInput(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'workplace': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': _('नाम'),
            'last_name': _('थर'),
            'middle_name': _('बिचको नाम'),
            'phone': _('फोन नम्बर'),
            'alternate_phone': _('अन्य फोन नम्बर'),
            'permanent_address': _('स्थायी ठेगाना'),
            'tole_name': _('टोल/गाउँको नाम'),
            'father_name': _('बुबाको नाम'),
            'mother_name': _('आमाको नाम'),
            'spouse_name': _('पत्नी/पतिको नाम'),
            'occupation': _('पेशा'),
            'workplace': _('कार्यस्थल'),
            'monthly_income': _('मासिक आम्दानी'),
            'profile_photo': _('प्रोफाइल फोटो'),
        }


class LoanApplicationForm(forms.ModelForm):
    """
    Form for loan applications
    """
    
    class Meta:
        model = MemberLoan
        fields = [
            'loan_type', 'loan_amount', 'purpose', 'tenure_months'
        ]
        widgets = {
            'loan_type': forms.Select(attrs={'class': 'form-control'}),
            'loan_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1000',
                'step': '1000'
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'ऋणको उद्देश्य विस्तृत रूपमा लेख्नुहोस्'
            }),
            'tenure_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '60'
            }),
        }
        labels = {
            'loan_type': _('ऋणको प्रकार'),
            'loan_amount': _('ऋण रकम'),
            'purpose': _('ऋणको उद्देश्य'),
            'tenure_months': _('ऋण अवधि (महिनामा)'),
        }
    
    def clean_loan_amount(self):
        amount = self.cleaned_data.get('loan_amount')
        if amount and amount < 1000:
            raise ValidationError(_('ऋण रकम कम्तिमा १,००० रुपैयाँ हुनुपर्छ।'))
        return amount
    
    def clean_tenure_months(self):
        tenure = self.cleaned_data.get('tenure_months')
        if tenure and (tenure < 1 or tenure > 60):
            raise ValidationError(_('ऋण अवधि १ देखि ६० महिना सम्म हुनुपर्छ।'))
        return tenure


class PasswordChangeForm(forms.Form):
    """
    Form for password change
    """
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'हालको पासवर्ड प्रविष्ट गर्नुहोस्'
        }),
        label=_('हालको पासवर्ड')
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'नयाँ पासवर्ड प्रविष्ट गर्नुहोस्'
        }),
        label=_('नयाँ पासवर्ड')
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'नयाँ पासवर्ड पुनः प्रविष्ट गर्नुहोस्'
        }),
        label=_('नयाँ पासवर्ड पुनः प्रविष्ट गर्नुहोस्')
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError(_('हालको पासवर्ड गलत छ।'))
        return current_password
    
    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError(_('नयाँ पासवर्डहरू मेल खाँदैन।'))
        return new_password2
    
    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


class ContactForm(forms.Form):
    """
    Contact form for member inquiries
    """
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'विषय प्रविष्ट गर्नुहोस्'
        }),
        label=_('विषय')
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'सन्देश लेख्नुहोस्'
        }),
        label=_('सन्देश')
    )
    priority = forms.ChoiceField(
        choices=[
            ('low', 'कम'),
            ('medium', 'मध्यम'),
            ('high', 'उच्च'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('प्राथमिकता')
    )
