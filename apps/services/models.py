from typing import Optional, Dict, Any, List
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# --- Abstract Base Models for Reusability ---

class BaseServiceModel(models.Model):
    """
    An abstract base model providing common fields for all financial services,
    including SEO-friendly slugs, icons, status tracking, and timestamps.
    """
    english_name = models.CharField(max_length=100, verbose_name=_("English Name"))
    nepali_name = models.CharField(max_length=100, verbose_name=_("Nepali Name"))
    slug = models.SlugField(max_length=120, unique=True, blank=True, help_text=_("A unique, URL-friendly identifier. Auto-generated if left blank."))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon Class (e.g., 'fas fa-piggy-bank')"))
    color = models.CharField(max_length=20, default='deuraligreen', verbose_name=_("Color Theme"), help_text=_("Tailwind CSS color name for branding."))
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured Product"), help_text=_("Featured products appear prominently on the site."))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"), help_text=_("Only active services are visible to users."))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-is_featured', 'english_name']

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Overrides the save method to automatically generate a slug if one doesn't exist."""
        if not self.slug:
            # slugify() drops non-ASCII, so a Devanagari-only english_name (or a
            # blank one) yields ''. An empty slug is not just cosmetic: every
            # listing template links with {% url '..._detail' obj.slug %}, and
            # reverse() with an empty argument raises NoReverseMatch, taking the
            # whole page down with a 500. Fall back until we have something.
            base_slug = (
                slugify(self.english_name)
                or slugify(self.english_name, allow_unicode=True)
                or slugify(self.nepali_name, allow_unicode=True)
                or self.__class__.__name__.lower()
            )
            self.slug = base_slug

            # Ensure uniqueness by appending id or a counter
            # Get the model class to check for existing slugs
            model_class = self.__class__
            counter = 1
            while model_class.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
                # Safety check to prevent infinite loop
                if counter > 1000:
                    # Fallback: use id if available, otherwise timestamp
                    if self.pk:
                        self.slug = f"{base_slug}-{self.pk}"
                    else:
                        from django.utils import timezone
                        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
                        self.slug = f"{base_slug}-{timestamp}"
                    break
        super().save(*args, **kwargs)

# --- Core Service Models ---

class SavingsAccount(BaseServiceModel):
    """Model for different types of savings accounts offered."""
    SAVING_CATEGORIES = [
        ('regular', _('Regular Savings (नियमित बचत)')),
        ('optional', _('Optional Savings (एच्छिक बचत)')),
        ('recurring', _('Recurring Savings (क्रमिक बचत)')),
    ]
    
    ACCOUNT_TYPES = [
        ('general', _('General Savings')), ('daily', _('Daily Savings')),
        ('institutional', _('Institutional Savings')), ('child', _('Child Savings')),
        ('senior_citizen', _('Senior Citizen Savings')), ('remit', _('Remit Savings')),
        ('insurance', _('Insurance Savings')), ('monthly', _('Monthly Savings')),
        ('regular_saving', _('Regular Savings')), ('recurring_saving', _('Recurring Savings')),
    ]
    
    category = models.CharField(max_length=20, choices=SAVING_CATEGORIES, default='optional', verbose_name=_("Category"))
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, unique=True, verbose_name=_("Account Type"))
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)],
        verbose_name=_("Interest Rate (%)"), help_text=_("Annual interest rate.")
    )
    minimum_balance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)],
        verbose_name=_("Minimum Balance (NPR)"), help_text=_("Required minimum balance to maintain.")
    )
    features = models.TextField(blank=True, verbose_name=_("Key Features"), help_text=_("List key features, one per line."))

    class Meta:
        verbose_name = _("Savings Account")
        verbose_name_plural = _("Savings Accounts")
        ordering = ['-is_featured', '-interest_rate']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['interest_rate']),
            models.Index(fields=['account_type', 'is_active']),  # For filtering by account type
            models.Index(fields=['slug']),  # For URL lookups
            models.Index(fields=['english_name']),  # For search
            models.Index(fields=['created_at']),  # For date-based queries
            models.Index(fields=['updated_at']),  # For date-based queries
        ]

    def __str__(self):
        return f"{self.english_name} ({self.interest_rate}%)"

    def get_absolute_url(self) -> str:
        return reverse('services:savings_detail', kwargs={'slug': self.slug})

