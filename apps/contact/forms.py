"""
Forms for the Contact app.

This module contains form classes for contact submissions and KYM (Know Your Member) forms.
"""
import re
from collections import Counter

import bleach
from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.widgets import NepaliDateInput

from .utils.constants import (
    ALLOWED_CONTACT_FILE_EXTENSIONS,
    ALLOWED_KYM_FILE_EXTENSIONS,
    ALLOWED_KYM_IMAGE_EXTENSIONS,
    DISPOSABLE_EMAIL_DOMAINS,
    FORM_INPUT_CSS,
    KYM_INPUT_CSS,
    MAX_CONTACT_FILE_SIZE_BYTES,
    MAX_DOMAIN_DIGITS,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_SUBJECT_LENGTH,
    MAX_WORD_REPETITION_RATIO,
    MIN_LOCAL_PART_DIGITS_FOR_SUSPICION,
    MIN_LOCAL_PART_LETTERS,
    MIN_MESSAGE_LENGTH,
    MIN_NAME_LENGTH,
    MIN_PHONE_LENGTH,
    MIN_SUBJECT_LENGTH,
    SPAM_PATTERNS,
)


class ContactForm(forms.Form):
    """Contact form for general inquiries."""
    
    name = forms.CharField(
        max_length=MAX_NAME_LENGTH,
        min_length=MIN_NAME_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_INPUT_CSS,
            'placeholder': _('Your full name'),
            'autocomplete': 'name'
        }),
        label=_('Name'),
        error_messages={
            'min_length': _('Name must be at least {min_length} characters long.').format(min_length=MIN_NAME_LENGTH),
        }
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': FORM_INPUT_CSS,
            'placeholder': _('your.email@example.com'),
            'autocomplete': 'email'
        }),
        label=_('Email')
    )
    
    phone = forms.CharField(
        max_length=MAX_PHONE_LENGTH,
        required=False,
        widget=forms.TextInput(attrs={
            'class': FORM_INPUT_CSS,
            'placeholder': _('+977-XXXXXXXXXX'),
            'autocomplete': 'tel'
        }),
        label=_('Phone (Optional)')
    )

    subject = forms.CharField(
        max_length=MAX_SUBJECT_LENGTH,
        min_length=MIN_SUBJECT_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_INPUT_CSS,
            'placeholder': _('Subject of your message'),
            'autocomplete': 'off'
        }),
        label=_('Subject')
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': f'{FORM_INPUT_CSS} resize-none',
            'rows': 5,
            'placeholder': _('Your message here...'),
            'autocomplete': 'off'
        }),
        label=_('Message'),
        min_length=MIN_MESSAGE_LENGTH
    )
    
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': FORM_INPUT_CSS,
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
        }),
        label=_('Attachment (Optional)'),
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_CONTACT_FILE_EXTENSIONS)]
    )
    
    # Honeypot field - hidden from users, traps bots
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'hidden absolute -left-9999px',
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true'
        }),
        label=''
    )
    
    # reCAPTCHA field (optional, configurable via settings)
    recaptcha_token = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=''
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enable reCAPTCHA if configured
        self.recaptcha_enabled = getattr(settings, 'CONTACT_RECAPTCHA_ENABLED', False)
        self.recaptcha_site_key = getattr(settings, 'RECAPTCHA_SITE_KEY', '')
        
        if not self.recaptcha_enabled:
            # Remove reCAPTCHA field if not enabled
            self.fields.pop('recaptcha_token', None)
        elif self.recaptcha_enabled and not self.recaptcha_site_key:
            # Keep the field but log error - validation will fail closed
            # This ensures security: if reCAPTCHA is required but misconfigured, reject submissions
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                "reCAPTCHA is enabled but RECAPTCHA_SITE_KEY is not configured. "
                "Form submissions will be rejected until site key is configured."
            )
    
    def clean_recaptcha_token(self):
        """Validate reCAPTCHA token if enabled."""
        if not self.recaptcha_enabled:
            return self.cleaned_data.get('recaptcha_token', '')
        
        token = self.cleaned_data.get('recaptcha_token', '')
        if not token:
            raise forms.ValidationError(_('reCAPTCHA verification failed. Please try again.'))
        
        # Verify token with Google reCAPTCHA API
        secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
        if not secret_key:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("reCAPTCHA verification failed: RECAPTCHA_SECRET_KEY not configured")
            raise forms.ValidationError(_('reCAPTCHA verification failed. Please contact support.'))
        
        # Try to import requests library
        try:
            import requests
        except (ImportError, ModuleNotFoundError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"reCAPTCHA verification failed: requests library not installed: {e}")
            # Fail closed: reject submission if requests library is missing
            raise forms.ValidationError(_('reCAPTCHA verification failed. Please contact support.'))
        
        # Verify token with Google reCAPTCHA API
        try:
            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            response = requests.post(verify_url, data={
                'secret': secret_key,
                'response': token
            }, timeout=5)
            
            # Parse JSON response - can raise JSONDecodeError or ValueError
            try:
                result = response.json()
            except (ValueError, TypeError) as json_error:
                # Handle invalid JSON response - fail closed for security
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"reCAPTCHA API returned invalid JSON: {json_error}. Response status: {response.status_code}, Content: {response.text[:200]}")
                raise forms.ValidationError(_('reCAPTCHA verification failed. Please try again.'))
            
            if not result.get('success', False):
                raise forms.ValidationError(_('reCAPTCHA verification failed. Please try again.'))
            
            return token
        except requests.RequestException as e:
            # Network errors - fail closed for security
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"reCAPTCHA verification network error: {e}")
            raise forms.ValidationError(_('reCAPTCHA verification failed. Please try again.'))
        except forms.ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Catch any other unexpected errors - fail closed for security
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"reCAPTCHA verification unexpected error: {type(e).__name__}: {e}")
            raise forms.ValidationError(_('reCAPTCHA verification failed. Please try again.'))

    def clean_subject(self):
        """Validate subject field for spam content."""
        subject = self.cleaned_data.get('subject', '')
        if 'spam' in subject.lower():
            raise forms.ValidationError(_("Invalid subject."))
        return subject

    def clean_name(self):
        """Validate name field - should not contain numbers."""
        name = self.cleaned_data.get('name', '')
        if any(char.isdigit() for char in name):
            raise forms.ValidationError(_("Name should not contain numbers."))
        return name

    def clean_phone(self):
        """Validate and normalize phone number."""
        phone = self.cleaned_data.get('phone', '')
        if not phone:
            return phone
            
        # Remove hyphens and spaces
        phone = phone.replace('-', '').replace(' ', '')
        
        # Must be digits or +digits
        if not re.match(r'^\+?\d+$', phone):
            raise forms.ValidationError(_("Invalid characters in phone number."))
        
        if len(phone) < MIN_PHONE_LENGTH:
            raise forms.ValidationError(_("Phone number too short."))
                 
        return phone

    def clean_email(self):
        """Validate email for disposable domains and suspicious patterns."""
        email = self.cleaned_data.get('email', '').lower()
        
        if '@' not in email:
            raise forms.ValidationError(_("Enter a valid email address."))
            
        local_part, domain = email.rsplit('@', 1)
        
        # Check for disposable email domains
        if domain in DISPOSABLE_EMAIL_DOMAINS:
            raise forms.ValidationError(_("Disposable email addresses are not allowed."))
        
        # Check suspicious patterns
        # 1. Starts with numbers
        if re.match(r'^\d+', local_part):
            raise forms.ValidationError(_("Email address should not start with numbers."))
            
        # 2. Domain with many digits
        domain_name = domain.split('.')[0] if '.' in domain else domain
        if sum(c.isdigit() for c in domain_name) > MAX_DOMAIN_DIGITS:
            raise forms.ValidationError(_("Suspicious email domain detected."))
            
        # 3. Short letters + many digits in local part
        letter_count = len(re.sub(r'\d', '', local_part))
        digit_count = sum(c.isdigit() for c in local_part)
        if letter_count <= MIN_LOCAL_PART_LETTERS and digit_count >= MIN_LOCAL_PART_DIGITS_FOR_SUSPICION:
            raise forms.ValidationError(_("Suspicious email pattern detected."))
            
        return email

    def clean_message(self):
        """Sanitize message and check for spam patterns."""
        message = self.cleaned_data.get('message', '')
        
        # Sanitize HTML/Script using bleach (converts to HTML entities)
        message = bleach.clean(message, tags=[], attributes={}, strip=False)
        
        # Spam detection
        for pattern in SPAM_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                raise forms.ValidationError(_("Message detected as spam."))

        # Check for excessive repetition
        words = message.split()
        if len(words) > 5:
            counts = Counter(w.lower() for w in words)
            most_common = counts.most_common(1)
            if most_common and most_common[0][1] > len(words) * MAX_WORD_REPETITION_RATIO:
                raise forms.ValidationError(_("Message seems to contain excessive repetition."))
                
        return message

    def clean_attachment(self):
        """Validate attachment file size."""
        file = self.cleaned_data.get('attachment')
        if file and file.size > MAX_CONTACT_FILE_SIZE_BYTES:
            raise forms.ValidationError(_("File size must be less than 5MB."))
        return file
    
    def clean(self):
        """Validate honeypot field - if filled, it's a bot."""
        cleaned_data = super().clean()
        
        # Honeypot check - if filled, reject submission
        website = cleaned_data.get('website')
        if website:
            raise forms.ValidationError(
                _("Invalid submission detected. Please try again.")
            )
        
        return cleaned_data



