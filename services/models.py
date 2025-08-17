from django.db import models
from django.utils.translation import gettext_lazy as _


class SavingsAccount(models.Model):
    """Model for different types of savings accounts"""
    
    ACCOUNT_TYPES = [
        ('general', 'साधारण बचत (General Savings)'),
        ('daily', 'दैनिक बचत (Daily Savings)'),
        ('institutional', 'संस्थागत बचत (Institutional Savings)'),
        ('child', 'बाल बचत (Child Savings)'),
        ('senior_citizen', 'जेष्ठ नागरिक बचत (Senior Citizen Savings)'),
        ('remit', 'रेमिट बचत (Remit Savings)'),
        ('insurance', 'बिमा बचत (Insurance Savings)'),
        ('monthly', 'मासिक बचत (Monthly Savings)'),
    ]
    
    account_type = models.CharField(
        max_length=20, 
        choices=ACCOUNT_TYPES, 
        unique=True,
        verbose_name=_("Account Type")
    )
    nepali_name = models.CharField(max_length=100, verbose_name=_("Nepali Name"))
    english_name = models.CharField(max_length=100, verbose_name=_("English Name"))
    interest_rate = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        verbose_name=_("Interest Rate (%)")
    )
    minimum_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_("Minimum Balance (NPR)")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    features = models.TextField(blank=True, verbose_name=_("Key Features"))
    icon = models.CharField(
        max_length=50,
        default='fas fa-piggy-bank',
        verbose_name=_("Icon Class (FontAwesome)")
    )
    color = models.CharField(
        max_length=20,
        default='deuraligreen',
        verbose_name=_("Color Theme")
    )
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured Product"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Savings Account")
        verbose_name_plural = _("Savings Accounts")
        ordering = ['-is_featured', 'interest_rate', 'account_type']
    
    def __str__(self):
        return f"{self.english_name} ({self.interest_rate}%)"


class FixedDeposit(models.Model):
    """Model for fixed deposit accounts with different durations and payment options"""
    
    DURATION_CHOICES = [
        (3, '3 Months'),
        (6, '6 Months'),
        (9, '9 Months'),
        (12, '1 Year'),
        (24, '2 Years'),
        (36, '3 Years'),
    ]
    
    PAYMENT_FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('lump_sum', 'Lump Sum'),
    ]
    
    duration_months = models.IntegerField(
        choices=DURATION_CHOICES,
        verbose_name=_("Duration (Months)")
    )
    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCY_CHOICES,
        verbose_name=_("Payment Frequency")
    )
    interest_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_("Interest Rate (%)")
    )
    minimum_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Minimum Amount (NPR)")
    )
    maximum_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Maximum Amount (NPR)")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    benefits = models.TextField(blank=True, verbose_name=_("Benefits"))
    icon = models.CharField(
        max_length=50,
        default='fas fa-certificate',
        verbose_name=_("Icon Class (FontAwesome)")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Fixed Deposit")
        verbose_name_plural = _("Fixed Deposits")
        unique_together = ['duration_months', 'payment_frequency']
        ordering = ['duration_months', 'payment_frequency']
    
    def __str__(self):
        return f"{self.get_duration_months_display()} - {self.get_payment_frequency_display()} ({self.interest_rate}%)"


class LoanType(models.Model):
    """Model for different types of loans"""
    
    LOAN_CATEGORIES = [
        ('business', 'व्यवसाय ऋण (Business Loan)'),
        ('agricultural', 'कृषि ऋण (Agricultural Loan)'),
        ('vehicle', 'सवारी खरिद ऋण (Vehicle Purchase Loan)'),
        ('foreign_employment', 'बैदेशिक रोजगार ऋण (Foreign Employment Loan)'),
        ('household', 'घरायसि ऋण (Household Loan)'),
        ('house_construction', 'घर निर्माण ऋण (House Construction Loan)'),
        ('land_purchase', 'जग्गा खरिद ऋण (Land Purchase Loan)'),
        ('education', 'शिक्षा ऋण (Education Loan)'),
        ('personal', 'व्यक्तिगत ऋण (Personal Loan)'),
    ]
    
    loan_category = models.CharField(
        max_length=30,
        choices=LOAN_CATEGORIES,
        unique=True,
        verbose_name=_("Loan Category")
    )
    nepali_name = models.CharField(max_length=100, verbose_name=_("Nepali Name"))
    english_name = models.CharField(max_length=100, verbose_name=_("English Name"))
    monthly_installment_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_("Monthly Installment Rate (%)")
    )
    quarterly_installment_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_("Quarterly Installment Rate (%)")
    )
    monthly_interest_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_("Monthly Interest Rate (%)")
    )
    minimum_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Minimum Loan Amount (NPR)")
    )
    maximum_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Maximum Loan Amount (NPR)")
    )
    max_tenure_years = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Maximum Tenure (Years)")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    requirements = models.TextField(blank=True, verbose_name=_("Requirements"))
    benefits = models.TextField(blank=True, verbose_name=_("Benefits"))
    icon = models.CharField(
        max_length=50,
        default='fas fa-hand-holding-usd',
        verbose_name=_("Icon Class (FontAwesome)")
    )
    color = models.CharField(
        max_length=20,
        default='bhanjyangred',
        verbose_name=_("Color Theme")
    )
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured Product"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Loan Type")
        verbose_name_plural = _("Loan Types")
        ordering = ['-is_featured', 'loan_category']
    
    def __str__(self):
        return f"{self.english_name}"


