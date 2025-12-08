"""
Account DTOs

Data Transfer Objects for account-related operations.
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from django.utils import timezone


@dataclass
class AccountCreationDTO:
    """DTO for account creation data."""
    account_type: str
    account_name: Optional[str] = None
    interest_rate: Optional[Decimal] = None
    is_primary: bool = False
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.account_type:
            raise ValueError("Account type is required")
        
        valid_types = ['savings', 'share', 'loan', 'fixed_deposit']
        if self.account_type not in valid_types:
            raise ValueError(f"Invalid account type. Must be one of: {valid_types}")


@dataclass
class TransactionDTO:
    """DTO for transaction data."""
    transaction_type: str
    amount: Decimal
    description: str
    reference_number: Optional[str] = None
    transaction_date: Optional[timezone.datetime] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.transaction_type:
            raise ValueError("Transaction type is required")
        if not self.amount or self.amount <= 0:
            raise ValueError("Amount must be positive")
        if not self.description:
            raise ValueError("Description is required")
        
        valid_types = [
            'deposit', 'withdrawal', 'transfer_in', 'transfer_out',
            'interest', 'fee', 'loan_disbursement', 'loan_repayment'
        ]
        if self.transaction_type not in valid_types:
            raise ValueError(f"Invalid transaction type. Must be one of: {valid_types}")
