from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

from .models import SavingsAccount, FixedDeposit, LoanType, ServiceApplication, RemittanceService, MemberRelief, DigitalService

# --- Base Widget Attributes for Brand Consistency ---

# Define common attributes for form inputs to ensure a consistent, professional look
# that matches the brand's aesthetic (deuraligreen focus color, rounded corners, etc.).
COMMON_INPUT_ATTRS = {
    'class': (
        'w-full px-4 py-3 bg-gray-50 rounded-lg border-2 border-gray-200 '
        'focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-deuraligreen '
        'focus:border-transparent transition-all duration-300 ease-in-out'
    )
}

COMMON_SELECT_ATTRS = COMMON_INPUT_ATTRS.copy()
COMMON_SELECT_ATTRS['class'] += ' appearance-none' # For custom dropdown arrows

# --- Calculator Forms ---

class LoanCalculatorForm(forms.Form):
    """
    Form for the Loan EMI Calculator.
    Uses ModelChoiceField to dynamically populate loan types from the database,
    ensuring the calculator is always in sync with active products.
    """
    loan_type = forms.ModelChoiceField(
        queryset=LoanType.objects.filter(is_active=True).order_by('english_name'),
        empty_label=_("Select a Loan Product"),
        label=_("Loan Product"),
        widget=forms.Select(attrs=COMMON_SELECT_ATTRS)
    )
    principal_amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=1000,
        label=_("Loan Amount (NPR)"),
        widget=forms.NumberInput(attrs={
            **COMMON_INPUT_ATTRS,
            'placeholder': _('e.g., 500000'),
            'step': '1000'
        })
    )
    tenure_years = forms.IntegerField(
        min_value=1, max_value=30,
        label=_("Loan Tenure (in Years)"),
        widget=forms.NumberInput(attrs={
            **COMMON_INPUT_ATTRS,
            'placeholder': _('e.g., 5')
        })
    )
    payment_frequency = forms.ChoiceField(
        choices=[('monthly', _('Monthly')), ('quarterly', _('Quarterly'))],
        label=_("Payment Frequency"),
        widget=forms.Select(attrs=COMMON_SELECT_ATTRS)
    )

    def clean(self):
        """Server-side validation to check loan amount against the selected loan type's limits."""
        cleaned_data = super().clean()
        loan_type = cleaned_data.get('loan_type')
        principal = cleaned_data.get('principal_amount')
        tenure = cleaned_data.get('tenure_years')

        if loan_type and principal:
            if loan_type.minimum_amount and principal < loan_type.minimum_amount:
                raise ValidationError(_(f"Minimum loan amount for this product is NPR {loan_type.minimum_amount:,.0f}."))
            if loan_type.maximum_amount and principal > loan_type.maximum_amount:
                raise ValidationError(_(f"Maximum loan amount for this product is NPR {loan_type.maximum_amount:,.0f}."))
        if loan_type and tenure:
            if loan_type.max_tenure_years and tenure > loan_type.max_tenure_years:
                raise ValidationError(_(f"Maximum tenure for this loan is {loan_type.max_tenure_years} years."))
        return cleaned_data

class SavingsCalculatorForm(forms.Form):
    """Form for the Savings Maturity Calculator."""
    savings_type = forms.ModelChoiceField(
        queryset=SavingsAccount.objects.filter(is_active=True).order_by('english_name'),
        empty_label=_("Select a Savings Product"),
        label=_("Savings Product"),
        widget=forms.Select(attrs=COMMON_SELECT_ATTRS)
    )
    monthly_deposit = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=100,
        label=_("Monthly Deposit (NPR)"),
        widget=forms.NumberInput(attrs={**COMMON_INPUT_ATTRS, 'placeholder': _('e.g., 10000')})
    )
    tenure_years = forms.IntegerField(
        min_value=1, max_value=40,
        label=_("Savings Period (in Years)"),
        widget=forms.NumberInput(attrs={**COMMON_INPUT_ATTRS, 'placeholder': _('e.g., 10')})
    )

