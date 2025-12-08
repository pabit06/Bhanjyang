"""
Member DTOs

Data Transfer Objects for member-related operations.
These DTOs provide a clean interface for data transfer
between different layers of the application.
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from django.core.files.uploadedfile import UploadedFile


@dataclass
class MemberRegistrationDTO:
    """DTO for member registration data."""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: str = ""
    phone: str = ""
    permanent_address: str = ""
    ward_id: int = 0
    tole_name: str = ""
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.first_name:
            raise ValueError("First name is required")
        if not self.last_name:
            raise ValueError("Last name is required")
        if not self.email:
            raise ValueError("Email is required")
        if not self.phone:
            raise ValueError("Phone is required")
        if not self.permanent_address:
            raise ValueError("Permanent address is required")
        if not self.ward_id:
            raise ValueError("Ward is required")
        if not self.tole_name:
            raise ValueError("Tole name is required")


@dataclass
class MemberProfileDTO:
    """DTO for member profile updates."""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: str = ""
    alternate_phone: Optional[str] = None
    permanent_address: str = ""
    tole_name: str = ""
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    spouse_name: Optional[str] = None
    occupation: Optional[str] = None
    workplace: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    profile_photo: Optional[UploadedFile] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.first_name:
            raise ValueError("First name is required")
        if not self.last_name:
            raise ValueError("Last name is required")
        if not self.phone:
            raise ValueError("Phone is required")
        if not self.permanent_address:
            raise ValueError("Permanent address is required")
        if not self.tole_name:
            raise ValueError("Tole name is required")
