"""
Account Service

Handles member account operations including account creation, balance management,
transaction processing, and account analytics. This service provides business
logic for all account-related operations.
"""

import logging
from typing import Optional, Dict, Any, List
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from ..models import Member, MemberAccount, MemberTransaction
from ..repositories import AccountRepository
from ..exceptions import AccountServiceException, ValidationException
from ..dto import AccountCreationDTO, TransactionDTO

logger = logging.getLogger('members.services')


class AccountService:
    """
    Service class for account-related operations.
    
    This service handles:
    - Account creation and management
    - Balance calculations
    - Transaction processing
    - Account analytics and reporting
    - Interest calculations
    """
    
    def __init__(self):
        self.account_repository = AccountRepository()
    
    def create_savings_account(self, member: Member, account_data: AccountCreationDTO) -> MemberAccount:
        """
        Create a new savings account for a member.
        
        Args:
            member: Member instance
            account_data: AccountCreationDTO containing account information
            
        Returns:
            MemberAccount: Created account instance
        """
        try:
            with transaction.atomic():
                # Validate member eligibility
                if not member.is_active or not member.is_verified:
                    raise ValidationException("Member must be active and verified to create accounts")
                
                # Generate account number
                account_number = self._generate_account_number(member, account_data.account_type)
                
                # Create account
                account = MemberAccount.objects.create(
                    member=member,
                    account_type=account_data.account_type,
                    account_number=account_number,
                    account_name=account_data.account_name or f"{member.get_full_name()} - {account_data.account_type.title()}",
                    balance=Decimal('0.00'),
                    interest_rate=account_data.interest_rate,
                    is_active=True,
                    is_primary=account_data.is_primary
                )
                
                # If this is set as primary, unset other primary accounts
                if account_data.is_primary:
                    self._set_primary_account(account)
                
                logger.info(f"Account created for member {member.id}: {account_number}")
                return account
                
        except Exception as e:
            logger.error(f"Error creating savings account: {e}")
            raise AccountServiceException(f"Failed to create account: {str(e)}")
    
    def process_transaction(self, account: MemberAccount, transaction_data: TransactionDTO) -> MemberTransaction:
        """
        Process a transaction for an account.
        
        Args:
            account: MemberAccount instance
            transaction_data: TransactionDTO containing transaction information
            
        Returns:
            MemberTransaction: Created transaction instance
        """
        try:
            with transaction.atomic():
                # Validate transaction
                self._validate_transaction(account, transaction_data)
                
                # Calculate new balance
                if transaction_data.transaction_type in ['deposit', 'transfer_in', 'interest']:
                    new_balance = account.balance + transaction_data.amount
                elif transaction_data.transaction_type in ['withdrawal', 'transfer_out', 'fee']:
                    new_balance = account.balance - transaction_data.amount
                else:
                    raise ValidationException("Invalid transaction type")
                
                # Check minimum balance for withdrawals
                if transaction_data.transaction_type in ['withdrawal', 'transfer_out']:
                    self._check_minimum_balance(account, new_balance)
                
                # Create transaction record
                transaction_record = MemberTransaction.objects.create(
                    account=account,
                    transaction_type=transaction_data.transaction_type,
                    amount=transaction_data.amount,
                    balance_after=new_balance,
                    description=transaction_data.description,
                    reference_number=transaction_data.reference_number,
                    transaction_date=transaction_data.transaction_date or timezone.now()
                )
                
                # Update account balance
                account.balance = new_balance
                account.save()
                
                logger.info(f"Transaction processed for account {account.account_number}: {transaction_data.transaction_type}")
                return transaction_record
                
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            raise AccountServiceException(f"Failed to process transaction: {str(e)}")
    
    def get_account_statement(self, account: MemberAccount, from_date: Optional[timezone.datetime] = None, 
                            to_date: Optional[timezone.datetime] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Get account statement with transactions.
        
        Args:
            account: MemberAccount instance
            from_date: Start date for statement
            to_date: End date for statement
            limit: Maximum number of transactions
            
        Returns:
            Dict containing statement data
        """
        try:
            # Set default date range if not provided
            if not from_date:
                from_date = timezone.now().replace(day=1)  # First day of current month
            if not to_date:
                to_date = timezone.now()
            
            # Get transactions
            transactions = self.account_repository.get_transactions_in_range(
                account, from_date, to_date, limit
            )
            
            # Calculate summary
            total_deposits = sum(
                t.amount for t in transactions 
                if t.transaction_type in ['deposit', 'transfer_in', 'interest']
            )
            total_withdrawals = sum(
                t.amount for t in transactions 
                if t.transaction_type in ['withdrawal', 'transfer_out', 'fee']
            )
            
            return {
                'account': account,
                'transactions': transactions,
                'opening_balance': account.balance - total_deposits + total_withdrawals,
                'closing_balance': account.balance,
                'total_deposits': total_deposits,
                'total_withdrawals': total_withdrawals,
                'transaction_count': transactions.count(),
                'from_date': from_date,
                'to_date': to_date
            }
            
        except Exception as e:
            logger.error(f"Error getting account statement: {e}")
            raise AccountServiceException(f"Failed to get account statement: {str(e)}")
    
    def calculate_interest(self, account: MemberAccount, period_days: int = 365) -> Decimal:
        """
        Calculate interest for an account.
        
        Args:
            account: MemberAccount instance
            period_days: Number of days for interest calculation
            
        Returns:
            Decimal: Calculated interest amount
        """
        try:
            if not account.interest_rate:
                return Decimal('0.00')
            
            # Simple interest calculation: Principal * Rate * Time
            # Rate is annual, so we convert to daily rate
            daily_rate = account.interest_rate / Decimal('365')
            interest = account.balance * daily_rate * Decimal(str(period_days))
            
            return interest.quantize(Decimal('0.01'))
            
        except Exception as e:
            logger.error(f"Error calculating interest: {e}")
            return Decimal('0.00')
    
    def get_account_summary(self, member: Member) -> Dict[str, Any]:
        """
        Get account summary for a member.
        
        Args:
            member: Member instance
            
        Returns:
            Dict containing account summary
        """
        try:
            accounts = member.accounts.filter(is_active=True)
            
            total_balance = sum(account.balance for account in accounts)
            account_count = accounts.count()
            
            # Get account types breakdown
            account_types = {}
            for account in accounts:
                account_type = account.get_account_type_display()
                if account_type not in account_types:
                    account_types[account_type] = {
                        'count': 0,
                        'total_balance': Decimal('0.00')
                    }
                account_types[account_type]['count'] += 1
                account_types[account_type]['total_balance'] += account.balance
            
            # Get recent transactions
            recent_transactions = self.account_repository.get_recent_transactions_for_member(member, limit=5)
            
            return {
                'total_balance': total_balance,
                'account_count': account_count,
                'account_types': account_types,
                'recent_transactions': recent_transactions,
                'primary_account': accounts.filter(is_primary=True).first()
            }
            
        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            raise AccountServiceException(f"Failed to get account summary: {str(e)}")
    
    def close_account(self, account: MemberAccount, reason: str, closed_by: User) -> MemberAccount:
        """
        Close an account.
        
        Args:
            account: MemberAccount instance
            reason: Reason for closing
            closed_by: User who closed the account
            
        Returns:
            MemberAccount: Updated account instance
        """
        try:
            with transaction.atomic():
                # Check if account has zero balance
                if account.balance != Decimal('0.00'):
                    raise ValidationException("Account must have zero balance to be closed")
                
                # Close account
                account.is_active = False
                account.save()
                
                logger.info(f"Account closed: {account.account_number} by {closed_by.username}")
                return account
                
        except Exception as e:
            logger.error(f"Error closing account: {e}")
            raise AccountServiceException(f"Failed to close account: {str(e)}")
    
    def _generate_account_number(self, member: Member, account_type: str) -> str:
        """Generate unique account number."""
        # Format: YYYYMMDD + Member ID + Account Type Code + Sequence
        from datetime import datetime
        
        date_prefix = datetime.now().strftime('%Y%m%d')
        member_id = str(member.id).zfill(4)
        
        type_codes = {
            'savings': '01',
            'share': '02',
            'loan': '03',
            'fixed_deposit': '04'
        }
        
        type_code = type_codes.get(account_type, '99')
        
        # Get next sequence number for this combination
        last_account = MemberAccount.objects.filter(
            account_number__startswith=f"{date_prefix}{member_id}{type_code}"
        ).order_by('-account_number').first()
        
        if last_account:
            sequence = int(last_account.account_number[-3:]) + 1
        else:
            sequence = 1
        
        return f"{date_prefix}{member_id}{type_code}{sequence:03d}"
    
    def _set_primary_account(self, account: MemberAccount) -> None:
        """Set account as primary and unset others."""
        MemberAccount.objects.filter(
            member=account.member,
            is_primary=True
        ).update(is_primary=False)
        
        account.is_primary = True
        account.save()
    
    def _validate_transaction(self, account: MemberAccount, transaction_data: TransactionDTO) -> None:
        """Validate transaction data."""
        if not account.is_active:
            raise ValidationException("Account is not active")
        
        if transaction_data.amount <= Decimal('0.00'):
            raise ValidationException("Transaction amount must be positive")
        
        if not transaction_data.description:
            raise ValidationException("Transaction description is required")
    
    def _check_minimum_balance(self, account: MemberAccount, new_balance: Decimal) -> None:
        """Check minimum balance requirement."""
        # This could be enhanced to check account-specific minimum balance rules
        if new_balance < Decimal('0.00'):
            raise ValidationException("Insufficient balance for transaction")