class KYMForm(forms.Form):
    """Know Your Member (KYM) form for member registration and verification."""
    
    # Personal Details
    full_name = forms.CharField(
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('As per your ID')
        }),
        label=_('Full Name'),
        help_text=_('Enter your full name as it appears on your citizenship/ID card')
    )
    
    dob = forms.DateField(
        widget=NepaliDateInput(attrs={
            'class': KYM_INPUT_CSS,
        }),
        label=_('Date of Birth')
    )
    
    gender = forms.ChoiceField(
        choices=[
            ('', _('Select Gender')),
            ('male', _('Male')),
            ('female', _('Female')),
            ('other', _('Other'))
        ],
        widget=forms.Select(attrs={'class': KYM_INPUT_CSS}),
        label=_('Gender')
    )
    
    marital_status = forms.ChoiceField(
        choices=[
            ('', _('Select Status')),
            ('single', _('Single')),
            ('married', _('Married')),
            ('divorced', _('Divorced')),
            ('widowed', _('Widowed'))
        ],
        widget=forms.Select(attrs={'class': KYM_INPUT_CSS}),
        label=_('Marital Status')
    )
    
    nationality = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('e.g., Nepali')
        }),
        label=_('Nationality'),
        initial='Nepali'
    )
    
    # Contact Information
    phone = forms.CharField(
        max_length=MAX_PHONE_LENGTH,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('+977-XXXXXXXXXX')
        }),
        label=_('Phone Number')
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('your.email@example.com')
        }),
        label=_('Email Address')
    )
    
    permanent_address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('Street, Village, Ward No.')
        }),
        label=_('Permanent Address')
    )
    
    district = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('e.g., Kaski')
        }),
        label=_('District'),
        initial='Kaski'
    )
    
    province = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('e.g., Gandaki Province')
        }),
        label=_('Province'),
        initial='Gandaki Province'
    )
    
    # Family Details
    father_name = forms.CharField(
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _("Father's Full Name")
        }),
        label=_("Father's Name")
    )
    
    mother_name = forms.CharField(
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _("Mother's Full Name")
        }),
        label=_("Mother's Name")
    )
    
    spouse_name = forms.CharField(
        max_length=MAX_NAME_LENGTH,
        required=False,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _("Spouse's Full Name")
        }),
        label=_("Spouse's Name (if married)")
    )
    
    grand_father_name = forms.CharField(
        max_length=MAX_NAME_LENGTH,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _("Grand Father's Full Name")
        }),
        label=_("Grand Father's Name")
    )
    
    nominee_name = forms.CharField(
        max_length=MAX_NAME_LENGTH,
        required=False,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('Full name of your nominee')
        }),
        label=_('Nominee Name (Optional)')
    )
    
    # Occupation & Income Details
    occupation = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('Your profession/business')
        }),
        label=_('Occupation')
    )
    
    income_source = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('e.g., Salary, Business, Agriculture')
        }),
        label=_('Source of Income')
    )
    
    estimated_income = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': KYM_INPUT_CSS,
            'placeholder': _('e.g., 500000')
        }),
        label=_('Estimated Annual Income (NPR)')
    )
    
    # Document Uploads
    citizenship_front = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': FORM_INPUT_CSS,
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label=_('Citizenship/ID Card (Front)'),
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_KYM_FILE_EXTENSIONS)]
    )
    
    citizenship_back = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': FORM_INPUT_CSS,
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label=_('Citizenship/ID Card (Back)'),
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_KYM_FILE_EXTENSIONS)]
    )
    
    passport_photo_upload = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': FORM_INPUT_CSS,
            'accept': '.jpg,.jpeg,.png'
        }),
        label=_('Passport-sized Photo'),
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_KYM_IMAGE_EXTENSIONS)]
    )
    
    address_proof_upload = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': FORM_INPUT_CSS,
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label=_('Address Proof (e.g., Utility Bill)'),
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_KYM_FILE_EXTENSIONS)]
    )
    
    income_proof_upload = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': FORM_INPUT_CSS,
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        label=_('Occupation/Income Proof (Optional)'),
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_KYM_FILE_EXTENSIONS)]
    )
    
    def clean(self):
        """Validate file sizes for all uploaded documents."""
        cleaned_data = super().clean()
        
        file_fields = [
            'citizenship_front', 'citizenship_back', 'passport_photo_upload',
            'address_proof_upload', 'income_proof_upload'
        ]
        
        for field in file_fields:
            file = cleaned_data.get(field)
            if file and file.size > MAX_CONTACT_FILE_SIZE_BYTES:
                field_label = field.replace('_', ' ').title()
                raise forms.ValidationError(_('{field_label} file size must be less than 5MB.').format(field_label=field_label))
        
        return cleaned_data
