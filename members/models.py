"""
Member Management Models for Bhanjyang Cooperative
Handles member registration, KYC, accounts, and CBS integration
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.urls import reverse
import uuid
from decimal import Decimal
from typing import Optional, Dict, Any

from .managers import (
    MemberManager, MemberRegistrationManager, 
    MemberAccountManager, MemberTransactionManager
)


# Temporarily using separate MemberProfile instead of custom User model
# class MemberUser(AbstractUser):
#     """
#     Custom User model extending Django's AbstractUser
#     Includes member-specific fields and relationships
#     """
#     
#     # Member-specific fields
#     member_id = models.CharField(
#         max_length=20, 
#         unique=True, 
#         null=True, 
#         blank=True,
#         help_text="Unique member identifier"
#     )
#     is_member = models.BooleanField(
#         default=False,
#         help_text="Whether this user is a cooperative member"
#     )
#     is_verified = models.BooleanField(
#         default=False,
#         help_text="Whether member status is verified"
#     )
#     phone_number = models.CharField(
#         max_length=15,
#         validators=[RegexValidator(
#             regex=r'^\+?1?\d{9,15}$',
#             message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
#         )],
#         help_text="Primary phone number"
#     )
#     
#     # Timestamps
#     member_since = models.DateTimeField(null=True, blank=True)
#     last_login_ip = models.GenericIPAddressField(null=True, blank=True)
#     
#     class Meta:
#         verbose_name = "Member User"
#         verbose_name_plural = "Member Users"
#         db_table = 'members_memberuser'
#     
#     def __str__(self):
#         return f"{self.username} ({self.member_id or 'Non-member'})"
#     
#     def save(self, *args, **kwargs):
#         if self.is_member and not self.member_id:
#             self.member_id = self.generate_member_id()
#         super().save(*args, **kwargs)
#     
#     def generate_member_id(self):
#         """Generate unique member ID"""
#         from datetime import datetime
#         year = datetime.now().year
#         last_member = MemberUser.objects.filter(
#             member_id__startswith=f"RUPA{year}"
#         ).order_by('-member_id').first()
#         
#         if last_member:
#             last_number = int(last_member.member_id[-4:])
#             new_number = last_number + 1
#         else:
#             new_number = 1
#         
#         return f"RUPA{year}{new_number:04d}"


class Ward(models.Model):
    """
    Ward model for Rupa Rural Municipality, Kaski
    Used for location verification during registration
    """
    
    ward_number = models.CharField(
        max_length=10, 
        unique=True,
        help_text="Ward number in Rupa RM"
    )
    ward_name = models.CharField(
        max_length=100,
        help_text="Ward name"
    )
    description = models.TextField(
        blank=True,
        help_text="Additional ward information"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this ward is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ward_number']
        verbose_name = "Ward"
        verbose_name_plural = "Wards"
    
    def __str__(self):
        return f"Ward {self.ward_number} - {self.ward_name}"


class MemberRegistration(models.Model):
    """
    Pre-membership registration with location verification
    Two-step process: Location verification → KYC approval
    """
    
    STATUS_CHOICES = [
        ('pending_location', 'Pending Location Verification'),
        ('location_verified', 'Location Verified'),
        ('kyc_pending', 'KYC Pending'),
        ('kyc_approved', 'KYC Approved'),
        ('member_active', 'Active Member'),
        ('rejected', 'Rejected'),
    ]
    
    # Custom manager
    objects = MemberRegistrationManager()
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    
    # Location Verification (CRITICAL for Rupa RM)
    permanent_address = models.TextField(
        help_text="Full permanent address"
    )
    ward = models.ForeignKey(
        Ward, 
        on_delete=models.PROTECT,
        help_text="Ward in Rupa RM"
    )
    tole_name = models.CharField(
        max_length=100,
        help_text="Tole/Village name"
    )
    
    # Verification
    location_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='location_verifications'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending_location'
    )
    
    # Documents for verification
    citizenship_document = models.FileField(
        upload_to='members/kyc/citizenship/', 
        null=True, 
        blank=True
    )
    address_proof = models.FileField(
        upload_to='members/kyc/address_proof/', 
        null=True, 
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Member Registration"
        verbose_name_plural = "Member Registrations"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_status_display()}"
    
    def get_absolute_url(self):
        return reverse('members:registration_status', kwargs={'pk': self.pk})