class FixedDeposit(BaseServiceModel):
    """Model for fixed deposit schemes with various terms and rates."""
    DURATION_CHOICES = [(3, _('3 Months')), (6, _('6 Months')), (12, _('1 Year')), (24, _('2 Years')), (36, _('3 Years'))]
    PAYMENT_CHOICES = [('monthly', _('Monthly Payout')), ('quarterly', _('Quarterly Payout')), ('lump_sum', _('Maturity Payout'))]
    
    duration_months = models.IntegerField(choices=DURATION_CHOICES, verbose_name=_("Duration"))
    payment_frequency = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name=_("Interest Payout"))
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_("Interest Rate (%)"))
    minimum_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_("Minimum Amount (NPR)"))
    maximum_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name=_("Maximum Amount (NPR)"))
    benefits = models.TextField(blank=True, verbose_name=_("Benefits"), help_text=_("List key benefits, one per line."))
    # is_active, created_at, updated_at are inherited from BaseServiceModel

    class Meta:
        verbose_name = _("Fixed Deposit")
        verbose_name_plural = _("Fixed Deposits")
        unique_together = ['duration_months', 'payment_frequency']
        ordering = ['duration_months', 'interest_rate']
        indexes = [
            models.Index(fields=['is_active', 'duration_months']),
            models.Index(fields=['interest_rate']),
            models.Index(fields=['created_at']),
            models.Index(fields=['payment_frequency', 'is_active']),  # For filtering by payment frequency
            models.Index(fields=['duration_months', 'payment_frequency']),  # For unique lookup optimization
            models.Index(fields=['updated_at']),  # For date-based queries
        ]

    def __str__(self):
        return f"{self.get_duration_months_display()} - {self.get_payment_frequency_display()} ({self.interest_rate}%)"

class LoanType(BaseServiceModel):
    """Model for different types of loans available to members."""
    LOAN_CATEGORIES = [
        ('business', _('Business Loan')), ('agricultural', _('Agricultural Loan')),
        ('vehicle', _('Vehicle Loan')), ('foreign_employment', _('Foreign Employment Loan')),
        ('household', _('Household Loan')), ('house_construction', _('House Construction Loan')),
        ('home', _('Home Loan')), ('land_purchase', _('Land Purchase Loan')),
        ('education', _('Education Loan')), ('personal', _('Personal Loan')),
    ]
    
    REPAYMENT_TYPES = [
        ('monthly', _('Monthly (मासिक)')),
        ('quarterly', _('Quarterly (त्रैमासिक)')),
        ('seasonal', _('Seasonal (मौसमी)')),
    ]
    
    loan_category = models.CharField(max_length=30, choices=LOAN_CATEGORIES, unique=True, verbose_name=_("Loan Category"))
    monthly_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], 
        verbose_name=_("Monthly Interest Rate (%)"),
        help_text=_("Monthly interest rate. Annual rate = Monthly rate × 12.")
    )
    repayment_type = models.CharField(
        max_length=20, choices=REPAYMENT_TYPES, default='monthly',
        verbose_name=_("Repayment Type"),
        help_text=_("Frequency of loan repayment. Seasonal is typically used for agricultural loans.")
    )
    minimum_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name=_("Minimum Loan Amount (NPR)"))
    maximum_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name=_("Maximum Loan Amount (NPR)"))
    max_tenure_years = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Maximum Tenure (Years)"))
    requirements = models.TextField(blank=True, verbose_name=_("Requirements"), help_text=_("List required documents, one per line."))
    benefits = models.TextField(blank=True, verbose_name=_("Benefits"), help_text=_("List key benefits, one per line."))
    image = models.ImageField(upload_to='services/loans/', null=True, blank=True, verbose_name=_("Image"))

    class Meta:
        verbose_name = _("Loan Type")
        verbose_name_plural = _("Loan Types")
        ordering = ['-is_featured', 'english_name']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['loan_category', 'is_active']),
            models.Index(fields=['monthly_interest_rate']),
            models.Index(fields=['slug']),
            models.Index(fields=['english_name']),  # For search
            models.Index(fields=['nepali_name']),  # For search
            models.Index(fields=['created_at']),  # For date-based queries
            models.Index(fields=['updated_at']),  # For date-based queries
        ]

    def __str__(self):
        return self.english_name

    def get_absolute_url(self):
        return reverse('services:loan_detail', kwargs={'slug': self.slug})

    @property
    def annual_interest_rate(self):
        """Calculates and returns the approximate annual interest rate."""
        return self.monthly_interest_rate * 12 if self.monthly_interest_rate else 0
    
    def has_active_carousel_images(self):
        """Check if loan has any active carousel images."""
        return self.carousel_images.filter(is_active=True).exists()

