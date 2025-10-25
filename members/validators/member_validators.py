"""
Member Validators

Validation logic for member-related operations.
"""

import re
import logging
from typing import List, Dict, Any
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from ..models import Member, MemberRegistration, Ward
from ..exceptions import ValidationException

logger = logging.getLogger('members.validators')


class MemberValidator:
    """
    Validator class for member-related operations.
    
    This validator handles:
    - Member data validation
    - Registration validation
    - Business rule validation
    - Format validation
    """
    
    def __init__(self):
        self.phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.nepali_name_pattern = re.compile(r'^[\u0900-\u097F\s]+$')
        self.english_name_pattern = re.compile(r'^[a-zA-Z\s]+$')
    
    def validate_registration_data(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate member registration data.
        
        Args:
            data: Dictionary containing registration data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'phone', 'permanent_address', 'ward_id', 'tole_name']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate name fields
        if data.get('first_name'):
            errors.extend(self._validate_name(data['first_name'], 'First name'))
        if data.get('last_name'):
            errors.extend(self._validate_name(data['last_name'], 'Last name'))
        if data.get('middle_name'):
            errors.extend(self._validate_name(data['middle_name'], 'Middle name'))
        
        # Validate email
        if data.get('email'):
            errors.extend(self._validate_email(data['email']))
        
        # Validate phone
        if data.get('phone'):
            errors.extend(self._validate_phone(data['phone']))
        
        # Validate ward
        if data.get('ward_id'):
            errors.extend(self._validate_ward(data['ward_id']))
        
        # Check for duplicate email
        if data.get('email'):
            errors.extend(self._check_email_uniqueness(data['email']))
        
        # Check for duplicate phone
        if data.get('phone'):
            errors.extend(self._check_phone_uniqueness(data['phone']))
        
        return errors
    
    def validate_profile_update_data(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate member profile update data.
        
        Args:
            data: Dictionary containing profile update data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'phone', 'permanent_address', 'tole_name']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate name fields
        if data.get('first_name'):
            errors.extend(self._validate_name(data['first_name'], 'First name'))
        if data.get('last_name'):
            errors.extend(self._validate_name(data['last_name'], 'Last name'))
        if data.get('middle_name'):
            errors.extend(self._validate_name(data['middle_name'], 'Middle name'))
        
        # Validate phone
        if data.get('phone'):
            errors.extend(self._validate_phone(data['phone']))
        
        # Validate alternate phone
        if data.get('alternate_phone'):
            errors.extend(self._validate_phone(data['alternate_phone']))
        
        # Validate monthly income
        if data.get('monthly_income'):
            errors.extend(self._validate_monthly_income(data['monthly_income']))
        
        return errors
    
    def validate_member_eligibility(self, member: Member) -> List[str]:
        """
        Validate member eligibility for various operations.
        
        Args:
            member: Member instance
            
        Returns:
            List of validation errors (empty if eligible)
        """
        errors = []
        
        if not member.is_active:
            errors.append("Member account is not active")
        
        if not member.is_verified:
            errors.append("Member account is not verified")
        
        if not member.citizenship_number:
            errors.append("Citizenship number is required")
        
        if not member.father_name:
            errors.append("Father's name is required")
        
        if not member.mother_name:
            errors.append("Mother's name is required")
        
        return errors
    
    def _validate_name(self, name: str, field_name: str) -> List[str]:
        """Validate name field."""
        errors = []
        
        if len(name.strip()) < 2:
            errors.append(f"{field_name} must be at least 2 characters long")
        
        if len(name.strip()) > 100:
            errors.append(f"{field_name} must not exceed 100 characters")
        
        # Check for valid characters (allow both English and Nepali)
        if not (self.nepali_name_pattern.match(name) or self.english_name_pattern.match(name)):
            errors.append(f"{field_name} contains invalid characters")
        
        return errors
    
    def _validate_email(self, email: str) -> List[str]:
        """Validate email address."""
        errors = []
        
        if not self.email_pattern.match(email):
            errors.append("Invalid email format")
        
        if len(email) > 254:
            errors.append("Email address is too long")
        
        return errors
    
    def _validate_phone(self, phone: str) -> List[str]:
        """Validate phone number."""
        errors = []
        
        if not self.phone_pattern.match(phone):
            errors.append("Invalid phone number format. Use format: +977XXXXXXXXX")
        
        return errors
    
    def _validate_ward(self, ward_id: int) -> List[str]:
        """Validate ward ID."""
        errors = []
        
        try:
            ward = Ward.objects.get(id=ward_id)
            if not ward.is_active:
                errors.append("Selected ward is not active")
        except Ward.DoesNotExist:
            errors.append("Invalid ward selected")
        
        return errors
    
    def _validate_monthly_income(self, income) -> List[str]:
        """Validate monthly income."""
        errors = []
        
        try:
            income_decimal = float(income)
            if income_decimal < 0:
                errors.append("Monthly income cannot be negative")
            if income_decimal > 1000000:  # 1 million NPR
                errors.append("Monthly income seems unrealistic")
        except (ValueError, TypeError):
            errors.append("Invalid monthly income format")
        
        return errors
    
    def _check_email_uniqueness(self, email: str) -> List[str]:
        """Check if email is already in use."""
        errors = []
        
        if User.objects.filter(email=email).exists():
            errors.append("Email address is already registered")
        
        if MemberRegistration.objects.filter(email=email).exists():
            errors.append("Email address is already registered")
        
        return errors
    
    def _check_phone_uniqueness(self, phone: str) -> List[str]:
        """Check if phone number is already in use."""
        errors = []
        
        if MemberRegistration.objects.filter(phone=phone).exists():
            errors.append("Phone number is already registered")
        
        return errors
    
    def validate_member_deactivation(self, member: Member, reason: str) -> List[str]:
        """
        Validate member deactivation request.
        
        Args:
            member: Member instance
            reason: Reason for deactivation
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not reason or len(reason.strip()) < 10:
            errors.append("Deactivation reason must be at least 10 characters long")
        
        # Check if member has active loans
        active_loans = member.loans.filter(status__in=['active', 'disbursed'])
        if active_loans.exists():
            errors.append("Cannot deactivate member with active loans")
        
        # Check if member has significant balance
        total_balance = sum(account.balance for account in member.accounts.filter(is_active=True))
        if total_balance > 10000:  # 10,000 NPR threshold
            errors.append("Member has significant account balance. Please transfer funds before deactivation")
        
        return errors