class Member(models.Model):
    """
    Active cooperative members
    Created after successful KYC approval
    """
    
    MEMBERSHIP_TYPES = [
        ('regular', 'Regular Member'),
        ('institutional', 'Institutional Member'),
        ('honorary', 'Honorary Member'),
    ]
    
    # Custom manager
    objects = MemberManager()
    
    # Link to User
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='member_profile'
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    
    # Address (Rupa RM specific)
    permanent_address = models.TextField()
    ward = models.ForeignKey(Ward, on_delete=models.PROTECT)
    tole_name = models.CharField(max_length=100)
    
    # Membership Details
    membership_type = models.CharField(
        max_length=20, 
        choices=MEMBERSHIP_TYPES, 
        default='regular'
    )
    membership_date = models.DateField()
    membership_fee_paid = models.BooleanField(default=False)
    membership_fee_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    
    # KYC Information
    citizenship_number = models.CharField(max_length=20, unique=True)
    citizenship_issue_date = models.DateField()
    citizenship_issue_district = models.CharField(max_length=50)
    
    # Family Information
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    spouse_name = models.CharField(max_length=100, blank=True)
    
    # Professional Information
    occupation = models.CharField(max_length=100)
    workplace = models.CharField(max_length=200, blank=True)
    monthly_income = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Documents
    profile_photo = models.ImageField(
        upload_to='members/photos/', 
        null=True, 
        blank=True
    )
    citizenship_document = models.FileField(
        upload_to='members/documents/citizenship/'
    )
    
    # CBS Integration
    cbs_member_id = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True
    )
    cbs_sync_status = models.CharField(
        max_length=20, 
        default='pending'
    )
    last_sync_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Member"
        verbose_name_plural = "Members"
    
    def __str__(self):
        return f"{self.user.member_id} - {self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('members:member_profile')
    
    def get_full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()
    
    def get_total_balance(self):
        """Get total balance across all active accounts."""
        return sum(account.balance for account in self.accounts.filter(is_active=True))
    
    def get_active_accounts_count(self):
        """Get count of active accounts."""
        return self.accounts.filter(is_active=True).count()
    
    def get_active_loans_count(self):
        """Get count of active loans."""
        return self.loans.filter(status__in=['active', 'disbursed']).count()
    
    def get_unread_notifications_count(self):
        """Get count of unread notifications."""
        return self.notifications.filter(is_read=False).count()
    
    def is_eligible_for_loan(self):
        """Check if member is eligible for loan."""
        return (
            self.is_active and 
            self.is_verified and 
            self.citizenship_number and
            self.get_total_balance() > Decimal('10000')  # Minimum balance requirement
        )
    
    def get_membership_duration_days(self):
        """Get membership duration in days."""
        if self.membership_date:
            return (timezone.now().date() - self.membership_date).days
        return 0
    
    def get_cbs_sync_status(self):
        """Get CBS sync status."""
        if self.cbs_member_id:
            return 'synced'
        return 'not_synced'
    
    def get_account_summary(self):
        """Get account summary for dashboard."""
        accounts = self.accounts.filter(is_active=True)
        return {
            'total_balance': self.get_total_balance(),
            'account_count': accounts.count(),
            'primary_account': accounts.filter(is_primary=True).first(),
            'account_types': list(accounts.values_list('account_type', flat=True).distinct())
        }


class KYCDocument(models.Model):
    """
    KYC documents for members
    Stores various document types with verification status
    """
    
    DOCUMENT_TYPES = [
        ('citizenship', 'Citizenship Certificate'),
        ('address_proof', 'Address Proof'),
        ('income_proof', 'Income Proof'),
        ('photo', 'Passport Photo'),
        ('other', 'Other Document'),
    ]
    
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='kyc_documents'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='members/kyc/')
    document_number = models.CharField(max_length=50, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "KYC Document"
        verbose_name_plural = "KYC Documents"
    
    def __str__(self):
        return f"{self.member.user.member_id} - {self.get_document_type_display()}"


class MemberAccount(models.Model):
    """
    Member's financial accounts
    Linked to CBS for real-time data
    """
    
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('share', 'Share Account'),
        ('loan', 'Loan Account'),
        ('fixed_deposit', 'Fixed Deposit Account'),
    ]
    
    # Custom manager
    objects = MemberAccountManager()
    
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='accounts'
    )
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=100, blank=True)
    
    # Financial Information
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    
    # CBS Integration
    cbs_account_id = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True
    )
    cbs_sync_status = models.CharField(
        max_length=20, 
        default='pending'
    )
    last_sync_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['account_type', 'account_number']
        verbose_name = "Member Account"
        verbose_name_plural = "Member Accounts"
    
    def __str__(self):
        return f"{self.member.user.member_id} - {self.get_account_type_display()} ({self.account_number})"


class MemberTransaction(models.Model):
    """
    Member transaction history
    Synced from CBS or created locally
    """
    
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('interest', 'Interest Credit'),
        ('fee', 'Fee'),
        ('loan_disbursement', 'Loan Disbursement'),
        ('loan_repayment', 'Loan Repayment'),
    ]
    
    # Custom manager
    objects = MemberTransactionManager()
    
    account = models.ForeignKey(
        MemberAccount, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Transaction Details
    description = models.CharField(max_length=200)
    reference_number = models.CharField(max_length=50, blank=True)
    transaction_date = models.DateTimeField()
    
    # CBS Integration
    cbs_transaction_id = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True
    )
    is_cbs_synced = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "Member Transaction"
        verbose_name_plural = "Member Transactions"
    
    def __str__(self):
        return f"{self.account.account_number} - {self.get_transaction_type_display()} - {self.amount}"


class MemberLoan(models.Model):
    """
    Member loan applications and management
    Integrated with CBS for loan processing
    """
    
    LOAN_STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]
    
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='loans'
    )
    loan_type = models.CharField(max_length=100)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tenure_months = models.IntegerField()
    
    # Loan Details
    purpose = models.TextField()
    monthly_installment = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=LOAN_STATUS_CHOICES, 
        default='applied'
    )
    
    # CBS Integration
    cbs_loan_id = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True
    )
    cbs_sync_status = models.CharField(
        max_length=20, 
        default='pending'
    )
    
    # Timestamps
    applied_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    disbursed_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-applied_date']
        verbose_name = "Member Loan"
        verbose_name_plural = "Member Loans"
    
    def __str__(self):
        return f"{self.member.user.member_id} - {self.loan_type} - {self.loan_amount}"


class MemberNotification(models.Model):
    """
    Member notifications and messages
    """
    
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]
    
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=10, 
        choices=NOTIFICATION_TYPES, 
        default='info'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Member Notification"
        verbose_name_plural = "Member Notifications"
    
    def __str__(self):
        return f"{self.member.user.member_id} - {self.title}"