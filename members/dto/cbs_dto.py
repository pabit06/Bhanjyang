"""
CBS DTOs

Data Transfer Objects for CBS integration operations.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date


@dataclass
class CBSMemberDTO:
    """DTO for CBS member data."""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: str = ""
    phone: str = ""
    citizenship_number: str = ""
    citizenship_issue_date: Optional[date] = None
    citizenship_issue_district: str = ""
    father_name: str = ""
    mother_name: str = ""
    occupation: str = ""
    permanent_address: str = ""
    ward_number: str = ""
    tole_name: str = ""
    membership_date: Optional[date] = None
    membership_type: str = "regular"


@dataclass
class CBSAccountDTO:
    """DTO for CBS account data."""
    account_id: str
    account_number: str
    account_type: str
    account_name: str
    balance: Decimal
    interest_rate: Optional[Decimal] = None
    is_active: bool = True


@dataclass
class CBSTransactionDTO:
    """DTO for CBS transaction data."""
    transaction_id: str
    account_number: str
    transaction_type: str
    amount: Decimal
    balance_after: Decimal
    description: str
    reference_number: Optional[str] = None
    transaction_date: str = ""


@dataclass
class CBSLoanDTO:
    """DTO for CBS loan data."""
    member_id: str
    loan_type: str
    loan_amount: Decimal
    purpose: str
    tenure_months: int
    interest_rate: Optional[Decimal] = None
    monthly_installment: Optional[Decimal] = None
    loan_id: Optional[str] = None
