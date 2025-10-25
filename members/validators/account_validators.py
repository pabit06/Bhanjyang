"""
Account Validators

Validation logic for account-related operations.
"""

import logging
from typing import List, Dict, Any
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum

from ..models import MemberAccount, MemberTransaction, Member
from ..exceptions import ValidationException

logger = logging.getLogger('members.validators')


class AccountValidator:
    """
    Validator class for account-related operations.
    
    This validator handles:
    - Account creation validation
    - Transaction validation
    - Balance validation
    - Business rule validation
    """
    
    def __init__(self):
        self.min_account_balance = Decimal('0.00')
        self.max_transaction_amount = Decimal('1000000.00')  # 1 million NPR
        self.min_transaction_amount = Decimal('1.00')
    
    def validate_account_creation(self, data: Dict[str, Any], member: Member) -> List[str]:
        """
        Validate account creation data.
        
        Args:
            data: Dictionary containing account creation data
            member: Member instance
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate required fields
        if not data.get('account_type'):
            errors.append("Account type is required")
        
        # Validate account type
        if data.get('account_type'):
            errors.extend(self._validate_account_type(data['account_type']))
        
        # Validate member eligibility
        errors.extend(self._validate_member_eligibility(member))
        
        # Validate account limits
        if data.get('account_type'):
            errors.extend(self._validate_account_limits(member, data['account_type']))
        
        return errors
    
    def validate_transaction(self, data: Dict[str, Any], account: MemberAccount) -> List[str]:
        """
        Validate transaction data.
        
        Args:
            data: Dictionary containing transaction data
            account: MemberAccount instance
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate required fields
        required_fields = ['transaction_type', 'amount', 'description']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate transaction type
        if data.get('transaction_type'):
            errors.extend(self._validate_transaction_type(data['transaction_type']))
        
        # Validate amount
        if data.get('amount'):
            errors.extend(self._validate_amount(data['amount']))
        
        # Validate account status
        errors.extend(self._validate_account_status(account))
        
        # Validate balance for withdrawals
        if data.get('transaction_type') in ['withdrawal', 'transfer_out'] and data.get('amount'):
            errors.extend(self._validate_sufficient_balance(account, data['amount']))
        
        return errors
    
    def validate_account_closure(self, account: MemberAccount, reason: str) -> List[str]:
        """
        Validate account closure request.
        
        Args:
            account: MemberAccount instance
            reason: Reason for closure
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate account status
        if not account.is_active:
            errors.append("Account is already closed")
        
        # Validate balance
        if account.balance != Decimal('0.00'):
            errors.append("Account must have zero balance to be closed")
        
        # Validate reason
        if not reason or len(reason.strip()) < 10:
            errors.append("Closure reason must be at least 10 characters long")
        
        # Check for pending transactions
        pending_transactions = MemberTransaction.objects.filter(
            account=account,
            transaction_date__gte=timezone.now() - timezone.timedelta(days=1)
        )
        
        if pending_transactions.exists():
            errors.append("Account has recent transactions. Please wait before closing")
        
        return errors
    
    def validate_transfer(self, from_account: MemberAccount, to_account: MemberAccount, 
                         amount: Decimal) -> List[str]:
        """
        Validate transfer between accounts.
        
        Args:
            from_account: Source account
            to_account: Destination account
            amount: Transfer amount
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate accounts
        if from_account == to_account:
            errors.append("Cannot transfer to the same account")
        
        if not from_account.is_active:
            errors.append("Source account is not active")
        
        if not to_account.is_active:
            errors.append("Destination account is not active")
        
        # Validate amount
        errors.extend(self._validate_amount(amount))
        
        # Validate sufficient balance
        errors.extend(self._validate_sufficient_balance(from_account, amount))
        
        # Validate transfer limits
        errors.extend(self._validate_transfer_limits(from_account, amount))
        
        return errors
    
    def _validate_account_type(self, account_type: str) -> List[str]:
        """Validate account type."""
        errors = []
        
        valid_types = ['savings', 'share', 'loan', 'fixed_deposit']
        if account_type not in valid_types:
            errors.append(f"Invalid account type. Must be one of: {valid_types}")
        
        return errors
    
    def _validate_transaction_type(self, transaction_type: str) -> List[str]:
        """Validate transaction type."""
        errors = []
        
        valid_types = [
            'deposit', 'withdrawal', 'transfer_in', 'transfer_out',
            'interest', 'fee', 'loan_disbursement', 'loan_repayment'
        ]
        
        if transaction_type not in valid_types:
            errors.append(f"Invalid transaction type. Must be one of: {valid_types}")
        
        return errors
    
    def _validate_amount(self, amount) -> List[str]:
        """Validate transaction amount."""
        errors = []
        
        try:
            amount_decimal = Decimal(str(amount))
            
            if amount_decimal <= self.min_transaction_amount:
                errors.append(f"Amount must be greater than {self.min_transaction_amount}")
            
            if amount_decimal > self.max_transaction_amount:
                errors.append(f"Amount cannot exceed {self.max_transaction_amount}")
            
        except (ValueError, TypeError):
            errors.append("Invalid amount format")
        
        return errors
    
    def _validate_member_eligibility(self, member: Member) -> List[str]:
        """Validate member eligibility for account creation."""
        errors = []
        
        if not member.is_active:
            errors.append("Member account is not active")
        
        if not member.is_verified:
            errors.append("Member account is not verified")
        
        return errors
    
    def _validate_account_status(self, account: MemberAccount) -> List[str]:
        """Validate account status."""
        errors = []
        
        if not account.is_active:
            errors.append("Account is not active")
        
        return errors
    
    def _validate_sufficient_balance(self, account: MemberAccount, amount: Decimal) -> List[str]:
        """Validate sufficient balance for transaction."""
        errors = []
        
        try:
            amount_decimal = Decimal(str(amount))
            
            if account.balance < amount_decimal:
                errors.append("Insufficient balance for transaction")
            
            # Check minimum balance requirement
            new_balance = account.balance - amount_decimal
            if new_balance < self.min_account_balance:
                errors.append(f"Transaction would result in balance below minimum requirement")
        
        except (ValueError, TypeError):
            errors.append("Invalid amount format")
        
        return errors
    
    def _validate_account_limits(self, member: Member, account_type: str) -> List[str]:
        """Validate account creation limits."""
        errors = []
        
        # Check existing accounts of same type
        existing_accounts = member.accounts.filter(
            account_type=account_type,
            is_active=True
        ).count()
        
        # Set limits based on account type
        limits = {
            'savings': 3,
            'share': 1,
            'loan': 5,
            'fixed_deposit': 10
        }
        
        max_accounts = limits.get(account_type, 1)
        
        if existing_accounts >= max_accounts:
            errors.append(f"Maximum {max_accounts} {account_type} account(s) allowed per member")
        
        return errors
    
    def _validate_transfer_limits(self, account: MemberAccount, amount: Decimal) -> List[str]:
        """Validate transfer limits."""
        errors = []
        
        # Daily transfer limit (could be configurable)
        daily_limit = Decimal('500000.00')  # 5 lakh NPR
        
        # Check daily transfer amount
        today = timezone.now().date()
        daily_transfers = MemberTransaction.objects.filter(
            account=account,
            transaction_type__in=['transfer_out'],
            transaction_date__date=today
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        if daily_transfers + amount > daily_limit:
            errors.append(f"Daily transfer limit exceeded. Limit: {daily_limit}")
        
        return errors
    
    def validate_interest_calculation(self, account: MemberAccount, interest_rate: Decimal) -> List[str]:
        """Validate interest calculation parameters."""
        errors = []
        
        if interest_rate < Decimal('0.00'):
            errors.append("Interest rate cannot be negative")
        
        if interest_rate > Decimal('20.00'):  # 20% maximum
            errors.append("Interest rate seems unrealistic")
        
        if not account.is_active:
            errors.append("Cannot calculate interest for inactive account")
        
        return errors