class LoanCarouselImage(models.Model):
    """Model for carousel images for loan types."""
    loan = models.ForeignKey(
        LoanType, 
        on_delete=models.CASCADE, 
        related_name='carousel_images',
        verbose_name=_("Loan Type")
    )
    image = models.ImageField(
        upload_to='services/loans/carousel/', 
        verbose_name=_("Carousel Image"),
        help_text=_("Upload image for carousel slide. Recommended size: 1920x1080px")
    )
    nepali_tagline = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name=_("Nepali Tagline"),
        help_text=_("Main Nepali tagline for this slide")
    )
    english_tagline = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name=_("English Tagline"),
        help_text=_("Main English tagline for this slide")
    )
    nepali_subtitle = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name=_("Nepali Subtitle"),
        help_text=_("Nepali subtitle/description for this slide")
    )
    english_subtitle = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name=_("English Subtitle"),
        help_text=_("English subtitle/description for this slide")
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name=_("Display Order"),
        help_text=_("Order in which this image appears in the carousel (lower numbers appear first)")
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name=_("Active"),
        help_text=_("Only active images are displayed in the carousel")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Loan Carousel Image")
        verbose_name_plural = _("Loan Carousel Images")
        ordering = ['loan', 'order', 'created_at']
        indexes = [
            models.Index(fields=['loan', 'is_active', 'order']),
            models.Index(fields=['loan', 'order']),
        ]

    def __str__(self):
        return f"{self.loan.english_name} - Slide {self.order + 1}"

class RemittanceService(BaseServiceModel):
    """Model for remittance and money transfer services."""
    SERVICE_TYPES = [
        ('domestic', _('Domestic Transfer')), ('international', _('International Remittance')),
        ('mobile_banking', _('Mobile Banking Transfer')),
    ]
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name=_("Service Type"))
    processing_time = models.CharField(max_length=100, blank=True, verbose_name=_("Processing Time"), help_text=_("e.g., 'Instant' or '1-2 business days'"))
    fees = models.TextField(blank=True, verbose_name=_("Fees & Charges"))

    class Meta:
        verbose_name = _("Remittance Service")
        verbose_name_plural = _("Remittance Services")
        ordering = ['english_name']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['service_type', 'is_active']),
            models.Index(fields=['slug']),
            models.Index(fields=['english_name']),  # For search
            models.Index(fields=['nepali_name']),  # For search
            models.Index(fields=['created_at']),  # For date-based queries
            models.Index(fields=['updated_at']),  # For date-based queries
        ]

    def __str__(self):
        return self.english_name

    def get_absolute_url(self):
        return reverse('services:remittance_detail', kwargs={'slug': self.slug})

    # Helper methods for template logic
    def is_himalremit(self):
        """Check if this service is HimalRemit/CFS."""
        name_lower = self.english_name.lower()
        return 'himal' in name_lower or 'himalremit' in name_lower or 'cfs' in name_lower

    def is_city_express(self):
        """Check if this service is City Express."""
        return 'city express' in self.english_name.lower()

    def is_ime(self):
        """Check if this service is IME."""
        return 'ime' in self.english_name.lower()

    def get_brand_color(self):
        """Get the brand color theme for this service."""
        if self.is_himalremit():
            return 'blue'
        elif self.is_city_express():
            return 'blue'
        elif self.is_ime():
            return 'red'
        return self.color or 'green'

    def get_brand_gradient(self):
        """Get the gradient classes for this service."""
        if self.is_himalremit():
            return 'from-blue-900 to-blue-800'
        elif self.is_city_express():
            return 'from-blue-900 to-blue-800'
        elif self.is_ime():
            return 'from-red-700 to-red-600'
        return 'from-deuraligreen to-green-800'

    def get_logo_path(self):
        """Get the static path to the service logo."""
        if self.is_himalremit():
            return 'images/remit_logos/himalremit.png'
        elif self.is_city_express():
            return 'images/remit_logos/cityexpress.jpg'
        elif self.is_ime():
            return 'images/remit_logos/ime.png'
        return None


