"""
KYC Validators

Validation logic for KYC-related operations.
"""

import re
import logging
from typing import List, Dict, Any
from django.core.files.uploadedfile import UploadedFile

from ..models import MemberRegistration
from ..exceptions import ValidationException

logger = logging.getLogger('members.validators')


class KYCValidator:
    """
    Validator class for KYC-related operations.
    
    This validator handles:
    - Document validation
    - KYC data validation
    - Compliance checks
    - Format validation
    """
    
    def __init__(self):
        self.citizenship_pattern = re.compile(r'^[0-9]{1,2}-[0-9]{2}-[0-9]{5}$')
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_file_types = [
            'application/pdf',
            'image/jpeg',
            'image/jpg',
            'image/png'
        ]
    
    def validate_kyc_documents(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate KYC document data.
        
        Args:
            data: Dictionary containing KYC document data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate required fields
        required_fields = [
            'citizenship_number', 'citizenship_issue_date', 'citizenship_issue_district',
            'father_name', 'mother_name', 'occupation'
        ]
        
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate citizenship number
        if data.get('citizenship_number'):
            errors.extend(self._validate_citizenship_number(data['citizenship_number']))
        
        # Validate names
        if data.get('father_name'):
            errors.extend(self._validate_name(data['father_name'], "Father's name"))
        if data.get('mother_name'):
            errors.extend(self._validate_name(data['mother_name'], "Mother's name"))
        if data.get('spouse_name'):
            errors.extend(self._validate_name(data['spouse_name'], "Spouse's name"))
        
        # Validate occupation
        if data.get('occupation'):
            errors.extend(self._validate_occupation(data['occupation']))
        
        # Validate documents
        if data.get('citizenship_document'):
            errors.extend(self._validate_document(data['citizenship_document']))
        
        if data.get('address_proof'):
            errors.extend(self._validate_document(data['address_proof']))
        
        # Check for duplicate citizenship number
        if data.get('citizenship_number'):
            errors.extend(self._check_citizenship_uniqueness(data['citizenship_number']))
        
        return errors
    
    def validate_document_file(self, file: UploadedFile) -> List[str]:
        """
        Validate uploaded document file.
        
        Args:
            file: UploadedFile instance
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check file size
        if file.size > self.max_file_size:
            errors.append(f"File size exceeds {self.max_file_size // (1024*1024)}MB limit")
        
        # Check file type
        if file.content_type not in self.allowed_file_types:
            errors.append("Only PDF, JPG, JPEG, and PNG files are allowed")
        
        # Check file name
        if not file.name or len(file.name.strip()) == 0:
            errors.append("File name is required")
        
        # Check for suspicious file extensions
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
        if any(file.name.lower().endswith(ext) for ext in suspicious_extensions):
            errors.append("File type not allowed for security reasons")
        
        return errors
    
    def validate_verification_data(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate KYC verification data.
        
        Args:
            data: Dictionary containing verification data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate approval decision
        if 'approved' not in data:
            errors.append("Approval decision is required")
        
        # Validate verification notes
        if data.get('verification_notes'):
            if len(data['verification_notes'].strip()) < 10:
                errors.append("Verification notes must be at least 10 characters long")
        
        # Validate scores
        if data.get('document_quality_score'):
            score = data['document_quality_score']
            if not isinstance(score, int) or not (0 <= score <= 100):
                errors.append("Document quality score must be between 0 and 100")
        
        if data.get('data_consistency_score'):
            score = data['data_consistency_score']
            if not isinstance(score, int) or not (0 <= score <= 100):
                errors.append("Data consistency score must be between 0 and 100")
        
        return errors
    
    def validate_citizenship_number_format(self, citizenship_number: str) -> bool:
        """
        Validate Nepali citizenship number format.
        
        Args:
            citizenship_number: Citizenship number to validate
            
        Returns:
            bool: True if valid format
        """
        return bool(self.citizenship_pattern.match(citizenship_number))
    
    def _validate_citizenship_number(self, citizenship_number: str) -> List[str]:
        """Validate citizenship number."""
        errors = []
        
        if not self.validate_citizenship_number_format(citizenship_number):
            errors.append("Invalid citizenship number format. Use format: XX-XX-XXXXX")
        
        return errors
    
    def _validate_name(self, name: str, field_name: str) -> List[str]:
        """Validate name field."""
        errors = []
        
        if len(name.strip()) < 2:
            errors.append(f"{field_name} must be at least 2 characters long")
        
        if len(name.strip()) > 100:
            errors.append(f"{field_name} must not exceed 100 characters")
        
        # Check for valid characters (allow both English and Nepali)
        nepali_pattern = re.compile(r'^[\u0900-\u097F\s]+$')
        english_pattern = re.compile(r'^[a-zA-Z\s]+$')
        
        if not (nepali_pattern.match(name) or english_pattern.match(name)):
            errors.append(f"{field_name} contains invalid characters")
        
        return errors
    
    def _validate_occupation(self, occupation: str) -> List[str]:
        """Validate occupation field."""
        errors = []
        
        if len(occupation.strip()) < 2:
            errors.append("Occupation must be at least 2 characters long")
        
        if len(occupation.strip()) > 100:
            errors.append("Occupation must not exceed 100 characters")
        
        return errors
    
    def _validate_document(self, file: UploadedFile) -> List[str]:
        """Validate document file."""
        return self.validate_document_file(file)
    
    def _check_citizenship_uniqueness(self, citizenship_number: str) -> List[str]:
        """Check if citizenship number is already in use."""
        errors = []
        
        if MemberRegistration.objects.filter(citizenship_number=citizenship_number).exists():
            errors.append("Citizenship number is already registered")
        
        return errors
    
    def validate_kyc_completeness(self, registration: MemberRegistration) -> List[str]:
        """
        Validate KYC completeness for a registration.
        
        Args:
            registration: MemberRegistration instance
            
        Returns:
            List of validation errors (empty if complete)
        """
        errors = []
        
        # Check required fields
        if not registration.citizenship_number:
            errors.append("Citizenship number is required")
        
        if not registration.citizenship_issue_date:
            errors.append("Citizenship issue date is required")
        
        if not registration.citizenship_issue_district:
            errors.append("Citizenship issue district is required")
        
        if not registration.father_name:
            errors.append("Father's name is required")
        
        if not registration.mother_name:
            errors.append("Mother's name is required")
        
        if not registration.occupation:
            errors.append("Occupation is required")
        
        # Check documents
        if not registration.citizenship_document:
            errors.append("Citizenship document is required")
        
        if not registration.address_proof:
            errors.append("Address proof document is required")
        
        return errors
    
    def validate_document_integrity(self, file: UploadedFile) -> Dict[str, Any]:
        """
        Validate document integrity and security.
        
        Args:
            file: UploadedFile instance
            
        Returns:
            Dict containing validation results
        """
        try:
            # Basic file validation
            errors = self.validate_document_file(file)
            
            if errors:
                return {
                    'valid': False,
                    'errors': errors
                }
            
            # Additional integrity checks could be added here
            # For example: virus scanning, content analysis, etc.
            
            return {
                'valid': True,
                'file_size': file.size,
                'content_type': file.content_type,
                'file_name': file.name
            }
            
        except Exception as e:
            logger.error(f"Error validating document integrity: {e}")
            return {
                'valid': False,
                'errors': ['Document validation failed']
            }