class FixedDepositCalculatorForm(forms.Form):
    """Form for the Fixed Deposit Maturity Calculator."""
    deposit_type = forms.ModelChoiceField(
        queryset=FixedDeposit.objects.filter(is_active=True).order_by('duration_months'),
        empty_label=_("Select a Deposit Scheme"),
        label=_("Fixed Deposit Scheme"),
        widget=forms.Select(attrs=COMMON_SELECT_ATTRS)
    )
    deposit_amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=1000,
        label=_("Deposit Amount (NPR)"),
        widget=forms.NumberInput(attrs={**COMMON_INPUT_ATTRS, 'placeholder': _('e.g., 100000')})
    )

    def clean(self):
        """Server-side validation for deposit amount against scheme limits."""
        cleaned_data = super().clean()
        deposit_type = cleaned_data.get('deposit_type')
        deposit_amount = cleaned_data.get('deposit_amount')
        
        if deposit_type and deposit_amount:
            if deposit_type.minimum_amount and deposit_amount < deposit_type.minimum_amount:
                raise ValidationError(_(f"Minimum deposit is NPR {deposit_type.minimum_amount:,.0f}."))
            if deposit_type.maximum_amount and deposit_amount > deposit_type.maximum_amount:
                raise ValidationError(_(f"Maximum deposit is NPR {deposit_type.maximum_amount:,.0f}."))
        return cleaned_data

# --- Core Service Interaction Forms ---

class ServiceApplicationForm(forms.ModelForm):
    """
    UPGRADED: Refactored to a ModelForm for direct integration with the ServiceApplication model.
    This simplifies the view, improves security, and makes the form more maintainable.
    """
    terms_accepted = forms.BooleanField(
        required=True,
        label=_("I agree to the Terms and Conditions and Privacy Policy."),
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-deuraligreen focus:ring-deuraligreen'})
    )

    class Meta:
        model = ServiceApplication
        fields = [
            'applicant_name', 'applicant_email', 
            'applicant_phone', 'applicant_address', 'additional_info'
        ]
        widgets = {
            'applicant_name': forms.TextInput(attrs={**COMMON_INPUT_ATTRS, 'placeholder': _('Your Full Name')}),
            'applicant_email': forms.EmailInput(attrs={**COMMON_INPUT_ATTRS, 'placeholder': _('your.email@example.com')}),
            'applicant_phone': forms.TextInput(attrs={**COMMON_INPUT_ATTRS, 'placeholder': _('+977-98XXXXXXXX')}),
            'applicant_address': forms.Textarea(attrs={**COMMON_INPUT_ATTRS, 'rows': 3, 'placeholder': _('Your Full Address')}),
            'additional_info': forms.Textarea(attrs={**COMMON_INPUT_ATTRS, 'rows': 4, 'placeholder': _('Optional: Any additional details...')}),
        }

    service_type = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    service_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        self.service_object = kwargs.pop('service_object', None)
        initial = kwargs.get('initial', {})
        
        # Pre-fill service_type and service_id if service_object is provided
        if self.service_object:
            # Determine service type from the object
            if isinstance(self.service_object, SavingsAccount):
                initial['service_type'] = 'savings'
            elif isinstance(self.service_object, LoanType):
                initial['service_type'] = 'loan'
            elif isinstance(self.service_object, FixedDeposit):
                initial['service_type'] = 'fixed_deposit'
            elif isinstance(self.service_object, RemittanceService):
                initial['service_type'] = 'remittance'
            elif isinstance(self.service_object, MemberRelief):
                initial['service_type'] = 'relief'
            elif isinstance(self.service_object, DigitalService):
                initial['service_type'] = 'digital'
            
            initial['service_id'] = str(self.service_object.id)
            kwargs['initial'] = initial
        
        super().__init__(*args, **kwargs)

    def clean_applicant_phone(self):
        """Validates the phone number to match a common Nepali format."""
        phone = self.cleaned_data.get('applicant_phone')
        if phone and not re.match(r'^\+?977-?[9][678]\d{8}$', phone):
            raise ValidationError(_("Please enter a valid Nepali mobile number, e.g., +977-98..."))
        return phone

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.service_object:
            instance.service_object = self.service_object
        if commit:
            instance.save()
        return instance

