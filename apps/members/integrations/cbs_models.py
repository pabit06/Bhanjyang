"""
CBS Integration Models
Mirrors CBS data structure for synchronization
"""

from django.db import models
from django.utils import timezone
from decimal import Decimal
from typing import Optional, Dict, Any


class CBSAccount(models.Model):
    """
    CBS Account data mirror
    Stores account information from CBS
    """
    
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('share', 'Share Account'),
        ('loan', 'Loan Account'),
        ('fixed_deposit', 'Fixed Deposit Account'),
    ]
    
    # CBS Identifiers
    cbs_account_id = models.CharField(max_length=50, unique=True)
    cbs_member_id = models.CharField(max_length=50)
    
    # Account Information
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_name = models.CharField(max_length=100)
    
    # Financial Data
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    available_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Status
    status = models.CharField(max_length=20, default='active')
    is_active = models.BooleanField(default=True)
    
    # CBS Timestamps
    cbs_created_date = models.DateTimeField()
    cbs_last_updated = models.DateTimeField()
    
    # Local Sync Info
    last_sync_date = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, default='synced')
    
    class Meta:
        ordering = ['account_number']
        verbose_name = "CBS Account"
        verbose_name_plural = "CBS Accounts"
    
    def __str__(self):
        return f"CBS {self.account_number} - {self.account_name}"


class CBSTransaction(models.Model):
    """
    CBS Transaction data mirror
    Stores transaction information from CBS
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
    
    # CBS Identifiers
    cbs_transaction_id = models.CharField(max_length=50, unique=True)
    cbs_account_id = models.CharField(max_length=50)
    
    # Transaction Information
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
    
    # CBS Timestamps
    cbs_created_date = models.DateTimeField()
    
    # Local Sync Info
    last_sync_date = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, default='synced')
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "CBS Transaction"
        verbose_name_plural = "CBS Transactions"
    
    def __str__(self):
        return f"CBS {self.cbs_transaction_id} - {self.get_transaction_type_display()}"


class CBSLoan(models.Model):
    """
    CBS Loan data mirror
    Stores loan information from CBS
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
    
    # CBS Identifiers
    cbs_loan_id = models.CharField(max_length=50, unique=True)
    cbs_member_id = models.CharField(max_length=50)
    
    # Loan Information
    loan_type = models.CharField(max_length=100)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    disbursed_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    outstanding_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
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
    
    # CBS Timestamps
    cbs_applied_date = models.DateTimeField()
    cbs_approved_date = models.DateTimeField(null=True, blank=True)
    cbs_disbursed_date = models.DateTimeField(null=True, blank=True)
    
    # Local Sync Info
    last_sync_date = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, default='synced')
    
    class Meta:
        ordering = ['-cbs_applied_date']
        verbose_name = "CBS Loan"
        verbose_name_plural = "CBS Loans"
    
    def __str__(self):
        return f"CBS {self.cbs_loan_id} - {self.loan_type}"


class CBSMember(models.Model):
    """
    CBS Member data mirror
    Stores member information from CBS
    """
    
    # CBS Identifiers
    cbs_member_id = models.CharField(max_length=50, unique=True)
    
    # Member Information
    member_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    
    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # Address
    permanent_address = models.TextField()
    ward_number = models.CharField(max_length=10)
    
    # Membership Details
    membership_date = models.DateField()
    membership_type = models.CharField(max_length=20, default='regular')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # CBS Timestamps
    cbs_created_date = models.DateTimeField()
    cbs_last_updated = models.DateTimeField()
    
    # Local Sync Info
    last_sync_date = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, default='synced')
    
    class Meta:
        ordering = ['member_id']
        verbose_name = "CBS Member"
        verbose_name_plural = "CBS Members"
    
    def __str__(self):
        return f"CBS {self.member_id} - {self.first_name} {self.last_name}"


class CBSSyncLog(models.Model):
    """
    CBS Synchronization Log
    Tracks sync operations and their status
    """
    
    SYNC_TYPES = [
        ('member', 'Member Sync'),
        ('account', 'Account Sync'),
        ('transaction', 'Transaction Sync'),
        ('loan', 'Loan Sync'),
        ('full', 'Full Sync'),
    ]
    
    SYNC_STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partial Success'),
    ]
    
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    sync_status = models.CharField(
        max_length=20, 
        choices=SYNC_STATUS_CHOICES, 
        default='started'
    )
    
    # Sync Details
    records_processed = models.IntegerField(default=0)
    records_successful = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    # Error Information
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(null=True, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "CBS Sync Log"
        verbose_name_plural = "CBS Sync Logs"
    
    def __str__(self):
        return f"{self.get_sync_type_display()} - {self.get_sync_status_display()} ({self.started_at})"