class RemittanceService(models.Model):
    """Model for remittance services"""
    
    SERVICE_TYPES = [
        ('domestic', 'Domestic Transfers'),
        ('international', 'International Remittance'),
        ('mobile_banking', 'Mobile Banking'),
    ]
    
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPES,
        unique=True,
        verbose_name=_("Service Type")
    )
    name = models.CharField(max_length=100, verbose_name=_("Service Name"))
    description = models.TextField(verbose_name=_("Description"))
    features = models.TextField(blank=True, verbose_name=_("Features"))
    transfer_limit_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Minimum Transfer Amount (NPR)")
    )
    transfer_limit_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Maximum Transfer Amount (NPR)")
    )
    processing_time = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Processing Time")
    )
    fees = models.TextField(blank=True, verbose_name=_("Fees & Charges"))
    icon = models.CharField(
        max_length=50,
        default='fas fa-exchange-alt',
        verbose_name=_("Icon Class (FontAwesome)")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Remittance Service")
        verbose_name_plural = _("Remittance Services")
        ordering = ['service_type']
    
    def __str__(self):
        return self.name


class MemberRelief(models.Model):
    """Model for member relief and support programs"""
    
    RELIEF_TYPES = [
        ('medical', 'Medical Relief'),
        ('education', 'Educational Support'),
        ('disaster', 'Disaster Relief'),
        ('welfare', 'Welfare Support'),
        ('emergency', 'Emergency Assistance'),
    ]
    
    relief_type = models.CharField(
        max_length=20,
        choices=RELIEF_TYPES,
        verbose_name=_("Relief Type")
    )
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    nepali_title = models.CharField(max_length=200, verbose_name=_("Nepali Title"))
    description = models.TextField(verbose_name=_("Description"))
    eligibility = models.TextField(verbose_name=_("Eligibility Criteria"))
    benefits = models.TextField(verbose_name=_("Benefits & Support"))
    application_process = models.TextField(blank=True, verbose_name=_("Application Process"))
    required_documents = models.TextField(blank=True, verbose_name=_("Required Documents"))
    contact_info = models.TextField(blank=True, verbose_name=_("Contact Information"))
    image = models.ImageField(
        upload_to='services/relief/',
        null=True,
        blank=True,
        verbose_name=_("Relief Image")
    )
    icon = models.CharField(
        max_length=50,
        default='fas fa-heart',
        verbose_name=_("Icon Class (FontAwesome)")
    )
    color = models.CharField(
        max_length=20,
        default='bhanjyangred',
        verbose_name=_("Color Theme")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Member Relief")
        verbose_name_plural = _("Member Relief Programs")
        ordering = ['relief_type', 'title']
    
    def __str__(self):
        return f"{self.get_relief_type_display()} - {self.title}"


class ServiceCategory(models.Model):
    """Model for organizing services into categories"""
    
    name = models.CharField(max_length=100, verbose_name=_("Category Name"))
    nepali_name = models.CharField(max_length=100, verbose_name=_("Nepali Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icon Class (FontAwesome)")
    )
    color = models.CharField(
        max_length=20,
        default='deuraligreen',
        verbose_name=_("Color Theme")
    )
    order = models.IntegerField(default=0, verbose_name=_("Display Order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Service Category")
        verbose_name_plural = _("Service Categories")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