class RemittanceCharge(models.Model):
    """Model for remittance service charges by country."""
    service = models.ForeignKey(
        RemittanceService,
        on_delete=models.CASCADE,
        related_name='charges',
        verbose_name=_("Remittance Service")
    )
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    charge = models.CharField(max_length=100, verbose_name=_("Charge"), help_text=_("e.g., 'US Dollar - 3.99'"))
    currency = models.CharField(max_length=10, blank=True, verbose_name=_("Currency Code"))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))
    
    class Meta:
        verbose_name = _("Remittance Charge")
        verbose_name_plural = _("Remittance Charges")
        ordering = ['service', 'display_order', 'country']
        indexes = [
            models.Index(fields=['service', 'display_order']),
            models.Index(fields=['country']),
        ]

    def __str__(self):
        return f"{self.service.english_name} - {self.country}: {self.charge}"


class ExchangeRate(models.Model):
    """Model for storing foreign exchange rates, primarily from NRB."""
    CURRENCY_CHOICES = [
        ('USD', _('US Dollar')), ('EUR', _('Euro')), ('GBP', _('British Pound')),
        ('AUD', _('Australian Dollar')), ('CAD', _('Canadian Dollar')),
        ('JPY', _('Japanese Yen')), ('CHF', _('Swiss Franc')),
        ('CNY', _('Chinese Yuan')), ('INR', _('Indian Rupee')),
        ('AED', _('UAE Dirham')), ('SAR', _('Saudi Riyal')),
        ('QAR', _('Qatari Riyal')), ('KWD', _('Kuwaiti Dinar')),
        ('BHD', _('Bahraini Dinar')), ('OMR', _('Omani Rial')),
        ('SGD', _('Singapore Dollar')), ('MYR', _('Malaysian Ringgit')),
        ('THB', _('Thai Baht')), ('HKD', _('Hong Kong Dollar')),
    ]
    
    currency_code = models.CharField(
        max_length=3, 
        choices=CURRENCY_CHOICES, 
        verbose_name=_("Currency Code"),
        help_text=_("ISO 4217 currency code")
    )
    buy_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        verbose_name=_("Buy Rate (NPR)"),
        help_text=_("Rate at which bank buys foreign currency")
    )
    sell_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        verbose_name=_("Sell Rate (NPR)"),
        help_text=_("Rate at which bank sells foreign currency")
    )
    mid_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        verbose_name=_("Mid Rate (NPR)"),
        help_text=_("Average of buy and sell rate")
    )
    rate_date = models.DateField(
        verbose_name=_("Rate Date"),
        help_text=_("Date for which this rate is valid")
    )
    source = models.CharField(
        max_length=50, 
        default='NRB',
        verbose_name=_("Source"),
        help_text=_("Source of exchange rate (e.g., NRB, Manual)")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Only active rates are used in calculations")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Additional notes or remarks")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Exchange Rate")
        verbose_name_plural = _("Exchange Rates")
        ordering = ['-rate_date', 'currency_code']
        unique_together = [['currency_code', 'rate_date']]
        indexes = [
            models.Index(fields=['currency_code', 'rate_date']),
            models.Index(fields=['is_active', 'rate_date']),
            models.Index(fields=['rate_date']),
        ]

    def __str__(self):
        return f"{self.currency_code} - {self.rate_date} (Buy: {self.buy_rate}, Sell: {self.sell_rate})"

    def save(self, *args, **kwargs):
        """Calculate mid_rate from buy_rate and sell_rate."""
        # Always recalculate mid_rate to ensure accuracy
        self.mid_rate = (self.buy_rate + self.sell_rate) / 2
        super().save(*args, **kwargs)

    @classmethod
    def get_latest_rate(cls, currency_code: str, date=None):
        """Get the latest exchange rate for a currency."""
        queryset = cls.objects.filter(
            currency_code=currency_code,
            is_active=True
        )
        if date:
            queryset = queryset.filter(rate_date__lte=date)
        return queryset.order_by('-rate_date').first()

    @classmethod
    def get_latest_rates(cls, date=None):
        """Get all latest exchange rates for all currencies."""
        from django.utils import timezone
        
        if date is None:
            date = timezone.now().date()
        
        # Get the latest rate for each currency
        latest_rates = {}
        for currency_code, _ in cls.CURRENCY_CHOICES:
            rate = cls.get_latest_rate(currency_code, date)
            if rate:
                latest_rates[currency_code] = rate
        return latest_rates