class ServiceComparisonForm(forms.Form):
    """
    Form for comparing different services, with dynamic choices and validation.
    """
    service_type = forms.ChoiceField(
        choices=[
            ('', _('Select Service Type')),
            ('savings', _('Savings Accounts')),
            ('loans', _('Loan Services')),
            ('fixed_deposits', _('Fixed Deposits')),
        ],
        label=_("Service Type"),
        widget=forms.Select(attrs={**COMMON_SELECT_ATTRS, 'id': 'comparison-service-type'})
    )
    services = forms.MultipleChoiceField(
        label=_("Select Services to Compare"),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        """Dynamically populates the 'services' choices based on the selected 'service_type'."""
        super().__init__(*args, **kwargs)
        # If the form is bound, 'data' will be present
        service_type = self.data.get('service_type') if self.is_bound else None
        
        if service_type:
            choices = []
            if service_type == 'savings':
                choices = [(s.id, s.english_name) for s in SavingsAccount.objects.filter(is_active=True)]
            elif service_type == 'loans':
                choices = [(s.id, s.english_name) for s in LoanType.objects.filter(is_active=True)]
            elif service_type == 'fixed_deposits':
                choices = [(s.id, f"{s.get_duration_months_display()} - {s.get_payment_frequency_display()}") 
                           for s in FixedDeposit.objects.filter(is_active=True)]
            self.fields['services'].choices = choices

    def clean_services(self):
        """Ensures the user selects between 2 and 4 services to compare."""
        services = self.cleaned_data.get('services')
        if services and not 2 <= len(services) <= 4:
            raise ValidationError(_("Please select between 2 and 4 services to compare."))
        return services

class ServiceSearchForm(forms.Form):
    """Comprehensive form for filtering and searching all financial services."""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            **COMMON_INPUT_ATTRS, 
            'placeholder': _('Search by name or keyword...')
        })
    )
    service_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All Service Types')),
            ('savings', _('Savings Accounts')),
            ('loans', _('Loan Services')),
            ('fixed_deposits', _('Fixed Deposits')),
        ],
        widget=forms.Select(attrs=COMMON_SELECT_ATTRS)
    )
    interest_rate_min = forms.DecimalField(
        required=False, max_digits=4, decimal_places=2,
        widget=forms.NumberInput(attrs={**COMMON_INPUT_ATTRS, 'placeholder': _('Min Rate (%)'), 'step': '0.1'})
    )
    featured_only = forms.BooleanField(
        required=False,
        label=_("Show Featured Only"),
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-deuraligreen focus:ring-deuraligreen'})
    )

class ServiceRecommendationForm(forms.Form):
    """
    NEW: A dedicated form for the service recommendation engine.
    This replaces raw request.POST handling in the view, adding structure and validation.
    """
    age = forms.IntegerField(
        min_value=18, max_value=100, label=_("Your Age"),
        widget=forms.NumberInput(attrs={**COMMON_INPUT_ATTRS, 'placeholder': _('e.g., 35')})
    )
    monthly_income = forms.IntegerField(
        min_value=0, label=_("Your Monthly Income (NPR)"),
        widget=forms.NumberInput(attrs={**COMMON_INPUT_ATTRS, 'placeholder': _('e.g., 75000')})
    )
    goals = forms.MultipleChoiceField(
        label=_("What are your financial goals? (Select multiple)"),
        choices=[
            ('house_purchase', _('Buy a House or Land')),
            ('education', _('Fund Education')),
            ('business', _('Start or Grow a Business')),
            ('vehicle', _('Purchase a Vehicle')),
            ('retirement', _('Save for Retirement')),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    risk_tolerance = forms.ChoiceField(
        label=_("Your Risk Tolerance"),
        choices=[
            ('conservative', _('Conservative (I prefer guaranteed returns)')),
            ('moderate', _('Moderate (I can take some risk for better returns)')),
            ('aggressive', _('Aggressive (I aim for high growth, even with higher risk)')),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
