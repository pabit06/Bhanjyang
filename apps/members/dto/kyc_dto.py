"""
KYC DTOs

Data Transfer Objects for KYC-related operations.
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from datetime import date
from django.core.files.uploadedfile import UploadedFile


@dataclass
class KYCDocumentDTO:
    """DTO for KYC document upload data."""
    citizenship_number: str
    citizenship_issue_date: date
    citizenship_issue_district: str
    father_name: str
    mother_name: str
    spouse_name: Optional[str] = None
    occupation: str = ""
    workplace: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    citizenship_document: Optional[UploadedFile] = None
    address_proof: Optional[UploadedFile] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.citizenship_number:
            raise ValueError("Citizenship number is required")
        if not self.citizenship_issue_date:
            raise ValueError("Citizenship issue date is required")
        if not self.citizenship_issue_district:
            raise ValueError("Citizenship issue district is required")
        if not self.father_name:
            raise ValueError("Father's name is required")
        if not self.mother_name:
            raise ValueError("Mother's name is required")
        if not self.occupation:
            raise ValueError("Occupation is required")


@dataclass
class KYCVerificationDTO:
    """DTO for KYC verification data."""
    approved: bool
    verification_notes: Optional[str] = None
    compliance_notes: Optional[str] = None
    document_quality_score: Optional[int] = None
    data_consistency_score: Optional[int] = None
    
    def __post_init__(self):
        """Validate scores if provided."""
        if self.document_quality_score is not None:
            if not (0 <= self.document_quality_score <= 100):
                raise ValueError("Document quality score must be between 0 and 100")
        
        if self.data_consistency_score is not None:
            if not (0 <= self.data_consistency_score <= 100):
                raise ValueError("Data consistency score must be between 0 and 100")