class MemberRelief(BaseServiceModel):
    """Model for member relief and social support programs."""
    RELIEF_TYPES = [
        ('medical', _('Medical Relief')), ('education', _('Educational Support')),
        ('disaster', _('Disaster Relief')), ('welfare', _('Welfare Support')),
    ]
    relief_type = models.CharField(max_length=20, choices=RELIEF_TYPES, verbose_name=_("Relief Type"))
    eligibility = models.TextField(verbose_name=_("Eligibility Criteria"))
    benefits = models.TextField(verbose_name=_("Benefits & Support"))
    application_process = models.TextField(blank=True, verbose_name=_("Application Process"))
    image = models.ImageField(upload_to='services/relief/', null=True, blank=True, verbose_name=_("Image"))

    class Meta:
        verbose_name = _("Member Relief Program")
        verbose_name_plural = _("Member Relief Programs")
        ordering = ['english_name']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['relief_type', 'is_active']),
            models.Index(fields=['slug']),
            models.Index(fields=['english_name']),  # For search
            models.Index(fields=['nepali_name']),  # For search
            models.Index(fields=['created_at']),  # For date-based queries
            models.Index(fields=['updated_at']),  # For date-based queries
        ]

    def __str__(self):
        return self.english_name

    def get_absolute_url(self):
        return reverse('services:relief_detail', kwargs={'slug': self.slug})

class DigitalService(BaseServiceModel):
    """Model for digital services like mobile banking, online banking, etc."""
    SERVICE_TYPES = [
        ('mobile_banking', _('Mobile Banking')), ('online_banking', _('Online Banking')),
        ('atm_card', _('ATM Card')), ('debit_card', _('Debit Card')),
        ('credit_card', _('Credit Card')), ('e_wallet', _('E-Wallet')),
        ('qr_payment', _('QR Payment')), ('sms_banking', _('SMS Banking')),
    ]
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name=_("Service Type"))
    features = models.TextField(blank=True, verbose_name=_("Key Features"), help_text=_("List key features, one per line."))
    requirements = models.TextField(blank=True, verbose_name=_("Requirements"), help_text=_("List requirements, one per line."))
    fees = models.TextField(blank=True, verbose_name=_("Fees & Charges"))
    image = models.ImageField(upload_to='services/digital/', null=True, blank=True, verbose_name=_("Image"))

    class Meta:
        verbose_name = _("Digital Service")
        verbose_name_plural = _("Digital Services")
        ordering = ['english_name']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['service_type', 'is_active']),
            models.Index(fields=['slug']),
            models.Index(fields=['english_name']),  # For search
            models.Index(fields=['nepali_name']),  # For search
            models.Index(fields=['created_at']),  # For date-based queries
            models.Index(fields=['updated_at']),  # For date-based queries
        ]

    def __str__(self):
        return self.english_name

    def get_absolute_url(self):
        return reverse('services:digital_detail', kwargs={'slug': self.slug})

# --- Tracking & Analytics Models ---

class ServiceApplication(models.Model):
    """
    Model for tracking member applications for any service.
    UPGRADED: Uses GenericForeignKey to create a robust link to any service model.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')), ('under_review', _('Under Review')),
        ('approved', _('Approved')), ('rejected', _('Rejected')),
    ]
    
    # GenericForeignKey fields to link to any service model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_("Service Type"))
    object_id = models.PositiveIntegerField(verbose_name=_("Service ID"))
    service_object = GenericForeignKey('content_type', 'object_id')

    applicant_name = models.CharField(max_length=100, verbose_name=_("Applicant Name"))
    applicant_email = models.EmailField(verbose_name=_("Email"))
    applicant_phone = models.CharField(max_length=20, verbose_name=_("Phone"))
    applicant_address = models.TextField(verbose_name=_("Address"))
    additional_info = models.TextField(blank=True, verbose_name=_("Additional Information"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    applied_date = models.DateTimeField(auto_now_add=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.CharField(max_length=100, blank=True, verbose_name=_("Reviewed By"))
    notes = models.TextField(blank=True, verbose_name=_("Review Notes"))

    class Meta:
        verbose_name = _("Service Application")
        verbose_name_plural = _("Service Applications")
        ordering = ['-applied_date']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['status']),
            models.Index(fields=['status', 'applied_date']),  # For filtering by status and date
            models.Index(fields=['applied_date']),  # For date-based queries
            models.Index(fields=['applicant_email']),  # For email lookups
            models.Index(fields=['applicant_phone']),  # For phone lookups
        ]

    def __str__(self):
        return f"Application from {self.applicant_name} for {self.service_name}"
    
    @property
    def service_name(self):
        """Returns the English name of the linked service object."""
        return self.service_object.english_name if self.service_object else _("N/A")

class ServiceAnalytics(models.Model):
    """Read-only model for tracking daily analytics for each service."""
    # GenericForeignKey to link to any service model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    service_object = GenericForeignKey('content_type', 'object_id')

    date = models.DateField(verbose_name=_("Date"))
    page_views = models.PositiveIntegerField(default=0)
    applications_received = models.PositiveIntegerField(default=0)
    calculator_usage = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _("Service Analytics")
        verbose_name_plural = _("Service Analytics")
        unique_together = ['content_type', 'object_id', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['content_type', 'object_id', 'date']),  # For unique lookup optimization
            models.Index(fields=['date']),  # For date-based queries
            models.Index(fields=['content_type', 'object_id']),  # For service-specific queries
        ]

    def __str__(self):
        return f"Analytics for {self.service_object} on {self.date}"

class ServiceRecommendation(models.Model):
    """Model for service recommendations"""
    
    user_profile = models.JSONField(default=dict, verbose_name=_("User Profile"))
    recommended_services = models.JSONField(default=list, verbose_name=_("Recommended Services"))
    recommendation_reason = models.TextField(verbose_name=_("Recommendation Reason"))
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name=_("Confidence Score")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Service Recommendation")
        verbose_name_plural = _("Service Recommendations")
        ordering = ['-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['confidence_score', 'created_at']),  # For ordering optimization
            models.Index(fields=['created_at']),  # For date-based queries
        ]
    
    def __str__(self):
        return f"Recommendation ({self.confidence_score}% confidence)"
